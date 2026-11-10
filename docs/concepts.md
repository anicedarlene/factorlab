# factorlab: core concepts

Notes on the ideas behind the project, organized by concept. Examples use made-up numbers to show the mechanics.

## The big picture

A backtest replays history to ask: **if I had followed this rule each day, using only what I knew at the time, what would have happened?** The question underneath is whether information available today can predict which stocks do better than others tomorrow, and whether that survives trading costs.

### Pipeline map

Almost every stage is a table with **dates as rows and tickers as columns**. Each stage transforms one table into the next.

```
 1.  PRICES      dates x tickers of adjusted closing prices
       |
 2.  RETURNS     how much each stock moved each day
       |
 3.  SIGNAL      a score per stock per day (higher = "should do better")
       |
 4.  LAG         shift the signal forward one day (use only the past)
       |
 5.  RANK        compare stocks to each other on each day
       |
 6.  EVALUATE    IC: does the ranking line up with the returns that followed?
       |
 7.  PORTFOLIO   quintiles -> weights: long the top bucket, short the bottom
       |
 8.  P&L         weights x returns = portfolio return per day
       |
 9.  COSTS       subtract the cost of trading (turnover x cost rate)
       |
10.  METRICS     Sharpe, max drawdown, turnover
       |
11.  VALIDATION  was this result real, or luck and bugs?
```

### How the 9 sections below map to the pipeline

| Section | Concept | Pipeline stage(s) |
|---|---|---|
| 1 | Prices + survivorship bias | 1 |
| 2 | Returns | 2 |
| 3 | Signal / factor + lookahead bias | 3-4 |
| 4 | Cross-sectional ranking | 5 |
| 5 | Information coefficient (IC) | 6 |
| 6 | Quintiles + portfolio P&L | 7-8 |
| 7 | Costs and turnover | 9 |
| 8 | Performance metrics | 10 |
| 9 | Validation and overfitting | 11 |

### The three problems hiding in the pipeline

| Problem | Where it enters | Defense |
|---|---|---|
| Survivorship bias | Stage 1 (the data) | Document it, use a shorter window |
| Lookahead bias | Stages 3-4 (signal and timing) | `shift(1)`, truncation test, planted-answer test |
| Overfitting | Stage 11 (the research process) | Fixed hypotheses, hold-out set, walk-forward, honest reporting |

### Running example

Five stocks, A to E, used throughout.

---

## 1. Prices + survivorship bias

**Prices.** The raw material is a table of daily **adjusted** closing prices. "Adjusted" means corrected for splits and dividends. Without that, a 2-for-1 split would look like a 50% crash.

| Date | A | B | C | D | E |
|---|---|---|---|---|---|
| Mon | 100 | 50 | 20 | 80 | 40 |
| Tue | 101 | 50.3 | 20.02 | 79.76 | 39.68 |

**Survivorship bias.** If the universe is built from **today's** index members and tested back to 2010, it only contains companies that were successful enough to still be there. Companies that went bankrupt, were delisted or were dropped for poor performance are missing. The test universe is therefore better than what an investor actually faced, and results look flattered.

- The proper fix is **point-in-time constituent lists** (what the index held on each date), which is usually paid data.
- With free data we can't fix it, so we use a shorter window and state it as a limitation in the README.

**In factorlab:** the data loader stores adjusted prices in DuckDB, and the README lists survivorship bias under known limitations.

---

## 2. Returns

**Why returns instead of prices.** A $1 move is 10% for a $10 stock and 0.1% for a $1,000 stock, and prices trend upward over time. Returns are comparable across stocks and years, which makes statistics meaningful.

**Simple return:** `r = P_today / P_yesterday - 1`

From the table above, Tuesday's returns: A +1.0%, B +0.6%, C +0.1%, D -0.3%, E -0.8%.

**Log return:** `ln(P_today / P_yesterday)`

Compare 100 -> 110 -> 99:

| Day | Price | Simple | Log |
|---|---|---|---|
| 1 | 110 | +10.00% | +9.53% |
| 2 | 99 | -10.00% | -10.54% |

- Simple returns don't add across time: you multiply, 1.10 x 0.90 = 0.99, so you end at 99, not 100.
- Log returns do add: 0.0953 + (-0.1054) = -0.0101 = ln(99/100).

**Which to use:** simple returns for portfolios, because a portfolio's return is the weighted average of its stocks' simple returns on that day. Log returns are handy for summing across time.

**In factorlab:** `prices.pct_change()` in pandas.

---

