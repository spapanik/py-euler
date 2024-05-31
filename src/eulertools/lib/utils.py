from __future__ import annotations

import csv
import re
from dataclasses import dataclass, field
from enum import StrEnum, auto, unique
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

NULL_STRING = "(null)"
TIME_UNIT = re.compile(r"(\d+(?:\.\d+)?)\s?(.{0,2})")


@unique
class UpdateMode(StrEnum):
    NONE = auto()
    APPEND = auto()
    UPDATE = auto()


@unique
class ParseResult(StrEnum):
    SUCCESS = auto()
    FAILURE = auto()


@unique
class CaseResult(StrEnum):
    SUCCESS = auto()
    NEW_RESPONSE = auto()
    WRONG_RESPONSE = auto()
    MISSING_KEY = auto()
    NON_DETERMINISTIC = auto()


@dataclass(frozen=True, slots=True, order=True)
class Language:
    name: str
    suffix: str = field(repr=False, compare=False)
    path: Path = field(repr=False, compare=False)
    solutions_path: Path = field(repr=False, compare=False)
    settings_path: Path = field(repr=False, compare=False)
    runner: Path = field(repr=False, compare=False)

    @classmethod
    def from_settings(cls, name: str) -> Self:
        project_root = _get_project_root()
        settings = get_settings()
        project_settings_root = _get_settings_root()
        language = settings["languages"][name]
        relative_path = language.get("path", name)
        path = project_root.joinpath(relative_path)
        solutions = language.get("solutions", "src/solutions")
        settings_path = project_settings_root.joinpath(relative_path)
        extension = language.get("extension", name)
        suffix = extension if extension.startswith(".") else f".{extension}"
        return cls(
            name=name,
            suffix=suffix,
            path=path,
            runner=path.joinpath(language["runner"]),
            solutions_path=path.joinpath(solutions),
            settings_path=settings_path,
        )


@dataclass(frozen=True, slots=True, order=True)
class Problem:
    id: str
    name: str
    statement: Path = field(repr=False)

    @classmethod
    def from_name(cls, name: str) -> Self:
        statement_dir = _get_statements_dir()
        path = Path(name).with_suffix(".toml")
        file = statement_dir.joinpath(path)
        statement = get_config(file)
        id_ = statement["common"].get("id", path.with_suffix("").as_posix())
        return cls(id=id_, name=name, statement=file)

    @property
    def path(self) -> Path:
        return Path(self.name).with_suffix(".toml")


@dataclass(frozen=True, slots=True, order=True)
class CaseId:
    problem: Problem
    case_key: str


@dataclass(slots=True, order=True)
class Summary:
    problems: dict[Problem, ProblemSummary]

    def get_or_create_problem(self, problem: Problem) -> ProblemSummary:
        problem_summary = self.problems.get(problem)
        if problem_summary is None:
            problem_summary = ProblemSummary(problem=problem, cases={})
            self.problems[problem] = problem_summary
        return problem_summary

    def for_csv(self) -> list[dict[str, str]]:
        return sorted(
            (case for problem in self.problems.values() for case in problem.for_csv()),
            key=lambda case: (case["problem"], case["case_key"]),
        )

    def problem_successful(self, language: Language, problem: Problem) -> bool:
        problem_summary = self.problems.get(problem)
        if problem_summary is None:
            return False
        if (
            problem_summary.result.get(language)
            and problem_summary.result[language] != ParseResult.FAILURE
        ):
            return False
        return any(
            case.result.get(language)
            in {
                CaseResult.WRONG_RESPONSE,
                CaseResult.MISSING_KEY,
                CaseResult.NON_DETERMINISTIC,
            }
            for case in problem_summary.cases.values()
        )

    def case_successful(self, language: Language, case_id: CaseId) -> bool:
        problem = case_id.problem
        problem_summary = self.problems.get(problem)
        if problem_summary is None:
            return False
        if (
            problem_summary.result.get(language)
            and problem_summary.result[language] != ParseResult.FAILURE
        ):
            return False

        case_summary = problem_summary.cases.get(case_id)
        if case_summary is None:
            return False
        return case_summary.result.get(language) in {
            CaseResult.WRONG_RESPONSE,
            CaseResult.MISSING_KEY,
            CaseResult.NON_DETERMINISTIC,
        }


@dataclass(slots=True, order=True)
class ProblemSummary:
    problem: Problem
    cases: dict[CaseId, CaseSummary]
    result: dict[Language, ParseResult] = field(default_factory=dict, repr=False)
    parse_info: dict[Language, str] = field(default_factory=dict, repr=False)

    def get_or_create_case(self, case_id: CaseId) -> CaseSummary:
        case_summary = self.cases.get(case_id)
        if case_summary is None:
            case_summary = CaseSummary(case_id=case_id, timings={})
            self.cases[case_id] = case_summary
        return case_summary

    def for_csv(self) -> list[dict[str, str]]:
        return [case.for_csv() for case in self.cases.values()]


