# To do stuff with make, you type `make` in a directory that has a file called
# "Makefile". You can also type `make -f <makefile>` to use a different filename.
#
# A Makefile is a collection of rules. Each rule is a recipe to do a specific
# thing, sort of like a grunt task or an npm package.json script.
#
# A rule looks like this:
#
# <target>: <prerequisites...>
# 	<commands>
#
# The "target" is required. The prerequisites are optional, and the commands
# are also optional, but you have to have one or the other.
#
# Type `make` to show the available targets and a description of each.
#
.DEFAULT_GOAL := help
.PHONY: help
help:  ## Display this help
	@awk 'BEGIN {FS = ":.*##"; printf "\nUsage:\n  make \033[36m<target>\033[0m\n"} /^[a-zA-Z_-]+:.*?##/ { printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2 } /^##@/ { printf "\n\033[1m%s\033[0m\n", substr($$0, 5) } ' $(MAKEFILE_LIST)

##@ Testing

.PHONY: unit-tests
unit-tests: ## run unit-tests with pytest
	@pytest --doctest-modules

.PHONY: unit-tests-cov
unit-tests-cov: ## run unit-tests with pytest and show coverage (terminal + html)
	@pytest --doctest-modules --cov=src --cov-report term-missing --cov-report=html

.PHONY: unit-tests-cov-fail
unit-tests-cov-fail: ## run unit tests with pytest and show coverage (terminal + html) & fail if coverage too low & create files for CI
	@pytest --doctest-modules --cov=src --cov-report term-missing --cov-report=html --cov-fail-under=80 --junitxml=pytest.xml | tee pytest-coverage.txt

##@ Formatting

.PHONY: format
format: ## ruff (code formatter)
	@ruff --fix .

##@ Linting
.PHONY: lint-ruff
lint-ruff: ## black in linting mode
	@ruff check .

.PHONY: lint-mypy
lint-mypy: ## mypy (static-type checker)
	@mypy --config-file pyproject.toml .

.PHONY: lint-mypy-report
lint-mypy-report: ## run mypy & create report
	@mypy --config-file pyproject.toml . --html-report ./mypy_html

lint: lint-ruff lint-mypy ## run all linters

##@ Documentation

docs-build: ## build documentation locally
	@mkdocs build

##@ Clean-up

clean-cov: ## remove output files from pytest & coverage
	@rm -rf .coverage
	@rm -rf htmlcov
	@rm -rf pytest.xml
	@rm -rf pytest-coverage.txt
	@rm -rf dist

clean-docs: ## remove output files from mkdocs
	@rm -rf site

clean: clean-cov clean-docs ## run all clean commands