## 3. Signal / factor + lookahead bias

### The signal

A **signal** (or factor) is a score for each stock on each day, where a higher value is supposed to mean "expected to do better." It is a ranking tool, not a forecast in percent. It must be computed from past prices only.

The three factors in this project:

- **Momentum (12-1):** return from 12 months ago to 1 month ago. The most recent month is skipped because very recent winners tend to give back gains, which would contaminate the trend effect.
- **Low volatility:** recent standard deviation of daily returns, multiplied by -1 so calm stocks score high.
- **Short-term reversal:** past 1-month return, multiplied by -1, because recent losers tend to bounce back.

Example momentum scores on Tuesday's close:

| A | B | C | D | E |
|---|---|---|---|---|
| +40% | +25% | +5% | -10% | -30% |

Each factor needs an **economic story** for why it might persist (for example, investors underreact to news, so trends continue). A pattern without a story is more likely noise.

### The lag

You compute the signal from Tuesday's close, but you only know that close after it happens. So you can't have traded on it at Tuesday's close. The earliest return you can capture is Wednesday's.

```
Tuesday close:  compute signal -> decide weights
Wednesday:      hold those weights, earn Wednesday's return
```

In pandas this is `signal.shift(1)` (or `weights.shift(1)` when multiplying with returns).

### Lookahead bias

**Lookahead bias** is using information that wasn't available at the moment of the trade. It is the most common bug in student backtests, and it makes any signal look brilliant.

Main ways it sneaks in:

1. **Missing the lag:** signal and return are from the same day.
2. **Full-sample statistics:** standardizing a signal with the mean and standard deviation of the whole dataset, which includes the future. Use rolling or expanding windows instead.
3. **Off-by-one date errors** when joining tables.
4. **Data known later than its date,** such as fundamentals reported weeks after the period ends (not an issue for price-only factors, but worth knowing).

**How we test for it** (in `tests/`):

- **Truncation test:** compute the signal on the full dataset and on data cut off at date T. The value at T must be identical in both. If it changes, the signal peeked ahead.
- **Planted-answer test:** feed the engine a fake "signal" equal to tomorrow's return. If the lag is handled correctly, it should not produce a perfect result from that.

---

## 4. Cross-sectional ranking

A signal can be viewed two ways:

- **Time series:** one stock across time ("is A's momentum high relative to A's own past?")
- **Cross-section:** many stocks on one day ("which stocks rank highest today?")

Factor investing uses the cross-section. Ranking the five stocks by momentum:

| | A | B | C | D | E |
|---|---|---|---|---|---|
| Momentum | +40% | +25% | +5% | -10% | -30% |
| Rank (5 = highest) | 5 | 4 | 3 | 2 | 1 |

**Why rank?** In a rising market nearly every stock has positive momentum, so raw values mostly measure the market, not the stock. Ranking removes the market-wide level and keeps only "better or worse than the others today," which is the bet a long-short factor actually makes.

**In factorlab:** `signal.rank(axis=1, pct=True)` with dates as rows and tickers as columns.

---

## 5. Information coefficient (IC)

Before building a portfolio, ask directly: **does a higher rank today go with a higher return afterward?**

The **IC** is the **Spearman rank correlation**, across stocks, between the lagged signal and the next-period return. You get one IC per day.

Example, signal ranks vs. Wednesday's returns:

| | A | B | C | D | E |
|---|---|---|---|---|---|
| Signal rank | 5 | 4 | 3 | 2 | 1 |
| Return rank | 5 | 4 | 3 | 2 | 1 |

The orders match perfectly, so **IC = +1.0**. If B and C swapped return ranks, the Spearman formula `1 - 6 * sum(d^2) / (n * (n^2 - 1))` gives `1 - 6*2/120 = 0.9`.

**What to expect in reality:** a mean IC of about **0.02-0.05** across many stocks is already useful. A much higher number usually means a bug, often lookahead.

**What we report:**

- **Mean IC:** the average over all days.
- **ICIR** = mean IC / standard deviation of IC. It measures consistency.
- **IC decay:** the IC against returns 1, 5 and 20 days later. Fast decay means the signal is short-lived and requires frequent, costly trading.

**Why rank correlation instead of ordinary correlation?** It is robust to outliers, so one stock jumping 80% can't dominate the result.

---

## 6. Quintiles + portfolio P&L

### Long and short

- **Long** = buy. You profit when the price goes **up**.
- **Short** = borrow a stock, sell it now, buy it back later to return it. You profit when the price goes **down**.

