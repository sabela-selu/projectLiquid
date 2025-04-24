#!/bin/bash
# Shell script to set up Python 3.11 virtual environment for the project
# Usage: bash setup_python311_venv.sh

set -e

# 1. Install Python 3.11 if not present (Homebrew)
if ! command -v python3.11 &> /dev/null; then
    echo "Python 3.11 not found. Installing via Homebrew..."
    brew install python@3.11
fi

# 2. Remove old venv if exists
if [ -d ".venv311" ]; then
    echo "Removing existing .venv311..."
    rm -rf .venv311
fi

# 3. Create new venv
python3.11 -m venv .venv311

# 4. Activate venv and install dependencies
source .venv311/bin/activate
pip install --upgrade pip
pip install typer rich pandas pyyaml yfinance scikit-learn tensorflow

echo "\n[INFO] Python 3.11 venv ready! Activate with: source .venv311/bin/activate"
echo "[INFO] Run your backtest with: python -m algotrade.cli backtest configs/btcusd_1h_backtest.yaml"
