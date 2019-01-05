# conda-package-handling
Create and extract conda packages of various formats

```
usage: cph [-h] {extract,x,create,c,transmute,t} ...

optional arguments:
  -h, --help            show this help message and exit

subcommands:
  {extract,x,create,c,transmute,t}
    extract (x)         extract package contents
    create (c)          bundle files into a package
    transmute (t)       convert from one package type to another
```

cph is an abstraction of conda package handling and a tool for extracting,
creating, and converting between formats.

At the time of writing, the standard conda package format is a .tar.bz2 file.
That will need to be maintained for quite a long time, thanks to the long tail
of people using old conda versions. There is a new conda format, described at
https://docs.google.com/document/d/1HGKsbg_j69rKXPihhpCb1kNQSE8Iy3yOsUU2x68x8uw/edit?usp=sharing.
This new format is designed to have much faster metadata access and utilize more
modern compression algorithms, while also facilitating package signing without
adding sidecar files.

For example, one can transmute (convert) the old package format to the new one with cph:

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

The new package format is an indexed, uncompressed zip file that contains
tarfiles that can use any compression supported by libarchive. The info metadata
about packages is separated into its own tarfile from the rest of the package
contents. By doing this, we can extract only the metadata, for speeding up
operations like indexing.

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
