from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import StrEnum, unique
from pathlib import Path
from typing import Any, Self

from dj_settings import ConfigParser
from pyutilkit.timing import Timing

from eulertools.__version__ import __version__
from eulertools.lib.exceptions import (
    InvalidLanguageError,
    InvalidProblemError,
    MissingProjectRootError,
)

TIME_UNIT = re.compile(r"(\d+(?:\.\d+)?)\s?(.{0,2})")


@unique
class Modes(StrEnum):
    TIMING = "timing"
    RUN = "run"


@dataclass(frozen=True, slots=True, order=True)
class Language:
    name: str
    extension: str = field(repr=False, compare=False)
    path: Path = field(repr=False, compare=False)
    solutions_path: Path = field(repr=False, compare=False)
    runner: Path = field(repr=False, compare=False)

    @classmethod
    def from_settings(cls, name: str) -> Self:
        project_root = _get_project_root()
        settings = get_settings()
        language = settings["languages"][name]
        path = project_root.joinpath(language.get("path", name))
        solutions = language.get("solutions", "src/solutions")
        return cls(
            name=name,
            extension=language.get("extension", name),
            path=path,
            runner=path.joinpath(language["runner"]),
            solutions_path=path.joinpath(solutions),
        )

    def get_settings_root(self) -> Path:
        project_root = _get_project_root()
        project_settings_root = _get_settings_root()
        path = project_settings_root.joinpath(self.path.relative_to(project_root))
        if not path.exists():
            path.mkdir(parents=True)
        return path


@dataclass(frozen=True, slots=True, order=True)
class Problem:
    id: str
    statement: Path
    path: Path


@dataclass(frozen=True, slots=True, order=True)
class Version:
    major: int
    minor: int
    patch: int

    @classmethod
    def from_string(cls, version: str) -> Version:
        version = re.sub("[^.0-9].*", "", version)
        if version.endswith("."):
            version += "0"
        while version.count(".") < 2:
            version += ".0"
        major, minor, patch, *_ = map(int, version.split("."))
        return cls(major, minor, patch)

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


def _get_project_root() -> Path:
    cwd = Path.cwd().resolve()
    while not cwd.joinpath(".euler").is_dir():
        if cwd.as_posix() == "/":
            message = f"Could not find .euler/euler.toml in {Path.cwd().resolve()} or any parent directory"
            raise MissingProjectRootError(message)
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


def get_template(language: Language) -> Path:
    return language.get_settings_root().joinpath("solution.jinja")


def get_solution(language: Language, problem: Problem) -> Path:
    suffix = f".{language.extension}"
    return language.solutions_path.joinpath(problem.path).with_suffix(suffix)


def get_config(path: Path) -> dict[str, Any]:
    return ConfigParser([path]).data


def get_statement(problem: Problem) -> dict[str, Any]:
    return ConfigParser([problem.statement]).data


def get_settings() -> dict[str, Any]:
    data = ConfigParser([_get_settings()]).data
    version_string = data.get("$meta", {}).get("version")
    if version_string is None:
        msg = "This `euler.toml` is missing a version"
        raise RuntimeError(msg)
    min_version = Version.from_string(data["$meta"]["version"])
    if min_version > Version.from_string(__version__):
        msg = f"This `euler.toml` requires an eulertools >= v{min_version}"
        raise RuntimeError(msg)
    return data


def get_line_timing(line: str) -> tuple[str, int, Timing]:
    prefix, run_id, timing = line.split(maxsplit=2)
    return prefix, int(run_id), Timing(nanoseconds=int(timing) or 1)


def get_line_answer(line: str) -> tuple[str, int, str]:
    prefix, run_id, *answers = line.split(maxsplit=2)
    try:
        answer = answers.pop()
    except IndexError:
        answer = ""
    return prefix, int(run_id), answer


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


def get_context(language: Language, problem: Problem) -> dict[str, str]:
    statement = get_statement(problem)
    output = {"problem": problem.id}
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


def get_average(values: list[Timing]) -> Timing:
    if not values:
        return Timing()
    if len(values) >= 3:
        values = sorted(values)[1:-1]
    return sum(values, start=Timing()) // len(values)


def get_all_languages() -> list[Language]:
    languages = get_settings()["languages"]
    return sorted(Language.from_settings(language) for language in languages)


def get_all_problems(languages: list[Language] | None = None) -> dict[str, Problem]:
    statement_dir = _get_statements_dir()
    if languages is None:
        languages = get_all_languages()

    output = {}
    for file in sorted(statement_dir.rglob("*")):
        if not file.is_file():
            continue
        statement = get_config(file)
        if any(statement.get(language.name) is not None for language in languages):
            path = file.relative_to(statement_dir)
            id_ = statement["common"].get("id", path.with_suffix("").as_posix())
            problem = Problem(id=id_, statement=file, path=path)
            if id_ in output:
                msg = f"Duplicate problem id: {id_}"
                raise ValueError(msg)
            output[id_] = problem

    return output


def get_all_keyed_problems() -> list[tuple[str, int]]:
    output = [
        (problem, key)
        for problem, problem_info in get_answers().items()
        for key in problem_info
    ]
    return sorted(output)


def filter_languages(parsed_languages: list[str] | None) -> list[Language]:
    all_languages = get_all_languages()
    if parsed_languages is None:
        return all_languages
    filtered_languages = []
    language_names = {language.name for language in all_languages}
    for language in parsed_languages:
        if language not in language_names:
            msg = f"{language} is not a valid language"
            raise InvalidLanguageError(msg)
        filtered_languages.append(Language.from_settings(language))
    return filtered_languages


def filter_problems(
    parsed_problems: list[str], languages: list[Language] | None = None
) -> list[Problem]:
    all_problems = get_all_problems(languages)
    if not parsed_problems:
        return sorted(all_problems.values())
    filtered_problems = []
    for problem in parsed_problems:
        if problem not in all_problems:
            if languages is None:
                language_names = "any language"
            else:
                language_names = ", ".join(language.name for language in languages)
            msg = f"{problem} is not a valid problem for {language_names}"
            raise InvalidProblemError(msg)
        filtered_problems.append(all_problems[problem])
    return filtered_problems
