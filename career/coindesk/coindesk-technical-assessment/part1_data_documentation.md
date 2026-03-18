# Competitive Intelligence Data Documentation
## Context for LLM-Powered Analysis

This document describes the dataset used to generate weekly competitive intelligence headlines for Bullish, an institutional cryptocurrency exchange. Feed this document alongside any week's data to ground the LLM in domain context before generating headlines.

---

## 1. About Bullish and Its Competitive Position

Bullish is an institutional-only cryptocurrency exchange regulated under the Gibraltar DLT Provider licence. It competes for institutional trading volume against three main rivals:

| Exchange | Character | Typical size vs Bullish |
|---|---|---|
| **Coinbase** | Largest US-regulated exchange, retail + institutional, dominant brand | 5–15× Bullish volume |
| **Kraken** | US-regulated, strong institutional desk, expanding into APAC | 1.5–3× Bullish volume |
| **Bitstamp** | Acquired by Robinhood in 2025, growing institutional push backed by retail base | 2–4× Bullish volume |

**Bullish's structural differentiator**: Unlike every other exchange in this dataset, Bullish runs a hybrid CLOB/AMM (Central Limit Order Book + Automated Market Maker). The AMM uses Bullish's own capital to provide algorithmic liquidity at all times. This means Bullish's order book never thins out during market stress — the AMM keeps posting prices even when human market makers flee. This is the core institutional value proposition: guaranteed execution quality during volatility.

**Bullish's client base**: Broker-dealers (FalconX, Hidden Road), prime brokers, market makers, and regulated asset managers who route institutional block trades via FIX/REST APIs. No retail users. This is deliberate — retail flow introduces "toxic flow" (informed traders front-running market maker quotes), which Bullish eliminates by design.

---

## 2. Dataset Structure

**File**: `data/signals.json`
**Coverage**: 10 weeks, Dec 21 2025 – Feb 22 2026
**Exchanges**: bullish, coinbase, kraken, bitstamp
**Instruments**: BTC-USD, ETH-USD

Each week contains:
- `week_starting`: ISO date string (Monday)
- `data`: array of 8 records (4 exchanges × 2 instruments), each with:
  - `exchange`: one of bullish / coinbase / kraken / bitstamp
  - `instrument`: BTC-USD or ETH-USD
  - `total_volume_usd`: total USD value of trades executed that week
  - `avg_close_price`: average daily closing price across the week
- `news`: array of 3–4 headlines with `headline` text and `source` (coindesk.com, theblock.co, reuters.com)

---

## 3. Key Derived Metrics

The raw data only contains volume and price. All intelligence comes from computing these derived metrics:

### 3.1 Market Share (most important metric)

```
market_share(exchange, instrument, week) =
    exchange_volume / sum(all_exchange_volumes) for that instrument × 100
```

Measures competitive position. A rising Bullish market share means it is winning flow from competitors. A falling share means losing ground.

**Baseline values (week 1, BTC-USD)**:
- Coinbase: 60.1% — dominant
- Bitstamp: 18.4%
- Kraken: 13.8%
- Bullish: 7.7% — smallest

**Key pattern**: Bullish's BTC market share is inversely correlated with BTC price. It rises during sell-offs and compresses during rallies. This is the AMM effect — when Coinbase's order book thins during panic selling, Bullish absorbs the flow.

### 3.2 ETH/BTC Volume Ratio

```
eth_btc_ratio(exchange, week) = ETH-USD volume / BTC-USD volume
```

Measures how balanced an exchange's book is across instruments. A low ratio means ETH is under-served relative to BTC.

**Baseline (week 1)**:
- Kraken: 0.43 — most ETH-heavy
- Coinbase: 0.37
- Bullish: 0.32 — close to Coinbase initially
- Bitstamp: 0.19 — most BTC-heavy

**Key pattern**: Bullish's ETH/BTC ratio collapsed from 0.32 to 0.19 over 10 weeks while Coinbase rose to 0.51. Bullish is becoming increasingly BTC-concentrated — a strategic risk if ETH demand grows.

### 3.3 Week-over-Week Volume Change

```
wow_change(exchange, instrument, week) =
    (this_week_volume - last_week_volume) / last_week_volume × 100
```

