from itertools import product

from eulertools.lib.utils import Language, Modes, Problem, get_solution
from eulertools.subcommands.run import Run


class Test:
    def __init__(
        self,
        languages: list[Language],
        problems: list[Problem],
        times: int,
        verbosity: int,
    ):
        self.languages = languages
        self.problems = problems
        self.times = times
        self.verbosity = verbosity

    def run(self) -> None:
        for language, problem in product(self.languages, self.problems):
            self.test_single_problem(language, problem)

    def test_single_problem(self, language: Language, problem: Problem) -> None:
        solution = get_solution(language, problem)
        if not solution.exists():
            return

        Run(
            [language],
            [problem],
            verbosity=self.verbosity,
            mode=Modes.RUN,
            times=self.times,
        ).run()[language][problem.id]
