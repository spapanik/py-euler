from pyutilkit.term import SGRCodes, SGRString

from eulertools.lib.utils import Problem, get_statement


class Statement:
    def __init__(self, problems: list[Problem], *, show_hints: bool):
        self.problems = problems
        self.show_hints = show_hints

    def run(self) -> None:
        for problem in self.problems:
            self.show_statement(problem)

    def show_statement(self, problem: Problem) -> None:
        statement = get_statement(problem)["common"]
        if title := statement.get("title", ""):
            print(SGRString(title, params=[SGRCodes.GREEN]))
            print(SGRString("~" * len(title), params=[SGRCodes.GREEN]))
        print(statement["description"].strip())
        if self.show_hints and (hint := statement.get("hint")):
            print()
            print(SGRString(title, params=[SGRCodes.BLUE]))
            print(SGRString("~" * len(title), params=[SGRCodes.BLUE]))
            print(hint.strip())
