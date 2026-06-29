# A-Share Provider Hardening

v0.8.0 introduces a provider registry and health-check layer.

Provider records include:

- provider id and type
- enabled status and priority
- dataset support matrix
- network and token requirements
- broker-account requirement flag
- timeout, retry, and rate-limit policy

Release mode uses local providers only:

- `local_file_provider`
- `cached_panel_provider`

Public providers are represented in the registry but disabled by default. `refresh_from_public_providers` requires explicit network and public-provider opt-in. Broker, account, and order providers are forbidden and cause audit failure if used.

Fallbacks must never be silent. Every fallback decision is written to `provider_fallback_report.json`.

v0.8.1 reads provider health and fallback evidence through the data refresh link. It does not enable broker, account, or order providers, and public provider refresh remains explicit opt-in only.
