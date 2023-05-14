from eulertools.utils import ANSIEscape, get_statement


class Statement:
    def __init__(self, problems: list[str]):
        self.problems = problems

    def run(self) -> None:
        for problem in self.problems:
            self.show_statement(problem)

    @staticmethod
    def show_statement(problem: str) -> None:
        statement = get_statement(problem)
        for line in statement["title"]:
            print(ANSIEscape.OKGREEN, line, ANSIEscape.ENDC, sep="")
            print(ANSIEscape.OKGREEN, "~" * len(line), ANSIEscape.ENDC, sep="")

        for line in statement["description"]:
            print(line)
