import pathlib
import typing

from .criteria import Criterion


class RootCriterion:
    """
    A root criterion is a collection of criteria in order to determine the
    project's root. The criteria are tested in sequence and the path of the
    first matching criterium is selected.

    This is different to the pyprojroot's root criterium, which uses

    ```python3
    RootCriterion(AnyCriteria(criterium1, criterium2, ...))
    ```

    For most projects this difference in the search algorithm is
    not important.
    """

    def __init__(self, *criteria: Criterion):
        self.criteria: typing.List[Criterion] = list(criteria)

    def find_file(self, *args: str, path: str = ".") -> pathlib.Path:
        """
        Find a file's path relative to the project's root.
        """
        # warning if file/path doesn't exist?!
        return pathlib.Path(self.find_root(path), *args)

    def find_root(self, path: str = ".") -> pathlib.Path:
        """
        Find the project's root trying out one criterion after the other.
        The first match will be returned.

        Raises FileNotFoundError if root not found.
        """
        # No MAX_DEPTH limit, as path shouldn't be able have infinite loops
        abspath = pathlib.Path(path).resolve()
        if not abspath.is_dir():
            abspath = abspath.parent

        for c in self.criteria:
            if c.is_met(abspath):
                return abspath

            for dir in abspath.parents:
                if c.is_met(dir):
                    return dir

        raise FileNotFoundError("could not find the project root")

    def find_root_with_reason(self, path: str = ".") -> typing.Tuple[pathlib.Path, str]:
        """
        Implementation of find_root returning the path and reason.
        """
        abspath = pathlib.Path(path).resolve()
        if not abspath.is_dir():
            abspath = abspath.parent

        for c in self.criteria:
            reason = c.is_met_with_reason(abspath)
            if isinstance(reason, str):
                return abspath, reason

            for dir in abspath.parents:
                reason = c.is_met_with_reason(dir)
                if isinstance(reason, str):
                    return dir, reason

        raise FileNotFoundError("could not find the project root")
