from itertools import chain

from eulertools.utils import Language, get_all_keyed_problems, get_timings


class Compare:
    def __init__(self, languages: list[Language], problems: list[str]):
        self.languages = languages
        self.timings = {language: get_timings(language) for language in languages}
        self.keyed_problems = self.get_keyed_problems(languages, problems)
        self.pad_length = self._pad_length()

    def run(self) -> None:
        matrix = [
            ["problem", *(f"{problem}/{key}" for problem, key in self.keyed_problems)],
            *(self.get_language_timings(language) for language in self.languages),
        ]
        self.print_table(self.transpose(matrix))

    def print_table(self, matrix: list[list[str]]) -> None:
        if len(matrix) == 1:
            raise RuntimeError("No data to print")
        n = len(self.languages) + 1
        spacing = ["─" * self.pad_length for _ in range(n)]
        top = "┌" + "┬".join(spacing) + "┐"
        mid = "├" + "┼".join(spacing) + "┤"
        btm = "└" + "┴".join(spacing) + "┘"
        print(top)
        for i, row in enumerate(matrix):
            if i % 4 == 1:
                print(mid)
            print(
                "│",
                "│".join(self.padded_print(item, heading=(i == 0)) for item in row),
                "│",
                sep="",
            )
        print(btm)

    def get_language_timings(self, language: Language) -> list[str]:
        timings = get_timings(language)
        return [
            language.name,
            *(
                str(timings.get(problem, {}).get(key, "N/A"))
                for problem, key in self.keyed_problems
            ),
        ]

    @staticmethod
    def transpose(matrix: list[list[str]]) -> list[list[str]]:
        new_lines = (list(row) for row in zip(*matrix, strict=True))
        return [line for line in new_lines if any(item != "N/A" for item in line[1:])]

    def padded_print(self, string: str, *, heading: bool) -> str:
        if heading:
            return string.center(self.pad_length)
        return string.rjust(self.pad_length)

    def get_keyed_problems(
        self, languages: list[Language], problems: list[str]
    ) -> list[tuple[str, int]]:
        return [
            (problem, key)
            for problem, key in get_all_keyed_problems()
            if any(
                problem_key
                for language in languages
                for problem_key in self.timings[language].get(problem, {})
            )
            and problem in problems
        ]

    def _pad_length(self) -> int:
        lengths = chain(
            (len(problem) + len(str(key)) for problem, key in self.keyed_problems),
            (len(language.name) for language in self.languages),
            [len("problem")],
        )
        return max(lengths) + 2
