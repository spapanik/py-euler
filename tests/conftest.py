import os
from pathlib import Path

import pytest

from eulertools.lib.utils import Problem


@pytest.fixture()
def problem() -> Problem:
    return Problem(id="1", name="p0001", statement=Path(os.devnull))
