import contextlib
import os
import pathlib
import shutil
import tempfile
import typing

import pytest

from pyprojroot2.criteria import (
    HasFile,
    IsCwd,
    AnyCriteria,
    HasBasename,
    HasEntry,
    AllCriteria,
    HasDir,
    HasFileGlob,
    HasFilePattern,
)


# todo: make this a fixture with pytest
@contextlib.contextmanager
def fs_structure(
    fs_structure: typing.Dict[str, typing.Union[str, None]]
) -> typing.Iterator[pathlib.Path]:
    """
    Create a temporary file structure on the fly

    Files: name (incl subdirs) -> contents as string
    Directories name (incl subdirs) -> None
    """

    tmpdir = pathlib.Path(tempfile.mkdtemp())

    for name, contents in fs_structure.items():
        assert not pathlib.Path(name).is_absolute()
        if contents is None:
            (tmpdir / name).mkdir(parents=True, exist_ok=True)
        elif isinstance(contents, str):
            filepath = tmpdir / name
            filepath.parent.mkdir(parents=True, exist_ok=True)
            with open(tmpdir / name, "wt") as f:
                f.write(contents)
        else:
            raise ValueError("unexpected type in fs_structure")

    try:
        yield tmpdir
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


@contextlib.contextmanager
def chdir(new_dir: typing.Union[str, pathlib.Path]) -> typing.Iterator[None]:
    """
    Changes the current directory for the time of the context and restores
    the previous one.
    """
    # NB this is not threadsafe as it manipulates the global current path
    old_cwd = os.curdir
    os.chdir(new_dir)
    try:
        yield
    finally:
        os.chdir(old_cwd)


def test_has_file_cirterion() -> None:
    testfile_contents = "a\nb\nc\nd\n"

    with fs_structure({"my_file": testfile_contents, "a/b/c/": None}) as test_dir:
        assert HasFile("my_file").is_met(test_dir)
        assert not HasFile("my_file.txt").is_met(test_dir)

        assert list(HasFile("my_file").read_lines_from_file(test_dir / "my_file")) == [
            "a",
            "b",
            "c",
            "d",
        ]
        assert (
            list(HasFile("my_file", n=0).read_lines_from_file(test_dir / "my_file"))
            == []
        )
        assert list(
            HasFile("my_file", n=2).read_lines_from_file(test_dir / "my_file")
        ) == ["a", "b"]

        # test "fixed" content
        assert HasFile("my_file", "c", fixed=True).is_met(test_dir)
        assert HasFile("my_file", "c", n=-3, fixed=True).is_met(test_dir)
        assert HasFile("my_file", "c", n=3, fixed=True).is_met(test_dir)
        assert not HasFile("my_file", "a", fixed=True, n=0).is_met(test_dir)
        assert not HasFile("my_file", "", fixed=True).is_met(test_dir)

        # test regexp matching
        assert HasFile("my_file", "[bc]").is_met(test_dir)
        assert not HasFile("my_file", "[bc]", n=1).is_met(test_dir)

        assert not HasFile("my_file.txt", "[bc]", n=1).is_met(test_dir)

        # test direct use as root criterion
        assert test_dir.resolve() == HasFile("my_file").find_root(test_dir / "a/b/c/")

        my_file = HasFile("my_file").find_file("my_file", path=test_dir)
        assert isinstance(my_file, pathlib.Path)
        assert open(my_file).read() == testfile_contents

        # test that non-existing root is returned as None
        with pytest.raises(FileNotFoundError):
            HasFile("my_file_not there").find_root(test_dir)

        # test current directory setting
        with chdir(test_dir):
            assert HasFile("my_file").find_file("my_file")

        with chdir(test_dir / "a"):
            assert HasFile("my_file").find_file("my_file")

        # look at the reason
        with pytest.raises(FileNotFoundError):
            HasFile("my_file_not there").find_root_with_reason(test_dir)

        assert HasFile("my_file").find_root_with_reason(test_dir) == (
            pathlib.Path(test_dir).resolve(),
            "criterion: has a file `my_file`",
        )
        assert HasFile("my_file", "a", 1, fixed=True).find_root_with_reason(
            test_dir
        ) == (
            pathlib.Path(test_dir).resolve(),
            "criterion: has a file `my_file` and file contains a line with the contents `a` in the first 1 line/s",
        )

        assert HasFile("my_file", "[ac]", 1, fixed=False).find_root_with_reason(
            test_dir
        ) == (
            pathlib.Path(test_dir).resolve(),
            "criterion: has a file `my_file` and file contains a line matching the regular expression `[ac]` in the first 1 line/s",
        )

        # test the description function
        assert (
            HasFile("my_file", "a", 1, fixed=True).description()
            == "has a file `my_file` and file contains a line with the contents `a` in the first 1 line/s"
        )
        assert (
            HasFile("my_file", "[ab]", 3).description()
            == "has a file `my_file` and file contains a line matching the regular expression `[ab]` in the first 3 line/s"
        )


