"""Shared immutable value objects for the decision core."""

from dataclasses import dataclass
from enum import Enum
from numbers import Real


class RiskLevel(str, Enum):
    """Coarse route selected before any tactical decision support."""

    NORMAL = "normal"
    ELEVATED = "elevated"
    EMERGENCY = "emergency"


@dataclass(frozen=True)
class SafetyAssessment:
    """Explainable result from the deterministic safety gate."""

    level: RiskLevel
    reasons: tuple[str, ...]
    next_steps: tuple[str, ...]


@dataclass(frozen=True)
class FactLayers:
    """A case split into observations, interpretations, and open questions."""

    facts: tuple[str, ...]
    inferences: tuple[str, ...]
    unknowns: tuple[str, ...]


class ReviewStatus(str, Enum):
    """Result of comparing observed signals with a precommitted plan."""

    STOP = "stop"
    DOWNGRADE = "downgrade"
    CONTINUE = "continue"
    UNKNOWN = "unknown"


@dataclass(frozen=True)
class OptionInput:
    """Explainable 0..10 metrics for one possible action."""

    name: str
    short_term_gain: float
    long_term_cost: float
    reversibility: float
    risk: float
    information_gain: float

    def __post_init__(self) -> None:
        normalized_name = " ".join(self.name.split()) if isinstance(self.name, str) else ""
        if not normalized_name:
            raise ValueError("option name must be a non-empty string")
        object.__setattr__(self, "name", normalized_name)
        for field_name in (
            "short_term_gain",
            "long_term_cost",
            "reversibility",
            "risk",
            "information_gain",
        ):
            value = getattr(self, field_name)
            if isinstance(value, bool) or not isinstance(value, Real) or not 0 <= value <= 10:
                raise ValueError(f"{field_name} must be a number in 0..10")


@dataclass(frozen=True)
class ScoredOption:
    """An option plus the transparent weighted result."""

    name: str
    short_term_gain: float
    long_term_cost: float
    reversibility: float
    risk: float
    information_gain: float
    score: float


@dataclass(frozen=True)
class ActionPlan:
    """A bounded action with an observation window and exit rules."""

    action: str
    observation_hours: int
    success_signals: tuple[str, ...]
    downgrade_signals: tuple[str, ...]
    stop_signals: tuple[str, ...]
