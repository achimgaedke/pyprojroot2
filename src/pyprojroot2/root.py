import os.path
import pathlib
import typing

from .criteria import Criterion, HasEntry


class RootCriterion:
    """
    A root criterion is a collection of criteria in order to determine the
    project's root directory. The first directory, which matches a criterion is
    returned as root directory.

    If a string is given, the existence of the file entry is tested, i.e. the
    string is converted to a ``HasEntry`` criterion.

    The test order matters (though for most projects this difference in the
    search algorithm is not important):

    First the criteria specified as unnamed parameters are tested, then the
    named parameter in order of specification. The "unnamed" criteria will be
    automatically named as ``criterion-0``, ``criterion-1``, and so on...

    ``criteria_first``:
    By default (``cirteria_first=True``) the criteria are tested in sequence and
    the path of the first matching criterium is selected, prefering the criteria
    tested first. This is behavior of ``rprojroot``.

    ``pyprojroot`` tests all each parent directory whether any cirteria matches,
    therefore prefers lower subdirectories (the ones with more path components).
    Set ``criteria_first=False`` to choose this behaviour.

    ``resolve_path``: by default (``False``), ``os.path.abspath()`` is used to
    determine the absolute start path. This is expected to give the most
    intuitive results in most situations. But see the caveats of using
    ``os.path.normpath``. If set to ``True` ``pathlib.resolve()`` is used,
    which resolves symlinks.
    """

    def __init__(
        self,
        *criteria: typing.Union[Criterion, str],
        cirteria_first: bool = True,
        resolve_path: bool = False,
        **named_criteria: typing.Union[Criterion, str],
    ):
        self.criteria: typing.List[Criterion] = [
            self.coerce_criteria(c) for c in criteria
        ]
        self.named_criteria = {
            k: self.coerce_criteria(v) for k, v in named_criteria.items()
        }
        self.criteria_first = cirteria_first
        self.resolve_path = resolve_path

    def as_start_path(self, path: str = ".") -> pathlib.Path:
        if self.resolve_path:
            abspath = pathlib.Path(path).resolve()
        else:
            abspath = pathlib.Path(os.path.abspath(path))
        if not abspath.is_dir():
            return abspath.parent
        return abspath

    @staticmethod
    def coerce_criteria(criterion: typing.Union[Criterion, str]) -> Criterion:
        if isinstance(criterion, str):
            return HasEntry(criterion)
        else:
            return criterion

    def iter_parents(self, path: str) -> typing.Iterator[pathlib.Path]:
        # No MAX_DEPTH limit, as path shouldn't be able have infinite loops
        # Todo: Resolve or abspath or os.path.normalise ?
        start_path = self.as_start_path(path)
        yield start_path
        yield from start_path.parents

    def iter_criteria(self) -> typing.Iterator[typing.Tuple[str, Criterion]]:
        for i, criterion in enumerate(self.criteria):
            yield f"criterion-{i}", criterion
        yield from self.named_criteria.items()

    def iter_criteria_parents(
        self, path: str
    ) -> typing.Iterator[typing.Tuple[str, Criterion, pathlib.Path]]:
        if self.criteria_first:
            # rprojroot
            dir_list = list(self.iter_parents(path))
            for name, criterion in self.iter_criteria():
                for dir in dir_list:
                    yield name, criterion, dir
        else:
            # pyprojroot
            criteria_list = list(self.iter_criteria())
            for dir in self.iter_parents(path):
                for name, criterion in criteria_list:
                    yield name, criterion, dir

    def __call__(self, *args: typing.Any, **kwargs: typing.Any) -> pathlib.Path:
        # convenience function for find_file
        return self.find_file(*args, **kwargs)

    def find_file(self, *args: str, path: str = ".") -> pathlib.Path:
        """
        Find a file's (or directory's) path relative to the project's root.

        The file path components are passed as arguments.

        Specify ``path`` if you want to start the root search at an alternative
        ``path``. By default the current work directory is used.

        Raises FileNotFoundError if no cirteria were met.
        """
        # warning if file/path doesn't exist?!
        return pathlib.Path(self.find_root(path), *args)

    def find_root(self, path: str = ".") -> pathlib.Path:
        """
        Find the project's root using the criteria. The first match will be
        returned.

        Raises FileNotFoundError if no cirteria were met.
        """
        for _, criterion, dir in self.iter_criteria_parents(path):
            if criterion.is_met(dir):
                return dir

        raise FileNotFoundError("could not find the project root")

    def find_root_with_reason(self, path: str = ".") -> typing.Tuple[pathlib.Path, str]:
        """
        Implementation of find_root returning the path as well as the reason.

        Raises FileNotFoundError if no cirteria were met.
        """
        for name, criterion, dir in self.iter_criteria_parents(path):
            reason = criterion.is_met_with_reason(dir)
            if isinstance(reason, str):
                return dir, f"{name}: {reason}"

        raise FileNotFoundError("could not find the project root")

    def list_met_criteria_names(self, path: str = ".") -> typing.List[str]:
        """
        List the names of all root criteria met. Use as

        ```python3
        "is_git_vcs" in root_c.list_met_criteria_names()
        ```

        to figure out what type of project you're working in.

        If no criteria are met, the list is empty.
        """
        return [
            name
            for name, criterion, dir in self.iter_criteria_parents(path)
            if criterion.is_met(dir)
        ]
