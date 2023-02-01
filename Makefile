.PHONY: deploy
deploy:
	rm -f dist/*
	python -m build
	python -m twine upload dist/*

.PHONY: lint
lint:
	python -m mypy src/pyprojroot2
	python -m flake8 src/pyprojroot2 tests
	python -m black --check --diff src/pyprojroot2 tests

.PHONY: fmt
fmt:
	python -m black src/pyprojroot2 tests

.PHONY: test
test:
	PYTHONPATH="src" python -m pytest
