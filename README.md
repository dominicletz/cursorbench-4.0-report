# CursorBench 4.0 — Selected Models Report

Visual report of [CursorBench 4.0](https://cursor.com/cursorbench) focused on:

- Claude Opus 5.5
- Claude Fable 5.1
- Grok 4.7
- Muse Spark 1.3
- GPT-6 Astra *(estimate)*
- GPT-6 Luna *(estimate)*

## Important

**Cursor has not published GPT-6 CursorBench scores.** Astra and Luna placements are unofficial rough estimates derived from relative performance on FrontierCode 1.1 and Terminal-Bench 4.0 versus models that do have official CursorBench results. Treat them as illustrative, not as Cursor-published numbers.

## Files

| File | Description |
|------|-------------|
| [index.html](index.html) | Self-contained HTML report (charts embedded) |
| [cursorbench-4.0-score-vs-cost.png](cursorbench-4.0-score-vs-cost.png) | Score vs cost scatter (log cost) |
| [cursorbench-4.0-top-bar.png](cursorbench-4.0-top-bar.png) | Horizontal ranking by score |
| [data.json](data.json) | Plotted points with `estimated` flags |
| [throughput.json](throughput.json) | Family average output tokens/s (Artificial Analysis) |

## Official headline scores

| Model | Score | Cost / task |
|-------|------:|------------:|
| Opus 5.5 Max | 57.8% | $13.43 |
| Fable 5.1 Max | 51.8% | $17.28 |
| Grok 4.7 Extra High | 46.3% | $6.01 |
| Muse Spark 1.3 Max | 41.6% | $2.64 |

## Estimated placements

| Model | Est. score | Est. cost / task |
|-------|-----------:|-----------------:|
| GPT-6 Astra Max | ~54% | ~$8.50 |
| GPT-6 Luna Max | ~31% | ~$0.22 |

Official data from [cursor.com/cursorbench](https://cursor.com/cursorbench) (Sep 2026). Not affiliated with Cursor.

## Live page

https://dominicletz.github.io/cursorbench-4.0-report/
