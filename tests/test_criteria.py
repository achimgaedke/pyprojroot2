import contextlib
import os
import pathlib
import shutil
import tempfile
import typing

from pyprojroot2.criteria import HasFile, IsCwd


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
        assert HasFile("my_file_not there").find_root(test_dir) is None

        # test current directory setting
        with chdir(test_dir):
            assert HasFile("my_file").find_file("my_file")

        with chdir(test_dir / "a"):
            assert HasFile("my_file").find_file("my_file")


def test_current_dir() -> None:
    with fs_structure({"my_file": "a\nb\nc\nd\n", "a/b/c/": None}) as test_dir:
        with chdir(test_dir):
            assert IsCwd().is_met(test_dir)
            assert test_dir.resolve() == IsCwd().find_root(test_dir / "a" / "b" / "c")
