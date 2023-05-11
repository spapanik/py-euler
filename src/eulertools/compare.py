from eulertools.utils import Language, get_timings


class Compare:
    def __init__(self, languages: list[Language], problems: list[str]):
        self.languages = languages
        self.problems = problems
        self.pad_length = max(max(len(language.name) for language in languages), 9)

    def run(self) -> None:
        matrix = [
            ["problem", *self.problems],
            *(self.get_language_timings(language) for language in self.languages),
        ]
        self.print_table(self.transpose(matrix))

    def print_table(self, matrix: list[list[str]]) -> None:
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
            *(str(timings.get(problem, "N/A")) for problem in self.problems),
        ]

    @staticmethod
    def transpose(matrix: list[list[str]]) -> list[list[str]]:
        return [list(row) for row in zip(*matrix, strict=True)]

    def padded_print(self, string: str, *, heading: bool) -> str:
        if heading:
            return string.center(self.pad_length)
        return string.rjust(self.pad_length)
