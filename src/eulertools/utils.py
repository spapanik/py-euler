from __future__ import annotations

import re
from collections.abc import Iterator
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
    TEST = "test"


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


@dataclass(frozen=True, slots=True)
class Languages:
    _all: tuple[Language, ...] = field(repr=False)
    _data: dict[str, Language] = field(init=False, repr=False)

    def __init__(self, languages: tuple[Language, ...]) -> None:
        object.__setattr__(self, "_all", languages)
        object.__setattr__(
            self, "_data", {language.name: language for language in languages}
        )

    def __len__(self) -> int:
        return len(self._all)

    def __iter__(self) -> Iterator[Language]:
        return iter(self._all)

    def __getitem__(self, item: str) -> Language:
        return self._data[item]


def get_project_root() -> Path:
    cwd = Path.cwd().resolve()
    while not cwd.joinpath("leet.toml").exists():
        if cwd.as_posix() == "/":
            raise RuntimeError("Could not find project root")
        cwd = cwd.parent
    return cwd


def get_settings() -> dict[str, Any]:
    return SettingsParser(get_project_root().joinpath("leet.toml")).data


def get_answers_dict(problem: str) -> dict[int, str]:
    answers = get_project_root().joinpath("answers.txt")
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


def get_problem(problem: str) -> str:
    settings = get_settings()
    problem_format: str = settings["problems"]["format"]
    return problem_format.format(problem=problem)


def get_statement(problem: str) -> Path:
    return get_project_root().joinpath("statements", f"{problem}.txt")


def get_template(language: Language) -> Path:
    return get_project_root().joinpath(
        "templates", f"template.solution.{language.extension}"
    )


def get_solution(language: Language, problem: str) -> Path:
    return get_project_root().joinpath(
        language.name, "src", "solutions", f"{problem}.{language.extension}"
    )


def get_languages() -> Languages:
    language_settings = get_settings()["languages"]
    languages = tuple(
        Language.from_settings(name) for name in sorted(language_settings)
    )
    return Languages(languages)
