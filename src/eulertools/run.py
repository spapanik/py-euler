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

    def run(self) -> None:
        for language, problem in product(self.languages, self.problems):
            self.run_single_problem(language, problem)

    def run_single_problem(self, language: Language, problem: str) -> list[int] | None:
        solution = get_solution(language, problem)
        if not solution.exists():
            return None
        raw_output = subprocess.run(
            [language.runner, problem, self.mode, str(self.times)],  # noqa: S603
            capture_output=True,
        )
        output = raw_output.stdout.decode()
        if self.verbosity > 3:
            print(output)
        timings = [
            int(line[6:]) or 1
            for line in output.splitlines()
            if line.startswith("Time: ")
        ]
        expected_answers = get_answers(problem)
        actual_answers: dict[int, str] = {}
        for line in output.strip().splitlines():
            if line.startswith("Time: "):
                continue
            raw_key, value = line.split(maxsplit=1)
            key = int(raw_key[:-1])
            actual_answers[key] = value
        success = True
        if self.mode != Modes.TIMING and len(actual_answers) != len(expected_answers):
            success = False
            print(f"🔴 Running {problem}...")
        for key, value in actual_answers.items():
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
        if not success:
            raise ValueError("Running failed. Aborting...")
        return timings
