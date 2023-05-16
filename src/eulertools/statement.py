from eulertools.utils import ANSIEscape, get_statement


class Statement:
    def __init__(self, problems: list[str]):
        self.problems = problems

    def run(self) -> None:
        for problem in self.problems:
            self.show_statement(problem)

    @staticmethod
    def show_statement(problem: str) -> None:
        statement = get_statement(problem)["common"]
        print(ANSIEscape.OKGREEN, statement["title"], ANSIEscape.ENDC, sep="")
        print(ANSIEscape.OKGREEN, "~" * len(statement["title"]), ANSIEscape.ENDC, sep="")
        print(statement["description"].strip())
