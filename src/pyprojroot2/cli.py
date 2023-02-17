# entrypoint for pyprojroot's cli
# usable, e.g. as `pyprojroot` returning the default root

from .here import HERE_CRITERION


def main():
    try:
        print(HERE_CRITERION.find_root())
        return 0
    except FileNotFoundError:
        return 1
