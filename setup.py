import importlib.util
import pathlib

from setuptools import find_packages, setup

spec = importlib.util.spec_from_file_location(
    "conda_package_handling", pathlib.Path("src/conda_package_handling/__init__.py")
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
version = module.__version__

setup(
    name="conda-package-handling",
    version=version,
    description="Create and extract conda packages of various formats.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Anaconda, Inc.",
    author_email="conda@anaconda.com",
    url="https://github.com/conda/conda-package-handling",
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["cph=conda_package_handling.cli:main"]},
    keywords="conda-package-handling",
    classifiers=["Programming Language :: Python :: 3"],
    python_requires=">=3.8",
    install_requires=["conda-package-streaming >= 0.9.0"],
    extras_require={
        "docs": [
            "furo",
            "sphinx",
            "sphinx-argparse",
            "myst-parser",
            "mdit-py-plugins>=0.3.0",
        ],
        "test": ["mock", "pytest", "pytest-cov", "pytest-mock"],
    },
)
