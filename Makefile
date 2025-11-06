install:
	poetry install

project:
	poetry run python -c "from wallet import main; main()"

build:
	poetry build

publish:
	poetry publish --dry-run

package-install:
	python3 -m pip install dist/*.whl

lint:
	poetry run ruff check .