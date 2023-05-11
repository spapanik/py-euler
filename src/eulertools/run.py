import subprocess
import sys

from eulertools.utils import Language, Modes, get_answers_dict, get_solution


class Run:
    def __init__(
        self,
        language: Language,
        problem: str,
        *,
        debug: bool = False,
        times: int = 1,
        mode: str = Modes.RUN,
    ):
        self.language = language
        self.problem = problem
        self.mode = mode
        self.times = times
        self.debug = debug

    def run(self) -> list[int]:
        if self.mode == Modes.TIMING and self.times < 3:
            raise ValueError("Timing mode requires at least 3 runs. Aborting...")

        if self.mode != Modes.TIMING and self.times != 1:
            raise ValueError("Only timing mode supports multiple runs. Aborting...")

        solution = get_solution(self.language, self.problem)
        if not solution.exists():
            raise FileNotFoundError(
                f"Problem {self.problem} not solved for {self.language}. Aborting..."
            )
        raw_output = subprocess.run(
            [  # noqa: S603
                self.language.runner,
                self.problem,
                self.mode,
                str(self.times),
            ],
            capture_output=True,
        )
        output = raw_output.stdout.decode()
        if self.debug:
            sys.tracebacklimit = 9999
            print(output)
        timings = [
            int(line[6:]) or 1
            for line in output.splitlines()
            if line.startswith("Time: ")
        ]
        expected_answers = get_answers_dict(self.problem)
        actual_answers: dict[int, str] = {}
        prefix = "Testing" if self.mode == "test" else "Running"
        for line in output.strip().splitlines():
            if line.startswith("Time: "):
                continue
            raw_key, value = line.split(maxsplit=1)
            key = int(raw_key[:-1])
            actual_answers[key] = value
        success = True
        if self.mode == "test" and len(actual_answers) != len(expected_answers):
            success = False
            print(f"🔴 {prefix} {self.problem}...")
        for key, value in actual_answers.items():
            if key not in expected_answers:
                if self.mode != "timing":
                    print(f"🟠 {prefix} {self.problem}/{key}... new response: {value}")
            elif value != expected_answers[key]:
                success = False
                print(
                    f"🔴 {prefix} {self.problem}/{key}... expected: {expected_answers[key]}, got: {value}"
                )
            elif self.mode != "timing":
                print(f"🟢 {prefix} {self.problem}/{key}... {value}")
        if not success:
            raise ValueError(f"{prefix} failed. Aborting...")
        return timings
