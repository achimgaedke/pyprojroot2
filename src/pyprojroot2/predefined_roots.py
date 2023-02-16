from .root import RootCriterion
from . import predefined_criteria

# see https://github.com/r-lib/rprojroot/blob/main/R/root.R#L349
R_ROOT_CRITERION = RootCriterion(
    predefined_criteria.is_rstudio_project,
    predefined_criteria.is_r_package,
    predefined_criteria.is_remake_project,
    predefined_criteria.is_pkgdown_project,
    predefined_criteria.is_projectile_project,
    predefined_criteria.is_git_root,
    predefined_criteria.is_svn_root,
    predefined_criteria.is_vcs_root,
    predefined_criteria.is_testthat,
    predefined_criteria.from_wd,
)

# see https://github.com/achimgaedke/pyprojroot2/blob/towards_v2/src/pyprojroot2/here.py#L17
# this is a more python centric root criterion
PY_ROOT_CRITERION = RootCriterion(
    predefined_criteria.has_file(".here"),
    predefined_criteria.has_dir(".git"),
    predefined_criteria.matches_glob("*.Rproj"),
    predefined_criteria.has_file("requirements.txt"),
    predefined_criteria.has_file("setup.py"),
    predefined_criteria.has_dir(".dvc"),
    predefined_criteria.has_dir(".spyproject"),
    predefined_criteria.has_file("pyproject.toml"),
    predefined_criteria.has_dir(".idea"),
    predefined_criteria.has_dir(".vscode"),
)