| | Price goes up | Price goes down |
|---|---|---|
| **Long** | make money | lose money |
| **Short** | lose money | make money |

**Why combine them:** if the whole market rises 2%, the long stocks gain about 2% and the short stocks lose about 2%, so the market's movement roughly cancels. What remains is whether the stocks we liked beat the stocks we disliked, which is exactly what a factor claims to predict. This is called being **market-neutral**.

### Quintile portfolios

A **quintile** is one of 5 equal groups of stocks sorted by signal. Q5 is the strongest signal, Q1 the weakest. With 500 stocks each holds about 100; with our five, each holds one.

- **Long** Q5 (stock A)
- **Short** Q1 (stock E)
- Leave B, C, D alone

**Weights**, scaled so total absolute exposure is 1: **A = +0.5, E = -0.5**, others 0. A positive weight means long, negative means short.

### Portfolio P&L

`portfolio return = sum(weight x stock return)`

With next-day returns A +1.0% and E -0.8%:

- Long A: 0.5 x (+1.0%) = **+0.5%**
- Short E: -0.5 x (-0.8%) = **+0.4%** (E fell, so the short gains)
- Portfolio: **+0.9%**

A negative weight times a negative return gives a positive profit.

### Monotonicity

Look at the average return of **all five quintiles**, not just the extremes.

| Q1 | Q2 | Q3 | Q4 | Q5 |
|---|---|---|---|---|
| 0.4% | 0.7% | 0.9% | 1.1% | 1.5% |

Returns rising steadily from Q1 to Q5 (**monotonicity**) is more convincing than a jumbled middle with the same Q5-minus-Q1 spread, which looks more like luck.

**Caveat for the write-up:** real shorting has borrow fees, some stocks can't be borrowed, and a short can lose more than 100% if the price keeps rising. The model ignores these.

---

## 7. Costs and turnover

**Turnover** measures how much you trade: the sum of absolute weight changes at a rebalance.

Example: if B becomes the top stock instead of A,

- A: +0.5 -> 0 (trade 0.5)
- B: 0 -> +0.5 (trade 0.5)
- E: unchanged
- Total traded = **1.0** (two-way turnover)

Always state whether turnover is quoted two-way (sum of all trades, as here) or one-way (half of it).

**Cost** = turnover x cost rate. At 10 basis points (0.10%) per unit traded: 1.0 x 0.10% = **0.10%** that day.

**Why it matters:** a strategy trading 100% every day would pay about 0.10% x 252 = **25% a year** in costs. Fast-decaying, high-turnover signals (short-term reversal is the classic case) often look profitable before costs and unprofitable after. That's why IC decay and cost sensitivity belong together in the analysis.

---

## 8. Performance metrics

Once you have a daily return series after costs, summarize it:

- **Annualized return and volatility:** scale the daily mean by 252 and the daily standard deviation by sqrt(252).
- **Sharpe ratio:** return per unit of risk.
  `Sharpe = (mean daily return / std of daily returns) x sqrt(252)`
  Example: mean 0.05% and std 0.8% gives 0.0005 / 0.008 x 15.9 = about **1.0**. For a long-short portfolio we can skip subtracting the risk-free rate, but we state that choice.
- **Max drawdown:** the worst peak-to-trough fall of cumulative returns.
  Equity 100 -> 120 -> 90 -> 110 gives (90 - 120) / 120 = **-25%**. It shows how painful the worst stretch was, which Sharpe hides.
- **Turnover:** the average per rebalance, as in section 7.

---

## 9. Validation and overfitting

Everything above produces numbers. This section asks whether to believe them.

**Overfitting (multiple testing).** Try enough ideas on the same data and some will look great by pure luck.

Example: backtest 100 completely random signals over 5 years. The Sharpe estimate has a standard error of about 1 / sqrt(5) = 0.45, and the best of 100 random draws lands roughly 2.5 standard errors above zero. So the best random signal will often show a Sharpe near **1.0** with no real skill.

**How we protect ourselves:**

1. **Fix factors and parameters beforehand,** based on their economic story. Don't tune lookbacks until something looks good.
2. **Hold out data:** keep the last couple of years untouched and look at them once, at the end.
3. **Walk-forward testing:** choose settings on one window, test on the next, then roll forward.
4. **Report everything tried,** including failures, not only the winners.
5. **Distrust spectacular results.** A Sharpe of 3 from a simple factor on free data almost always means a bug or lookahead bias.

This is what "disciplined about validation and wary of overfitting" means in practice.

