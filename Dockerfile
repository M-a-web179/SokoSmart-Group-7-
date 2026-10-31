# Use the pinned Python image to build production dependency wheels separately.
FROM python:3.11.13-slim-bookworm AS builder
# Keep dependency artifacts outside the application source tree.
WORKDIR /build
# Copy dependencies first so application edits do not invalidate this layer.
COPY services/price-service/requirements-demo-missing.txt ./requirements.txt
# Build wheels for all production dependencies from the service requirements.
RUN pip wheel --no-cache-dir --wheel-dir /wheels -r requirements.txt
# Start a clean runtime stage from the same pinned Python base image.
FROM python:3.11.13-slim-bookworm AS runtime
# Place the Flask entry point and package in a predictable working directory.
WORKDIR /app
# Create an unprivileged account for running the web service.
RUN groupadd --system appuser && useradd --system --gid appuser --create-home appuser
# Copy the production dependency wheels from the builder stage.
COPY --from=builder /wheels /wheels
# Install only the production dependencies and remove the temporary wheel files.
RUN pip install --no-cache-dir /wheels/*.whl && rm -rf /wheels
# Copy the Flask application package needed by the service entry point.
COPY services/price-service/app ./app
# Copy the Flask application entry point.
COPY services/price-service/run.py ./run.py
# Copy seed data at the path expected by the service configuration.
COPY services/price-service/data/seed_prices.json ./data/seed_prices.json
# Run the service without root privileges.
USER appuser
# Document the port used by Gunicorn and the health endpoint.
EXPOSE 5000
# Check service health using Python's standard-library HTTP client.
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 CMD ["python", "-c", "from urllib.request import urlopen; urlopen('http://localhost:5000/health', timeout=2).read()"]
# Serve the Flask application with Gunicorn on all container interfaces.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
