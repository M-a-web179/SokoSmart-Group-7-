"use strict";

const $ = (sel) => document.querySelector(sel);

async function getJSON(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url} -> ${res.status}`);
  return res.json();
}

function fmt(n) {
  return Number(n).toLocaleString("en", { maximumFractionDigits: 2 });
}

async function checkHealth() {
  const badge = $("#health");
  try {
    const data = await getJSON("/health");
    badge.textContent = data.status === "ok" ? "service online" : "degraded";
    badge.classList.toggle("down", data.status !== "ok");
  } catch {
    badge.textContent = "service offline";
    badge.classList.add("down");
  }
}

async function loadSummary() {
  const { summary } = await getJSON("/api/prices/summary");
  $("#summary-cards").innerHTML = summary
    .map(
      (s) => `
      <div class="crop-card">
        <h3>${s.crop}</h3>
        <div class="avg">${fmt(s.average_price)} ${s.currency}</div>
        <div class="meta">per ${s.unit} · ${s.markets_reporting} markets</div>
        <div class="meta">min ${fmt(s.min_price)} (${s.cheapest_market})</div>
        <div class="meta">max ${fmt(s.max_price)} (${s.most_expensive_market})</div>
      </div>`
    )
    .join("");
  const select = $("#crop-select");
  select.innerHTML = summary
    .map((s) => `<option value="${s.crop}">${s.crop}</option>`)
    .join("");
  await loadComparison(select.value);
}

async function loadComparison(crop) {
  const table = $("#compare-table");
  const empty = $("#compare-empty");
  try {
    const data = await getJSON(`/api/crops/${encodeURIComponent(crop)}/compare`);
    table.querySelector("tbody").innerHTML = data.markets
      .map(
        (m, i) => `
        <tr>
          <td>${i + 1}</td>
          <td>${m.market}</td>
          <td>${fmt(m.price)} ${m.currency}/${m.unit}</td>
          <td>${m.reported_on || "-"}</td>
        </tr>`
      )
      .join("");
    table.hidden = data.markets.length === 0;
    empty.hidden = data.markets.length > 0;
  } catch {
    table.hidden = true;
    empty.hidden = false;
  }
}

function bindReportForm() {
  const form = $("#report-form");
  const result = $("#report-result");
  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    result.classList.remove("error");
    const body = Object.fromEntries(new FormData(form).entries());
    try {
      const res = await fetch("/api/prices", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await res.json();
      if (!res.ok) throw new Error(data.error || `HTTP ${res.status}`);
      result.textContent = `Saved: ${data.crop} in ${data.market} at ${fmt(data.price)} ${data.currency}/${data.unit}.`;
      form.reset();
      await loadSummary();
    } catch (err) {
      result.textContent = `Error: ${err.message}`;
      result.classList.add("error");
    }
  });
}

document.addEventListener("DOMContentLoaded", () => {
  checkHealth();
  loadSummary().catch((err) => {
    $("#summary-cards").innerHTML = `<p class="hint">Could not load prices: ${err.message}</p>`;
  });
  $("#crop-select").addEventListener("change", (e) => loadComparison(e.target.value));
  bindReportForm();
});
