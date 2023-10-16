from itertools import product

from eulertools.run import Run
from eulertools.utils import Language, Modes, get_solution


class Test:
    def __init__(
        self, languages: list[Language], problems: list[str], times: int, verbosity: int
    ):
        self.languages = languages
        self.problems = problems
        self.times = times
        self.verbosity = verbosity

    def run(self) -> None:
        for language, problem in product(self.languages, self.problems):
            self.test_single_problem(language, problem)

    def test_single_problem(self, language: Language, problem: str) -> None:
        solution = get_solution(language, problem)
        if not solution.exists():
            return

        output = Run(
            [language],
            [problem],
            verbosity=self.verbosity,
            mode=Modes.RUN,
            times=self.times,
        ).run()[language][problem]
        if not output:
            raise ValueError("No lines returned from Run.")
