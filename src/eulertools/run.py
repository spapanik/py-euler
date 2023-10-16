import subprocess
from itertools import product

from eulertools.utils import (
    Language,
    Modes,
    get_answers,
    get_line_answer,
    get_solution,
    update_answers,
)


class Run:
    def __init__(
        self,
        languages: list[Language],
        problems: list[str],
        verbosity: int,
        *,
        run_update: bool = False,
        times: int = 1,
        mode: str = Modes.RUN,
    ):
        self.languages = languages
        self.problems = problems
        self.mode = mode
        self.times = times
        self.verbosity = verbosity
        self.expected_answers = get_answers()
        self.run_update = run_update

    def run(self) -> dict[Language, dict[str, dict[int, list[int]]]]:
        output: dict[Language, dict[str, dict[int, list[int]]]] = {}
        success = True
        for language, problem in product(self.languages, self.problems):
            run_success, timings = self.run_single_problem(language, problem)
            if run_success is not None:
                success = success and run_success
                output.setdefault(language, {})[problem] = timings
        if not success:
            raise RuntimeError("Some tests failed")
        if self.run_update:
            update_answers(self.expected_answers)
        return output

    def run_single_problem(
        self, language: Language, problem: str
    ) -> tuple[bool | None, dict[int, list[int]]]:
        solution = get_solution(language, problem)
        if not solution.exists():
            return None, {}
        raw_output = subprocess.run(
            [language.runner, problem, str(self.times)],  # noqa: S603
            capture_output=True,
            check=True,
        )
        output = raw_output.stdout.decode()
        if self.verbosity > 3:
            print(output)
        actual_answers: dict[int, set[str]] = {}
        timings: dict[int, list[int]] = {}
        for line in output.splitlines():
            output_type, run_id, value = get_line_answer(line)
            if output_type == "Time":
                timings.setdefault(run_id, []).append(int(value) or 1)
            elif output_type == "Answer":
                actual_answers.setdefault(run_id, set()).add(value)
        expected_answers = self.expected_answers.setdefault(problem, {})
        success = True
        if missing_answers := {
            answer for answer in expected_answers if answer not in actual_answers
        }:
            success = False
            print(
                f"🔴 Running {problem}... Missing answers with keys {missing_answers}."
            )
        for key, values in actual_answers.items():
            value = values.pop()
            if len(values) != 0:
                success = False
                print(
                    f"🔴 Running {language.name}/{problem}/{key}... Not deterministic answer."
                )
            elif key not in expected_answers:
                if self.mode != Modes.TIMING:
                    print(
                        f"🟠 Running {language.name}/{problem}/{key}... new response: {value}"
                    )
                expected_answers[key] = value
            elif value != expected_answers[key]:
                success = False
                print(
                    f"🔴 Running {language.name}/{problem}/{key}... expected: {expected_answers[key]}, got: {value}"
                )
            elif self.mode != Modes.TIMING:
                print(f"🟢 Running {language.name}/{problem}/{key}... {value}")
        return success, timings
