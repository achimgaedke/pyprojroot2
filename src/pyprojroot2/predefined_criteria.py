from .core_criteria import AnyCriteria
from .generic_criteria import (
    HasBasename,
    HasDir,
    HasEntry,
    HasEntryGlob,
    HasFile,
    HasFilePattern,
    IsCwd,
    as_root_criterion,
)

# todo: __all__

# functions to make criteria defined by rprojroot
has_file_pattern = HasFilePattern
has_basename = HasBasename

# rprojroot and pyprojroot 0.3.0
has_file = HasFile
has_dir = HasDir

# only pyprojroot 0.3.0
# https://github.com/chendaniely/pyprojroot/blob/dev/src/pyprojroot/criterion.py#L66
matches_glob = HasEntryGlob

# hmmm, that criterion is a bit odd, relies on the assumption
# that the first tested directory is the current directory.
from_wd = IsCwd()

# criteria provided by this package

# https://github.com/iterative/dvc/blob/8edaef010322645ccfc83936e5b7f706ad9773a4/dvc/repo/__init__.py#L399
is_dvc_root = HasDir(".dvc")

# Visual Studio Code IDE
# refine this criterion to .vscode/settings.json
# as there is a .vscode directory in the home directory as well
is_vscode_project = HasFile(".vscode/settings.json")

# IntelliJ IDEA IDE
is_idea_project = HasDir(".idea")

# Spyder IDE
is_spyder_project = HasDir(".spyproject")

# https://anaconda-project.readthedocs.io/en/latest/index.html
is_anaconda_project = HasFile("anaconda-project.yml")

# a python packaging project
# todo: Specify file contents? HasFile("pyproject.toml", "[project]", fixed=True)
is_python_project = (
    HasFile("setup.py") | HasFile("setup.cfg") | HasFile("pyproject.toml")
)

# criteria from rprojroot specific to R

# https://github.com/r-lib/rprojroot/blob/main/R/root.R#L309
is_rstudio_project = has_file_pattern("[.]Rproj$", contents="^Version: ", n=1)

is_r_package = has_file("DESCRIPTION", contents="^Package: ")

is_remake_project = has_file("remake.yml")

is_drake_project = has_dir(".drake")

is_pkgdown_project = (
    has_file("_pkgdown.yml")
    | has_file("_pkgdown.yaml")
    | has_file("pkgdown/_pkgdown.yml")
    | has_file("inst/_pkgdown.yml")
)

is_projectile_project = has_file(".projectile")

# TODO: use subdir
# is_testthat = has_basename("testthat", c("tests/testthat", "testthat"))
# or try... but doesn't reeturn the subdir...
# is_testthat = has_dir("tests/testthat") | has_dir("testthat") | has_basename("testthat")
is_testthat = has_basename("testthat")

# Version control

is_git_root = has_dir(".git") | has_file(".git", contents="^gitdir: ")

is_svn_root = has_dir(".svn")

is_vcs_root = is_git_root | is_svn_root

# criteria from R project here

# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/set_here.R#L46
is_here = has_file(".here")

# see https://github.com/r-lib/rprojroot/blob/main/R/root.R#L349
r_criteria = as_root_criterion(
    # todo: can we do anything with those list item names?
    {
        "is_rstudio_project": is_rstudio_project,
        "is_r_package": is_r_package,
        "is_remake_project": is_remake_project,
        "is_pkgdown_project": is_pkgdown_project,
        "is_projectile_project": is_projectile_project,
        "is_git_root": is_git_root,
        "is_svn_root": is_svn_root,
        "is_vcs_root": is_vcs_root,
        "is_testthat": is_testthat,
        # "from_wd": from_wd,
    }
)


# https://github.com/r-lib/here/blob/970dd2726c5cddda4a0e44e910fe5290be063485/R/zzz.R#L3
r_here_criteria = AnyCriteria(
    is_here
    | is_rstudio_project
    | is_r_package
    | is_remake_project
    | is_projectile_project
    | is_vcs_root
)

# criteria provided by pyprojroot 0.2.0 and 0.3.0

# see https://github.com/achimgaedke/pyprojroot2/blob/towards_v2/src/pyprojroot2/here.py#L17
# these are a more python centric root criteria
py_here_criteria_0_3_0 = as_root_criterion(
    [
        HasFile(".here"),  # difference to 0.2.0
        HasDir(".git"),
        HasEntryGlob("*.Rproj"),
        HasFile("requirements.txt"),
        HasFile("setup.py"),
        HasDir(".dvc"),
        HasDir(".spyproject"),
        HasFile("pyproject.toml"),
        HasDir(".idea"),
        HasDir(".vscode"),
    ]
)

# https://github.com/chendaniely/pyprojroot/blob/master/pyprojroot/pyprojroot.py#L23
py_here_criteria_0_2_0 = as_root_criterion(
    [
        HasEntry(".git"),  # difference to 0.3.0
        HasEntry(".here"),
        HasEntryGlob("*.Rproj"),
        HasEntry("requirements.txt"),
        HasEntry("setup.py"),
        HasEntry(".dvc"),
        HasEntry(".spyproject"),
        HasEntry("pyproject.toml"),
        HasEntry(".idea"),
        HasEntry(".vscode"),
    ]
)

# the default root criterion for this project
py_here_criteria = py_here_criteria_0_2_0
