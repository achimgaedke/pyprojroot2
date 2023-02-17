import abc
import pathlib
import re
import typing

if typing.TYPE_CHECKING:
    from .root import RootCriterion


class Criterion(abc.ABC):
    """
    Base class of a criterion.

    A criterion tests whether it applies to a given path.
    """

    def description(self) -> str:
        return type(self).__name__

    def __repr__(self) -> str:
        return f"<Criterion: {self.description().capitalize()}>"

    def find_root(self, *args: typing.Any, **kwargs: typing.Any) -> pathlib.Path:
        # convenience function
        return self.as_root_criterion().find_root(*args, **kwargs)

    def find_root_with_reason(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Tuple[pathlib.Path, str]:
        # convenience function
        return self.as_root_criterion().find_root_with_reason(*args, **kwargs)

    def find_file(self, *args: typing.Any, **kwargs: typing.Any) -> pathlib.Path:
        # convenience function
        return self.as_root_criterion().find_file(*args, **kwargs)

    def as_root_criterion(self) -> "RootCriterion":
        # convenience function
        from .root import RootCriterion

        return RootCriterion(criterion=self)

    @abc.abstractmethod
    def is_met(self, dir: pathlib.Path) -> bool:
        # the criterion is met for this path
        ...

    def is_met_with_reason(self, dir: pathlib.Path) -> typing.Union[str, bool]:
        if self.is_met(dir):
            return self.description()
        return False

    def __or__(self, other: "Criterion") -> "AnyCriteria":
        if isinstance(other, AnyCriteria):
            return AnyCriteria(self, *other.criteria)
        return AnyCriteria(self, other)

    def __and__(self, other: "Criterion") -> "AllCriteria":
        if isinstance(other, AllCriteria):
            return AllCriteria(self, *other.criteria)
        return AllCriteria(self, other)


class HasFile(Criterion):
    """
    Matches if the named file is present, optionally the file's contents
    can be matched.

    ``contents`` is the matching string or regular expression
    ``n`` limits the number of lines searched, -1 is unlimited.
    ``fixed`` is True if a fixed string should match an entire line.
              is False if the contents is a regular expression matching a part
              of the line (i.e. use the anchors ``^``, ``$`` for start and end).
    """

    def __init__(
        self,
        filename: str,
        contents: typing.Optional[str] = None,
        n: int = -1,
        fixed: bool = False,
    ):
        self.filename = filename
        self.contents = contents
        self.fixed = bool(fixed)
        self.max_lines_to_search = int(n)
        super().__init__()

    def read_lines_from_file(self, file: pathlib.Path) -> typing.Iterator[str]:
        """
        read the lines, strip off the newline at the end and stop at max_lines_to_search
        """
        max_lines = self.max_lines_to_search
        with open(file, "rt") as txt_file:
            while max_lines != 0:
                line = txt_file.readline()
                if not line:
                    return
                # removesuffix introduced at python 3.9
                if line[-1] == "\n":
                    yield line[:-1]
                else:
                    yield line
                max_lines -= 1

    def check_file_contents(self, file: pathlib.Path) -> bool:
        """
        check the contents of the file
        """
        if self.contents is None:
            return True

        if not self.fixed:
            pattern = re.compile(self.contents)
            return any(pattern.search(line) for line in self.read_lines_from_file(file))

        return any(line == self.contents for line in self.read_lines_from_file(file))

    def contents_description(self) -> str:
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

    def is_met(self, dir: pathlib.Path) -> bool:
        full_filename = pathlib.Path(dir) / self.filename
        return full_filename.is_file() and self.check_file_contents(full_filename)

    def description(self) -> str:
        pattern_description = f"has a file `{self.filename}`"
        if self.contents is not None:
            pattern_description += f" and {self.contents_description()}"
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

    def is_met(self, dir: pathlib.Path) -> bool:
        pattern = re.compile(self.filename)
        for full_filename in dir.iterdir():
            if (
                full_filename.is_file()
                and pattern.search(full_filename.name)
                and self.check_file_contents(full_filename)
            ):
                return True
        return False

    def description(self) -> str:
        pattern_description = (
            f"has a file matching the regular expression `{self.filename}`"
        )
        if self.contents is not None:
            pattern_description += f" and {self.contents_description()}"
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

    def is_met(self, dir: pathlib.Path) -> bool:
        for full_filename in dir.glob(self.filename):
            if full_filename.is_file() and self.check_file_contents(full_filename):
                return True
        return False

    def description(self) -> str:
        pattern_description = f"has a file matching `{self.filename}`"
        if self.contents is not None:
            pattern_description += f" and {self.contents_description()}"
        return pattern_description


class HasDir(Criterion):
    """
    Match if a directory of the given name is present.
    """

    def __init__(self, dirname: str):
        self.dirname = dirname
        super().__init__()

    def is_met(self, dir: pathlib.Path) -> bool:
        return (pathlib.Path(dir) / self.dirname).is_dir()

    def description(self) -> str:
        return f"contains the directory `{self.dirname}`"


class HasEntry(Criterion):
    """
    Match if a filesystem entry (file/directory/link/...) of this name exists.

    Note:

    ``/`` or ``/.`` at the end of the entryname are stripped off, i.e. oddly
    ``myfile/`` will match a file - this is a sideffect of python's
    ``pathlib.Path.joinpath``. Consider using ``HasDir`` instead.
    """

    def __init__(self, entryname: str):
        self.entryname = entryname
        super().__init__()

    def is_met(self, dir: pathlib.Path) -> bool:
        return (pathlib.Path(dir) / self.entryname).exists()

    def description(self) -> str:
        return f"contains the entry `{self.entryname}`"


Exists = HasEntry


class HasBasename(Criterion):
    """
    The directory's basename is equal to the name specified.
    """

    def __init__(self, basename: str):
        self.basename = basename
        super().__init__()

    def is_met(self, dir: pathlib.Path) -> bool:
        return self.basename == dir.name

    def description(self) -> str:
        return f"has the basename `{self.basename}`"


class IsCwd(Criterion):
    """
    Directory is the current directory while searching
    for the project root.
    """

    def is_met(self, dir: pathlib.Path) -> bool:
        return pathlib.Path.cwd().resolve() == dir.resolve()

    def description(self) -> str:
        return "is the current working directory"


class AnyCriteria(Criterion):
    """
    The directory matches when at least one of the cirteria is met.

    Criteria can be linked together with ``|`` to form ``AnyCriteria``.
    """

    def __init__(self, *criteria: Criterion):
        self.criteria = criteria
        super().__init__()

    def description(self) -> str:
        return " or ".join(c.description() for c in self.criteria)

    def is_met(self, dir: pathlib.Path) -> bool:
        return any(c.is_met(dir) for c in self.criteria)

    def is_met_with_reason(self, dir: pathlib.Path) -> typing.Union[str, bool]:
        for c in self.criteria:
            c_met = c.is_met_with_reason(dir)
            if isinstance(c_met, str):
                return c_met
        return False

    def __or__(self, other: Criterion) -> "AnyCriteria":
        if isinstance(other, AnyCriteria):
            return AnyCriteria(*self.criteria, *other.criteria)
        return AnyCriteria(*self.criteria, other)


class AllCriteria(Criterion):
    """
    The directory matches when all cirteria are met.

    Criteria can be linked together with ``&`` to form ``AllCriteria``.
    """

    def __init__(self, *criteria: Criterion):
        self.criteria = criteria
        super().__init__()

    def description(self) -> str:
        return " and ".join(c.description() for c in self.criteria)

    def is_met(self, dir: pathlib.Path) -> bool:
        return all(c.is_met(dir) for c in self.criteria)

    def is_met_with_reason(self, dir: pathlib.Path) -> typing.Union[str, bool]:
        reasons: typing.List[str] = []
        for c in self.criteria:
            reason = c.is_met_with_reason(dir)
            if isinstance(reason, str):
                reasons.append(reason)
            else:
                return False
        return " and ".join(reasons)

    def __and__(self, other: Criterion) -> "AllCriteria":
        if isinstance(other, AllCriteria):
            return AllCriteria(*self.criteria, *other.criteria)
        return AllCriteria(*self.criteria, other)
