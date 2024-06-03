from unittest import mock

from eulertools.lib.utils import Language, Problem, Summary
from eulertools.subcommands.compare import Compare


@mock.patch("eulertools.subcommands.compare.get_summary", new_callable=mock.MagicMock)
@mock.patch("eulertools.subcommands.compare.print", new_callable=mock.MagicMock)
def test_compare_two_languages(
    mock_print: mock.MagicMock,
    mock_get_summary: mock.MagicMock,
    summary: Summary,
    problems: list[Problem],
    languages: list[Language],
) -> None:
    mock_get_summary.return_value = summary
    statement_command = Compare(languages=languages, problems=problems)

    statement_command.run()
    assert mock_print.call_count == 7
    calls = [
        mock.call("┌──────────┬──────────┬──────────┬──────────┐"),
        mock.call("│", " problem  │ case_key │    c     │  python  ", "│", sep=""),
        mock.call("├──────────┼──────────┼──────────┼──────────┤"),
        mock.call("│", "    p0001 │        1 │     44ns │    662ns ", "│", sep=""),
        mock.call("│", "    p0001 │        2 │     48ns │    721ns ", "│", sep=""),
        mock.call("│", "    p0042 │        1 │      N/A │    1.4ms ", "│", sep=""),
        mock.call("└──────────┴──────────┴──────────┴──────────┘"),
    ]
    assert mock_print.call_args_list == calls
