# Contribution guide
This guide provides rules and examples for writing clean and consistent Python code. Following these guidelines 
will help ensure code readability, maintainability, and collaboration within a development team.

## Code Style & Naming Convention
To ensure seemless development in which developer does not need to worry about remembering all of the 
convention several linters and formatter has been implemented inside Makefile.

```py hl_lines="10-21"
Usage:
  make <target>
  help                  Display this help

Testing
  unit-tests            run unit-tests with pytest
  unit-tests-cov        run unit-tests with pytest and show coverage (terminal + html)
  unit-tests-cov-fail   run unit tests with pytest and show coverage (terminal + html) & fail if coverage too low & create files for CI

Formatting
  format-black          black (code formatter)
  format-isort          isort (import formatter)
  format                run all formatters

Linting
  lint-black            black in linting mode
  lint-isort            isort in linting mode
  lint-pylint           pylint (linter)
  lint-mypy             mypy (static-type checker)
  lint-mypy-report      run mypy & create report
  lint                  run all linters

Documentation
  docs-build            build documentation locally

Clean-up
  clean-cov             remove output files from pytest & coverage
  clean-docs            remove output files from mkdocs
  clean                 run all clean commands
```

In order to make the full use of the implemented formatters and linters simply use ```make format``` followed by 
```make lint```  in the root folder of the repository!

Please note that **pre-commit has been configured** to run before each commit. When pre-commit implements the same logic
as ```make format``` and  results in changing the code. If there are any changes made commit will be rejected, but 
changes will be applied. In such case, you have to commit twice - first to apply changes and secondly to commit the 
files. In case there are no changes made single commit works as expected.

## Code Organization
Well-organized code is easier to navigate and understand. Consider the following guidelines:

* Separate different concerns into modules, classes, and functions.
* Keep each function or method focused on a single task.
* Group related functions or methods within classes or modules.
* Use meaningful file and directory names to reflect the purpose of the code.

## Branching Strategy
Adopting a consistent branching strategy promotes collaboration and code isolation. Follow the structure 
```feature/{task_id}-{task_name}``` for each new task branch. For example:

```feature/123-add-user-authentication```

This structure allows for easy identification of the task and ensures a clear separation of code changes.
Furthermore there are several important things to remeber:

* main branch should be reserved for a production-ready version of the code
* develop branch should contain latest stable version
* each merge request should be performed with squash and deletion of the source branch

## Docstring Format
Writing clear and concise docstrings helps others understand your code's purpose and usage. Follow the Google Style 
Python Docstrings format, which includes sections for the summary, parameters, return values, and more. 
Here's an example:
```py 
def calculate_sum(a, b):
    """Calculate the sum of two numbers.

    Args:
        a (int): The first number.
        b (int): The second number.

    Returns:
        int: The sum of the two numbers.
    """
    return a + b
```

Using a consistent docstring format improves code documentation and helps generate accurate API documentation automatically.
