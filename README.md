# Intelliginet File System

An AI-powered file monitoring and processing pipeline that watches a directory for incoming files, cleans the data, runs ML analysis, and produces structured intelligence reports — automatically, with no manual intervention.

[![CI](https://github.com/ajme-abes/intelligent-file-system/actions/workflows/ci.yml/badge.svg)](https://github.com/your-org/intelliginet-file-system/actions/workflows/ci.yml)

---

## What it does

Drop a file into `data/input/` and the system will:

1. **Detect** it in real-time (OS-level file system events via watchdog)
2. **Validate** the file type (CSV, JSON, TXT supported)
3. **Clean** the data — deduplication, null imputation, column normalisation, whitespace stripping
4. **Classify** the file semantically — `config`, `user_data`, `financial`, `log`, or `unknown`
5. **Detect anomalies** — flags statistical outliers in numeric columns using Isolation Forest
6. **Save** the processed file to `data/output/processed_<filename>`
7. **Generate** a structured JSON intelligence report at `data/output/reports/<filename>.report.json`

All steps are fully concurrent — up to 4 files are processed in parallel by default.

---

## Project structure

```
intelliginet-file-system/
├── app/
│   ├── cleaning/          # DataCleaner — normalise, dedup, fill nulls
│   ├── config/            # Settings — all config via env vars
│   ├── core/              # DataFile, BaseProcessor abstractions
│   ├── model/             # ML — classifier, anomaly detector, report generator
│   │   └── weights/       # Trained model (auto-generated on first run)
│   ├── monitoring/        # FileMonitor, FileHandler, structured logging
│   ├── pipeline/          # ProcessingPipeline, TaskDispatcher
│   └── processors/        # CSVProcessor, JsonProcessor, TXTProcessor
├── data/
│   ├── input/             # Drop files here
│   └── output/            # Processed files + reports appear here
│       └── reports/       # JSON intelligence reports
├── logs/                  # system.log (JSON structured)
├── test/                  # pytest suite (69 tests)
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── requirements.txt
```

---

## Quick start

### Option A — Docker (recommended)

```bash
# 1. Copy the env template
cp .env.example .env

# 2. Build and start
docker compose up --build

# 3. Drop a file into data/input/ on your host machine
#    The container will detect and process it automatically
cp mydata.csv data/input/
```

### Option B — Local Python

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Run
python run.py
```

---

## Configuration

All settings are controlled via environment variables. Copy `.env.example` to `.env` to customise.

| Variable | Default | Description |
|---|---|---|
| `INPUT_DIR` | `data/input` | Directory to watch for new files |
| `OUTPUT_DIR` | `data/output` | Where processed files are saved |
| `LOG_DIR` | `logs` | Log directory |
| `LOG_LEVEL` | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `LOG_FORMAT` | `json` | `json` (structured) or `text` (human-readable) |
| `MAX_WORKERS` | `4` | Parallel processing threads |
| `DEBOUNCE_SECONDS` | `2.0` | Min seconds between re-processing modified files |
| `FILE_WRITE_DELAY` | `0.5` | Seconds to wait after detection before reading |
| `ANOMALY_CONTAMINATION` | `auto` | IsolationForest contamination — `auto` or `0.0`–`0.5` |

---

## Supported file types

| Extension | Processor | Cleaning | Anomaly detection |
|---|---|---|---|
| `.csv` | CSVProcessor | ✅ | ✅ |
| `.json` | JsonProcessor | ✅ | ✅ |
| `.txt` | TXTProcessor | ✅ (blank lines, whitespace) | — |

JSON shapes supported: array-of-objects `[{...}]`, dict-of-dicts `{"0": {...}}`, flat dict `{"key": "value"}`.

---

## Intelligence report

Every processed file produces a `.report.json` in `data/output/reports/`. Example:

```json
{
  "file": { "name": "sales.csv", "type": "csv", "size_bytes": 4096 },
  "cleaning": {
    "original_rows": 1000, "final_rows": 987,
    "duplicates_removed": 13,
    "nulls_filled": { "revenue": 5 }
  },
  "ml": {
    "classification": { "label": "financial", "confidence": 0.91 },
    "anomaly": { "total_rows": 987, "anomaly_count": 12, "anomaly_ratio": 0.0122 }
  },
  "statistics": {
    "row_count": 987, "col_count": 5,
    "col_stats": { "revenue": { "min": 0, "max": 99500, "mean": 4821.3 } }
  },
  "generated_at": "2026-07-28T10:00:00+00:00"
}
```

---

## Running tests

```bash
# Run full suite
pytest test/ -v

# With coverage report
pytest test/ --cov=app --cov-report=term-missing

# Single module
pytest test/test_ml.py -v
```

Current test coverage: **69 tests** across all modules.

---

## CI / CD

Every push and pull request to `main` or `develop` runs:

1. **Lint** — flake8 (max line length 100)
2. **Type check** — mypy
3. **Tests** — full pytest suite with coverage on Python 3.11 and 3.12
4. **Docker build** — ensures the image builds and the app starts cleanly

See [`.github/workflows/ci.yml`](.github/workflows/ci.yml).

---

## ML layer

### File classifier
A Random Forest trained on 13 content features extracted from the file (character ratios, line structure, key-value density). Ships pre-trained on synthetic seed data. To train on your own labelled data:

```python
from app.model.classifier import FileTypeClassifier
import numpy as np

clf = FileTypeClassifier()
X = np.array([...])   # shape (n_samples, 13)
y = ["user_data", "config", ...]
clf.fit(X, y).save()
```

### Anomaly detector
Uses `IsolationForest` on all numeric columns. The `_anomaly` column added to output files marks rows as `True` (anomalous) or `False` (normal).

---

## Development

```bash
# Install dev dependencies
pip install -r requirements.txt
pip install flake8 mypy

# Lint
flake8 app/

# Type check
mypy app/ --ignore-missing-imports

# Tests
pytest test/ -v --cov=app
```
