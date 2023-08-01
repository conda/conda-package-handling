# conda-package-handling

[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/conda/conda-package-handling/main.svg)](https://results.pre-commit.ci/latest/github/conda/conda-package-handling/main)

Create and extract conda packages of various formats.

`conda` and `conda-build` use `conda_package_handling.api` to create and extract
conda packages. This package also provides the `cph` command line tool to
extract, create, and convert between formats.

See also
[conda-package-streaming](https://conda.github.io/conda-package-streaming), an
efficient library to read from new and old format .conda and .tar.bz2 conda
packages.

Full documentation at [https://conda.github.io/conda-package-handling/](https://conda.github.io/conda-package-handling/)
