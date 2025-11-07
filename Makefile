install:
	poetry install

project:
	poetry run python main.py

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl

lint:
	poetry run ruff check .

format:
	poetry run ruff format .

test:
	poetry run python -m pytest tests/ -v

clean:
	rm -rf dist/ build/ *.egg-info/ .ruff_cache/ __pycache__/ valutatrade_hub/__pycache__/ valutatrade_hub/*/__pycache__/
	