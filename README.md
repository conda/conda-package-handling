# conda-package-handling
Create and extract conda packages of various formats

```
usage: cph [-h] [-V] {extract,x,create,c,transmute,t} ...

options:
  -h, --help            show this help message and exit
  -V, --version         Show the conda-package-handling version number and
                        exit.

subcommands:
  {extract,x,create,c,transmute,t}
    extract (x)         extract package contents
    create (c)          bundle files into a package
    transmute (t)       convert from one package type to another

```

Full documentation at https://conda.github.io/conda-package-handling/

cph is an abstraction of conda package handling and a tool for extracting,
creating, and converting between formats.

There are two conda formats. The new conda format, described at [.conda file
format](https://docs.conda.io/projects/conda/en/latest/user-guide/concepts/packages.html?highlight=format#conda-file-format),
consists of an outer, uncompressed ZIP-format container, with 2 inner compressed
.tar files. It is designed to have much faster metadata access and utilize more
modern compression algorithms. The old conda format is a `.tar.bz2` archive.

One can transmute (convert) the old package format to the new one with cph:

```
cph transmute mkl-2018.0.3-1.tar.bz2 .conda
```

One can then test the speed of extracting the old file and the new one:

```
$ time cph extract mkl-2018.0.3-1.tar.bz2 --dest mkl-a
cph extract mkl-2018.0.3-1.tar.bz2 --dest mkl-a  18.16s user 0.59s system 98% cpu 19.015 total
$ time cph extract mkl-2018.0.3-1.conda --dest mkl-b
cph extract mkl-2018.0.3-1.conda --dest mkl-b  1.41s user 0.65s system 87% cpu 2.365 total
```

The new package format is an indexed, uncompressed zip file that contains two
Zstandard compressed tarfiles. The info metadata about packages is separated
into its own tarfile from the rest of the package contents. By doing this, we
can extract only the metadata, for speeding up operations like indexing.

```
$ time cph extract mkl-2018.0.3-1.conda --dest mkl-b --info
cph extract mkl-2018.0.3-1.conda --dest mkl-b --info  0.21s user 0.07s system 98% cpu 0.284 total```
```

Package creation is primarily something that conda-build uses, as cph does
absolutely nothing to create metadata that makes a conda package useful.
However, you may consider it useful to abuse cph's package creation as a way of
utilizing newer compression formats.

```
cph create /path/to/some/dir my-cute-archive.conda
```

Again, this would not necessarily create a valid conda package, unless the
directory being archived contained all the metadata in an "info" directory that
a standard conda package needs. The .conda file it creates, however, uses all
the nice new compression formats, though, and you could use cph on some other
computer to extract it.

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
