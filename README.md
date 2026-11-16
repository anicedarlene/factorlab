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

## Data

- **Universe:** S&P 500 constituents from the iShares Core S&P 500 ETF (IVV) holdings file, as of 2026-11-09. The file lists 505 equity tickers after cleaning.
- **Prices:** daily prices from Yahoo Finance via `yfinance`, adjusted for splits and dividends, from 2015-01-02 to 2026-11-10 (end date fixed so all tickers cover the same period). Downloaded [date].
- **Storage:** DuckDB (`data/factorlab.duckdb`), one row per date and ticker. Data files are not committed to the repository.

### Excluded tickers

Two tickers in the holdings file were excluded because they have no usable price history:

| Ticker | Reason |
|---|---|
| `HOLX` | Hologic was acquired by Blackstone and TPG and delisted from Nasdaq in April 2026, yet it still appears in the November 2026 holdings file. Yahoo Finance has no price data for it. |
| `SKYD-WS` | A warrant, not a common stock. |

The final universe is 503 tickers.

## Known limitations

- **Survivorship bias.** The universe is today's index membership, so companies that went bankrupt, were acquired or were dropped from the index before November 2026 are not in the sample. This flatters results, especially for strategies that buy beaten-down stocks.
  - The `HOLX` case shows the problem has a second layer. Even if point-in-time index membership were available, Yahoo Finance removes the price history of delisted stocks, so those stocks could not be tested with this data source anyway. A fix would need a professional data source (such as CRSP or Bloomberg) with point-in-time constituents and delisted prices.
- **Data quality.** Yahoo Finance is an unofficial, free source and may contain errors or gaps. Basic checks are in `scripts/check_data.py`.
- **Simplified costs.** Transaction costs and slippage use a simple flat model.
- **No shorting frictions.** Borrow fees and short-sale restrictions are ignored.

## Results

To be added once the backtests are complete.

## Milestones

- [x] Project setup and README plan
- [x] Concept notes (`docs/concepts.md`)
- [x] Data layer: download universe and store in DuckDB
- [ ] Backtest engine with lagged signals and transaction costs
- [ ] Momentum, low-volatility and reversal factors
- [ ] Quintile and IC analysis
- [ ] Performance metrics
- [ ] Walk-forward validation and lookahead-bias tests
- [ ] Research write-up with results and limitations
- [ ] Final README polish (results charts, usage example)