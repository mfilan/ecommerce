# User guide
This guide provides rules and examples on how to get started with Cytops!

## Setting up project

Some of the libraries used do not support newer versions of python. Therefore, one have to create
virtual environment with specified version of python. There are several ways to do this, e.g. using conda:

```conda create --name ecommerce python=3.10.13```

Having created the environment we have to active it:

```conda activate ecommerce```

Subsequently one have to install poetry:

```conda install -c conda-forge poetry==1.5.1```

Last step is to install libraries using poetry:

```poetry install```

Do not forget about setting up pre-commit :)

```pre-commit install```


## Adding new packages

Adding new packages is as simple as ```poetry add {package_name}```. However, poetry introduces nice feature called 
[dependecy groups](https://python-poetry.org/docs/master/managing-dependencies/). In order to add packages as a part 
of a group, all you need to do is ```poetry add --group {group_name} {package_name}```.
