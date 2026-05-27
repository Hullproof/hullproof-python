"""Type definitions mirroring the canonical CoatingPassport and ISO 19030 schemas.

These TypedDicts are advisory — the server is authoritative. They let editors and
type-checkers warn about obvious mistakes (typo'd field names, wrong unit values),
but the SDK does not validate at runtime. For runtime validation, use the
`/api/openapi` endpoint and a pydantic model generated from the OpenAPI schema.

Fields use snake_case to match the persisted CoatingPassport schema in
`src/lib/passport/types.ts`. ISO 19030 internal types in
`src/lib/attribution/types.ts` use camelCase; the camelCase / snake_case mapping
is done by `toCoatingPassportPerformance()` server-side.
"""

from __future__ import annotations

from typing import Literal, TypedDict


# ──── ISO 19030 ────


class WeatherObservation(TypedDict, total=False):
    """Per-segment weather context for the biofouling attribution engine."""

    hsMetres: float
    windSpeedMs: float
    windAngleDeg: float
    currentAlongMs: float


class VoyageSegmentInput(TypedDict, total=False):
    """One leg of a voyage with observed consumption and conditions."""

    start: str
    end: str
    speedKnots: float
    draftMetres: float
    consumptionTonnes: float
    weather: WeatherObservation
    note: str


VesselType = Literal[
    "bulker",
    "tanker",
    "container",
    "pcc",
    "general_cargo",
    "offshore_supply",
    "fishing",
    "other",
]


class VoyageInput(TypedDict, total=False):
    """Full voyage input to ISO 19030 PV computation."""

    vesselImo: str
    vesselName: str
    vesselType: VesselType
    designDraftMetres: float
    dwt: float
    daysSinceLastClean: float
    hullInspectionAnalysisId: str
    segments: list[VoyageSegmentInput]


ReferenceConditionSource = Literal[
    "sea_trial",
    "post_drydock",
    "design_point",
    "rolling_baseline",
]


class ReferencePeriod(TypedDict, total=False):
    """ISO 19030 reference period — anchored to sea trial or dry-dock."""

    startUtc: str
    endUtc: str
    source: ReferenceConditionSource
    documentationUri: str


class EvaluationPeriod(TypedDict):
    """ISO 19030 in-service evaluation window."""

    startUtc: str
    endUtc: str


CorrectionKind = Literal[
    "wind",
    "wave",
    "draft",
    "current",
    "water_density",
    "shallow_water",
]


class CorrectionEntry(TypedDict):
    """One line in the ISO 19030 correction log."""

    kind: CorrectionKind
    tonnes: float
    rationale: str


PerformanceMethod = Literal[
    "iso_19030_2",
    "iso_19030_3_a",
    "iso_19030_3_b",
    "hullproof_attribution_v1",
]


class PerformanceValue(TypedDict):
    """The ISO 19030 Performance Value with confidence band and audit lineage."""

    value: float
    unit: Literal["pct_speed_loss", "pct_power_excess"]
    confidenceBand: tuple[float, float]
    iso19030Compliant: bool
    referencePeriod: ReferencePeriod
    evaluationPeriod: EvaluationPeriod
    correctionLog: list[CorrectionEntry]
    method: PerformanceMethod
    computedAt: str


class Iso19030ValidationResult(TypedDict):
    """Result of `validateIso19030Completeness()` — what is missing or warned about."""

    compliant: bool
    missing: list[str]
    warnings: list[str]
