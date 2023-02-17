## Reference documentation

More to come... Here some pointers:

* the "machinery" is in `criteria.py` and `root.py`,
* the files `predefined_criteria.py` and `predefined_roots.py` provide criteria definitions ported from `rprojroot` and `pyprojroot`
* the files `__init__.py`, `root.py` and `here.py` should contain the "public interface",

The main distinction is to be made between:

* Criterion: tests a given directory, provides a reason for a match and allows combining with `&` (and) and `|` (or). Concrete examples are: `HasDir(".git")`, `HasFile("setup.cfg")`, ...
* RootCriteria: tests a list of criteria and uses the first criterion returning a match on one of the parent directories, e.g. typical RootCriteria for a python data-science project or an R project.

So far, I've written and tested the "machinery". Now I have to write the documentation
to see how the public interface should look like.
