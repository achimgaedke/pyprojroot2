import pathlib
import sys

import pytest

from pyprojroot2 import RootCriterion, cli


def test_criteria_access() -> None:
    assert cli.list_criteria_names()
    assert isinstance(cli.get_criterion(cli.DEFAULT_CRITERION), RootCriterion)


def test_argparse() -> None:
    parser = cli.make_argument_parser()

    default_result = parser.parse_args([])
    assert default_result.criterion == cli.DEFAULT_CRITERION
    assert default_result.path == pathlib.Path(".")

    criterion_result = parser.parse_args(["-c", "is_git_root"])
    assert criterion_result.criterion == "is_git_root"
    assert criterion_result.path == pathlib.Path(".")

    with pytest.raises(SystemExit):
        parser.parse_args(["-c", "is_dir"])

    # only one criterion, the last one specified
    criterion_result = parser.parse_args(
        ["-c", "is_dvc_root", "--criterion", "is_git_root"]
    )
    assert criterion_result.criterion == "is_git_root"

    path_result = parser.parse_args(["--criterion", "is_git_root", "bla"])
    assert path_result.criterion == "is_git_root"
    assert path_result.path == pathlib.Path("bla")


def test_cli(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    entrypoint_name = "pyprojroot2"

    monkeypatch.chdir(tmp_path)

    monkeypatch.setattr(sys, "argv", [entrypoint_name, "--criterion", "is_git_root"])
    assert cli.cli_main() == 1
    output = capsys.readouterr()
    assert not output.out
    assert output.err

    # mock a git repo, but not a dvc repo
    (tmp_path / "project/.git").mkdir(parents=True)

    monkeypatch.setattr(sys, "argv", [entrypoint_name, "--criterion", "is_git_root"])
    assert cli.cli_main() == 1
    output = capsys.readouterr()
    assert not output.out
    assert output.err

    monkeypatch.setattr(
        sys, "argv", [entrypoint_name, "--criterion", "is_git_root", "project"]
    )
    assert cli.cli_main() == 0
    output = capsys.readouterr()
    assert pathlib.Path(output.out.rstrip()) == tmp_path / "project"
    assert not output.err

    monkeypatch.setattr(
        sys, "argv", [entrypoint_name, "--criterion", "is_dvc_root", "project"]
    )
    assert cli.cli_main() == 1
    output = capsys.readouterr()
    assert not output.out
    assert output.err
