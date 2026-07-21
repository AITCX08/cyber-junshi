"""Conservative and explainable safety routing.

This is a phrase-based screening gate, not a diagnosis or emergency service.
"""

from cyber_junshi.core.models import RiskLevel, SafetyAssessment

_EMERGENCY_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "immediate self-harm signal",
        (
            "现在就要伤害自己",
            "马上伤害自己",
            "我要自杀",
            "不想活了",
            "hurt myself right now",
            "kill myself",
            "going to commit suicide",
        ),
    ),
    (
        "immediate violence signal",
        (
            "现在就要伤害他",
            "马上去杀",
            "我要杀了他",
            "hurt them right now",
            "kill them now",
        ),
    ),
)

_ELEVATED_RULES: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "threat or coercion signal",
        ("持续威胁", "强迫我", "勒索我", "threatening me", "blackmail"),
    ),
    (
        "stalking or privacy-exposure signal",
        ("跟踪我", "公开我的住址", "泄露我的隐私", "stalking me", "publish my address"),
    ),
)


def _normalize_text(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        raise ValueError("text must be a non-empty string")
    return " ".join(text.casefold().split())


def _matched_categories(
    normalized_text: str,
    rules: tuple[tuple[str, tuple[str, ...]], ...],
) -> tuple[str, ...]:
    return tuple(
        category
        for category, phrases in rules
        if any(phrase in normalized_text for phrase in phrases)
    )


def assess_safety(text: str) -> SafetyAssessment:
    """Route a text into normal, elevated, or emergency handling.

    Returned reasons are rule categories and never repeat the supplied text.
    """

    normalized = _normalize_text(text)
    emergency_reasons = _matched_categories(normalized, _EMERGENCY_RULES)
    if emergency_reasons:
        return SafetyAssessment(
            level=RiskLevel.EMERGENCY,
            reasons=emergency_reasons,
            next_steps=(
                "停止策略分析，优先确保当事人和周围人的即时安全。",
                "联系当地紧急服务、危机热线或可信任且能立即到场的人。",
                "若可以安全做到，远离武器、药物或其他可能造成伤害的物品。",
            ),
        )

    elevated_reasons = _matched_categories(normalized, _ELEVATED_RULES)
    if elevated_reasons:
        return SafetyAssessment(
            level=RiskLevel.ELEVATED,
            reasons=elevated_reasons,
            next_steps=(
                "优先保存证据、减少暴露并告知可信任的人。",
                "根据所在地情况联系专业支持、平台安全团队或执法机构。",
                "不要使用可能升级冲突或绕过对方边界的策略。",
            ),
        )

    return SafetyAssessment(
        level=RiskLevel.NORMAL,
        reasons=("no immediate-risk signal matched",),
        next_steps=("继续进行事实分层和可逆的方案比较。",),
    )
