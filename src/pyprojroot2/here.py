from .predefined_roots import py_root_criterion

# this module presents functions, which are largely provided as
# methods of RootCriterion

# Todo: implement:
# set_here
# dr_here
# set_criterion
# i_am
# do_refresh_here

# these function should/could be cached
# R seems to set this once on library load time
# and reset at at i_am or do_refresh_here

# also look at
# https://pypi.org/project/pyhere/
# https://github.com/wildland-creative/pyhere

HERE_CRITERION = py_root_criterion

here = HERE_CRITERION.find_file

# that's from https://github.com/chendaniely/pyprojroot/blob/dev/src/pyprojroot/here.py#L29
# do I want to support this?
get_here = HERE_CRITERION.find_root_with_reason
