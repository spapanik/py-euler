import subprocess
from itertools import product

from eulertools.utils import Language, Modes, get_answers, get_solution


class Run:
    def __init__(
        self,
        languages: list[Language],
        problems: list[str],
        verbosity: int,
        *,
        times: int = 1,
        mode: str = Modes.RUN,
    ):
        self.languages = languages
        self.problems = problems
        self.mode = mode
        self.times = times
        self.verbosity = verbosity

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
        )
        output = raw_output.stdout.decode()
        if self.verbosity > 3:
            print(output)
        actual_answers: dict[int, set[str]] = {}
        timings: dict[int, list[int]] = {}
        for line in output.splitlines():
            output_type, run_id, value = line.split(maxsplit=2)
            key = int(run_id)
            if output_type == "Time":
                timings.setdefault(key, []).append(int(value) or 1)
            elif output_type == "Answer":
                actual_answers.setdefault(key, set()).add(value)
        expected_answers = get_answers(problem)
        success = True
        if self.mode != Modes.TIMING and len(actual_answers) != len(expected_answers):
            success = False
            print(f"🔴 Running {problem}... Not the expected number of answers.")
        for key, values in actual_answers.items():
            if len(values) != 1:
                success = False
                print(
                    f"🔴 Running {language.name}/{problem}/{key}... Not deterministic answer."
                )
            value = values.pop()
            if key not in expected_answers:
                if self.mode != Modes.TIMING:
                    print(
                        f"🟠 Running {language.name}/{problem}/{key}... new response: {value}"
                    )
            elif value != expected_answers[key]:
                success = False
                print(
                    f"🔴 Running {language.name}/{problem}/{key}... expected: {expected_answers[key]}, got: {value}"
                )
            elif self.mode != Modes.TIMING:
                print(f"🟢 Running {language.name}/{problem}/{key}... {value}")
        return success, timings
