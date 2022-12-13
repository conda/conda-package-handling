# conda-package-handling
Create and extract conda packages of various formats

Full documentation at https://conda.github.io/conda-package-handling/

`conda` and `conda-build` use `conda_package_handling.api` to create and extract
conda packages. This package also provides the `cph` command line tool to
extract, create, and convert between formats.

## A new major version

As of version 2.x, `conda-package-handling` provides a backwards-compatible
wrapper around
[`conda-package-streaming`](https://conda.github.io/conda-package-streaming/), plus additional package creation functionality not found in `conda-package-streaming`, and `conda-package-handling` always expects to read and write to the filesystem. If you need a simpler API to extract, or inspect conda packages, check out `conda-package-streaming`.

Version 2.x is approximately two times faster extracting `.conda` packages, by extracting `.conda`'s embedded `.tar.zst` without first writing it to a temporary file. It uses [`python-zstandard`](https://github.com/indygreg/python-zstandard) and the Python standard library instead of a custom `libarchive` and so is easier to build.

Version 2.x creates `.conda` packages slightly differently as well.

* `.conda`'s `info-` archive comes after the `pkg-` archive.
* Inside `.conda`, the `info-` and `pkg-`'s ZIP metadata use a fixed timestamp, instead of the current time - can be seen with `python -m zipfile -l [filename].conda`.
* `.conda`'s embedded `.tar.zst` strip `uid`/`gid`/`username`/`groupname` instead of preserving these from the filesystem.
* Both `.conda` and `.tar.bz2` are created by Python's standard `zipfile` and `tarfile` instead of `libarchive`.

No particular attention has been paid to archiving time which will be dominated by the compression algorithm, but this also avoids using a temporary `.tar.zst`.

## Overview

There are two conda formats. The new conda format, described at [.conda file
format](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/packages.html?highlight=format#conda-file-format),
consists of an outer, uncompressed ZIP-format container, with 2 inner compressed
.tar files. It is designed to have much faster metadata access and utilize more
modern compression algorithms. The old conda format is a `.tar.bz2` archive.

The cph command line tool can transmute (convert) the old package format to the
new one, and vice versa.

```
cph transmute mkl-2018.0.3-1.tar.bz2 .conda
```

The new package format is an indexed, uncompressed zip file that contains two
Zstandard-compressed tarfiles. The info metadata about packages is separated
into its own tarfile from the rest of the package contents. By doing this, we
can extract only the metadata, for speeding up operations like indexing.

And, the Zstandard algorithm is much, much faster to decompress than bz2.

Package creation is primarily something that conda-build uses, as cph only
packages but does not create metadata that makes a conda package useful.

```
cph create /path/to/some/dir my-cute-archive.conda
```

This would not necessarily create a valid conda package, unless the directory
being archived contained all the metadata in an "info" directory that a standard
conda package needs. The .conda file it creates, however, uses all the nice new
compression formats, though, and you could use cph on some other computer to
extract it.

## Development

Install this package and its test dependencies; run tests.

```
pip install -e ".[test]"
pytest
```

## Releasing

Conda-package-handling releases may be performed via the `rever command
<https://regro.github.io/rever-docs/>`_. Rever is configured to perform the
activities for a typical conda-build release. To cut a release, simply run
``rever <X.Y.Z>`` where ``<X.Y.Z>`` is the release number that you want bump to.
For example, ``rever 1.2.3``.  However, it is always good idea to make sure that
the you have permissions everywhere to actually perform the release.  So it is
customary to run ``rever check`` before the release, just to make sure.  The
standard workflow is thus::

    rever check
    rever 1.2.3

If for some reason a release fails partway through, or you want to claw back a
release that you have made, rever allows you to undo activities. If you find
yourself in this pickle, you can pass the ``--undo`` option a comma-separated
list of activities you'd like to undo.  For example::

     rever --undo tag,changelog,authors 1.2.3

 Happy releasing!
