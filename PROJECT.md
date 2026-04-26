# Chimera — Autonomous Earning System v2

> "All numbers are REAL. No simulation."

## What Is Chimera?

Chimera is an autonomous earning system that runs AI agents to generate real revenue.
Each agent does actual work (generate content, publish to social media, create digital products)
and honestly tracks financial outcomes.

## Architecture

```
chimera/
├── daemon.py          # Orchestrator: runs agents, updates ledger
├── agents_src/        # Agent Python modules
│   ├── seo_farm.py        # Generate SEO articles → ad/affiliate revenue
│   ├── social_operator.py # Publish to Toutiao/Weibo → platform earnings
│   └── product_scout.py   # Create Gumroad products → sales revenue
├── agents/            # Agent state (JSON) — auto-managed
├── domains/           # Content output
│   ├── seo_farm/sites/    # Generated HTML articles
│   └── products/          # Digital product packages
├── ledger.json        # Real financial tracking (NEVER fake)
├── logs/              # Execution logs (daily)
└── PROJECT.md         # This file
```

## Agents

### 1. SEO Farm (`seo_farm`)
- **What**: Generates SEO-optimized HTML articles from keyword list
- **Revenue model**: Ad impressions + affiliate links (requires deployed site)
- **Current status**: ✅ Generating articles locally | ❌ Not deployed yet
- **Next step**: Deploy to Cloudflare Pages + add analytics (Plausible/Umami)

### 2. Social Operator (`social_operator`)
- **What**: Publishes micro-posts to Toutiao (头条号) via Selenium+CDP
- **Revenue model**: Platform creator fund (头条创作收益)
- **Current status**: ✅ CDP connected | ❌ Login session expired
- **Next step**: Refresh Toutiao login session, then auto-publish

### 3. Product Scout (`product_scout`)
- **What**: Creates digital product content packages for Gumroad
- **Revenue model**: Direct sales ($4.99-$19.99 per product)
- **Current status**: ✅ Content generation works | ❌ Not listed on Gumroad yet
- **Next step**: List products on Gumroad via CDP automation

## Revenue Tracking Rules

1. **NEVER simulate revenue** — `random.uniform()` is forbidden
2. **Only count verified money** — API confirmed or dashboard scraped
3. **$0 is honest** — Unknown revenue = $0, not estimated
4. **Log everything** — All actions recorded in daily logs

## How to Run

```bash
cd ~/chimera
python3 daemon.py  # Run one cycle
```

## Continue Development

1. `cat PROJECT.md` — Read this file
2. `cat ledger.json` — Check real revenue
3. `cat agents/<name>.json` — Check agent state
4. `cat logs/$(date +%Y-%m-%d).log` — Check today's log
5. Pick a "next step" from any agent and implement it

## Goals

| Milestone | Target | Current |
|-----------|--------|---------|
| First real $1 | $1.00 | $0.00 |
| First real $10 | $10.00 | $0.00 |
| First real $100 | $100.00 | $0.00 |
| Monthly $100 | $100/mo | $0/mo |
| Monthly $1000 | $1000/mo | $0/mo |

## Key Decisions

- v1 used `random.uniform()` for fake profits → **REJECTED**
- v2 uses real execution + honest $0 until verified revenue comes in
- All agent state persisted as JSON for easy inspection
- Daemon is stateless per cycle — cron calls `daemon.py` which runs once and exits

## Last Updated
2026-04-24
