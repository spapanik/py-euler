from eulertools.utils import ANSIEscape, get_statement


class Statement:
    def __init__(self, problems: list[str], *, show_hints: bool):
        self.problems = problems
        self.show_hints = show_hints

    def run(self) -> None:
        for problem in self.problems:
            self.show_statement(problem)

    def show_statement(self, problem: str) -> None:
        statement = get_statement(problem)["common"]
        if title := statement.get("title", ""):
            print(ANSIEscape.OKGREEN, title, ANSIEscape.ENDC, sep="")
            print(ANSIEscape.OKGREEN, "~" * len(title), ANSIEscape.ENDC, sep="")
        print(statement["description"].strip())
        if self.show_hints and (hint := statement.get("hint")):
            print("")
            print(ANSIEscape.OKBLUE, "Hint", ANSIEscape.ENDC, sep="")
            print(ANSIEscape.OKBLUE, "~" * len("Hint"), ANSIEscape.ENDC, sep="")
            print(hint.strip())
