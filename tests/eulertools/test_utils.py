import pytest

from eulertools import utils


@pytest.mark.parametrize(
    ("values", "expected"),
    [
        ([1, 4, 3, 2], 2),
        ([1, 2, 3], 2),
        ([1, 2, 3, 4], 2),
        ([1, 45, 3, 34569], 24),
    ],
)
def test_get_average(values: list[int], expected: int) -> None:
    timings = [utils.Timing.from_nanoseconds(value) for value in values]
    assert utils.get_average(timings) == utils.Timing.from_nanoseconds(expected)
