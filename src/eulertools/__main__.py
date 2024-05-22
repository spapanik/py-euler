from eulertools.lib.parser import parse_args
from eulertools.subcommands.compare import Compare
from eulertools.subcommands.generate import Generate
from eulertools.subcommands.run import Run
from eulertools.subcommands.statement import Statement
from eulertools.subcommands.test import Test
from eulertools.subcommands.time import Time


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
