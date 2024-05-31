import subprocess
import sys
from collections.abc import Iterator
from itertools import product

from eulertools.lib.utils import (
    CaseId,
    CaseResult,
    Language,
    ParseResult,
    Problem,
    Summary,
    UpdateMode,
    get_solution,
    get_summary,
    parse_answer_result,
    parse_timing_result,
    update_summary,
)


class Run:
    __slots__ = (
        "success",
        "languages",
        "problems",
        "times",
        "verbosity",
        "update_mode",
        "summary",
    )

    def __init__(
        self,
        languages: list[Language],
        problems: list[Problem],
        verbosity: int,
        times: int,
        update_mode: UpdateMode = UpdateMode.NONE,
    ):
        self.success = True
        self.languages = languages
        self.problems = problems
        self.times = times
        self.verbosity = verbosity
        self.update_mode = update_mode
        self.summary = get_summary()

    def run(self) -> None:
        for language, problem, _ in self.get_summaries(self.languages, self.problems):
            self.print_summary(language, problem)
            if not self.summary.problem_successful(language, problem):
                self.success = False
            if self.update_mode != UpdateMode.NONE:
                self.prepare_summary(language, problem)
        if self.update_mode != UpdateMode.NONE:
            update_summary(self.summary)
        if not self.success:
            sys.exit(81)

    def get_summaries(
        self, languages: list[Language], problems: list[Problem]
    ) -> Iterator[tuple[Language, Problem, Summary]]:
        for language, problem in product(languages, problems):
            solution = get_solution(language, problem)
            if not solution.exists():
                continue

            self.run_single_problem(language, problem)
            yield language, problem, self.summary

    def run_single_problem(self, language: Language, problem: Problem) -> None:
        problem_summary = self.summary.get_or_create_problem(problem)
        problem_summary.result[language] = ParseResult.SUCCESS
        raw_output = subprocess.run(
            [language.runner, problem.id, str(self.times)],  # noqa: S603
            capture_output=True,
            check=True,
        )
        output = raw_output.stdout.decode()
        error = raw_output.stderr.decode()
        if self.verbosity > 3:
            if output:
                print(output)
            if error:
                print(error, file=sys.stderr)
        for line in output.splitlines():
            if line.startswith("Time"):
                _, case_key, timing = parse_timing_result(line)
                case_id = CaseId(problem, case_key)
                case_summary = problem_summary.get_or_create_case(case_id)
                case_summary.new_timings.setdefault(language, []).append(timing)
            elif line.startswith("Answer"):
                _, case_key, answer = parse_answer_result(line)
                case_id = CaseId(problem, case_key)
                case_summary = problem_summary.get_or_create_case(case_id)
                case_summary.new_answers.setdefault(language, set()).add(answer)
            else:
                problem_summary.result[language] = ParseResult.FAILURE
                problem_summary.parse_info[language] = line
                return
        for case_summary in problem_summary.cases.values():
            new_answers = case_summary.new_answers.get(language, set())
            if len(new_answers) == 0:
                case_summary.result[language] = CaseResult.MISSING_KEY
            elif len(new_answers) > 1:
                case_summary.result[language] = CaseResult.NON_DETERMINISTIC
            elif case_summary.answer is None:
                case_summary.result[language] = CaseResult.NEW_RESPONSE
            elif case_summary.answer not in new_answers:
                case_summary.result[language] = CaseResult.WRONG_RESPONSE
            else:
                case_summary.result[language] = CaseResult.SUCCESS

    def print_summary(self, language: Language, problem: Problem) -> None:
        problem_summary = self.summary.problems[problem]
        parse_result = problem_summary.result[language]
        if parse_result == ParseResult.FAILURE:
            parse_info = problem_summary.parse_info[language]
            print(
                f"🔴 Running {language.name} // {problem.id}... Cannot parse `{parse_info}`",
                file=sys.stderr,
            )
            return
        for case_id, case_summary in sorted(problem_summary.cases.items()):
            case_key = case_id.case_key
            result = case_summary.result[language]
            run_text = f"Running {language.name} // {problem.id} // {case_key}..."
            answer = case_summary.answer
            try:
                new_answers = case_summary.new_answers[language]
            except KeyError:
                new_answer = None
            else:
                new_answer = next(iter(new_answers))
            if result == CaseResult.MISSING_KEY:
                print(f"🔴 {run_text} Missing answer", file=sys.stderr)
            elif case_summary.result[language] == CaseResult.NON_DETERMINISTIC:
                print(f"🔴 {run_text} Not deterministic answer", file=sys.stderr)
            elif case_summary.result[language] == CaseResult.NEW_RESPONSE:
                print(f"🟠 {run_text} new response: `{new_answer}`")
            elif case_summary.result[language] == CaseResult.WRONG_RESPONSE:
                print(
                    f"🔴 {run_text} expected: `{answer}`, got: `{new_answer}`",
                    file=sys.stderr,
                )
            elif case_summary.result[language] == CaseResult.SUCCESS:
                print(f"🟢 {run_text} response: `{answer}`")

    def prepare_summary(self, language: Language, problem: Problem) -> None:
        problem_summary = self.summary.problems[problem]
        parse_result = problem_summary.result[language]
        if parse_result == ParseResult.FAILURE:
            return

        for case_summary in problem_summary.cases.values():
            case_result = case_summary.result[language]
            if case_result in {
                CaseResult.SUCCESS,
                CaseResult.MISSING_KEY,
                CaseResult.NON_DETERMINISTIC,
            }:
                continue
            if (
                case_result == CaseResult.WRONG_RESPONSE
                and self.update_mode == UpdateMode.APPEND
            ):
                continue
            new_answer = next(iter(case_summary.new_answers[language]))
            case_summary.answer = new_answer
