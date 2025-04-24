"""Command‑line entry point for back‑testing, paper‑trading, and live trading.

Usage:
    $ algotrade backtest config.yaml
    $ algotrade live config.yaml --broker binance

The CLI is intentionally minimal; most heavy lifting happens in the underlying `algotrade.*` modules.
"""

from pathlib import Path
from typing import Optional

import typer
from rich import print as rprint

app = typer.Typer(add_completion=False, help="Algorithmic Trading Toolkit CLI")


@app.command()
def backtest(config: Path):
    """Run a back‑test defined by the YAML `config`."""

    from algotrade.runner import run_backtest

    rprint(f"[bold cyan]Running back‑test[/] using {config}…")
    run_backtest(config)


@app.command()
def live(config: Path, broker: Optional[str] = typer.Option("binance", help="Broker adapter to use")):
    """Launch live trading with the given CONFIG and BROKER (default: binance)."""

    from algotrade.runner import run_live

    rprint(f"[bold green]Starting live trading on {broker}[/] with {config}…")
    run_live(config, broker)


if __name__ == "__main__":
    app()
