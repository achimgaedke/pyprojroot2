# entrypoint for pyprojroot's cli
# usable, e.g. as `pyprojroot` returning the default root

import argparse
import sys

from . import __version__
from .predefined_criteria import py_here_criteria


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Determines the root directory of a project (e.g. git)",
        epilog="""
Based on pyprojroot2, this command searches for a project root signature in the parent
directories starting from the current directory. When successful it prints out the
absolute pathname of the project root, otherwise exits with an error (1) and a message.
""",
    )
    parser.add_argument(
        "--version", action="version", version=f"%(prog)s {__version__}"
    )
    parser.parse_args()

    # this should be specifically "--here"
    # other predefined roots (instances of RootCriterion) should be selectable
    # with --criterion xxx
    try:
        print(py_here_criteria.find_root())
        return 0
    except FileNotFoundError:
        print("could not find the project root", file=sys.stderr)
        return 1
