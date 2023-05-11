from eulertools.utils import Language, Timing, get_solution, get_timings, update_timings


class Update:
    def __init__(self, language: Language, problem: str, timing: str):
        self.language = language
        self.problem = problem
        self.timing = timing

    def run(self) -> None:
        solution = get_solution(self.language, self.problem)
        if not solution.exists():
            raise FileNotFoundError(
                f"Problem {self.problem} not solved for {self.language}. Aborting..."
            )
        timings = get_timings(self.language)

        old_timing = timings.get(self.problem)
        new_timing = Timing.from_string(self.timing, old_timing)
        timings[self.problem] = new_timing
        if old_timing is None:
            print(f"Initial timing: {new_timing}")
        else:
            print(f"Old timing: {old_timing}\nNew timing: {new_timing}")
        update_timings(self.language, timings)
