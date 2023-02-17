from .here import here, HERE_CRITERION
from .root import RootCriterion
from .predefined_criteria import has_file, has_dir, matches_glob

find_root = HERE_CRITERION.find_root
find_root_with_reason = HERE_CRITERION.find_root_with_reason
as_root_criterion = RootCriterion

# TODO:
# find match for CriterionFunction, Criterion, Criteria
# criteria.PathSpec - do I want to expose this?

# todo: understand what is useful here...
# either rprojroot's stuff or pyprojroot's stuff?
# and where does the "here" functionality go?

__all__ = [
    "as_root_criterion",
    "has_file",
    "has_dir",
    "here",
    "matches_glob",
    "find_root",
    "find_root_with_reason",
]
