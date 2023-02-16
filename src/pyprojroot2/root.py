import pathlib
import typing

from .criteria import Criterion


class RootCriterion:
    """
    A root criterion is a collection of criteria in order to determine the
    project's root. The criteria are tested in sequence and the path of the
    first matching criterium is selected.

    This is different to the pyprojroot's root criterium, use

    ```python3
    RootCriterion(AnyCriteria(criterium1, criterium2, ...))
    ```

    to emulate this behaviour. For most projects this difference in the search
    algorithm is not important.
    """

    def __init__(self, *criteria: Criterion):
        self.criteria: typing.List[Criterion] = list(criteria)

    def find_file(
        self, *args: str, path: str = "."
    ) -> typing.Union[pathlib.Path, None]:
        """
        Find a file's path relative to the project's root.
        """
        root = self.find_root(path)
        if root is None:
            return None
        return pathlib.Path(root, *args)

    def find_root(self, path: str = ".") -> typing.Union[pathlib.Path, None]:
        # This is the behavior of rprojroot's root_cirterion.
        """
        Find the project's root trying out one criterion after the other.
        The first match will be returned.

        Returns None if no criterion is met.
        """
        abspath = pathlib.Path(path).resolve()

        for c in self.criteria:
            if c.is_met(abspath):
                return abspath
            for dir in abspath.parents:
                if c.is_met(dir):
                    return dir

        return None

    def find_root_with_reason(
        self, path: str = "."
    ) -> typing.Union[typing.Tuple[pathlib.Path, str], typing.Tuple[None, None]]:
        abspath = pathlib.Path(path).resolve()
        for c in self.criteria:
            reason = c.is_met_with_reason(abspath)
            if isinstance(reason, str):
                return abspath, reason

            for dir in abspath.parents:
                reason = c.is_met_with_reason(abspath)
                if isinstance(reason, str):
                    return dir, reason

        return None, None
