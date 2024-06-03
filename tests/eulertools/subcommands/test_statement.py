from unittest import mock

from eulertools.lib.utils import Problem
from eulertools.subcommands.statement import Statement


@mock.patch(
    "eulertools.subcommands.statement.get_statement", new_callable=mock.MagicMock
)
@mock.patch("eulertools.subcommands.statement.print", new_callable=mock.MagicMock)
def test_statement_with_title_and_hint(
    mock_print: mock.MagicMock, mock_get_statement: mock.MagicMock, problem: Problem
) -> None:
    mock_get_statement.return_value = {
        "common": {"title": "Title", "description": "Desc", "hint": "Hint"}
    }
    statement_command = Statement(
        problems=[problem],
        show_hints=True,
    )

    statement_command.run()
    assert mock_print.call_count == 8
    calls = [
        mock.call("Title"),
        mock.call("~~~~~"),
        mock.call("Desc"),
        mock.call(),
        mock.call("Hint for Title"),
        mock.call("~~~~~~~~~~~~~~"),
        mock.call("Hint"),
        mock.call(),
    ]
    assert mock_print.call_args_list == calls


@mock.patch(
    "eulertools.subcommands.statement.get_statement", new_callable=mock.MagicMock
)
@mock.patch("eulertools.subcommands.statement.print", new_callable=mock.MagicMock)
def test_statement_with_title_but_not_hint(
    mock_print: mock.MagicMock, mock_get_statement: mock.MagicMock, problem: Problem
) -> None:
    mock_get_statement.return_value = {
        "common": {"title": "Title", "description": "Desc"}
    }
    statement_command = Statement(
        problems=[problem],
        show_hints=True,
    )

    statement_command.run()
    assert mock_print.call_count == 4
    calls = [
        mock.call("Title"),
        mock.call("~~~~~"),
        mock.call("Desc"),
        mock.call(),
    ]
    assert mock_print.call_args_list == calls


@mock.patch(
    "eulertools.subcommands.statement.get_statement", new_callable=mock.MagicMock
)
@mock.patch("eulertools.subcommands.statement.print", new_callable=mock.MagicMock)
def test_statement_without_title_but_with_hint(
    mock_print: mock.MagicMock, mock_get_statement: mock.MagicMock, problem: Problem
) -> None:
    mock_get_statement.return_value = {
        "common": {"description": "Desc", "hint": "Hint"}
    }
    statement_command = Statement(
        problems=[problem],
        show_hints=True,
    )

    statement_command.run()
    assert mock_print.call_count == 8
    calls = [
        mock.call("p0001"),
        mock.call("~~~~~"),
        mock.call("Desc"),
        mock.call(),
        mock.call("Hint for p0001"),
        mock.call("~~~~~~~~~~~~~~"),
        mock.call("Hint"),
        mock.call(),
    ]
    assert mock_print.call_args_list == calls


@mock.patch(
    "eulertools.subcommands.statement.get_statement", new_callable=mock.MagicMock
)
@mock.patch("eulertools.subcommands.statement.print", new_callable=mock.MagicMock)
def test_statement_without_title_and_hint(
    mock_print: mock.MagicMock, mock_get_statement: mock.MagicMock, problem: Problem
) -> None:
    mock_get_statement.return_value = {"common": {"description": "Desc"}}
    statement_command = Statement(
        problems=[problem],
        show_hints=True,
    )

    statement_command.run()
    assert mock_print.call_count == 4
    calls = [
        mock.call("p0001"),
        mock.call("~~~~~"),
        mock.call("Desc"),
        mock.call(),
    ]
    assert mock_print.call_args_list == calls