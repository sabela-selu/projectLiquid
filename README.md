# Algorithmic Trading Cookbook Project 🐍📈

A production‑ready implementation of every recipe in *Python for Algorithmic Trading Cookbook* (Packt, 2024). Supports back‑testing, paper‑trading, and live execution on Binance (additional brokers pluggable).

## Quick Start (Dev)
```bash
# Install Poetry (if not already)
curl -sSL https://install.python-poetry.org | python3 -

# Create & activate virtualenv
poetry install --with dev
poetry shell

# Run a dummy back‑test
algotrade backtest examples/ma_crossover.yaml
```

## Docker
```bash
# Build image
docker build -t algotrade:dev -f docker/Dockerfile .

# Run inside container
docker run --rm -it algotrade:dev algotrade --help
```

## Directory Layout
See [`PROJECT_PLAN.md`](PROJECT_PLAN.md) for the master execution plan.

## Broker API Keys
Create a `.env` (see `.env.sample`) with:
```
BINANCE_API_KEY=...
BINANCE_API_SECRET=...
```

## Tests
```bash
pytest -q
```

---
© 2025 Your Name. MIT License.
