"""Smoke tests for the Hullproof client.

These tests verify the client constructs correctly, types compose without
import errors, and the HTTP layer is wired without hitting the network.
"""

from __future__ import annotations

import httpx
import pytest

from hullproof import (
    AsyncClient,
    Client,
    CorrectionEntry,
    EvaluationPeriod,
    HullproofError,
    PerformanceValue,
    ReferencePeriod,
    VoyageInput,
)


def test_client_constructs_with_api_key() -> None:
    client = Client(api_key="hp_test_smoke")
    assert client._client.headers["Authorization"] == "Bearer hp_test_smoke"
    client.close()


def test_client_constructs_without_api_key() -> None:
    client = Client()
    assert "Authorization" not in client._client.headers
    client.close()


def test_client_user_agent_set() -> None:
    client = Client()
    assert client._client.headers["User-Agent"].startswith("hullproof-python/")
    client.close()


def test_client_context_manager_closes() -> None:
    with Client() as client:
        assert client._client is not None
    # After exit the client should be closed; httpx raises on subsequent use.
    with pytest.raises(RuntimeError):
        client._client.get("/api/mcp/tools")


def test_async_client_constructs() -> None:
    client = AsyncClient(api_key="hp_test_smoke_async")
    assert client._client.headers["Authorization"] == "Bearer hp_test_smoke_async"


def test_hullproof_error_str() -> None:
    err = HullproofError(404, "passport not found", body={"error": "missing"})
    assert "[404]" in str(err)
    assert err.status_code == 404
    assert err.message == "passport not found"
    assert err.body == {"error": "missing"}


def test_typed_dicts_compose() -> None:
    """All TypedDicts should accept the canonical example shapes."""
    voyage: VoyageInput = {
        "vesselImo": "9123456",
        "vesselName": "TEST",
        "vesselType": "container",
        "designDraftMetres": 12.5,
        "dwt": 60000,
        "segments": [
            {
                "start": "2026-01-01T00:00:00Z",
                "end": "2026-01-02T00:00:00Z",
                "speedKnots": 21,
                "draftMetres": 12.5,
                "consumptionTonnes": 95.0,
                "weather": {
                    "hsMetres": 1.5,
                    "windSpeedMs": 4.0,
                    "windAngleDeg": 60,
                    "currentAlongMs": 0.0,
                },
            }
        ],
    }
    reference_period: ReferencePeriod = {
        "startUtc": "2025-01-01T00:00:00Z",
        "endUtc": "2025-01-10T00:00:00Z",
        "source": "sea_trial",
        "documentationUri": "gs://example/sea-trial.pdf",
    }
    evaluation_period: EvaluationPeriod = {
        "startUtc": "2026-01-01T00:00:00Z",
        "endUtc": "2026-01-11T00:00:00Z",
    }
    correction: CorrectionEntry = {
        "kind": "wind",
        "tonnes": 1.0,
        "rationale": "Aertssen head-wind.",
    }
    pv: PerformanceValue = {
        "value": 1.35,
        "unit": "pct_speed_loss",
        "confidenceBand": (1.2, 1.5),
        "iso19030Compliant": True,
        "referencePeriod": reference_period,
        "evaluationPeriod": evaluation_period,
        "correctionLog": [correction],
        "method": "hullproof_attribution_v1",
        "computedAt": "2026-01-11T00:00:00Z",
    }
    # If we reach here, types compose; no runtime assertion needed.
    assert pv["value"] == 1.35
    assert voyage["segments"][0]["speedKnots"] == 21


def test_client_methods_exist() -> None:
    client = Client()
    assert callable(client.list_tools)
    assert callable(client.get_coating_passport_schema)
    assert callable(client.list_supported_asset_types)
    assert callable(client.get_passport)
    assert callable(client.ask_passport)
    assert callable(client.diff_passports)
    assert callable(client.export_passport_to_cdf)
    assert callable(client.export_passport_to_osdu)
    assert callable(client.compute_iso19030_performance_value)
    client.close()


def test_async_client_methods_exist() -> None:
    client = AsyncClient()
    assert callable(client.list_tools)
    assert callable(client.compute_iso19030_performance_value)


def test_base_url_override() -> None:
    client = Client(base_url="http://localhost:3000")
    assert str(client._client.base_url) == "http://localhost:3000"
    client.close()
