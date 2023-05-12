from itertools import product

from eulertools.run import Run
from eulertools.utils import (
    Language,
    Modes,
    Timing,
    get_average,
    get_solution,
    get_timings,
    update_timings,
)


class Time:
    def __init__(
        self,
        languages: list[Language],
        problems: list[str],
        times: int,
        verbosity: int,
        *,
        run_update: bool,
    ):
        self.languages = languages
        self.problems = problems
        self.times = times
        self.verbosity = verbosity
        self.run_update = run_update
        self.timings = {language: get_timings(language) for language in languages}

    def run(self) -> None:
        for language, problem in product(self.languages, self.problems):
            self.time_single_problem(language, problem)

    def time_single_problem(self, language: Language, problem: str) -> None:
        solution = get_solution(language, problem)
        if not solution.exists():
            return

        if (old_timing := self.timings[language].get(problem)) and not self.run_update:
            print(f"Old timing: {old_timing}")
        returned_lines = Run(
            [language],
            [problem],
            verbosity=self.verbosity,
            mode=Modes.TIMING,
            times=self.times,
        ).run_single_problem(language, problem)
        if not returned_lines:
            raise ValueError("No lines returned from Run.")
        average = Timing.from_nanoseconds(get_average(returned_lines))
        if self.verbosity > 0:
            print("New timings:")
            for i, returned_line in enumerate(returned_lines):
                print(f"* Run {i + 1} took: {Timing.from_nanoseconds(returned_line)}")
        if self.run_update:
            self.update(language, problem, str(average))
        else:
            print(f"New timing: {average}")
        if self.verbosity > 1 and old_timing is not None:
            old_nanosecond = old_timing.to_nanoseconds()
            new_nanosecond = average.to_nanoseconds()
            change = 100 * (old_nanosecond - new_nanosecond) / old_nanosecond
            print(f"Performance difference: {change:.2f}%")

    def update(self, language: Language, problem: str, average: str) -> None:
        old_timing = self.timings[language].get(problem)
        new_timing = Timing.from_string(average, old_timing)
        self.timings[language][problem] = new_timing
        if old_timing is None:
            print(f"Initial timing: {new_timing}")
        else:
            print(f"Old timing: {old_timing}\nNew timing: {new_timing}")
        update_timings(language, self.timings[language])
