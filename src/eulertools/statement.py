from eulertools.utils import ANSIEscape, get_statement


class Statement:
    def __init__(self, problem: str):
        self.problem = problem

    def run(self) -> None:
        statement = get_statement(self.problem)
        if not statement.exists():
            raise FileNotFoundError("No problem description found. Aborting...")

        with statement.open() as file:
            printed_title = False
            for line in file.readlines():
                if line.startswith("::"):
                    continue

                stripped_line = line.strip()
                if printed_title:
                    print(stripped_line)
                else:
                    n = len(stripped_line)
                    print(ANSIEscape.OKGREEN, stripped_line, ANSIEscape.ENDC, sep="")
                    print(ANSIEscape.OKGREEN, "~" * n, ANSIEscape.ENDC, sep="")
                    printed_title = True
