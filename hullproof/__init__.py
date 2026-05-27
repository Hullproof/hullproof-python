"""Hullproof Python client.

Quick start:

    from hullproof import Client

    client = Client(api_key="hp_...", base_url="https://hullproof.com")
    passport = client.get_passport("demo-offshore-jacket-001")
    print(passport["findings"][0]["confidence"])

Async variant:

    from hullproof import AsyncClient

    async with AsyncClient(api_key="hp_...") as client:
        passport = await client.get_passport("demo-offshore-jacket-001")
"""

from .client import AsyncClient, Client, HullproofError
from .types import (
    CorrectionEntry,
    EvaluationPeriod,
    Iso19030ValidationResult,
    PerformanceValue,
    ReferencePeriod,
    VoyageInput,
    VoyageSegmentInput,
    WeatherObservation,
)

__version__ = "0.1.0"

__all__ = [
    "AsyncClient",
    "Client",
    "CorrectionEntry",
    "EvaluationPeriod",
    "HullproofError",
    "Iso19030ValidationResult",
    "PerformanceValue",
    "ReferencePeriod",
    "VoyageInput",
    "VoyageSegmentInput",
    "WeatherObservation",
    "__version__",
]
