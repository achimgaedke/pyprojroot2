import abc
import itertools
import os
import pathlib
import re
import typing

PathSpec = typing.Union[str, pathlib.Path]


class RootCriterion(abc.ABC):
    """
    Base class of a root-criterion.

    A criterion tests whether it applies to a given path.
    """

    def describe(self) -> str:
        """
        Describes the test criterion.
        """
        return type(self).__name__

    def __repr__(self) -> str:
        return f"<RootCriterion: {self.describe().capitalize()}>"

    @staticmethod
    def get_start_path(
        path: PathSpec = ".", resolve_path: bool = False
    ) -> pathlib.Path:
        """
        Determines the start path for the root directory search.

        ``resolve_path`` will use pathlib.resolve_path to get an absolute start
        path. Otherwise ``os.path.abspath`` is used (default).
        """
        if resolve_path:
            abspath = pathlib.Path(path).resolve()
        else:
            abspath = pathlib.Path(os.path.abspath(path))
        if not abspath.is_dir():
            return abspath.parent
        return abspath

    @classmethod
    def list_parents(
        cls,
        path: PathSpec = ".",
        limit_parents: typing.Union[int, None] = None,
        resolve_path: bool = False,
    ) -> typing.List[pathlib.Path]:
        """
        Determine the (parent) directories to test against the root criteria.

        ``resolve_path`` will use ``pathlib.resolve_path`` to get an absolute start
        path. Otherwise ``os.path.abspath`` is used (default).

        ``limit_parents`` if None (default) all parents are considered, a
        positive number will consider the next n parents. A negative number
        will limit the search to the -limit_parents level in the file system.

        ``list_parents("/home/me/projects/fancy-project/src", limit_parents=-2)``

        will search only ``src``, ``fancy-project``, and ``projects``. A value
        of 1 will search ``src`` and ``fancy-projects``.
        """
        start_path = cls.get_start_path(path, resolve_path)
        # slicing pathlib.Path.parents is supportered since python-3.10 only
        return [start_path, *list(start_path.parents)[slice(limit_parents)]]

    def find_root(self, *args: typing.Any, **kwargs: typing.Any) -> pathlib.Path:
        """
        Find the project's root.

        Raises FileNotFoundError if no criteria were met.
        """
        parents = self.list_parents(*args, **kwargs)

        for dir in parents:
            if self.test(dir):
                return dir

        # todo: add criterion to error message
        raise FileNotFoundError(
            f"No root directory found in {parents[0]} or its parent directories."
        )

    def find_file(self, *args: PathSpec, **kwargs: typing.Any) -> pathlib.Path:
        """
        Find a file's (or directory's) path relative to the project's root.

        The file path components are passed as arguments.

        Specify ``path`` if you want to start the root search at an alternative
        ``path``. By default the current work directory is used.

        Raises FileNotFoundError if no criteria were met.
        """
        # rprojroot checks that all but first components are relative
        if any(pathlib.Path(arg).is_absolute() for arg in args[1:]):
            raise ValueError("only first path component may be absolute")
        file_path = pathlib.Path(*args)
        if file_path.is_absolute():
            # bypass as done by rprojroot
            return file_path
        return self.find_root(**kwargs).joinpath(file_path)

    def make_fix_file(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Callable[..., pathlib.Path]:
        # typing.Callable[[typing.Unpack[PathSpec]], pathlib.Path]
        # Unpack is only experimental in mypy-1.0.0
        """
        Create and return a function to generate the absolute paths of
        project files.
        """
        root_dir = self.find_root(*args, **kwargs)

        def fix_file_fn(*fx_args: PathSpec) -> pathlib.Path:
            if any(pathlib.Path(arg).is_absolute() for arg in fx_args[1:]):
                raise ValueError("only first path component may be absolute")
            file_path = pathlib.Path(*fx_args)
            if file_path.is_absolute():
                return file_path
            return root_dir.joinpath(file_path)

        return fix_file_fn

    def find_root_with_reason(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Tuple[pathlib.Path, str]:
        """
        Return the root directory and the reason why it matches.
        """
        parents = self.list_parents(*args, **kwargs)
        for dir in parents:
            success, reason = self.test_with_reason(dir)
            if success:
                return dir, reason

        # todo: add criterion to error message
        raise FileNotFoundError(
            f"No root directory found in {parents[0]} or its parent directories."
        )

    @abc.abstractmethod
    def test(self, dir: PathSpec) -> bool:
        """
        Tests whether the criterion is met for ``path``.
        """
        ...

    def test_with_reason(self, dir: PathSpec) -> typing.Tuple[bool, str]:
        """
        Returns the result of the check and the reason for the result.

        The reason is a human readable text describing why the check gave
        the result as it did. If the check is successful, then the reason
        can be the same as the description. If the check fails, then the
        reason should contain a statement why it failed, i.e. the negation of
        the successful reason.
        """
        if self.test(dir):
            return True, self.describe()
        # awkward to read, but easy to implement
        return False, f"not ({self.describe()})"

    def __or__(self, other: "RootCriterion") -> "AnyCriteria":
        if isinstance(other, AnyCriteria):
            return AnyCriteria(self, *other.criteria)
        return AnyCriteria(self, other)

    def __and__(self, other: "RootCriterion") -> "AllCriteria":
        if isinstance(other, AllCriteria):
            return AllCriteria(self, *other.criteria)
        return AllCriteria(self, other)


class TestFunCriterion(RootCriterion):
    """
    Create a criterion by providing a test function and optional description.
    """

    def __init__(
        self,
        testfun: typing.Callable[[PathSpec], bool],
        description: typing.Optional[str] = None,
    ):
        # todo: check whether testfun has one path argument
        self.testfun = testfun
        if description is None:
            self.description = f"Test Function `{testfun.__name__}`"
        else:
            self.description = description
        super().__init__()

    def describe(self) -> str:
        return self.description

    def test(self, dir: PathSpec) -> bool:
        return self.testfun(dir)


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

    def read_lines_from_file(self, file: PathSpec) -> typing.Iterator[str]:
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


class AnyCriteria(RootCriterion):
    """
    The directory matches when at least one of the criteria is met.

    Criteria can be linked together with ``|`` to form ``AnyCriteria``.
    """

    def __init__(self, *criteria: RootCriterion):
        self.criteria = criteria
        super().__init__()

    def describe(self) -> str:
        return " or ".join(c.describe() for c in self.criteria)

    def test(self, dir: PathSpec) -> bool:
        return any(c.test(dir) for c in self.criteria)

    def test_with_reason(self, dir: PathSpec) -> typing.Tuple[bool, str]:
        all_reasons = []
        for c in self.criteria:
            c_met, reason = c.test_with_reason(dir)
            if c_met:
                return True, reason
            all_reasons.append(reason)
        return False, " and ".join(all_reasons)

    def __or__(self, other: RootCriterion) -> "AnyCriteria":
        if isinstance(other, AnyCriteria):
            return AnyCriteria(*self.criteria, *other.criteria)
        return AnyCriteria(*self.criteria, other)


class AllCriteria(RootCriterion):
    """
    The directory matches when all criteria are met.

    Criteria can be linked together with ``&`` to form ``AllCriteria``.
    """

    def __init__(self, *criteria: RootCriterion):
        self.criteria = criteria
        super().__init__()

    def describe(self) -> str:
        return " and ".join(c.describe() for c in self.criteria)

    def test(self, dir: PathSpec) -> bool:
        return all(c.test(dir) for c in self.criteria)

    def test_with_reason(self, dir: PathSpec) -> typing.Tuple[bool, str]:
        reasons: typing.List[str] = []
        for c in self.criteria:
            c_met, reason = c.test_with_reason(dir)
            if not c_met:
                return False, reason
            reasons.append(reason)

        return True, " and ".join(reasons)

    def __and__(self, other: RootCriterion) -> "AllCriteria":
        if isinstance(other, AllCriteria):
            return AllCriteria(*self.criteria, *other.criteria)
        return AllCriteria(*self.criteria, other)


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
        return TestFunCriterion(criterion)
    if isinstance(criterion, dict):
        return AnyCriteria(*map(as_root_criterion, criterion.values()))
    if isinstance(criterion, (list, tuple)):
        return AnyCriteria(*map(as_root_criterion, criterion))
    raise ValueError(f"can not convert {type(criterion)} to criterion")
