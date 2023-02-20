import itertools
import pathlib
import re
import typing

from .core_criteria import AnyCriteria, CriterionFromTestFun, PathSpec, RootCriterion

# todo: for this and below: check for relative paths in criterion args


class HasFile(RootCriterion):
    """
    Matches if the named file is present, optionally the file's contents
    can be matched.

    ``filename`` name of the file (can be in a subdirectory, ``a/b.txt``)
    ``contents`` is the matching string or regular expression
    ``n`` limits the number of lines searched, -1 is unlimited.
    ``fixed`` is True if a fixed string should match an entire line.
              is False if the contents is a regular expression matching a part
              of the line (i.e. use the anchors ``^``, ``$`` for start and end).
    """

    def __init__(
        self,
        filename: PathSpec,
        contents: typing.Optional[str] = None,
        n: int = -1,
        fixed: bool = False,
    ):
        self.filename = filename
        self.contents = contents
        self.fixed = bool(fixed)
        self.max_lines_to_search = int(n)
        super().__init__()

    @staticmethod
    def read_lines_from_file(file: PathSpec) -> typing.Iterator[str]:
        """
        Read the lines from the text file and retruns them without the
        newline character at the end.
        """
        with open(file, "rt") as txt_file:
            yield from (line.rstrip("\n") for line in txt_file)

    def check_file_contents(self, file: PathSpec) -> bool:
        """
        Check whether in the contents of the file meets the line match
        criterion.
        """
        # early returns have the side effect that the read permission for the
        # file is not checked.
        if self.contents is None:
            return True
        if self.max_lines_to_search == 0:
            return False

        line_iterator = self.read_lines_from_file(file)

        if self.max_lines_to_search >= 0:
            line_iterator = itertools.islice(
                line_iterator,
                self.max_lines_to_search,
            )

        if self.fixed:
            fixed_pattern = self.contents

            def match_function(line: str) -> bool:
                return fixed_pattern == line

        else:
            regexp_pattern = re.compile(self.contents)

            def match_function(line: str) -> bool:
                return regexp_pattern.search(line) is not None

        return any((match_function(line) for line in line_iterator))

    def describe_contents_matching(self) -> str:
        if self.contents is None:
            return ""

        description = "file contains "

        if self.fixed:
            description += f"a line with the contents `{self.contents}`"
        else:
            description += f"a line matching the regular expression `{self.contents}`"

        if self.max_lines_to_search >= 0:
            description += f" in the first {self.max_lines_to_search} line/s"

        return description

    def test(self, dir: PathSpec) -> bool:
        full_filename = pathlib.Path(dir) / self.filename
        return full_filename.is_file() and self.check_file_contents(full_filename)

    def describe(self) -> str:
        pattern_description = f"has a file `{self.filename}`"
        if self.contents is not None:
            pattern_description += f" and {self.describe_contents_matching()}"
        return pattern_description


class HasFilePattern(HasFile):
    """
    Search for file matching regular expression pattern.

    Limitation: Searches only for entries at the same directory level
    """

    def __init__(
        self,
        pattern: str,
        contents: typing.Optional[str] = None,
        n: int = -1,
        fixed: bool = False,
    ):
        self.contents = contents
        self.fixed = bool(fixed)
        self.max_lines_to_search = int(n)
        super().__init__(pattern)

    def test(self, dir: PathSpec) -> bool:
        pattern = re.compile(str(self.filename))
        for full_filename in pathlib.Path(dir).iterdir():
            if (
                full_filename.is_file()
                and pattern.search(full_filename.name)
                and self.check_file_contents(full_filename)
            ):
                return True
        return False

    # todo: test_with_reason should print matching filename

    def describe(self) -> str:
        pattern_description = (
            f"has a file matching the regular expression `{self.filename}`"
        )
        if self.contents is not None:
            pattern_description += f" and {self.describe_contents_matching()}"
        return pattern_description


class HasFileGlob(HasFile):
    """
    Search for filename matching the glob pattern.

    The glob pattern allows searching in subdirectories.
    """

    def __init__(
        self,
        pattern: str,
        contents: typing.Optional[str] = None,
        n: int = -1,
        fixed: bool = False,
    ):
        self.contents = contents
        self.fixed = bool(fixed)
        self.max_lines_to_search = int(n)
        super().__init__(pattern)

    def test(self, dir: PathSpec) -> bool:
        for full_filename in pathlib.Path(dir).glob(str(self.filename)):
            if full_filename.is_file() and self.check_file_contents(full_filename):
                return True
        return False

    # todo: test_with_reason should print matching filename

    def describe(self) -> str:
        pattern_description = f"has a file matching `{self.filename}`"
        if self.contents is not None:
            pattern_description += f" and {self.describe_contents_matching()}"
        return pattern_description


class HasDir(RootCriterion):
    """
    Match if a directory of the given name is present.
    """

    def __init__(self, dirname: PathSpec):
        self.dirname = dirname
        super().__init__()

    def test(self, dir: PathSpec) -> bool:
        return (pathlib.Path(dir) / self.dirname).is_dir()

    def describe(self) -> str:
        return f"contains the directory `{self.dirname}`"


class HasEntry(RootCriterion):
    """
    Match if a filesystem entry (file/directory/link/...) of this name exists.

    Note:

    ``/`` or ``/.`` at the end of the entryname are stripped off, i.e. oddly
    ``myfile/`` will match a file - this is a sideffect of python's
    ``pathlib.Path.joinpath``. Consider using ``HasDir`` instead.
    """

    def __init__(self, entryname: PathSpec):
        self.entryname = entryname
        super().__init__()

    def test(self, dir: PathSpec) -> bool:
        return (pathlib.Path(dir) / self.entryname).exists()

    def describe(self) -> str:
        return f"contains the entry `{self.entryname}`"


class HasEntryGlob(RootCriterion):
    """
    Search for filesystem entry matching the glob pattern.

    The glob pattern allows searching in subdirectories.
    """

    def __init__(
        self,
        pattern: str,
    ):
        self.pattern = pattern
        super().__init__()

    def test(self, dir: PathSpec) -> bool:
        for _ in pathlib.Path(dir).glob(self.pattern):
            return True
        return False

    # TODO test with reason could actually print the entry found

    def describe(self) -> str:
        return f"has a file matching `{self.pattern}`"


Exists = HasEntry


class HasBasename(RootCriterion):
    """
    The directory's basename is equal to the name specified.
    """

    def __init__(self, basename: PathSpec):
        self.basename = basename
        super().__init__()

    def test(self, dir: PathSpec) -> bool:
        return self.basename == pathlib.Path(dir).name

    def describe(self) -> str:
        return f"has the basename `{self.basename}`"


class IsCwd(RootCriterion):
    """
    Directory is the current directory while searching
    for the project root.
    """

    def test(self, dir: PathSpec) -> bool:
        return pathlib.Path.cwd().resolve() == pathlib.Path(dir).resolve()

    def describe(self) -> str:
        return "is the current working directory"


def as_root_criterion(criterion: typing.Any) -> "RootCriterion":
    """
    Converts its input into a Criterion.
    """
    # take anything and try to make a criterion out of it
    if isinstance(criterion, RootCriterion):
        return criterion
    if isinstance(criterion, (str, pathlib.Path)):
        return HasFile(criterion)
    if callable(criterion):
        return CriterionFromTestFun(criterion)
    if isinstance(criterion, dict):
        return AnyCriteria(*map(as_root_criterion, criterion.values()))
    if isinstance(criterion, (list, tuple)):
        return AnyCriteria(*map(as_root_criterion, criterion))
    raise ValueError(f"can not convert {type(criterion)} to criterion")
