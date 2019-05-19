from setuptools import setup
import versioneer
import sys

requirements = [
    # package requirements go here
    "six",
    # "python-libarchive-c"
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
    packages=['conda_package_handling'],
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
    ]
)
