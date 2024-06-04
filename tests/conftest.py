import os
from pathlib import Path

import pytest
from pyutilkit.timing import Timing

from eulertools.lib.utils import CaseId, Language, Problem, Summary

DEV_NULL = Path(os.devnull)


@pytest.fixture()
def problems() -> list[Problem]:
    return [
        Problem(id="1", name="p0001", statement=DEV_NULL),
        Problem(id="42", name="p0042", statement=DEV_NULL),
    ]


@pytest.fixture()
def languages() -> list[Language]:
    return [
        Language(
            name="c",
            suffix=".c",
            path=DEV_NULL,
            solutions_path=DEV_NULL,
            settings_path=DEV_NULL,
            runner=DEV_NULL,
        ),
        Language(
            name="python",
            suffix="py",
            path=DEV_NULL,
            solutions_path=DEV_NULL,
            settings_path=DEV_NULL,
            runner=DEV_NULL,
        ),
    ]


@pytest.fixture()
def summary(problems: list[Problem], languages: list[Language]) -> Summary:
    problem_1 = problems[0]
    problem_42 = problems[1]
    c = languages[0]
    python = languages[1]
    summary = Summary(problems={})
    p1_summary = summary.get_or_create_problem(problem_1)
    case_1_1 = p1_summary.get_or_create_case(CaseId(problem=problem_1, case_key="1"))
    case_1_1.answer = "233168"
    case_1_1.timings = {c: Timing(nanoseconds=44), python: Timing(nanoseconds=662)}

    case_1_2 = p1_summary.get_or_create_case(CaseId(problem=problem_1, case_key="2"))
    case_1_2.answer = "23331668"
    case_1_2.timings = {c: Timing(nanoseconds=48), python: Timing(nanoseconds=721)}

    p42_summary = summary.get_or_create_problem(problem_42)
    case_42_1 = p42_summary.get_or_create_case(CaseId(problem=problem_42, case_key="1"))
    case_42_1.answer = "162"
    case_42_1.timings = {python: Timing(nanoseconds=1400121)}

    return summary


@pytest.fixture()
def data_dir() -> Path:
    return Path(__file__).parent.joinpath("data")
