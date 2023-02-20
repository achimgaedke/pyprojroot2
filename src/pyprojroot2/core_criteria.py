import abc
import functools
import os
import pathlib
import typing

PathSpec = typing.Union[str, pathlib.Path]


class RootCriterion(abc.ABC):
    """
    Abstract base class of a root-criterion.

    A criterion tests whether it applies to a given path.
    """

    def describe(self) -> str:
        """
        Describes the test criterion.
        """
        return type(self).__name__

    def __repr__(self) -> str:
        return f"<RootCriterion: {self.describe().capitalize()}>"

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
        if not abspath.exists():
            raise FileNotFoundError(f"`{path}` does not exist.")
        if not abspath.is_dir():
            return abspath.parent
        return abspath

    @classmethod
    def list_search_dirs(
        cls,
        path: PathSpec = ".",
        limit_parents: typing.Union[int, None] = None,
        resolve_path: bool = False,
    ) -> typing.List[pathlib.Path]:
        """
        Determine the (parent) directories to test against the root criteria.

        Parameters are described in ``find_root``.
        """
        start_path = cls.get_start_path(path, resolve_path)
        # slicing pathlib.Path.parents is supportered since python-3.10 only
        return [start_path, *list(start_path.parents)[slice(limit_parents)]]

    def find_root(self, *args: typing.Any, **kwargs: typing.Any) -> pathlib.Path:
        """
        Find the project's root.

        ``path`` - the start path - will be converted into an asbolute path

        ``resolve_path`` will use ``pathlib.resolve_path`` to get an absolute start
        path. Otherwise ``os.path.abspath`` is used (default).

        ``limit_parents`` if None (default) all parents are considered, a
        positive number will consider the next n parents. A negative number
        will limit the search to the -limit_parents level in the file system.

        ``list_parents("/home/me/projects/fancy-project/src", limit_parents=-2)``

        will search only ``src``, ``fancy-project``, and ``projects``. A value
        of 1 will search ``src`` and ``fancy-projects``.


        Raises FileNotFoundError if no criteria were met.
        """
        parents = self.list_search_dirs(*args, **kwargs)

        for dir in parents:
            if self.test(dir):
                return dir

        # todo: add criterion to error message
        raise FileNotFoundError(
            f"No root directory found in {parents[0]} or its parent directories."
        )

    def find_file(self, *args: PathSpec, **kwargs: typing.Any) -> pathlib.Path:
        """
        Construct a file's (or directory's) path relative to the project's root.

        The file path components are passed as (unnamed) arguments.

        Other named parameters are the same as for ``find_root``.

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

    @staticmethod
    def root_joinpath(root_dir: pathlib.Path, *args: PathSpec) -> pathlib.Path:
        """
        Function to extend the root path by path components from `args`.

        Caveats:
        * only the first entry of `args` can be an absolute path
        * if so, the returned path only uses the path components of args
        * otherwise root_dir is extended by the path components of args
        """
        if any(pathlib.Path(arg).is_absolute() for arg in args[1:]):
            raise ValueError("only first path component may be absolute")
        file_path = pathlib.Path(*args)
        if file_path.is_absolute():
            return file_path
        return root_dir.joinpath(file_path)

    def make_fix_file(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Callable[..., pathlib.Path]:
        # typing.Callable[[typing.Unpack[PathSpec]], pathlib.Path]
        # Unpack is only experimental in mypy-1.0.0
        """
        Return a function to generate the absolute paths of project files.

        All parameters are the same as for ``find_root``.

        * relative path components will be concatenated to the (fixed) root,
        * if the first component is absolute, it is assumed the file is
          outside the project and the paths are concatenated wo the root.
        """
        root_dir = self.find_root(*args, **kwargs)
        fix_file_fn = functools.partial(self.root_joinpath, root_dir)

        return fix_file_fn

    def find_root_with_reason(
        self, *args: typing.Any, **kwargs: typing.Any
    ) -> typing.Tuple[pathlib.Path, str]:
        """
        Return the root directory and the reason why it matches.

        All parameters are the same as for ``find_root``.
        """
        parents = self.list_search_dirs(*args, **kwargs)
        for dir in parents:
            success, reason = self.test_with_reason(dir)
            if success:
                return dir, reason

        # todo: add criterion to error message
        raise FileNotFoundError(
            f"No root directory found in {parents[0]} or its parent directories."
        )

    def __or__(self, other: "RootCriterion") -> "AnyCriteria":
        if isinstance(other, AnyCriteria):
            return AnyCriteria(self, *other.criteria)
        return AnyCriteria(self, other)

    def __and__(self, other: "RootCriterion") -> "AllCriteria":
        if isinstance(other, AllCriteria):
            return AllCriteria(self, *other.criteria)
        return AllCriteria(self, other)


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
        descriptions = []
        for c in self.criteria:
            c_description = c.describe()
            if isinstance(c, AnyCriteria):
                # make sure the nested "or" clauses stay together
                c_description = f"({c_description})"
            descriptions.append(c_description)
        return " and ".join(descriptions)

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


class CriterionFromTestFun(RootCriterion):
    """
    Create a criterion by providing a test function and optional description.
    """

    def __init__(
        self,
        testfun: typing.Callable[[PathSpec], bool],
        description: typing.Optional[str] = None,
    ):
        # todo: check whether testfun has one path argument
        assert callable(testfun)
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
