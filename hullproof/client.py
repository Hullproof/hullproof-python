"""Hullproof HTTP client — sync + async variants over httpx.

Auth: bearer token in the `Authorization` header. Obtain from the Hullproof
account page or via an API-key-issuance endpoint (`/api/account/api-keys` —
operator-tier and above per CLAUDE.md §5).

Tier note: methods are tier-gated server-side. The client does not enforce
tiers locally — calling an endpoint your tier does not cover returns 403.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

import httpx

from .types import (
    EvaluationPeriod,
    Iso19030ValidationResult,
    PerformanceValue,
    ReferencePeriod,
    VoyageInput,
)

DEFAULT_BASE_URL = "https://hullproof.com"
DEFAULT_TIMEOUT_S = 30.0


class HullproofError(Exception):
    """Raised when the Hullproof API returns a non-2xx response."""

    def __init__(self, status_code: int, message: str, body: Any = None) -> None:
        super().__init__(f"[{status_code}] {message}")
        self.status_code = status_code
        self.message = message
        self.body = body


def _build_headers(api_key: str | None, extra: Mapping[str, str] | None = None) -> dict[str, str]:
    headers = {
        "User-Agent": "hullproof-python/0.1.0",
        "Accept": "application/json",
    }
    if api_key:
        headers["Authorization"] = f"Bearer {api_key}"
    if extra:
        headers.update(extra)
    return headers


def _raise_for_response(response: httpx.Response) -> None:
    if response.is_success:
        return
    body: Any
    try:
        body = response.json()
    except ValueError:
        body = response.text
    message = body.get("message") if isinstance(body, dict) else str(body)
    raise HullproofError(response.status_code, message or response.reason_phrase, body=body)


class Client:
    """Synchronous Hullproof client."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            timeout=timeout,
            headers=_build_headers(api_key),
        )

    def __enter__(self) -> "Client":
        return self

    def __exit__(self, *exc: object) -> None:
        self._client.close()

    def close(self) -> None:
        self._client.close()

    # ── MCP / discovery ──

    def list_tools(self) -> dict[str, Any]:
        """List MCP-compatible tools the server exposes."""
        response = self._client.get("/api/mcp/tools")
        _raise_for_response(response)
        return response.json()

    def get_coating_passport_schema(self) -> dict[str, Any]:
        """Get the canonical CoatingPassport JSON Schema."""
        response = self._client.get("/api/mcp/schema/coating-passport")
        _raise_for_response(response)
        return response.json()

    def list_supported_asset_types(self) -> dict[str, Any]:
        """List supported asset types and their applicable standards."""
        response = self._client.get("/api/mcp/asset-types")
        _raise_for_response(response)
        return response.json()

    # ── Passport CRUD-ish ──

    def get_passport(self, passport_id: str) -> dict[str, Any]:
        """Retrieve a CoatingPassport by id (or demo fixture id)."""
        response = self._client.get(f"/api/passports/{passport_id}")
        _raise_for_response(response)
        return response.json()

    def ask_passport(self, passport_id: str, question: str) -> dict[str, Any]:
        """Visual Question Answering against a CoatingPassport."""
        response = self._client.post(
            f"/api/passports/{passport_id}/qa",
            json={"question": question},
        )
        _raise_for_response(response)
        return response.json()

    def diff_passports(self, base_passport_id: str, compare_passport_id: str) -> dict[str, Any]:
        """Diff two CoatingPassport versions of the same asset."""
        response = self._client.get(
            f"/api/passports/{base_passport_id}/diff",
            params={"against": compare_passport_id},
        )
        _raise_for_response(response)
        return response.json()

    # ── Exports ──

    def export_passport_to_cdf(self, passport_id: str) -> dict[str, Any]:
        """Export a CoatingPassport to Cognite Data Fusion shape."""
        response = self._client.get(f"/api/passports/{passport_id}/cdf")
        _raise_for_response(response)
        return response.json()

    def export_passport_to_osdu(self, passport_id: str) -> dict[str, Any]:
        """Export a CoatingPassport to OSDU work-product format."""
        response = self._client.get(f"/api/passports/{passport_id}/osdu")
        _raise_for_response(response)
        return response.json()

    # ── ISO 19030 ──

    def compute_iso19030_performance_value(
        self,
        voyage: VoyageInput,
        reference_period: ReferencePeriod,
        evaluation_period: EvaluationPeriod,
    ) -> dict[str, Any]:
        """Compute ISO 19030 PV with confidence band and correction log.

        Returns a dict containing `performance_value` (PerformanceValue),
        `validation` (Iso19030ValidationResult), and `meta`.
        """
        response = self._client.post(
            "/api/v1/iso19030/performance-value",
            json={
                "voyage": voyage,
                "referencePeriod": reference_period,
                "evaluationPeriod": evaluation_period,
            },
        )
        _raise_for_response(response)
        return response.json()


class AsyncClient:
    """Asynchronous Hullproof client. Mirror of `Client` over httpx.AsyncClient."""

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = DEFAULT_BASE_URL,
        timeout: float = DEFAULT_TIMEOUT_S,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            timeout=timeout,
            headers=_build_headers(api_key),
        )

    async def __aenter__(self) -> "AsyncClient":
        return self

    async def __aexit__(self, *exc: object) -> None:
        await self._client.aclose()

    async def aclose(self) -> None:
        await self._client.aclose()

    async def list_tools(self) -> dict[str, Any]:
        response = await self._client.get("/api/mcp/tools")
        _raise_for_response(response)
        return response.json()

    async def get_coating_passport_schema(self) -> dict[str, Any]:
        response = await self._client.get("/api/mcp/schema/coating-passport")
        _raise_for_response(response)
        return response.json()

    async def list_supported_asset_types(self) -> dict[str, Any]:
        response = await self._client.get("/api/mcp/asset-types")
        _raise_for_response(response)
        return response.json()

    async def get_passport(self, passport_id: str) -> dict[str, Any]:
        response = await self._client.get(f"/api/passports/{passport_id}")
        _raise_for_response(response)
        return response.json()

    async def ask_passport(self, passport_id: str, question: str) -> dict[str, Any]:
        response = await self._client.post(
            f"/api/passports/{passport_id}/qa",
            json={"question": question},
        )
        _raise_for_response(response)
        return response.json()

    async def diff_passports(
        self, base_passport_id: str, compare_passport_id: str
    ) -> dict[str, Any]:
        response = await self._client.get(
            f"/api/passports/{base_passport_id}/diff",
            params={"against": compare_passport_id},
        )
        _raise_for_response(response)
        return response.json()

    async def export_passport_to_cdf(self, passport_id: str) -> dict[str, Any]:
        response = await self._client.get(f"/api/passports/{passport_id}/cdf")
        _raise_for_response(response)
        return response.json()

    async def export_passport_to_osdu(self, passport_id: str) -> dict[str, Any]:
        response = await self._client.get(f"/api/passports/{passport_id}/osdu")
        _raise_for_response(response)
        return response.json()

    async def compute_iso19030_performance_value(
        self,
        voyage: VoyageInput,
        reference_period: ReferencePeriod,
        evaluation_period: EvaluationPeriod,
    ) -> dict[str, Any]:
        response = await self._client.post(
            "/api/v1/iso19030/performance-value",
            json={
                "voyage": voyage,
                "referencePeriod": reference_period,
                "evaluationPeriod": evaluation_period,
            },
        )
        _raise_for_response(response)
        return response.json()


# Re-export validation result type for convenience.
__all__ = [
    "AsyncClient",
    "Client",
    "HullproofError",
    "Iso19030ValidationResult",
]
