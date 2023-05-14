from pathlib import Path

import jinja2

from eulertools.utils import Language, get_context, get_solution, get_template


class Generate:
    def __init__(self, languages: list[Language], problems: list[str]):
        self.languages = languages
        self.problems = problems

    def run(self) -> None:
        for problem in self.problems:
            for language in self.languages:
                self.generate_solution(language, problem)

    def generate_solution(self, language: Language, problem: str) -> None:
        template = get_template(language)
        solution = get_solution(language, problem)
        if get_solution(language, problem).exists():
            return

        self.generate(template, solution, get_context(language, problem))

    @staticmethod
    def generate(
        template_path: Path, output_path: Path, context: dict[str, str]
    ) -> None:
        template = jinja2.Template(template_path.read_text())
        output_path.write_text(template.render(**context))