@dataclass(slots=True, order=True)
class CaseSummary:
    case_id: CaseId
    answer: str | None = None
    timings: dict[Language, Timing] = field(default_factory=dict)
    result: dict[Language, CaseResult] = field(default_factory=dict, repr=False)
    new_timings: dict[Language, list[Timing]] = field(default_factory=dict, repr=False)
    new_answers: dict[Language, set[str]] = field(default_factory=dict, repr=False)

    def for_csv(self) -> dict[str, str]:
        if self.answer is None:
            msg = f"Case {self.case_id.case_key} has no answer"
            raise ValueError(msg)
        return {
            "problem": self.case_id.problem.name,
            "case_key": self.case_id.case_key,
            "answer": self.answer,
            **{
                language.name: str(timing.nanoseconds)
                for language, timing in self.timings.items()
            },
        }


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


def _get_legacy_summary() -> Summary:
    summary = Summary(problems={})
    answers = _get_settings_root().joinpath("answers.txt")
    with answers.open() as file:
        for line in file:
            problem_name, case_key, answer = parse_answer_result(line.strip())
            problem = Problem.from_name(problem_name)
            problem_summary = summary.get_or_create_problem(problem)
            case_id = CaseId(problem=problem, case_key=case_key)
            summary_case = problem_summary.get_or_create_case(case_id)
            summary_case.answer = answer
    answers.unlink()

    for language in get_all_languages():
        timings = language.settings_path.joinpath("timings.txt")
        with timings.open() as file:
            for line in file:
                problem_name, case_key, timing = parse_timing_result(line.strip())
                problem = Problem.from_name(problem_name)
                case_id = CaseId(problem=problem, case_key=case_key)
                case_summary = summary.problems[problem].cases[case_id]
                case_summary.timings[language] = timing
        timings.unlink()

    return summary


def _create_summary(file: Path) -> None:
    file.touch(mode=0o644)
    if _get_settings_root().joinpath("answers.txt").exists():
        summary = _get_legacy_summary()
    else:
        summary = Summary(problems={})
    update_summary(summary)


def _get_summary() -> Path:
    file = _get_settings_root().joinpath("results.csv")
    if not file.exists():
        _create_summary(file)
    return file


def _get_statements_dir() -> Path:
    return _get_settings_root().joinpath("statements")


def _get_templates_dir() -> Path:
    return _get_settings_root().joinpath("templates")


def get_template(language: Language) -> Path:
    template_dir = _get_templates_dir()
    new_path = template_dir.joinpath(f"{language.name}.jinja")
    if not new_path.exists():
        template_dir.mkdir(parents=True, exist_ok=True)
        old_path = language.settings_path.joinpath("solution.jinja")
        old_path.rename(new_path)
    return new_path


def get_solution(language: Language, problem: Problem) -> Path:
    return language.solutions_path.joinpath(problem.path).with_suffix(language.suffix)


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


def parse_timing_result(line: str) -> tuple[str, str, Timing]:
    prefix, response_key, timing = line.split(maxsplit=2)
    return prefix, response_key, Timing(nanoseconds=int(timing) or 1)


def parse_answer_result(line: str) -> tuple[str, str, str]:
    prefix, response_key, *answers = line.split(maxsplit=2)
    try:
        answer = answers.pop()
    except IndexError:
        answer = ""
    return prefix, response_key, answer


def get_summary() -> Summary:
    results_file = _get_summary()
    languages = get_all_languages()
    summary = Summary(problems={})
    with results_file.open() as file:
        csv_reader = csv.DictReader(file)
        for row in csv_reader:
            problem = Problem.from_name(row["problem"])
            problem_summary = summary.get_or_create_problem(problem)
            case_id = CaseId(problem=problem, case_key=row["case_key"])
            case_summary = problem_summary.get_or_create_case(case_id)
            case_summary.answer = row["answer"]
            for language in languages:
                timing = row.get(language.name, NULL_STRING)
                if timing != NULL_STRING:
                    case_summary.timings[language] = Timing(nanoseconds=int(timing))
    return summary


def get_context(language: Language, problem: Problem) -> dict[str, str]:
    statement = get_statement(problem)
    output = {"problem": problem.id}
    output |= statement.get(language.name, {})
    return output


def update_summary(summary: Summary) -> None:
    fieldnames = [
        "problem",
        "case_key",
        "answer",
        *(language.name for language in get_all_languages()),
    ]
    results_file = _get_summary()
    with results_file.open("w") as file:
        writer = csv.DictWriter(
            file, fieldnames=fieldnames, restval=NULL_STRING, lineterminator="\n"
        )
        writer.writeheader()
        for csv_dict in summary.for_csv():
            writer.writerow(csv_dict)


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
        path = file.relative_to(statement_dir)
        name = path.with_suffix("").as_posix()
        problem = Problem.from_name(name)
        statement = get_config(file)
        if any(statement.get(language.name) is not None for language in languages):
            if problem.id in output:
                msg = f"Duplicate problem id: {problem.id}"
                raise ValueError(msg)
            output[problem.id] = problem

    return output


def _filter_languages(parsed_languages: list[str] | None) -> list[Language]:
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


def _filter_problems(
    parsed_problems: list[str], languages: list[Language] | None = None
) -> list[Problem]:
    all_problems = get_all_problems(languages)
    if not parsed_problems:
        return list(all_problems.values())
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


def filter_languages(parsed_languages: list[str] | None) -> list[Language]:
    return sorted(
        _filter_languages(parsed_languages), key=lambda language: language.name
    )


def filter_problems(
    parsed_problems: list[str], languages: list[Language] | None = None
) -> list[Problem]:
    return sorted(
        _filter_problems(parsed_problems, languages),
        key=lambda problem: problem.statement,
    )
