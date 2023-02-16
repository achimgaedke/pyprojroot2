from .predefined_roots import PY_ROOT_CRITERION

# Todo: implement:
# set_here
# dr_here
# set_criterion
# i_am
# do_refresh_here

# these function should/could be cached
# R seems to set this once on library load time
# or at i_am
# or do_refresh_here

here = PY_ROOT_CRITERION.find_file

# that's from https://github.com/chendaniely/pyprojroot/blob/dev/src/pyprojroot/here.py#L29
get_here = PY_ROOT_CRITERION.find_root_with_reason
