from eulertools.timeit import TimeIt
from eulertools.utils import Language, get_timings


class Benchmark:
    def __init__(self, languages: list[Language], times: int):
        self.languages = languages
        self.times = times

    def run(self) -> None:
        for language in self.languages:
            self.benchmark_language(language)

    def benchmark_language(self, language: Language) -> None:
        print(f"Benchmarking {language.name}:")
        timings = get_timings(language)
        for problem in sorted(timings):
            print(f"Problem {problem}:")
            TimeIt(
                language,
                problem,
                self.times,
                run_update=True,
                quiet=True,
                print_report=True,
            ).run()