def test_current_dir() -> None:
    with fs_structure({"my_file": "a\nb\nc\nd\n", "a/b/c/": None}) as test_dir:
        with chdir(test_dir):
            assert IsCwd().is_met(test_dir)
            assert test_dir.resolve() == IsCwd().find_root(test_dir / "a" / "b" / "c")

def test_has_entry() -> None:
    with fs_structure({"my_file": "a\nb\nc\nd\n", "a/b/c/": None}) as test_dir:
        assert HasEntry("a").is_met(test_dir)
        assert HasEntry("a/").is_met(test_dir)
        assert HasEntry(".").is_met(test_dir)  # that's an odd case?!
        assert HasEntry("my_file").is_met(test_dir)
        assert HasEntry("my_file/").is_met(
            test_dir
        )  # oddly this succeeds, though it is a file
        assert HasEntry("my_file/.").is_met(
            test_dir
        )  # oddly this succeeds, though it is a file
        assert not HasEntry("b").is_met(test_dir)
        assert HasEntry("a").is_met_with_reason(test_dir) == "contains the entry `a`"


def test_has_basename() -> None:
    with fs_structure({"my_file": "a\nb\nc\nd\n", "a/b/c/": None}) as test_dir:
        assert HasBasename("a").is_met(test_dir / "a")
        assert not HasBasename("a").is_met(test_dir)
        assert HasBasename(test_dir.name).is_met(test_dir)


def test_pattern_filenames() -> None:
    with fs_structure({"my_file": "a\nb\nc\nd\n", "a/b/c/": None}) as test_dir:
        assert HasFileGlob("my_*").is_met(test_dir)
        assert HasFilePattern("_fil").is_met(test_dir)
        assert not HasFilePattern("^_fil").is_met(test_dir)
        assert not HasFilePattern("[ab]").is_met(test_dir)

        assert HasFileGlob("my_*").description() == "has a file matching `my_*`"
        assert (
            HasFilePattern("_fil").description()
            == "has a file matching the regular expression `_fil`"
        )


def test_any_criteria() -> None:
    with fs_structure({"my_file": "a\nb\nc\nd\n", "a/b/c/": None}) as test_dir:
        combined_criteria = HasBasename("a") | HasFile("my_file")
        assert isinstance(combined_criteria, AnyCriteria)

        assert combined_criteria.is_met(test_dir)
        assert combined_criteria.is_met(test_dir / "a")
        assert not combined_criteria.is_met(test_dir / "b")

        assert (
            combined_criteria.description()
            == "has the basename `a` or has a file `my_file`"
        )


def test_all_criteria() -> None:
    with fs_structure({"my_file": "a\nb\nc\nd\n", "a/b/c/": None}) as test_dir:
        combined_criteria = HasDir("a") & HasFile("my_file")
        assert isinstance(combined_criteria, AllCriteria)

        assert combined_criteria.is_met(test_dir)
        assert not (combined_criteria & HasDir("b")).is_met(test_dir)

        assert (
            combined_criteria.description()
            == "contains the directory `a` and has a file `my_file`"
        )
        combined_root, combined_reason = combined_criteria.find_root_with_reason(
            test_dir / "a/b"
        )
        assert combined_root == test_dir.resolve()
        assert (
            combined_reason
            == "criterion: contains the directory `a` and has a file `my_file`"
        )

        combined_all_any = combined_criteria & HasDir("b") | HasBasename(test_dir.name)
        assert isinstance(combined_all_any, AnyCriteria)  # due to operator precedence
        assert combined_all_any.is_met(test_dir)

        assert combined_all_any.find_root(test_dir / "a")
        combined_root, reason = combined_all_any.find_root_with_reason(test_dir / "a")
        assert combined_root == test_dir.resolve()
        assert reason == f"criterion: has the basename `{test_dir.name}`"
