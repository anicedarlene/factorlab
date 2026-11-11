# factorlab

Vectorized factor backtesting framework in Python with transaction costs, walk-forward validation and lookahead-bias tests.

## Overview

factorlab is a backtesting framework for cross-sectional equity factors, built to learn quantitative research and to practice careful validation. It takes a signal and a stock universe, simulates a long-short portfolio, and reports performance after costs.

The goal is not to find a profitable strategy. It is to build tooling that gives trustworthy results and to evaluate a few well-known factors honestly, including when they don't work.

## Factors

- **Momentum (12-1):** past 12-month return, skipping the most recent month
- **Low volatility:** trailing realized volatility, lower is better
- **Short-term reversal:** past 1-month return, lower is better

## Planned features

- Data layer: daily prices stored in DuckDB / Parquet, queried with SQL
- Backtest engine: signal, lagged weights, daily P&L, transaction costs, turnover
- Factor analysis: quintile long-short portfolios, information coefficient (IC), IC decay
- Metrics: annualized return, volatility, Sharpe ratio, max drawdown, turnover
- Validation: walk-forward / out-of-sample split, automated lookahead-bias tests
- Write-up: results, interpretation and limitations

## Tech stack

Python, pandas, NumPy, DuckDB, pytest, matplotlib

## Project structure

```
src/backtester/   core library (data, signals, engine, metrics)
tests/            unit tests, including lookahead-bias checks
notebooks/        exploration and sanity checks
docs/             concept notes and the research write-up
data/             local data (not committed)
```

## Setup

```
python3 -m venv .venv
source .venv/bin/activate      
python3 -m pip install -r requirements.txt
python3 -m pip install -e
python3 notebooks/sanity.py
```

## Milestones

- [x] Project setup and README plan
- [x] Concept notes (`docs/concepts.md`)
- [ ] Data layer: download universe and store in DuckDB
- [ ] Backtest engine with lagged signals and transaction costs
- [ ] Momentum, low-volatility and reversal factors
- [ ] Quintile and IC analysis
- [ ] Performance metrics
- [ ] Walk-forward validation and lookahead-bias tests
- [ ] Research write-up with results and limitations
- [ ] Final README polish (results charts, usage example)

## Known limitations (to be expanded)

- The universe is based on current index constituents, so results are subject to survivorship bias.
- Free data sources (Yahoo Finance) may contain errors and gaps.
- Transaction cost and slippage models are simplified.

## Results

To be added once the backtests are complete.