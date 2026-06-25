# Day-0 Accepted Warning Register

## Scope
This register classifies known warnings before any future forward dry-run.
It does not start forward dry-run.
Historical data authorization is not trading authorization.

## Accepted Warnings
- source_download_failed: raw_count=5 rationale=optional source failed but replacement/proxy source is active or documented
- source_download_failed: raw_count=4 rationale=optional source failed but replacement/proxy source is active or documented
- missing_optional_package: raw_count=2 rationale=internal global-briefing package not_configured accepted in proxy mode; internal signal not validated
- missing_signal_component: raw_count=2 rationale=EPU partial accepted because Global/China proxy components are available
- source_download_failed: raw_count=2 rationale=optional source failed but replacement/proxy source is active or documented
- missing_signal_component: raw_count=1 rationale=OECD macro-cycle proxy accepted only when clearly marked as proxy
- source_download_failed: raw_count=1 rationale=optional source failed but replacement/proxy source is active or documented
- lot_size_constraint: raw_count=172 rationale=isolated replay execution model limitation from lot size and target weight
- missing_price: raw_count=156 rationale=remaining missing prices are accepted historical replay limitations, not forward validation evidence
- coverage_gap: raw_count=123 rationale=proxy coverage accepted: 0.9490196078431372

## Unresolved Warnings
- none

## Blocking Warnings
- none

## Boundary
- warning register only
- not forward dry-run
- run-daily not called
- main ledger not written
