import argparse
import sys

from eulertools.__version__ import __version__
from eulertools.lib.utils import filter_languages, filter_problems
from eulertools.subcommands.compare import Compare
from eulertools.subcommands.generate import Generate
from eulertools.subcommands.run import Run
from eulertools.subcommands.statement import Statement
from eulertools.subcommands.test import Test
from eulertools.subcommands.time import Time

sys.tracebacklimit = 0


def language_specific(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-l", "--language", nargs="*", dest="languages")


def problem_specific(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("-p", "--problem", nargs="*", dest="problems")


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

    subparsers = parser.add_subparsers(dest="subcommand", required=True)

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
    group = time_parser.add_mutually_exclusive_group()
    group.add_argument("-a", "--append", action="store_true")
    group.add_argument("-u", "--update", action="store_true")

    compare_parser = subparsers.add_parser("compare", parents=[parent_parser])
    language_specific(compare_parser)
    problem_specific(compare_parser)

    test_parser = subparsers.add_parser("test", parents=[parent_parser])
    language_specific(test_parser)
    problem_specific(test_parser)
    test_parser.add_argument("-t", "--times", type=int, default=2)

    statement_parser = subparsers.add_parser("statement", parents=[parent_parser])
    problem_specific(statement_parser)
    statement_parser.add_argument("-s", "--show-hints", action="store_true")

    args = parser.parse_args()
    if args.verbosity > 0:
        sys.tracebacklimit = 1000
    if hasattr(args, "languages"):
        args.languages = filter_languages(args.languages)
        args.problems = filter_problems(args.problems, args.languages)
    elif hasattr(args, "problems"):
        args.problems = filter_problems(args.problems)

    return args


def main() -> None:
    args = parse_args()
    match args.subcommand:
        case "generate":
            Generate(args.languages, args.problems).run()
        case "run":
            Run(
                args.languages, args.problems, args.verbosity, run_update=args.update
            ).run()
        case "time":
            Time(
                args.languages,
                args.problems,
                args.times,
                args.verbosity,
                run_update=args.update,
                append_new=args.append,
            ).run()
        case "test":
            Test(args.languages, args.problems, args.times, args.verbosity).run()
        case "compare":
            Compare(args.languages, args.problems).run()
        case "statement":
            Statement(args.problems, show_hints=args.show_hints).run()
