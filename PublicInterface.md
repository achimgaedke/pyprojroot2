# here

another package, but based on pyprojroot


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


predefined criteria

see https://rprojroot.r-lib.org/reference/criteria.html