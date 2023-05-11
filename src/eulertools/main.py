import argparse
import sys

from eulertools.benchmark import Benchmark
from eulertools.compare import Compare
from eulertools.generate import Generate
from eulertools.run import Run
from eulertools.statement import Statement
from eulertools.test import Test
from eulertools.timeit import TimeIt
from eulertools.update import Update
from eulertools.utils import get_languages, get_problem

sys.tracebacklimit = 0
LANGUAGES = get_languages()


def valid_languages() -> set[str]:
    return {language.name for language in LANGUAGES}


def language_specific(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("language", choices=valid_languages())
    parser.add_argument("problem")


def multilanguage(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-l",
        "--language",
        nargs="*",
        dest="languages",
        choices=valid_languages(),
        default=valid_languages(),
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate")
    language_specific(generate_parser)
    generate_parser.add_argument("-f", "--force", action="store_true")

    run_parser = subparsers.add_parser("run")
    language_specific(run_parser)
    run_parser.add_argument("-d", "--debug", action="store_true")

    update_parser = subparsers.add_parser("update")
    language_specific(update_parser)
    update_parser.add_argument("timing")

    timeit_parser = subparsers.add_parser("timeit")
    language_specific(timeit_parser)
    timeit_parser.add_argument("-u", "--update", action="store_true")
    timeit_parser.add_argument("-q", "--quiet", action="store_true")
    timeit_parser.add_argument("-r", "--report", action="store_true")
    timeit_parser.add_argument("-t", "--times", type=int, default=10)

    benchmark_parser = subparsers.add_parser("benchmark")
    multilanguage(benchmark_parser)
    benchmark_parser.add_argument("-t", "--times", type=int, default=10)

    compare_parser = subparsers.add_parser("compare")
    multilanguage(compare_parser)
    compare_parser.add_argument("problems", nargs="+")

    test_parser = subparsers.add_parser("test")
    test_parser.add_argument("language", choices=valid_languages())
    test_parser.add_argument("problems", nargs="*")

    statement_parser = subparsers.add_parser("statement")
    statement_parser.add_argument("problem")

    return parser.parse_args()


def main() -> None:
    options = parse_args()
    match options.command:
        case "generate":
            language = LANGUAGES[options.language]
            problem = get_problem(options.problem)
            Generate(language, problem, force=options.force).run()
        case "run":
            language = LANGUAGES[options.language]
            problem = get_problem(options.problem)
            Run(language, problem, debug=options.debug).run()
        case "update":
            language = LANGUAGES[options.language]
            problem = get_problem(options.problem)
            Update(language, problem, options.timing).run()
        case "timeit":
            language = LANGUAGES[options.language]
            problem = get_problem(options.problem)
            TimeIt(
                language,
                problem,
                options.times,
                run_update=options.update,
                quiet=options.quiet,
                print_report=options.report,
            ).run()
        case "benchmark":
            languages = [LANGUAGES[language] for language in sorted(options.languages)]
            Benchmark(languages, options.times).run()
        case "compare":
            languages = [LANGUAGES[language] for language in sorted(options.languages)]
            problems = sorted(get_problem(problem) for problem in options.problems)
            Compare(languages, problems).run()
        case "test":
            language = LANGUAGES[options.language]
            problems = sorted(get_problem(problem) for problem in options.problems)
            Test(language, problems).run()
        case "statement":
            problem = get_problem(options.problem)
            Statement(problem).run()
