[//]: # (current developments)

## 2.3.0 (2024-06-05)

### Enhancements

* Add `cph list` to report artifact contents without prior extraction. (#236)
* Added formal support for Python 3.10, 3.11, and 3.12. (#231)

### Bug fixes

* Delay ``os.getcwd()`` call to body of ``CondaFormat_v2.create()`` when
  ``out_folder`` is not passed. (#205)

### Deprecations

* Removed formal support for Python 3.7. (#231)

### Other

* Remove MANIFEST.in, used for Python sdists, which referenced
  non-existent files. Source distributions appear correct without
  MANIFEST.in. (#163)
* Add explicit `zstandard` dependency. ([#222](https://github.com/conda/conda-package-handling/issues/222))

### Contributors

* @conda-bot
* @dholth
* @callek
* @jaimergp
* @pre-commit-ci[bot]



## 2.2.0 (2023-07-28)

### Bug fixes

* Respect umask when unpacking packages, by requiring `conda-package-streaming >= 0.9.0`.

### Docs

* Include README.md in pypi metadata. (#215)

### Contributors

* @conda-bot
* @dbast
* @dholth
* @pre-commit-ci[bot]



## 2.1.0 (2023-05-04)

### Bug fixes

* Include decompressed size when creating `.conda` archives with
  `CondaFormat_v2.create()`, to reduce memory usage on decompression. (#171)
  Transmuted archives (converted from `.tar.bz2`) do not contain the
  decompressed size.
* Include LICENSE, not just LICENSE.txt in info/ section (#172)

### Contributors

* @conda-bot
* @dbast
* @dholth
* @pre-commit-ci[bot]



## 2.0.2 (2022-12-01)

### Bug fixes

* Reduce memory usage when creating `.conda`. Allocate only one zstd comperssor
  when creating `.conda`. Lower default compression level to 19 from 22.
  (#168)

### Contributors

* @dholth



## 2.0.1 (2022-11-18)

### Bug fixes

* Require conda-package-streaming 0.7.0 for Windows c:\ vs C:\ check, pypy
  support

### Contributors

* @dholth



## 2.0.0 (2022-11-17)

### Enhancements

* Remove progress bars.
* Based on conda-package-streaming instead of libarchive.
* Requires the `python-zstandard` (`zstandard`) library.
* Threadsafe `extract()` function.
* More efficient `.conda` handling.

### Deprecations

* Remove broken `verify` subcommand.
* Remove support for `binsort` (was supposed to help with `tar.bz2`
  compression). (Use `.conda` instead.)

### Docs

* Add sphinx documentation.

### Other

* Reformat entire codebase with `black`, `isort`. (#132)

### Contributors

* @conda-bot
* @dholth
* @jezdez
* @kenodegard
* @mariusvniekerk



## 1.9.0 (2022-09-06)

### Enhancements

* Support setting the zstd compression level on the cli. (#114)

### Bug fixes

* Include tested fix for "``info/`` sorts first in ``.tar.bz2``" feature, useful
  for streaming ``.tar.bz2``. (#102)
* Fix extracting ``.conda`` given as relative path. (#116)
* Gracefully handle missing subcommands. (#105)

### Contributors

* @conda-bot
* @jezdez
* @dholth
* @kenodegard made their first contribution in #112
* @mariusvniekerk made their first contribution in #114

## 1.8.1 (2022-04-01)

### Bug fixes

* Don't drop empty directories that happen to be prefixes of something else (#99)

### Contributors

* @tobijk
* @conda-bot
* @chenghlee

## 1.8.0 (2022-03-12)

### Enhancements

* Compute package hashes in threads. (#83)

### Bug fixes

* Fix running from a read-only working directory (#44)
* Fix symlinks to directories being incorrectly placed in the ``info`` tarball
  when transmuting ``.tar.bz2``- to ``.conda``-format packages (#84)
* No longer generate emtpy metadata.json in v2 packages (#88)
* Fix for TypeError in tarball.py. (#86)

### Deprecations

* Remove Python 2 support.

### Other

* Added project board, issue staleness, thread locking and label automation
  using GitHub action workflows to improve maintenance of GitHub project.

  More information can be found in the infra repo: https://github.com/conda/infra

* Removed unused continuous integration platform config files.

### Contributors

* @dholth
* @conda-bot
* @chenghlee
* @analog-cbarber
* @chrisburr
* @vz-x
* @jezdez


## 1.7.3 (2021-04-12)

### Enhancements

* Python tar extraction now used as a fallback if libarchive fails

### Bug fixes

* Fix binsort's mangling of symlinks
* Fix #71, larger directories fail to extract using libarchive
* When testing that exceptions are raised or archives containing abs paths, first check that such a "broken" archive was created during test setup... otherwise skip the test.
* api.create now raises an error correctly if archive creation failed or extension is not supported.
* Travis CI issue now resolved, mock added as dependency for conda test environments and system dependencies
* Fixed bug where extract parser cli failed due to not having ``out_folder`` attribute.

### Contributors

* @mingwandroid
* @leej3
* @beckermr
* @seemethere



## 1.7.2 (2020-10-16)

### Enhancements

* add --force to transmute

### Bug fixes

* Do not report symlinks as missing files
* Fixes for --process and --out-folder  #68
* --out-folder: Normalise, expand user-ify and ensure it ends with os.sep

### Contributors

* @mingwandroid
* @nehaljwani

## 1.6.0 (2019-09-20)

### Enhancements

* add a "prefix" keyword argument to the api.extract function.  When combined with dest_dir, the prefix is the base directory, and the dest_dir is the folder name.  dest_dir alone as an abspath is both the base directory and the folder name.

### Bug fixes

* provide a non-ProcessPoolExecutor path when number of processes is 1
* open files to be added to archives in binary mode.  On Windows, the implicit default was text mode, which was corrupting newline data and putting in null characters.
* extraction prefix defaults to the folder containing the specified archive.  This is a behavior change from 1.3.x, which extracted into the CWD by default.

### Contributors

* @msarahan
* @jjhelmus


## 1.5.0 (2019-08-31)

### Contributors

* @msarahan
* @jjhelmus


## 1.4.1 (2019-08-04)

### Enhancements

* several small error fixes from bad copypasta

### Contributors

* @msarahan


## 1.4.0 (2019-08-02)

### Bug fixes

* provide fallback to built-in tarfile if libarchive fails to import.  Won't support new .conda format (obviously)
* tmpdir created in output folder (defaults to cwd, but not always cwd)

### Contributors

* @msarahan


## 1.3.11 (2019-07-11)

### Bug fixes

* fix BadZipFile exception handling on py27

### Contributors

* @msarahan


## 1.3.10 (2019-06-24)

### Contributors

* @msarahan


## 1.3.9 (2019-06-14)

### Bug fixes

* put temporary files in CWD/.cph_tmp(random) instead of default temp dir.  Hope that this fixes the permission problems seen on appveyor and azure.

### Contributors

* @msarahan


## 1.3.8 (2019-06-13)

### Bug fixes

* Write output files to output path directly, rather than any temporary.  Hope that this fixes permission errors on appveyor/azure

### Contributors

* @msarahan


## 1.3.7 (2019-06-12)

### Bug fixes

* Don't print message for every skipped file that already exists.  Don't even look at files that match the target conversion pattern.

### Contributors

* @msarahan


## 1.3.6 (2019-06-12)

### Contributors



## 1.3.5 (2019-06-12)

### Bug fixes

* fix recursion issue with TemporaryDirectory

### Contributors

* @msarahan


## 1.3.4 (2019-06-11)

### Bug fixes

* fix setup.cfg path issue with versioneer
* try copying temporary artifact to final location instead of moving it, in hopes of avoiding permission errors

### Contributors

* @msarahan


## 1.3.3 (2019-06-11)

### Bug fixes

* add .gitattributes file to fix versioneer not working

### Contributors

* @msarahan


## 1.3.2 (2019-06-11)

### Bug fixes

* port rm_rf functionality from conda, to better handle permissions errors being observed on Azure and Appveyor windows hosts (but not on local machines)

### Contributors

* @msarahan


## 1.3.1 (2019-06-11)

### Bug fixes

* try to wrap tempdir cleanup so that it never exits violently.  Add warning message.

### Contributors

* @msarahan


## 1.3.0 (2019-06-10)

### Enhancements

* add a cph-specific exception, so that downstream consumers of cph don't have to handle libarchive exceptions

### Contributors

* @msarahan


## 1.2.0 (2019-06-08)

### Enhancements

* add get_default_extracted_folder api function that returns the folder location where a file would be extracted to by default (no dest folder specified)
* add --processes flag to cph t, to limit number of processes spawned.  Defaults to number of CPUs if not set.

### Contributors

* @msarahan


## 1.1.5 (2019-05-21)

### Bug fixes

* generate symlink tests rather than including file layout, to avoid issues on win

### Contributors

* @msarahan


## 1.1.4 (2019-05-21)

### Enhancements

* moved conda_package_handling into src (src layout)

### Contributors

* @msarahan


## 1.1.3 (2019-05-20)

### Bug fixes

* improve tests of symlink and other file contents

### Contributors

* @msarahan


## 1.1.2 (2019-05-20)

### Bug fixes

* fix creation dropping symlinks and things that are not otherwise "files"

### Contributors

* @msarahan


## 1.1.1 (2019-05-14)

### Bug fixes

* fix path join bug, where an absolute path for out_fn was causing file writing problems

### Contributors

* @msarahan


## 1.1.0 (2019-05-10)

### Bug fixes

* simplify .conda package info, to work with conda/conda#8639 and conda/conda-build#3500
* add missing six dep
* fix reference in cli.py to incorrect API function (how was this working?)
* Wrap calls to shutil.move in try, because of windows permission errors observed on Appveyor

### Contributors

* @msarahan
* @nehaljwani


## 1.0.4 (2019-02-13)

### Enhancements

* new api-only function, ``get_pkg_details`` that returns package size and checksum info in dictionary form
* add version info output to the CLI

### Contributors

* @msarahan


## 1.0.3 (2019-02-04)

### Bug fixes

* fix support for python 2.7

### Contributors

* @msarahan


## 1.0.2 (2019-02-04)

### Contributors

* @msarahan


## 1.0.1 (2019-02-04)

### Contributors
