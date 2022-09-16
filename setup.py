from setuptools import setup, find_packages
import versioneer


setup(
    name="conda-package-handling",
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
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
    install_requires=["conda-package-streaming >= 0.4.0"],
)
