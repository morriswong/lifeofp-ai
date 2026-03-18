# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a take-home technical assessment for an AI & Data Platform Engineer role. The goal is to build an **AI-powered competitive intelligence system** for a cryptocurrency exchange (Bullish). The system ingests weekly market data + news headlines and maintains a set of evolving intelligence headlines about the competitive landscape.

## Task Structure

The assessment has three parts:

1. **Part 1 — Data Understanding**: Explore `data/signals.json` and write data documentation suitable as LLM context
2. **Part 2 — Headline Generation**: Build a system using an LLM + vector DB to generate intelligence headlines per week
3. **Part 3 — Weekly Evolution**: Process all 10 weeks sequentially, updating/retiring headlines as evidence changes

## Data

**`data/signals.json`** — 10 weeks of data (Dec 21, 2025 – Feb 22, 2026):
- `exchanges`: bullish, coinbase, kraken, bitstamp
- `instruments`: BTC-USD, ETH-USD
- Per week: array of `{exchange, instrument, total_volume_usd, avg_close_price}` plus 3–4 news `headlines` with source
- The 10 weeks cover a full market cycle: rally (BTC $87K→$94K), major sell-off (→$66K), consolidation

Key derived metrics to compute: market share (exchange volume / total volume per instrument), ETH/BTC volume ratio per exchange, week-over-week volume changes.

## Dependencies

Add LLM and vector DB libraries to `requirements.txt`. Common choices:
- LLM: `openai>=1.0` or `anthropic>=0.30`
- Vector DB: `chromadb>=0.4`, `faiss-cpu`, or `pinecone-client`
- Embeddings: `sentence-transformers>=2.0` or use the LLM provider's embedding API

Install: `pip install -r requirements.txt`

## Deliverable Format

Working Python — notebook (`.ipynb`) or scripts. The solution should be runnable end-to-end.

## Domain Context

- **Bullish**: Regulated exchange (Gibraltar DLT licence), hybrid CLOB/AMM, institutional focus (broker-dealers, prime brokers). AMM provides deep liquidity structurally even at lower volume.
- **Competitors**: Coinbase (~3–5× Bullish volume), Kraken (~1.5–2.5×), Bitstamp/Robinhood (~2–3×)
- **Key metrics**: market share %, ETH/BTC volume ratio, week-over-week volume changes, price convergence across exchanges

## Headline Format

Each headline should include confidence level (HIGH/MEDIUM/LOW) and a brief rationale citing specific data points. Example:
```
"Bullish BTC-USD market share has doubled since the sell-off (7.7% -> 16.8%). Confidence: HIGH"
```

## Architecture Guidance

The core pipeline per week:
1. Compute numerical metrics from raw data (market share, ratios, deltas)
2. Embed and store week context (data summary + news) in vector DB
3. Retrieve relevant prior context (previous headlines, similar weeks)
4. Prompt LLM with: domain docs + current week data + retrieved context → generate/update headlines
5. Score existing headlines against new data; retire those no longer supported

The vector DB serves to store prior week summaries and headlines so the LLM can reason about trends over time without exceeding context limits.
