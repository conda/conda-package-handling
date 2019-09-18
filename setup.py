from setuptools import setup, find_packages
import versioneer
import sys

from setuptools.extension import Extension
from Cython.Build import cythonize

_libraries = ["archive_and_deps"]
if sys.platform == 'win32':
    _libraries.append('advapi32')
    _libraries.append('user32')
    _libraries.append('kernel32')
archive_utils_cy_extension = Extension(
    name="conda_package_handling.archive_utils_cy",
    sources=["src/conda_package_handling/archive_utils_cy.pyx"],
    libraries=_libraries,
)

requirements = [
    # package requirements go here
    "six",
]
if sys.version_info.major == 2:
    requirements.append('futures')

setup(
    name='conda-package-handling',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description="Create and extract conda packages of various formats",
    author="Anaconda, Inc.",
    author_email='conda@anaconda.com',
    url='https://github.com/conda/conda-package-handling',
    ext_modules=cythonize([archive_utils_cy_extension]),
    packages=find_packages("src", exclude=["tests"]),
    package_dir={"": "src"},
    entry_points={
        'console_scripts': [
            'cph=conda_package_handling.cli:main'
        ]
    },
    install_requires=requirements,
    keywords='conda-package-handling',
    classifiers=[
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)
