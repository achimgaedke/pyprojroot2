import pytest


def test_public_interface() -> None:
    # the most frequent use
    import pyprojroot2 as pyprojroot

    assert callable(pyprojroot.here)

    from pyprojroot2 import here

    assert callable(here)


def test_legacy_import() -> None:
    with pytest.warns(DeprecationWarning, match="legacy module"):
        from pyprojroot2.pyprojroot import here

    assert callable(here)