Measures momentum. A positive WoW during a flat or declining market is a strong signal of competitive share gain.

### 3.4 Relative Size vs Competitors

```
relative_size(competitor, week) = competitor_volume / bullish_volume
```

Tracks how many times larger each competitor is. When this ratio falls, Bullish is closing the gap. When it rises, the gap is widening.

**Bitstamp ratio trend (BTC-USD)**:
- Week 1: 2.4× — Bitstamp 2.4× bigger than Bullish
- Week 4 (rally peak): 4.1× — gap widened as rally benefited Bitstamp more
- Week 8 (sell-off): 1.6× — Bullish surged, Bitstamp didn't

---

## 4. The Market Cycle Narrative (10 Weeks)

The dataset captures a complete market cycle. Understanding the narrative is essential for interpreting whether volume changes are exchange-specific or market-wide:

| Weeks | Dates | BTC Price | Market Phase | What to look for |
|---|---|---|---|---|
| 1–4 | Dec 21 – Jan 11 | $87K → $94K | **Rally** | Volume surges everywhere, Coinbase captures lion's share, Bullish compresses |
| 5–7 | Jan 18 – Feb 1 | $94K → $72K | **Sell-off** | Panic selling, Bullish AMM absorbs flow, market share spikes |
| 8–10 | Feb 8 – Feb 22 | $69K → $66K | **Consolidation** | Volume normalises, see who held share gains and who regressed |

**Why this matters for headlines**: A volume increase during a rally is noise — everyone goes up. A volume increase during a sell-off is signal — it means the exchange absorbed stress flow that competitors couldn't handle.

---

## 5. What Good Intelligence Looks Like

Headlines should be:
- **Specific**: cite exact numbers and dates, not vague trends
- **Comparative**: always frame Bullish relative to a competitor or a prior period
- **Causal**: link the number to a business reason (AMM, regulation, acquisition)
- **Actionable**: tell the sales team something they can use in a client meeting

**Good example**:
> "Bullish BTC market share rose from 7.9% to 11.9% during the Feb sell-off (BTC $85K→$69K), while Coinbase slipped from 57.7% to 56.9%. AMM structural liquidity absorbing panic flow. Confidence: HIGH"

**Weak example**:
> "Bullish had more volume this week. Confidence: MEDIUM"

---

## 6. Known Competitive Dynamics to Track

These are the standing hypotheses the system should continuously evaluate:

**Bullish strengths to confirm or deny:**
- AMM liquidity advantage during sell-offs (look for share rising as BTC falls)
- Regulatory positioning as Gibraltar DLT cited in news
- Institutional flow routing from prime brokers (FalconX, Hidden Road in news)

**Bullish weaknesses to monitor:**
- Rally underperformance — share compresses when BTC rises sharply
- ETH under-penetration — ratio declining vs all competitors
- Absolute scale gap — even at Bullish's best, Coinbase is 6–7× larger

**Competitor threats to watch:**
- Bitstamp/Robinhood — acquisition-driven growth, retail base funding institutional push
- Coinbase fee cuts — 30% maker fee reduction announced Jan 18, monitor volume impact
- Kraken APAC expansion — targeting European and Asian broker-dealer flow

---

## 7. News Source Interpretation

| Source | Bias / Focus |
|---|---|
| `coindesk.com` | Broad crypto market coverage, price and volume moves |
| `theblock.co` | Institutional and industry focus, exchange business news |
| `reuters.com` | Macro and regulatory context, traditional finance perspective |

Reuters headlines are particularly important for regulatory signals that affect Bullish's institutional positioning. The Block headlines tend to carry direct competitive intelligence (fee cuts, expansions, acquisitions).

---

## 8. Confidence Level Definitions

When generating headlines, use these definitions consistently:

| Level | Meaning |
|---|---|
| **HIGH** | Supported by 2+ consecutive weeks of data in the same direction AND corroborated by news OR a clear structural explanation |
| **MEDIUM** | Supported by current week data but not yet a confirmed trend, OR trend is real but causation is uncertain |
| **LOW** | Single data point, contradicted by some evidence, or claim is plausible but not yet demonstrated |

Confidence should increase when new data reinforces the claim and decrease when data contradicts it. A headline that drops from HIGH to LOW over two weeks should be considered for retirement.
