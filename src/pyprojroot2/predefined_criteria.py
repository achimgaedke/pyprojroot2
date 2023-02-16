from .criteria import HasFile, HasDir, HasFilePattern, HasBasename, IsCwd, HasFileGlob

has_file_pattern = HasFilePattern

has_file = HasFile

has_dir = HasDir

has_basename = HasBasename

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

is_git_root = has_dir(".git") | has_file(".git", contents="^gitdir: ")

is_svn_root = has_dir(".svn")

is_vcs_root = is_git_root | is_svn_root

from_wd = IsCwd()

# TODO: matches_glob matchs directories as well
matches_glob = HasFileGlob

# TODO: uses subdir
# is_testthat = has_basename("testthat", c("tests/testthat", "testthat"))
is_testthat = has_basename("testthat")
