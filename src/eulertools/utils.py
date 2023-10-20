from __future__ import annotations

import re
from dataclasses import dataclass, field
from decimal import Decimal
from enum import StrEnum, unique
from pathlib import Path
from typing import Any, Self

from dj_settings import SettingsParser

TIME_UNIT = re.compile(r"(\d+(?:\.\d+)?)\s?(.{0,2})")


@unique
class ANSIEscape(StrEnum):
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    FAIL = "\033[31m"
    OKGREEN = "\033[32m"
    OKBLUE = "\033[34m"
    WARNING = "\033[33m"


@unique
class Modes(StrEnum):
    TIMING = "timing"
    RUN = "run"


@dataclass(frozen=True, slots=True, order=True)
class Timing:
    time: Decimal = field(compare=False)
    unit: str = field(compare=False)
    nanoseconds: int = field(repr=False)

    @classmethod
    def from_nanoseconds(cls, nanoseconds: int) -> Self:
        if nanoseconds < 1000:
            return cls(time=Decimal(nanoseconds), unit="ns", nanoseconds=nanoseconds)
        microseconds = nanoseconds / 1000
        if microseconds < 1000:
            return cls(
                time=Decimal(f"{microseconds:.1f}"), unit="µs", nanoseconds=nanoseconds
            )
        milliseconds = microseconds / 1000
        if milliseconds < 1000:
            return cls(
                time=Decimal(f"{milliseconds:.1f}"), unit="ms", nanoseconds=nanoseconds
            )
        seconds = milliseconds / 1000
        return cls(time=Decimal(f"{seconds:.2f}"), unit="s", nanoseconds=nanoseconds)

    def __str__(self) -> str:
        return f"{self.time}{self.unit}"


@dataclass(frozen=True, slots=True, order=True)
class Language:
    name: str
    extension: str = field(repr=False, compare=False)
    path: Path = field(repr=False, compare=False)
    runner: Path = field(repr=False, compare=False)

    @classmethod
    def from_settings(cls, name: str) -> Self:
        project_root = _get_project_root()
        settings = get_settings()
        language = settings["languages"][name]
        return cls(
            name=name,
            extension=language.get("extension", name),
            path=project_root.joinpath(language.get("path", name)),
            runner=project_root.joinpath(language["runner"]),
        )

    def get_settings_root(self) -> Path:
        project_root = _get_project_root()
        project_settings_root = _get_settings_root()
        path = project_settings_root.joinpath(self.path.relative_to(project_root))
        if not path.exists():
            path.mkdir(parents=True)
        return path


def _get_project_root() -> Path:
    cwd = Path.cwd().resolve()
    while not cwd.joinpath(".euler").is_dir():
        if cwd.as_posix() == "/":
            raise RuntimeError("Could not find project root")
        cwd = cwd.parent
    return cwd


def _get_settings_root() -> Path:
    return _get_project_root().joinpath(".euler")


def _get_settings() -> Path:
    return _get_settings_root().joinpath("euler.toml")


def _get_answers() -> Path:
    file = _get_settings_root().joinpath("answers.txt")
    if not file.exists():
        file.touch(mode=0o644)
    return file


def _get_timings(language: Language) -> Path:
    file = language.get_settings_root().joinpath("timings.txt")
    if not file.exists():
        file.touch(mode=0o644)
    return file


def _get_statements_dir() -> Path:
    return _get_settings_root().joinpath("statements")


def _get_statement(problem: str) -> Path:
    statement = _get_statements_dir().joinpath(f"{problem}.toml")
    if not statement.exists():
        raise FileNotFoundError("No problem description found. Aborting...")

    return statement


def get_template(language: Language) -> Path:
    return language.get_settings_root().joinpath("solution.jinja")


def get_solution(language: Language, problem: str) -> Path:
    return language.path.joinpath("src", "solutions", f"{problem}.{language.extension}")


def get_statement(problem: str) -> dict[str, Any]:
    return SettingsParser(_get_statement(problem)).data


def get_settings() -> dict[str, Any]:
    return SettingsParser(_get_settings()).data


def get_line_timing(line: str) -> tuple[str, int, Timing]:
    problem_part, mode_id, timing = line.split(maxsplit=2)
    return problem_part, int(mode_id), Timing.from_nanoseconds(int(timing))


def get_line_answer(line: str) -> tuple[str, int, str]:
    problem_part, mode_id, *answers = line.split(maxsplit=2)
    if len(answers) == 0:
        answer = ""
    elif len(answers) == 1:
        answer = answers[0]
    else:
        raise RuntimeError("Too many answers")
    return problem_part, int(mode_id), answer


def get_answers() -> dict[str, dict[int, str]]:
    answers = _get_answers()
    output: dict[str, dict[int, str]] = {}
    for line in answers.read_text().splitlines():
        problem, mode_id, answer = get_line_answer(line)
        output.setdefault(problem, {})[mode_id] = answer
    return output


def get_timings(language: Language) -> dict[str, dict[int, Timing]]:
    timings = _get_timings(language)
    output: dict[str, dict[int, Timing]] = {}
    for line in timings.read_text().splitlines():
        problem, mode_id, timing = get_line_timing(line)
        output.setdefault(problem, {})[mode_id] = timing
    return output


def get_context(language: Language, problem: str) -> dict[str, str]:
    statement = get_statement(problem)
    output = {"problem": problem}
    output |= statement.get(language.name, {})
    return output


def update_answers(answers: dict[str, dict[int, str]]) -> None:
    answers_path = _get_answers()
    with answers_path.open("w") as file:
        for problem in sorted(answers):
            for key in sorted(answers[problem]):
                answer = answers[problem][key]
                file.write(f"{problem} {key} {answer}\n")


def update_timings(language: Language, timings: dict[str, dict[int, Timing]]) -> None:
    timings_path = _get_timings(language)
    with timings_path.open("w") as file:
        for problem in sorted(timings):
            for key in sorted(timings[problem]):
                timing = timings[problem][key]
                file.write(f"{problem} {key} {timing.nanoseconds}\n")


def get_average(values: list[int]) -> int:
    if len(values) >= 3:
        values = sorted(values)[1:-1]
    return sum(values) // len(values)


def get_all_languages() -> list[str]:
    languages = get_settings()["languages"]
    return sorted(languages)


def get_all_problems() -> list[str]:
    statement_dir = _get_statements_dir()
    return sorted(file.stem for file in statement_dir.iterdir())


def get_all_keyed_problems() -> list[tuple[str, int]]:
    output = [
        (problem, key)
        for problem, problem_info in get_answers().items()
        for key in problem_info
    ]
    return sorted(output)


def filter_languages(parsed_languages: list[str]) -> list[Language]:
    language_strings = get_all_languages()
    return [
        Language.from_settings(language)
        for language in language_strings
        if language in parsed_languages
    ]


def filter_problems(parsed_problems: list[str]) -> list[str]:
    problem_strings = get_all_problems()
    return [problem for problem in problem_strings if problem in parsed_problems]
