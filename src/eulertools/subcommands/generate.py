import jinja2

from eulertools.lib.utils import (
    Language,
    Problem,
    get_context,
    get_solution,
    get_template,
)


class Generate:
    def __init__(self, languages: list[Language], problems: list[Problem]):
        self.languages = languages
        self.problems = problems

    def run(self) -> None:
        for problem in self.problems:
            for language in self.languages:
                self.generate_solution(language, problem)

    @staticmethod
    def generate_solution(language: Language, problem: Problem) -> None:
        template_path = get_template(language)
        solution = get_solution(language, problem)
        context = get_context(language, problem)
        if solution.exists():
            return

        template = jinja2.Template(
            template_path.read_text(), keep_trailing_newline=True
        )
        solution.write_text(template.render(context))
