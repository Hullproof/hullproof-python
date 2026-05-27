# Changelog

All notable changes to the `hullproof` Python client are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] — 2026-05-27

### Added
- `Client.download_iso19030_evidence_pdf(passport_id, draft=False)` — returns raw PDF bytes. Tribunal-grade evidence report for charter-party disputes, P&I claims, EU MRV verifier challenges. Raises `HullproofError(409)` if the passport has no `PerformanceValue`.
- `Client.get_fleet_summary(passport_ids=None, asset_type=None)` — aggregates a fleet of CoatingPassports into per-severity / per-category / PV-distribution counts plus a sorted high-severity findings list. Without arguments, runs against the public demo fixtures (zero-setup).
- Same two methods mirrored on `AsyncClient`.

## [0.1.0] — 2026-05-27

Initial public release.

### Added
- `Client` and `AsyncClient` over httpx, mirror APIs for sync and async use.
- MCP discovery: `list_tools`, `get_coating_passport_schema`, `list_supported_asset_types`.
- Passport access: `get_passport`, `ask_passport`, `diff_passports`.
- Exports: `export_passport_to_cdf`, `export_passport_to_osdu`.
- ISO 19030: `compute_iso19030_performance_value` covering voyage, reference period, evaluation period.
- `HullproofError` with `status_code`, `message`, `body` for non-2xx responses.
- TypedDict stubs for `VoyageInput`, `VoyageSegmentInput`, `WeatherObservation`, `ReferencePeriod`, `EvaluationPeriod`, `CorrectionEntry`, `PerformanceValue`, `Iso19030ValidationResult`.

### Notes
- Built against the public Hullproof API at `https://hullproof.com` and its MCP discovery endpoint at `/api/mcp/tools`.
- The canonical CoatingPassport JSON Schema lives at [Hullproof/coating-passport-spec](https://github.com/Hullproof/coating-passport-spec).
- Python 3.10+ required.
