import os.path
import pathlib
import typing

from .criteria import Criterion, as_criterion, PathSpec


class RootCriterion(typing.OrderedDict[str, Criterion]):
    """
    A root criterion is a collection of criteria in order to determine the
    project's root directory. The first directory, which matches a criterion is
    returned as root directory.

    The test order matters (though for most projects this difference in the
    search algorithm is not important).

    ``criteria_first``:
    By default (``criteria_first=True``) the criteria are tested in sequence and
    the path of the first matching criterium is selected, prefering the criteria
    tested first. This is behavior of ``rprojroot``.

    ``pyprojroot`` tests all each parent directory whether any criteria matches,
    therefore prefers lower subdirectories (the ones with more path components).
    Set ``criteria_first=False`` to choose this behaviour.

    ``resolve_path``: by default (``False``), ``os.path.abspath()`` is used to
    determine the absolute start path. This is expected to give the most
    intuitive results in most situations. But see the caveats of using
    ``os.path.normpath``. If set to ``True` ``pathlib.resolve()`` is used,
    which resolves symlinks.
    """

    criteria_first: bool = True
    resolve_path: bool = False

    def __init__(
        self,
        criteria: typing.Union[
            "RootCriterion",
            typing.Dict[str, Criterion],
        ],
        criteria_first: typing.Optional[bool] = None,
        resolve_path: typing.Optional[bool] = None,
    ):
        criteria_dict = {}

        if isinstance(criteria, RootCriterion):
            # copy constructor
            self.criteria_first = criteria.criteria_first
            self.resolve_path = criteria.resolve_path
            criteria_dict = {k: as_criterion(v) for k, v in criteria.items()}
        elif isinstance(criteria, dict):
            criteria_dict = {k: as_criterion(v) for k, v in criteria.items()}
        else:
            criteria_dict = as_root_criterion(criteria)

        super().__init__(criteria_dict)
        if criteria_first is not None:
            self.criteria_first = criteria_first
        if resolve_path is not None:
            self.resolve_path = resolve_path

    def as_start_path(self, path: PathSpec = ".") -> pathlib.Path:
        if self.resolve_path:
            abspath = pathlib.Path(path).resolve()
        else:
            abspath = pathlib.Path(os.path.abspath(path))
        if not abspath.is_dir():
            return abspath.parent
        return abspath

    def iter_parents(self, path: PathSpec) -> typing.Iterator[pathlib.Path]:
        # No MAX_DEPTH limit, as path shouldn't be able have infinite loops
        start_path = self.as_start_path(path)
        yield start_path
        yield from start_path.parents

    def iter_criteria_parents(
        self, path: PathSpec
    ) -> typing.Iterator[typing.Tuple[str, Criterion, pathlib.Path]]:
        if self.criteria_first:
            # rprojroot
            dir_list = list(self.iter_parents(path))
            for name, criterion in self.items():
                for dir in dir_list:
                    yield name, criterion, dir
        else:
            # pyprojroot
            for dir in self.iter_parents(path):
                for name, criterion in self.items():
                    yield name, criterion, dir

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> pathlib.Path:
        # convenience function for find_file
        return self.find_file(*args, **kwargs)

    def find_file(self, *args: str, path: PathSpec = ".") -> pathlib.Path:
        """
        Find a file's (or directory's) path relative to the project's root.

        The file path components are passed as arguments.

        Specify ``path`` if you want to start the root search at an alternative
        ``path``. By default the current work directory is used.

        Raises FileNotFoundError if no criteria were met.
        """
        # warning if file/path doesn't exist?!
        return pathlib.Path(self.find_root(path), *args)

    def find_root(self, path: PathSpec = ".") -> pathlib.Path:
        """
        Find the project's root using the criteria. The first match will be
        returned.

        Raises FileNotFoundError if no criteria were met.
        """
        for _, criterion, dir in self.iter_criteria_parents(path):
            if criterion.is_met(dir):
                return dir

        raise FileNotFoundError("could not find the project root")

    def find_root_with_reason(
        self, path: PathSpec = "."
    ) -> typing.Tuple[pathlib.Path, str]:
        """
        Implementation of find_root returning the path as well as the reason.

        Raises FileNotFoundError if no criteria were met.
        """
        for name, criterion, dir in self.iter_criteria_parents(path):
            reason = criterion.is_met_with_reason(dir)
            if isinstance(reason, str):
                return dir, f"{name}: {reason}"

        raise FileNotFoundError("could not find the project root")

    def find_all_root_names_and_dirs(
        self, path: PathSpec = "."
    ) -> typing.Dict[str, pathlib.Path]:
        """
        List the names of all root criteria met. Use as

        ```python3
        "is_git_vcs" in root_c.find_all_root_names_and_dirs()
        ```

        to figure out what type of projects you're working in.

        If no criteria are met, the dictionary is empty.
        """
        return {
            name: dir
            for name, criterion, dir in self.iter_criteria_parents(path)
            if criterion.is_met(dir)
        }


def as_root_criterion(
    criteria: typing.Any,
    criteria_first: typing.Optional[bool] = True,
    resolve_path: typing.Optional[bool] = False,
) -> RootCriterion:
    """
    If a string is given, the existence of the file entry is tested, i.e. the
    string is converted to a ``HasEntry`` criterion.
    """
    if isinstance(criteria, RootCriterion):
        return RootCriterion(
            criteria, criteria_first=criteria_first, resolve_path=resolve_path
        )
    if isinstance(criteria, dict):
        return RootCriterion(
            {k: as_criterion(v) for k, v in criteria.items()},
            criteria_first=criteria_first,
            resolve_path=resolve_path,
        )
    if isinstance(criteria, (Criterion, str)):
        return RootCriterion(
            {"criterion": as_criterion(criteria)},
            criteria_first=criteria_first,
            resolve_path=resolve_path,
        )
    if isinstance(criteria, typing.Sequence):
        return RootCriterion(
            {
                f"criterion-{i}": as_criterion(criterion)
                for i, criterion in enumerate(criteria)
            },
            criteria_first=criteria_first,
            resolve_path=resolve_path,
        )
    # fallback, assume it is a single criterion
    return RootCriterion(
        {"criterion": as_criterion(criteria)},
        criteria_first=criteria_first,
        resolve_path=resolve_path,
    )
