# Algorithmic Trading Cookbook – Project Execution Plan

*(Implements all recipes from “Python for Algorithmic Trading Cookbook” and enables back‑testing, paper‑trading and live execution)*

---
## 1. High‑Level Objectives
* Achieve code parity with every recipe in the book.
* Provide a unified workflow: one command toggles **back‑test ⇄ paper ⇄ live**.
* Ship production‑grade safety (risk checks, monitoring, CI/CD, secrets management).

---
## 2. Tech Stack & Conventions
| Layer | Choice |
|-------|--------|
| Language | **Python 3.11** (via `pyenv`) |
| Env / Pkg | **Poetry** for dependency + virtualenv |
| Core Libs | `pandas`, `numpy`, `pandas‑ta`, `TA‑Lib`, `scikit‑learn`, `xgboost`, `backtrader`, `zipline‑reloaded`, `vectorbt`, `PyPortfolioOpt` |
| Broker API | `ib_insync`, `alpaca‑trade‑api` (pluggable) |
| Infra | **Docker + docker‑compose** |
| Data | Yahoo/Polygon/Tiingo, stored in Postgres‑Timescale or Parquet (S3/MinIO) |
| CI/CD | GitHub Actions → build, test, paper‑trade smoke, Docker push |
| Observability | `structlog` → Loki/Grafana, Prometheus metrics |
| Secrets | `.env` (dev), Vault/Parameter Store (prod) |

---
## 3. Directory / Module Layout
```
project/
├─ README.md, CONTRIBUTING.md
├─ pyproject.toml, poetry.lock
├─ .env.sample, .envrc
├─ bin/                    # helper scripts
├─ notebooks/              # exploratory only
├─ recipes/                # exact book recipes
│   ├─ ch01_data_ingest/
│   ├─ ch02_indicators/
│   └─ …
├─ algotrade/              # production library
│   ├─ data/               # adapters: Yahoo, Polygon, CSV, DB
│   ├─ signals/            # TA, ML, DL
│   ├─ portfolio/          # risk & sizing
│   ├─ execution/          # broker adapters
│   ├─ backtest/           # wrappers
│   ├─ cli.py              # Typer/Click entry point
│   └─ utils/
├─ experiments/            # YAML configs + results
├─ tests/                  # pytest
└─ docker/
    └─ Dockerfile, compose.yml
```

---
## 4. Development Phases & Milestones
| Phase | Timeline | Deliverables |
|-------|----------|--------------|
| **0** Project Bootstrap | Week 1 | Git repo, Poetry, lint hooks, Dockerfile |
| **1** Core Recipe Port | Weeks 1‑4 | Every cookbook recipe refactored & unit‑tested |
| **2** Back‑Testing Engine | Weeks 3‑6 | YAML‑driven back‑test runner, HTML reports |
| **3** Live Execution Layer | Weeks 6‑9 | Broker adapters, OrderManager, risk checks |
| **4** Experiment Mgmt | Weeks 8‑10 | Hydra configs, MLflow/DVC tracking |
| **5** Monitoring & Ops | Weeks 10‑12 | Prom/Grafana dashboards, alerts |
| **6** Compliance & CI/CD | Weeks 11‑13 | Secrets hardening, vulnerability scans |
| **7** Validation & Launch | Week 14 | 30‑day paper burn‑in → limited capital live |

---
## 5. Key Implementation Details
* **Config‑Driven**: single YAML selects data source, strategy, mode, broker, sizing, schedule.
* **Recipe Parity**: original code lives under `recipes/`; production abstractions in `algotrade/` import or wrap these.
* **Type‑Safety**: Pydantic models; mypy enforced.
* **Observability**: JSON logs to Loki, Prom metrics; auto‑generated HTML back‑test reports.
* **Fail‑Safe Runtime**: Two‑process model (`StrategyProcess` ⇄ `ExecutionProcess` via ZeroMQ).

---
## 6. Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Data quality | Dual sources, checksum raw vs processed |
| Slippage/Latency | Forward‑test with small capital, log order latency |
| Regulatory | Pre‑trade risk checks, 5‑year audit logs |
| Security | Principle of least privilege, no secrets in CI |

---
## 7. Immediate Next Steps
1. **Confirm broker preference** (IBKR vs Alpaca vs Binance).
2. **Bootstrap repository** (Poetry init, directory skeleton, Dockerfile).
3. Port Chapter 1 recipes & write corresponding unit tests.
4. Set up GitHub Actions (lint + tests).

---
*This document serves as the single source of truth throughout the project.*
