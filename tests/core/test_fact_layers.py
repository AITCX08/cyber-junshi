import pytest

from cyber_junshi.core.decision import structure_case


def test_structure_case_normalizes_and_deduplicates_each_layer() -> None:
    result = structure_case(
        facts=["对方取消了一次见面", " 对方取消了一次见面 "],
        inferences=["对方可能在回避"],
        unknowns=["取消的具体原因"],
    )

    assert result.facts == ("对方取消了一次见面",)
    assert result.inferences == ("对方可能在回避",)
    assert result.unknowns == ("取消的具体原因",)


def test_structure_case_rejects_an_item_in_multiple_layers() -> None:
    with pytest.raises(ValueError, match="multiple layers"):
        structure_case(["对方取消了见面"], ["对方取消了见面"], [])


def test_structure_case_rejects_completely_empty_case() -> None:
    with pytest.raises(ValueError, match="at least one"):
        structure_case([], [], [])
