# entrypoint for pyprojroot's cli
# usable, e.g. as `pyprojroot` returning the default root

import argparse
import sys

from . import __version__
from .here import HERE_CRITERION


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

    try:
        print(HERE_CRITERION.find_root())
        return 0
    except FileNotFoundError:
        print("could not find the project root", file=sys.stderr)
        return 1
