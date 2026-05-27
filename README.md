# hullproof — Python client for the Hullproof API

`pip install hullproof` *(once published — currently lives in `clients/python/` of the dashboard repo)*

Python client for the Hullproof asset-condition intelligence platform. Wraps the public HTTP API: CoatingPassport retrieval, ISO 19030 hull performance evaluation, exports to Cognite Data Fusion, OSDU, and DNV Veracity, and the MCP tool surface.

## Quick start

```python
from hullproof import Client

client = Client(api_key="hp_...")

# Fetch a passport (demo or live)
passport = client.get_passport("demo-offshore-jacket-001")
for finding in passport["findings"]:
    print(finding["category"], finding["severity"], finding["confidence"])

# Compute an ISO 19030 Performance Value
result = client.compute_iso19030_performance_value(
    voyage={
        "vesselImo": "9123456",
        "vesselName": "MV EXAMPLE",
        "vesselType": "container",
        "designDraftMetres": 12.5,
        "dwt": 60000,
        "segments": [
            {
                "start": "2026-01-01T00:00:00Z",
                "end": "2026-01-02T00:00:00Z",
                "speedKnots": 21,
                "draftMetres": 12.5,
                "consumptionTonnes": 100.0,
                "weather": {"hsMetres": 1.5, "windSpeedMs": 4.0, "windAngleDeg": 60},
            },
        ],
    },
    reference_period={
        "startUtc": "2025-01-01T00:00:00Z",
        "endUtc": "2025-01-10T00:00:00Z",
        "source": "sea_trial",
        "documentationUri": "gs://your-bucket/sea-trial.pdf",
    },
    evaluation_period={
        "startUtc": "2026-01-01T00:00:00Z",
        "endUtc": "2026-01-11T00:00:00Z",
    },
)

pv = result["performance_value"]
print(f"PV: {pv['value']:.2f} % speed loss")
print(f"ISO 19030 compliant: {pv['iso19030Compliant']}")
print(f"Validation missing fields: {result['validation']['missing']}")
```

## Async variant

```python
import asyncio
from hullproof import AsyncClient

async def main() -> None:
    async with AsyncClient(api_key="hp_...") as client:
        passport = await client.get_passport("demo-offshore-jacket-001")
        return passport

asyncio.run(main())
```

## Methods

| Method | Tier | What it does |
|---|---|---|
| `list_tools()` | open | MCP-compatible tool discovery |
| `get_coating_passport_schema()` | open | Canonical CoatingPassport JSON Schema |
| `list_supported_asset_types()` | open | Asset types + applicable standards |
| `get_passport(passport_id)` | `self_serve` | Retrieve passport |
| `ask_passport(passport_id, question)` | `enterprise_api` | Visual Question Answering |
| `diff_passports(base_id, compare_id)` | `enterprise_api` | Diff two passport versions |
| `export_passport_to_cdf(passport_id)` | `platform` | Cognite Data Fusion shape |
| `export_passport_to_osdu(passport_id)` | `platform` | OSDU work-product format |
| `compute_iso19030_performance_value(...)` | `enterprise_api` | ISO 19030 PV with confidence band |

Tier names follow the pricing table in CLAUDE.md §5. Tier enforcement is server-side — calling above your tier returns HTTP 403.

## Errors

The client raises `HullproofError` on non-2xx responses with `status_code`, `message`, and `body`:

```python
from hullproof import Client, HullproofError

try:
    passport = client.get_passport("does-not-exist")
except HullproofError as exc:
    if exc.status_code == 404:
        print("Passport not found")
    else:
        raise
```

## Development

```bash
cd clients/python
pip install -e ".[dev]"
ruff check .
mypy hullproof
pytest
```

## License

Proprietary. Contact `support@hullproof.com` for usage outside the standard tier model.
