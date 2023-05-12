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


@dataclass(frozen=True, slots=True)
class Timing:
    time: Decimal
    unit: str

    @classmethod
    def from_string(cls, timing: str, old_timing: Timing | None = None) -> Self:
        match = re.match(TIME_UNIT, timing)
        if match is None:
            raise ValueError(f"Invalid timing: {timing}")
        time, unit = match.groups()
        if not unit:
            if old_timing is None:
                raise ValueError("Missing unit in initial timing")
            unit = old_timing.unit
        if unit == "us":
            unit = "µs"
        return cls(time=Decimal(time), unit=unit)

    @classmethod
    def from_nanoseconds(cls, nanoseconds: float) -> Self:
        if nanoseconds < 1000:
            return cls.from_string(f"{nanoseconds:.0f}ns")
        microseconds = nanoseconds / 1000
        if microseconds < 1000:
            return cls.from_string(f"{microseconds:.1f}µs")
        milliseconds = microseconds / 1000
        if milliseconds < 1000:
            return cls.from_string(f"{milliseconds:.1f}ms")
        seconds = milliseconds / 1000
        return cls.from_string(f"{seconds:.2f}s")

    def to_nanoseconds(self) -> int:
        if self.unit == "ns":
            return int(self.time)
        if self.unit == "µs":
            return int(self.time * 1000)
        if self.unit == "ms":
            return int(self.time * 1000 * 1000)
        return int(self.time * 1000 * 1000 * 1000)

    def __str__(self) -> str:
        return f"{self.time} {self.unit}"


@dataclass(frozen=True, slots=True, order=True)
class Language:
    name: str
    extension: str
    runner: Path = field(repr=False, compare=False)

    @classmethod
    def from_settings(cls, name: str) -> Self:
        project_root = get_project_root()
        settings = get_settings()
        language = settings["languages"][name]
        return cls(
            name=language["name"],
            extension=language["extension"],
            runner=project_root.joinpath(language["runner"]),
        )


def get_project_root() -> Path:
    cwd = Path.cwd().resolve()
    while not cwd.joinpath("leet.toml").exists():
        if cwd.as_posix() == "/":
            raise RuntimeError("Could not find project root")
        cwd = cwd.parent
    return cwd


def get_settings() -> dict[str, Any]:
    return SettingsParser(get_project_root().joinpath("leet.toml")).data


def get_answers(problem: str) -> dict[int, str]:
    answers = get_project_root().joinpath("common", "answers.txt")
    output: dict[int, str] = {}
    for line in answers.read_text().splitlines():
        if line.startswith(problem):
            problem_part, mode_id, answer = line.split(maxsplit=2)
            output[int(mode_id[:-1])] = answer
    return output


def get_timings(language: Language) -> dict[str, Timing]:
    timings = get_project_root().joinpath(language.name, "timings.txt")
    output: dict[str, Timing] = {}
    for line in timings.read_text().splitlines():
        problem, timing = line.split(maxsplit=1)
        output[problem] = Timing.from_string(timing)
    return output


def update_timings(language: Language, timings: dict[str, Timing]) -> None:
    timings_path = get_project_root().joinpath(language.name, "timings.txt")
    with timings_path.open("w") as file:
        for key in sorted(timings):
            timing = timings[key]
            file.write(" ".join([key, str(timing.time), timing.unit]) + "\n")


def get_average(values: list[int]) -> float:
    if len(values) >= 3:
        values = sorted(values)[1:-1]
    return sum(values) // len(values)


def get_statement(problem: str) -> Path:
    return get_project_root().joinpath("common", "statements", f"{problem}.txt")


def get_signature(language: Language, problem: str) -> str:
    statement = get_project_root().joinpath("common", "statements", f"{problem}.txt")
    with statement.open() as file:
        for line in file.readlines():
            if line.startswith(f"::{language.name}::"):
                return line.split("::")[2].strip()

    return ""


def get_template(language: Language) -> Path:
    return get_project_root().joinpath(language.name, ".leet", "template")


def get_solution(language: Language, problem: str) -> Path:
    return get_project_root().joinpath(
        language.name, "src", "solutions", f"{problem}.{language.extension}"
    )


def get_context(language: Language, problem: str) -> dict[str, str]:
    signature = get_signature(language, problem)
    regex_list = get_settings()["languages"][language.name].get("regex", [])
    context = {"problem": problem}
    for regex in regex_list:
        if regex_match := re.search(regex, signature):
            context |= regex_match.groupdict()
    return context


def get_all_languages() -> list[str]:
    languages = get_settings()["languages"]
    return sorted(languages)


def get_all_problems() -> list[str]:
    statement_dir = get_project_root().joinpath("common", "statements")
    return sorted(file.stem for file in statement_dir.glob("*.txt"))


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
