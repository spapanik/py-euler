from pathlib import Path

import jinja2

from eulertools.utils import Language, get_solution, get_statement, get_template


class Generate:
    def __init__(self, language: Language, problem: str, *, force: bool = False):
        self.language = language
        self.problem = problem
        self.force = force

    def run(self) -> None:
        solution = get_solution(self.language, self.problem)
        if solution.exists() and not self.force:
            raise FileExistsError("Solution already exists. Aborting...")
        template = get_template(self.language)

        statement = get_statement(self.problem)
        if not statement.exists():
            raise FileNotFoundError("No problem description found. Aborting...")

        context = self.get_context(self.problem)
        self.generate(template, solution, context)

    @staticmethod
    def generate(
        template_path: Path, output_path: Path, context: dict[str, str]
    ) -> None:
        template = jinja2.Template(template_path.read_text())
        output_path.write_text(template.render(**context))

    @staticmethod
    def get_context(padded_number: str) -> dict[str, str]:
        return {"padded_number": padded_number}
