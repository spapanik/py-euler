from pathlib import Path
from unittest import mock

from eulertools.lib.utils import Language, Problem
from eulertools.subcommands.generate import Generate


@mock.patch("eulertools.subcommands.generate.get_context", new_callable=mock.MagicMock)
@mock.patch("eulertools.subcommands.generate.get_solution", new_callable=mock.MagicMock)
@mock.patch("eulertools.subcommands.generate.get_template", new_callable=mock.MagicMock)
def test_generate_existing_solution(
    mock_get_template: mock.MagicMock,
    mock_get_solution: mock.MagicMock,
    mock_get_context: mock.MagicMock,
    problems: list[Problem],
    languages: list[Language],
    data_dir: Path,
) -> None:
    mock_get_template.return_value = data_dir.joinpath("template.jinja")
    mock_write_text = mock.MagicMock()
    mock_file = mock.MagicMock()
    mock_file.exists.return_value = True
    mock_file.write_text = mock_write_text
    mock_get_solution.return_value = mock_file
    mock_get_context.return_value = {}
    statement_command = Generate(
        languages=languages,
        problems=problems,
    )

    statement_command.run()
    assert mock_write_text.call_count == 0


@mock.patch("eulertools.subcommands.generate.get_context", new_callable=mock.MagicMock)
@mock.patch("eulertools.subcommands.generate.get_solution", new_callable=mock.MagicMock)
@mock.patch("eulertools.subcommands.generate.get_template", new_callable=mock.MagicMock)
def test_generate_missing_solutions(
    mock_get_template: mock.MagicMock,
    mock_get_solution: mock.MagicMock,
    mock_get_context: mock.MagicMock,
    problems: list[Problem],
    languages: list[Language],
    data_dir: Path,
) -> None:
    mock_get_template.return_value = data_dir.joinpath("template.jinja")
    mock_write_text = mock.MagicMock()
    mock_file = mock.MagicMock()
    mock_file.exists = mock.MagicMock(side_effect=[True, False, True, True])
    mock_file.write_text = mock_write_text
    mock_get_solution.return_value = mock_file
    mock_get_context.return_value = {}
    statement_command = Generate(
        languages=languages,
        problems=problems,
    )

    statement_command.run()
    assert mock_write_text.call_count == 1
    calls = [mock.call("Jinja template\n")]
    assert mock_write_text.call_args_list == calls


@mock.patch("eulertools.subcommands.generate.get_context", new_callable=mock.MagicMock)
@mock.patch("eulertools.subcommands.generate.get_solution", new_callable=mock.MagicMock)
@mock.patch("eulertools.subcommands.generate.get_template", new_callable=mock.MagicMock)
def test_generate_one_missing_solution(
    mock_get_template: mock.MagicMock,
    mock_get_solution: mock.MagicMock,
    mock_get_context: mock.MagicMock,
    problems: list[Problem],
    languages: list[Language],
    data_dir: Path,
) -> None:
    mock_get_template.return_value = data_dir.joinpath("template.jinja")
    mock_write_text = mock.MagicMock()
    mock_file = mock.MagicMock()
    mock_file.exists.return_value = False
    mock_file.write_text = mock_write_text
    mock_get_solution.return_value = mock_file
    mock_get_context.return_value = {}
    statement_command = Generate(
        languages=languages,
        problems=problems,
    )

    statement_command.run()
    assert mock_write_text.call_count == 4
    calls = [
        mock.call("Jinja template\n"),
        mock.call("Jinja template\n"),
        mock.call("Jinja template\n"),
        mock.call("Jinja template\n"),
    ]
    assert mock_write_text.call_args_list == calls
