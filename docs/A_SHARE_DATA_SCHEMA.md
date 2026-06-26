# A-share Data Schema

v0.7.1 defines the first local schema contract for future A-share selection research. These schemas are data inputs only and are not stock recommendations.

## Equity Master

Primary key: `symbol`

Required columns:

```text
symbol
exchange
market
name
list_date
delist_date
board
is_active
is_st
is_star_market
is_chinext
is_bse
currency
source
source_timestamp
```

Symbol format is normalized to forms such as `600000.SH`, `000001.SZ`, and `430047.BJ`.

## Trading Calendar

Primary key: `date`, `exchange`

Required columns:

```text
date
exchange
is_trading_day
previous_trading_day
next_trading_day
source
source_timestamp
```

v0.7.1 covers SSE, SZSE, and BSE. The foundation calendar can use a weekday fallback, which must remain visible through `source` and audit documentation.

## Daily Price Panel

Primary key: `date`, `symbol`

Required columns:

```text
date
symbol
open
high
low
close
volume
amount
turnover
pre_close
change
pct_change
source
source_timestamp
```

Schema audit checks symbol/date format, duplicate primary keys, finite numeric values, price sanity, high/low consistency, and non-negative volume/amount.

## Adjusted Price Panel

Primary key: `date`, `symbol`, `adjustment_type`

Required columns:

```text
date
symbol
adj_open
adj_high
adj_low
adj_close
adj_factor
adjustment_type
source
source_timestamp
```

Allowed adjustment types are `forward_adjusted`, `backward_adjusted`, and `raw`. When only raw prices are available, the fallback must be labeled and coverage-audited.

## Daily Basic Panel

Primary key: `date`, `symbol`

Required columns:

```text
date
symbol
total_mv
circ_mv
turnover_rate
volume_ratio
pe
pe_ttm
pb
ps
ps_ttm
dv_ratio
dv_ttm
source
source_timestamp
```

Free provider gaps are allowed as nullable fields only when the manifest and audit retain the missing-field evidence.

## Industry Classification

Primary key: `symbol`, `industry_standard`, `effective_date`

Required columns:

```text
symbol
industry_level_1
industry_level_2
industry_level_3
industry_standard
effective_date
source
source_timestamp
```

If a public industry taxonomy is unavailable, v0.7.1 can use board-level fallback labels. That fallback is not a real industry signal and must remain audit-visible.

## Basic Financials Panel

Primary key: `report_date`, `symbol`

Required columns:

```text
report_date
ann_date
symbol
revenue
net_profit
roe
gross_margin
net_margin
operating_cash_flow
debt_to_asset
eps
bps
source
source_timestamp
```

v0.7.1 permits nullable basic-financial fields when free-source coverage is unavailable. The panel must still provide symbol coverage and field coverage metadata.

## Common Requirements

Every persisted data table must include `source` and `source_timestamp`. Later v0.7 filters, features, scores, and portfolios must read these local schemas rather than provider-specific raw responses.
