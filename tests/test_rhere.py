import pathlib

import pytest

from pyprojroot2 import py_here_criteria, rhere


@pytest.fixture
def rhere_setup(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> pathlib.Path:
    monkeypatch.setattr(rhere, "_rhere_root_criterion", py_here_criteria)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "something").touch()
    return tmp_path


def test_rhere_set_here(rhere_setup: pathlib.Path) -> None:
    with pytest.raises(FileNotFoundError):
        rhere.here("something")

    # explicitly mark here
    rhere.set_here()
    assert (rhere_setup / ".here").is_file()

    something_file = rhere.here("something")
    assert rhere_setup / "something" == something_file
    assert something_file.is_file()
    assert ".here" in rhere.dr_here()


def test_rhere_i_am(rhere_setup: pathlib.Path) -> None:
    # no repo root marker present
    with pytest.raises(FileNotFoundError):
        rhere.here("something")

    # inform that "something" is expected
    rhere.i_am("something")

    # now it should work
    something_file = rhere.here("something")
    assert rhere_setup / "something" == something_file
    assert something_file.is_file()
    assert "something" in rhere.dr_here()


def test_rhere_default(rhere_setup: pathlib.Path) -> None:
    # mock a git repo
    (rhere_setup / ".git").mkdir()

    # default criterion is enough
    assert rhere.here("something").is_file()

    # git was the reason...
    assert ".git" in rhere.dr_here()
