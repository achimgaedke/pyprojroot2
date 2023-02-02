"""
This module is inspired by the `here` library for R.
See https://github.com/r-lib/here.

It is intended for interactive use only.
"""

__all__ = ["CRITERIA", "get_here", "here"]

from pathlib import Path
from typing import Tuple
from warnings import warn

from .criterion import PathSpec, has_dir, has_file, matches_glob
from .root import find_root_with_reason

CRITERIA = [
    has_file(".here"),
    has_dir(".git"),
    matches_glob("*.Rproj"),
    has_file("requirements.txt"),
    has_file("setup.py"),
    has_dir(".dvc"),
    has_dir(".spyproject"),
    has_file("pyproject.toml"),
    has_dir(".idea"),
    has_dir(".vscode"),
]


def get_here() -> Tuple[Path, str]:
    # TODO: This should only find_root once per session
    start = Path.cwd()
    path, reason = find_root_with_reason(CRITERIA, start=start)
    return path, reason


# TODO: Implement set_here


def here(relative_project_path: PathSpec = "", warn_missing: bool = False) -> Path:
    """
    Returns the path relative to the projects root directory.
    :param relative_project_path: relative path from project root
    :param project_files: list of files to track inside the project
    :param warn_missing: warn user if path does not exist (default=False)
    :return: pathlib path
    """
    path, reason = get_here()
    # TODO: Show reason when requested

    if relative_project_path:
        path = path / relative_project_path

    if warn_missing and not path.exists():
        warn(f"Path doesn't exist: {path!s}")
    return path
