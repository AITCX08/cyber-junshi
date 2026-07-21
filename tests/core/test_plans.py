import pytest

from cyber_junshi.core.decision import create_action_plan, review_decision
from cyber_junshi.core.models import ReviewStatus


def test_stop_signal_has_priority_over_success_signal() -> None:
    plan = create_action_plan(
        action="发送一次边界清晰的消息",
        observation_hours=48,
        success_signals=["对方给出明确回复"],
        downgrade_signals=["只回复表情"],
        stop_signals=["明确要求不要再联系"],
    )

    result = review_decision(plan, ["对方给出明确回复", "明确要求不要再联系"])

    assert result is ReviewStatus.STOP


@pytest.mark.parametrize(
    ("signals", "expected"),
    [
        (["只回复表情"], ReviewStatus.DOWNGRADE),
        (["对方给出明确回复"], ReviewStatus.CONTINUE),
        (["还没有可判断信号"], ReviewStatus.UNKNOWN),
    ],
)
def test_review_uses_explicit_signal_priority(signals: list[str], expected: ReviewStatus) -> None:
    plan = create_action_plan(
        "发送一次边界清晰的消息",
        48,
        ["对方给出明确回复"],
        ["只回复表情"],
        ["明确要求不要再联系"],
    )

    assert review_decision(plan, signals) is expected


def test_plan_rejects_missing_stop_signal() -> None:
    with pytest.raises(ValueError, match="stop"):
        create_action_plan("观察", 24, ["有回复"], ["含糊"], [])


@pytest.mark.parametrize("hours", [0, 8761, 24.5, True])
def test_plan_rejects_invalid_observation_window(hours: object) -> None:
    with pytest.raises(ValueError, match="observation_hours"):
        create_action_plan("观察", hours, ["有回复"], ["含糊"], ["拒绝联系"])  # type: ignore[arg-type]
