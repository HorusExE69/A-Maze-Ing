NORM = flake8
TYPE_CHECK = mypy
TC_FLAGS = --warn-return-any --warn-unused-ignores --ignore-missing-imports --disallow-untyped-defs --check-untyped-defs
SCRIPT = a_maze_ing.py
DEFAULT_CONFIG = config.txt

install:
	pip3 install -r requirements.txt

run:
	@python3 $(SCRIPT) $(DEFAULT_CONFIG)

debug:
	python3 -m pdb $(SCRIPT) $(DEFAULT_CONFIG)

clean:
	@find . -type d \( -name "__pycache__" -o -name ".mypy_cache" -o -name ".pytest_cache" \) -prune -exec rm -rf {} +
	@find . -type f -name "*.pyc" -delete

f8:
	$(NORM) .

lint: f8
	$(TYPE_CHECK) . $(TC_FLAGS)

lint-strict: f8
	$(TYPE_CHECK) . --strict

.PHONY: install run debug clean lint lint-strict
