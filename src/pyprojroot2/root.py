import pathlib
import typing

from .criteria import Criterion


class RootCriterion:
    """
    A root criterion is a collection of criteria in order to determine the
    project's root. The first directory, which matches a criterion is returned
    as root directory.

    First the criteria specified as unnamed parameters are tested, then the
    named parameter in order of specification.

    For most projects this difference in the search algorithm is not important,
    but here the details nonetheless:

    By default (``cirteria_first=True``) the criteria are tested in sequence and
    the path of the first matching criterium is selected, prefering the first
    criterion.

    `pyprojroot` tests all each parent directory whether any cirteria matches,
    therefore prefers higher subdirectories. Set ``criteria_first=False`` to
    choose this behaviour.
    """

    def __init__(
        self,
        *criteria: Criterion,
        cirteria_first: bool = True,
        **named_criteria: Criterion,
    ):
        self.criteria: typing.List[Criterion] = list(criteria)
        self.named_criteria = named_criteria
        self.criteria_first = cirteria_first

    def find_file(self, *args: str, path: str = ".") -> pathlib.Path:
        """
        Find a file's path relative to the project's root.
        """
        # warning if file/path doesn't exist?!
        return pathlib.Path(self.find_root(path), *args)

    def iter_parents(self, path: str) -> typing.Iterator[pathlib.Path]:
        # No MAX_DEPTH limit, as path shouldn't be able have infinite loops
        # Todo: Resolve or abspath or os.path.normalise ?
        abspath = pathlib.Path(path).resolve()
        if abspath.is_dir():
            yield abspath
        yield from abspath.parents

    def iter_criteria(self) -> typing.Iterator[typing.Tuple[str, Criterion]]:
        for i, criterion in enumerate(self.criteria):
            yield f"criterion-{i}", criterion
        yield from self.named_criteria.items()

    def iter_criteria_parents(
        self, path: str
    ) -> typing.Iterator[typing.Tuple[str, Criterion, pathlib.Path]]:
        if self.criteria_first:
            # rprojroot
            for name, criterion in self.iter_criteria():
                for dir in self.iter_parents(path):
                    yield name, criterion, dir
        else:
            # pyprojroot
            for dir in self.iter_parents(path):
                for name, criterion in self.iter_criteria():
                    yield name, criterion, dir

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
