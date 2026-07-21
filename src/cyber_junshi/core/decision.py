"""Pure functions for structuring and reviewing decisions."""

from collections.abc import Iterable

from cyber_junshi.core.models import (
    ActionPlan,
    FactLayers,
    OptionInput,
    ReviewStatus,
    ScoredOption,
)


def _normalize_items(values: Iterable[str], field_name: str) -> tuple[str, ...]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        if not isinstance(value, str):
            raise ValueError(f"{field_name} entries must be strings")
        item = " ".join(value.split())
        if item and item not in seen:
            seen.add(item)
            normalized.append(item)
    return tuple(normalized)


def structure_case(
    facts: Iterable[str],
    inferences: Iterable[str],
    unknowns: Iterable[str],
) -> FactLayers:
    """Normalize a case while keeping evidence layers mutually exclusive."""

    normalized_facts = _normalize_items(facts, "facts")
    normalized_inferences = _normalize_items(inferences, "inferences")
    normalized_unknowns = _normalize_items(unknowns, "unknowns")
    if not (normalized_facts or normalized_inferences or normalized_unknowns):
        raise ValueError("at least one case item is required")

    layer_sets = (set(normalized_facts), set(normalized_inferences), set(normalized_unknowns))
    overlap = (layer_sets[0] & layer_sets[1]) | (layer_sets[0] & layer_sets[2]) | (
        layer_sets[1] & layer_sets[2]
    )
    if overlap:
        raise ValueError("the same item cannot appear in multiple layers")

    return FactLayers(
        facts=normalized_facts,
        inferences=normalized_inferences,
        unknowns=normalized_unknowns,
    )


def compare_options(options: Iterable[OptionInput]) -> tuple[ScoredOption, ...]:
    """Rank options with an explicit, stable, and inspectable scoring rule."""

    option_list = list(options)
    if len(option_list) < 2:
        raise ValueError("at least two options are required")
    if not all(isinstance(option, OptionInput) for option in option_list):
        raise ValueError("options must contain OptionInput values")

    scored = [
        ScoredOption(
            name=option.name,
            short_term_gain=option.short_term_gain,
            long_term_cost=option.long_term_cost,
            reversibility=option.reversibility,
            risk=option.risk,
            information_gain=option.information_gain,
            score=round(
                0.30 * option.short_term_gain
                + 0.25 * option.information_gain
                + 0.20 * option.reversibility
                - 0.20 * option.long_term_cost
                - 0.25 * option.risk,
                3,
            ),
        )
        for option in option_list
    ]
    return tuple(sorted(scored, key=lambda option: option.score, reverse=True))


def create_action_plan(
    action: str,
    observation_hours: int,
    success_signals: Iterable[str],
    downgrade_signals: Iterable[str],
    stop_signals: Iterable[str],
) -> ActionPlan:
    """Create a bounded plan whose stop conditions exist before action."""

    normalized_action = " ".join(action.split()) if isinstance(action, str) else ""
    if not normalized_action:
        raise ValueError("action must be a non-empty string")
    if (
        isinstance(observation_hours, bool)
        or not isinstance(observation_hours, int)
        or not 1 <= observation_hours <= 8_760
    ):
        raise ValueError("observation_hours must be an integer from 1 through 8760")

    normalized_success = _normalize_items(success_signals, "success_signals")
    normalized_downgrade = _normalize_items(downgrade_signals, "downgrade_signals")
    normalized_stop = _normalize_items(stop_signals, "stop_signals")
    if not normalized_success:
        raise ValueError("at least one success signal is required")
    if not normalized_stop:
        raise ValueError("at least one stop signal is required")

    signal_sets = (set(normalized_success), set(normalized_downgrade), set(normalized_stop))
    overlap = (signal_sets[0] & signal_sets[1]) | (signal_sets[0] & signal_sets[2]) | (
        signal_sets[1] & signal_sets[2]
    )
    if overlap:
        raise ValueError("the same signal cannot appear in multiple conditions")

    return ActionPlan(
        action=normalized_action,
        observation_hours=observation_hours,
        success_signals=normalized_success,
        downgrade_signals=normalized_downgrade,
        stop_signals=normalized_stop,
    )


def review_decision(plan: ActionPlan, observed_signals: Iterable[str]) -> ReviewStatus:
    """Review observed signals with safety-oriented deterministic priority."""

    if not isinstance(plan, ActionPlan):
        raise ValueError("plan must be an ActionPlan")
    observed = set(_normalize_items(observed_signals, "observed_signals"))
    if observed & set(plan.stop_signals):
        return ReviewStatus.STOP
    if observed & set(plan.downgrade_signals):
        return ReviewStatus.DOWNGRADE
    if observed & set(plan.success_signals):
        return ReviewStatus.CONTINUE
    return ReviewStatus.UNKNOWN
