from itertools import chain

from eulertools.lib.utils import CaseId, Language, Problem, get_summary

PROBLEM = "problem"
CASE_KEY = "case_key"
MISSING = "N/A"


class Compare:
    __slots__ = (
        "languages",
        "problems",
        "summary",
        "case_ids",
        "pad_length",
    )

    def __init__(self, languages: list[Language], problems: list[Problem]):
        self.languages = languages
        self.problems = problems
        self.summary = get_summary()
        self.case_ids = self.get_case_ids()
        self.pad_length = self._pad_length()

    def run(self) -> None:
        matrix = [
            *self.transpose(self.labels),
            *(self.get_language_timings(language) for language in self.languages),
        ]
        self.print_table(self.transpose(matrix))

    @property
    def labels(self) -> list[list[str]]:
        return [
            [PROBLEM, CASE_KEY],
            *(
                [case_id.problem.name, str(case_id.case_key)]
                for case_id in self.case_ids
            ),
        ]

    def print_table(self, matrix: list[list[str]]) -> None:
        n = len(self.languages) + 2
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
        return [
            language.name,
            *(
                str(
                    self.summary.problems[case_id.problem]
                    .cases[case_id]
                    .timings.get(language, MISSING)
                )
                for case_id in self.case_ids
            ),
        ]

    @classmethod
    def transpose(cls, matrix: list[list[str]]) -> list[list[str]]:
        return [list(row) for row in zip(*matrix, strict=True)]

    def padded_print(self, string: str, *, heading: bool) -> str:
        if heading:
            return string.center(self.pad_length)
        return string.rjust(self.pad_length)

    def get_case_ids(self) -> list[CaseId]:
        return sorted(
            (
                case_id
                for problem_summary in self.summary.problems.values()
                if problem_summary.problem in self.problems
                for case_id, case_summary in problem_summary.cases.items()
                if any(language in case_summary.timings for language in self.languages)
            ),
            key=lambda case_id: (case_id.problem.name, case_id.case_key),
        )

    def _pad_length(self) -> int:
        lengths = chain(
            [len(MISSING)],
            (len(language.name) for language in self.languages),
            [len(row) for label in self.labels for row in label],
        )
        return max(lengths) + 2
