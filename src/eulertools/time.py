from itertools import product

from eulertools.run import Run
from eulertools.utils import (
    ANSIEscape,
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
        for run_index, (language, problem) in enumerate(
            product(self.languages, self.problems)
        ):
            self.time_single_problem(language, problem, run_index)
        if self.run_update:
            for language in self.languages:
                update_timings(language, self.timings[language])

    def time_single_problem(
        self, language: Language, problem: str, run_index: int
    ) -> None:
        self.timings[language].setdefault(problem, {})
        solution = get_solution(language, problem)
        if not solution.exists():
            return

        raw_timings = Run(
            [language],
            [problem],
            verbosity=self.verbosity,
            mode=Modes.TIMING,
            times=self.times,
        ).run()[language][problem]
        if not raw_timings:
            raise ValueError("No lines returned from Run.")
        old_timings = self.timings[language][problem]
        new_timings = {
            run_id: Timing.from_nanoseconds(get_average(timings))
            for run_id, timings in raw_timings.items()
        }
        for key_index, key in enumerate(sorted(new_timings)):
            old_timing = old_timings.get(key)
            raw_timing = raw_timings[key]
            new_timing = new_timings[key]
            if old_timing is None:
                overall_difference = None
            elif old_timing < new_timing:
                overall_difference = "🔴"
            elif old_timing > new_timing:
                overall_difference = "🟢"
            else:
                overall_difference = "🔵"
            self.timings[language][problem][key] = new_timing
            title = f"Timing {language.name}/{problem}/{key}..."
            if run_index or key_index:
                print()
            print(ANSIEscape.OKGREEN, title, ANSIEscape.ENDC, sep="")
            print(ANSIEscape.OKGREEN, "~" * len(title), ANSIEscape.ENDC, sep="")
            if old_timing:
                print(f"🟤 Old timing: {old_timing}")
            prefix = (
                f"{overall_difference} New" if old_timing is not None else "🔵 Initial"
            )
            print(f"{prefix} timing: {new_timing}")
            if self.verbosity > 0:
                print("    ⏱️  New timings:")
                for i, timing in enumerate(raw_timing):
                    run_timing = Timing.from_nanoseconds(timing)
                    if old_timing is None:
                        prefix = "🔵"
                    elif run_timing > old_timing:
                        prefix = "⬆️ "
                    elif run_timing < old_timing:
                        prefix = "⬇️ "
                    else:
                        prefix = "↔️ "
                    print(f"       {prefix} Run {i + 1} took: {run_timing}")
            if self.verbosity > 1 and old_timing is not None:
                old_nanoseconds = old_timing.nanoseconds
                new_nanoseconds = new_timing.nanoseconds
                change = 100 * (old_nanoseconds - new_nanoseconds) / old_nanoseconds
                print(f"{overall_difference} Performance difference: {change:.2f}%")
