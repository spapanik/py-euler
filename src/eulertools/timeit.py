from eulertools.run import Run
from eulertools.update import Update
from eulertools.utils import Language, Timing, get_average, get_solution, get_timings


class TimeIt:
    def __init__(
        self,
        language: Language,
        problem: str,
        times: int,
        *,
        run_update: bool,
        quiet: bool,
        print_report: bool,
    ):
        self.language = language
        self.problem = problem
        self.times = times
        self.run_update = run_update
        self.quiet = quiet
        self.print_report = print_report

    def run(self) -> None:
        solution = get_solution(self.language, self.problem)
        if not solution.exists():
            raise FileNotFoundError(
                f"Problem {self.problem} not solved for {self.language}. Aborting..."
            )
        timings = get_timings(self.language)
        if (old_timing := timings.get(self.problem)) and not self.run_update:
            print(f"Old timing: {old_timing}")
        returned_lines = Run(
            self.language, self.problem, mode="timing", times=self.times
        ).run()
        if not returned_lines:
            raise ValueError("No lines returned from Run.")
        average = Timing.from_nanoseconds(get_average(returned_lines))
        if not self.quiet:
            print("New timings:")
            for i, returned_line in enumerate(returned_lines):
                print(f"* Run {i + 1} took: {Timing.from_nanoseconds(returned_line)}")
        if self.run_update:
            Update(self.language, self.problem, str(average)).run()
        else:
            print(f"New timing: {average}")
        if self.print_report and old_timing is not None:
            old_nanosecond = old_timing.to_nanoseconds()
            new_nanosecond = average.to_nanoseconds()
            change = 100 * (old_nanosecond - new_nanosecond) / old_nanosecond
            print(f"Performance difference: {change:.2f}%")
