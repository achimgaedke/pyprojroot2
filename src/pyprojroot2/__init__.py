from .here import here
from .root import RootCriterion
from .predefined_criteria import has_file, has_dir, matches_glob
from .predefined_roots import PY_ROOT_CRITERION

as_root_criterion = RootCriterion
find_root = PY_ROOT_CRITERION.find_root
find_root_with_reason = PY_ROOT_CRITERION.find_root_with_reason

# TODO:
# find match for CriterionFunction, Criterion, Criteria, PathSpec

__all__ = [
    "here",
    "has_file",
    "has_dir",
    "matches_glob",
    "find_root",
    "find_root_with_reason",
]
