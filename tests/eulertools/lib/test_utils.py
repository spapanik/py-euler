import pytest
from pyutilkit.timing import Timing

from eulertools.lib import utils


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
    timings = [Timing(nanoseconds=value) for value in values]
    assert utils.get_average(timings) == Timing(nanoseconds=expected)
