# ──────────────────────────────────────────────────────────────────────────────
# Stage 1 — builder
#   Install all Python dependencies into an isolated prefix so the final
#   image only copies what is needed (no pip cache, no build tools).
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# Copy only the dependency manifest first so Docker can cache this layer
COPY requirements.txt .

RUN pip install --upgrade pip --no-cache-dir \
 && pip install --prefix=/install --no-cache-dir -r requirements.txt


# ──────────────────────────────────────────────────────────────────────────────
# Stage 2 — runtime
#   Copy the installed packages and application source into a clean image.
#   Run as a non-root user for security.
# ──────────────────────────────────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Create a non-root user
RUN groupadd -r appgroup && useradd -r -g appgroup -d /app appuser

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app/        ./app/
COPY run.py      ./run.py
COPY pyproject.toml ./pyproject.toml

# Create runtime directories and set ownership
RUN mkdir -p data/input data/output data/output/reports logs \
 && chown -R appuser:appgroup /app

# Switch to non-root user
USER appuser

# ── Environment defaults (all overridable via docker-compose / -e flags) ──────
ENV INPUT_DIR=/app/data/input \
    OUTPUT_DIR=/app/data/output \
    LOG_DIR=/app/logs \
    LOG_FILE=/app/logs/system.log \
    LOG_LEVEL=INFO \
    LOG_FORMAT=json \
    MAX_WORKERS=4 \
    DEBOUNCE_SECONDS=2.0 \
    FILE_WRITE_DELAY=0.5 \
    MODEL_DIR=/app/app/model/weights \
    ANOMALY_CONTAMINATION=auto \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Health check — verify the app module is importable
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "from app.config import settings; settings.ensure_dirs()" || exit 1

ENTRYPOINT ["python", "run.py"]
