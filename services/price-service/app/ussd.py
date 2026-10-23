"""USSD menu handler for feature-phone users.

Follows the common Africa's Talking-style protocol:
- The gateway POSTs the user's input as ``text`` with menu selections
  separated by ``*`` (e.g. ``1*2``).
- The reply is plain text starting with ``CON`` (continue, show menu and
  wait for input) or ``END`` (terminate the session).

Menu levels:
    ""        -> main menu                       (level 1)
    "1"       -> pick a crop                     (level 2)
    "1*<n>"   -> latest prices for that crop     (level 3)
    "2"       -> pick a crop to compare          (level 2)
    "2*<n>"   -> markets for crop, cheapest first(level 3)
    "3"       -> price summary                   (level 2)
    "4"       -> report-price flow               (levels 2-5)
In any menu, ``0`` exits and ``00`` goes back one level.
"""

from typing import List

from .services import PriceService

BACK = "00"
EXIT = "0"


class UssdMenuHandler:
    def __init__(self, service: PriceService) -> None:
        self.service = service

    def handle(self, text: str = "") -> str:
        parts = [p for p in text.strip().split("*") if p != ""]
        if not parts:
            return self._main_menu()
        return self._dispatch(parts)

    # ------------------------------------------------------------------ menus

    def _main_menu(self) -> str:
        return _con(
            "Welcome to SokoSmart",
            "1. Check crop prices",
            "2. Compare markets for a crop",
            "3. Price summary (all crops)",
            "4. Report a price",
            f"{EXIT}. Exit",
        )

    def _crops(self) -> List[str]:
        return sorted({row["crop"] for row in self.service.summary()})

    def _crop_menu(self) -> str:
        crops = self._crops()
        if not crops:
            return _end("No crops in the system yet. Dial again after prices are reported.")
        lines = [f"{i}. {crop}" for i, crop in enumerate(crops, start=1)]
        lines.append(f"{BACK}. Back")
        lines.append(f"{EXIT}. Exit")
        return _con("Select a crop", *lines)

    def _prices_for_crop(self, crop: str) -> str:
        prices = self.service.list_prices(crop=crop)
        if not prices:
            return _end(f"No prices recorded for {crop}.")
        prices.sort(key=lambda p: p["price"])
        lines = [
            f"{p['market']}: {p['price']:g} {p['currency']}/{p['unit']}" for p in prices
        ]
        return _end(f"Latest prices for {crop} (cheapest first)", *lines)

    def _compare_crop(self, crop: str) -> str:
        try:
            data = self.service.compare_markets(crop)
        except LookupError:
            return _end(f"No prices found for {crop}.")
        lines = [
            f"{m['market']}: {m['price']:g} {m['currency']}/{m['unit']}"
            for m in data["markets"]
        ]
        return _end(
            f"{data['crop']} - cheapest in {data['cheapest_market']}",
            *lines,
        )

    def _summary(self) -> str:
        rows = self.service.summary()
        if not rows:
            return _end("No price data yet.")
        lines = [
            f"{r['crop']}: avg {r['average_price']:g} "
            f"({r['min_price']:g}-{r['max_price']:g} {r['currency']}/{r['unit']})"
            for r in rows
        ]
        return _end("Price summary (avg, min-max)", *lines)

    # ------------------------------------------------------- report a price

    def _report(self, parts: List[str]) -> str:
        inputs = parts[1:]
        if len(inputs) == 0:
            return _con("Report a price", "Enter the crop name (e.g. Maize)", f"{BACK}. Back")
        if len(inputs) == 1:
            return _con(f"Crop: {inputs[0].title()}", "Enter the market name (e.g. Huye)", f"{BACK}. Back")
        if len(inputs) == 2:
            return _con(
                f"Crop: {inputs[0].title()}",
                f"Market: {inputs[1].title()}",
                "Enter the price per kg (e.g. 410)",
                f"{BACK}. Back",
            )
        crop, market, price = inputs[0], inputs[1], inputs[2]
        try:
            self.service.add_price({"crop": crop, "market": market, "price": price})
        except ValueError as err:
            return _end(f"Could not save the price: {err}. Please try again.")
        return _end(
            f"Thank you! {crop.title()} in {market.title()} recorded at {float(price):g} RWF/kg."
        )

    # -------------------------------------------------------------- dispatch

    def _dispatch(self, parts: List[str]) -> str:
        choice = parts[0]
        if choice == EXIT:
            return _end("Thank you for using SokoSmart. Know the price before you go!")

        if choice == "1":
            if len(parts) == 1:
                return self._crop_menu()
            if parts[1] == BACK:
                return self._main_menu()
            return self._pick_crop(parts[1], self._prices_for_crop)

        if choice == "2":
            if len(parts) == 1:
                return self._crop_menu()
            if parts[1] == BACK:
                return self._main_menu()
            return self._pick_crop(parts[1], self._compare_crop)

        if choice == "3":
            return self._summary()

        if choice == "4":
            if len(parts) > 1 and parts[-1] == BACK:
                return self._main_menu()
            return self._report(parts)

        return _end("Invalid selection. Please dial again and choose 1-4.")

    def _pick_crop(self, raw_index: str, action) -> str:
        crops = self._crops()
        try:
            index = int(raw_index)
        except ValueError:
            return _end("Invalid selection. Please dial again.")
        if not 1 <= index <= len(crops):
            return _end("Invalid crop number. Please dial again.")
        return action(crops[index - 1])


def _con(*lines: str) -> str:
    return "CON " + "\n".join(lines)


def _end(*lines: str) -> str:
    return "END " + "\n".join(lines)
