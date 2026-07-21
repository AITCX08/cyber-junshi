import pytest

from cyber_junshi.core.models import RiskLevel
from cyber_junshi.core.safety import assess_safety


@pytest.mark.parametrize(
    ("text", "level"),
    [
        ("我们下周再约时间聊", RiskLevel.NORMAL),
        ("对方持续威胁要公开我的住址", RiskLevel.ELEVATED),
        ("我现在就要伤害自己", RiskLevel.EMERGENCY),
        ("I am going to hurt myself right now", RiskLevel.EMERGENCY),
    ],
)
def test_routes_synthetic_text_by_immediate_risk(text: str, level: RiskLevel) -> None:
    result = assess_safety(text)

    assert result.level is level
    assert result.reasons
    assert text not in result.reasons


def test_emergency_route_prioritizes_immediate_local_help() -> None:
    result = assess_safety("我现在就要伤害自己")

    assert result.level is RiskLevel.EMERGENCY
    assert any("紧急" in step for step in result.next_steps)


def test_personality_label_alone_is_not_risk_evidence() -> None:
    result = assess_safety("我觉得他是NPD，所以他一定危险")

    assert result.level is RiskLevel.NORMAL


def test_rejects_blank_safety_input() -> None:
    with pytest.raises(ValueError, match="non-empty"):
        assess_safety("  ")
