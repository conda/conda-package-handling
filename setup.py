import pathlib
import re

from setuptools import find_packages, setup

version = re.search(
    r'__version__\s+=\s+"(.*)"',
    pathlib.Path("src/conda_package_handling/__init__.py").read_text(),
)[1]

setup(
    name="conda-package-handling",
    version=version,
    description="Create and extract conda packages of various formats",
    author="Anaconda, Inc.",
    author_email="conda@anaconda.com",
    url="https://github.com/conda/conda-package-handling",
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    entry_points={"console_scripts": ["cph=conda_package_handling.cli:main"]},
    keywords="conda-package-handling",
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires=">=3.7",
    install_requires=["conda-package-streaming >= 0.4.0", "tqdm"],
    extras_require={"docs": ["furo", "sphinx", "myst-parser", "mdit-py-plugins>=0.3.0"]},
)
