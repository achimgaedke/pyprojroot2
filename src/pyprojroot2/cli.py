# entrypoint for pyprojroot's cli
# usable, e.g. as `pyprojroot` returning the default root

import sys

from .here import HERE_CRITERION


def main() -> int:
    try:
        print(HERE_CRITERION.find_root())
        return 0
    except FileNotFoundError:
        print("could not find the project root", file=sys.stderr)
        return 1
