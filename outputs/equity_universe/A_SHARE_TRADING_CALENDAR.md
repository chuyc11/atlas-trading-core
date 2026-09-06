# A-Share Trading Calendar

- source: official_exchange_holiday_schedule_v1
- source_url: https://www.sse.com.cn/disclosure/dealinstruc/closed/
- exchanges: BSE, SSE, SZSE
- trading_days: 486
- min_date: 2025-01-02
- max_date: 2027-01-01
- forward_horizon_end: 2027-01-02
- calendar_horizon_end: 2027-01-02
- horizon_clamped: false
years beyond official holiday coverage use weekday projection (source=weekday_projection_v1); unknown 2027+ holidays (New Year, Spring Festival, ...) are NOT excluded until the official schedule is published: 2027

## Boundary
- Data ingestion only.
- No stock scores generated.
- No candidates generated.
- No virtual portfolios generated.
- Official forward dry-run status unchanged.
- Day2 was not executed.
- run-daily was not called.
- No broker is connected.
- No real orders were placed.
- Third-party code was not merged into the main flow.
- This is not a model profit guarantee.
