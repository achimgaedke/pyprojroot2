# entrypoint for pyprojroot's cli
# usable, e.g. as `pyprojroot` returning the default root

import argparse
import pathlib
import sys
import typing

from . import __version__
from .root_criterion import RootCriterion
from . import predefined_criteria

DEFAULT_CRITERION = "py_here_criteria"


def get_criterion(name: str) -> RootCriterion:
    criterion = getattr(predefined_criteria, name)
    assert isinstance(criterion, RootCriterion)
    return criterion


def list_criteria_names() -> typing.List[str]:
    # todo: check with "__all__"
    # todo: return a dict with criteria
    # todo: move this function to the predefined_criteria module
    all_criteria_names = [
        name
        for name in dir(predefined_criteria)
        if isinstance(getattr(predefined_criteria, name), RootCriterion)
    ]
    assert DEFAULT_CRITERION in all_criteria_names
    return all_criteria_names


def make_argument_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Determines the root directory of a project (e.g. git)",
        epilog="""
This command searches for the project root starting with the current directory
and iterating through the parent directories. When successfully matching the
criterion, it prints out the absolute pathname of the project root.
Otherwise prints a message on STDERR and exits with an error (1).
""",
    )

    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )

    # add criterion argument
    parser.add_argument(
        "-c",
        "--criterion",
        type=str,
        default=DEFAULT_CRITERION,
        choices=list_criteria_names(),
        help="project root criterion",
    )

    # add start path positional argument
    parser.add_argument("path", type=pathlib.Path, nargs="?", default=".")
    return parser


def cli_main() -> int:
    parser = make_argument_parser()
    parse_result = parser.parse_args()
    criterion = get_criterion(parse_result.criterion)

    try:
        print(criterion.find_root(path=parse_result.path))
        return 0
    except FileNotFoundError:
        print("could not find the project root", file=sys.stderr)
        return 1
