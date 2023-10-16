import argparse
import sys

from eulertools.__version__ import __version__
from eulertools.compare import Compare
from eulertools.generate import Generate
from eulertools.run import Run
from eulertools.statement import Statement
from eulertools.test import Test
from eulertools.time import Time
from eulertools.utils import (
    filter_languages,
    filter_problems,
    get_all_languages,
    get_all_problems,
)

sys.tracebacklimit = 0
LANGUAGES = get_all_languages()
PROBLEMS = get_all_problems()


def language_specific(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "-l", "--language", nargs="*", dest="languages", default=LANGUAGES
    )


def problem_specific(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-p", "--problem", nargs="*", dest="problems", default=PROBLEMS)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="eulertools", description="Competitive programming CLI"
    )
    parser.add_argument(
        "-V",
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
        help="print the version and exit",
    )

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-v",
        "--verbose",
        action="count",
        default=0,
        dest="verbosity",
        help="increase the level of verbosity",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", parents=[parent_parser])
    language_specific(generate_parser)
    problem_specific(generate_parser)

    run_parser = subparsers.add_parser("run", parents=[parent_parser])
    language_specific(run_parser)
    problem_specific(run_parser)
    run_parser.add_argument("-u", "--update", action="store_true")

    time_parser = subparsers.add_parser("time", parents=[parent_parser])
    language_specific(time_parser)
    problem_specific(time_parser)
    time_parser.add_argument("-t", "--times", type=int, default=10)
    time_parser.add_argument("-u", "--update", action="store_true")

    compare_parser = subparsers.add_parser("compare", parents=[parent_parser])
    language_specific(compare_parser)
    problem_specific(compare_parser)

    test_parser = subparsers.add_parser("test", parents=[parent_parser])
    language_specific(test_parser)
    problem_specific(test_parser)
    test_parser.add_argument("-t", "--times", type=int, default=2)

    statement_parser = subparsers.add_parser("statement", parents=[parent_parser])
    problem_specific(statement_parser)
    statement_parser.add_argument(
        "-s", "--show-hints", dest="show_hints", action="store_true"
    )

    return parser.parse_args()


def main() -> None:
    options = parse_args()
    if options.verbosity > 0:
        sys.tracebacklimit = 9999
    options.languages = (
        filter_languages(options.languages) if hasattr(options, "languages") else []
    )
    options.problems = filter_problems(options.problems)
    match options.command:
        case "generate":
            Generate(options.languages, options.problems).run()
        case "run":
            Run(
                options.languages,
                options.problems,
                options.verbosity,
                run_update=options.update,
            ).run()
        case "time":
            Time(
                options.languages,
                options.problems,
                options.times,
                options.verbosity,
                run_update=options.update,
            ).run()
        case "test":
            Test(
                options.languages, options.problems, options.times, options.verbosity
            ).run()
        case "compare":
            Compare(options.languages, options.problems).run()
        case "statement":
            Statement(options.problems, show_hints=options.show_hints).run()
