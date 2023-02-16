# here

another package, but based on pyprojroot

Missing: make_fixed_file
subdir functions

Understand: how to return when no root found
How to describe?!

subdir: I believe can be emulated by providing path as a relative path
make_fixed_file: use pathlib features


# pyprojroot

for criteria

base class root_criterion

method
find_file()


new criteria

has_license <- has_file("LICENSE")
is_projecttemplate_project <- has_file("config/global.dcf", "^version: ")


You can also combine criteria via the | operator:
is_r_package | is_rstudio_project

needs to fullfill all criteria


