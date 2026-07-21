import pytest

from cyber_junshi.core.decision import compare_options
from cyber_junshi.core.models import OptionInput


def test_compare_options_ranks_reversible_information_gaining_action_first() -> None:
    ranked = compare_options(
        [
            OptionInput("连续追问", 8, 8, 2, 8, 2),
            OptionInput("发一次澄清并观察", 6, 2, 9, 3, 8),
        ]
    )

    assert ranked[0].name == "发一次澄清并观察"
    assert ranked[0].score > ranked[1].score


def test_compare_options_keeps_explainable_raw_metrics() -> None:
    ranked = compare_options(
        [
            OptionInput("方案甲", 5, 4, 8, 2, 7),
            OptionInput("方案乙", 4, 3, 7, 3, 6),
        ]
    )

    assert ranked[0].short_term_gain in range(11)
    assert ranked[0].information_gain in range(11)


def test_option_rejects_metrics_outside_zero_to_ten() -> None:
    with pytest.raises(ValueError, match=r"0\.\.10"):
        OptionInput("越界", 11, 0, 0, 0, 0)


def test_compare_options_requires_two_options() -> None:
    with pytest.raises(ValueError, match="at least two"):
        compare_options([OptionInput("只有一个", 5, 5, 5, 5, 5)])
