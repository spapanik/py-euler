import os
from math import ceil, floor

from eulertools.run import Run
from eulertools.utils import ANSIEscape, Language, Modes, get_timings


class Test:
    def __init__(self, language: Language, problems: list[str]):
        self.language = language
        self.problems = self.discover_problems(problems)

    def run(self) -> None:
        cols = os.get_terminal_size().columns
        report_title = f" Testing {self.language} solutions "
        padding = "="
        half = (cols - len(report_title)) / 2
        print(
            f"{ANSIEscape.BOLD}{padding * ceil(half)}{report_title}{padding * floor(half)}{ANSIEscape.ENDC}"
        )
        for problem in self.problems:
            self.test_single_problem(problem)

    def discover_problems(self, problems: list[str]) -> list[str]:
        if problems:
            return problems
        timings = get_timings(self.language)
        return sorted(timings)

    def test_single_problem(self, problem: str) -> None:
        Run(self.language, problem, mode=Modes.TEST).run()
