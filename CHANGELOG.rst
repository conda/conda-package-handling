.. current developments

2022-04-01 1.8.1:
==================

Bug fixes:
----------

* Don't drop empty directories that happen to be prefixes of something else (#99)

Contributors:
-------------

* @tobijk
* @conda-bot
* @chenghlee

2022-03-12 1.8.0:
==================

Enhancements:
-------------

* Compute package hashes in threads. (#83)

Bug fixes:
----------

* Fix running from a read-only working directory (#44)
* Fix symlinks to directories being incorrectly placed in the ``info`` tarball
  when transmuting ``.tar.bz2``- to ``.conda``-format packages (#84)
* No longer generate emtpy metadata.json in v2 packages (#88)
* Fix for TypeError in tarball.py. (#86)

Deprecations:
-------------

* Remove Python 2 support.

Other:
------

* Added project board, issue staleness, thread locking and label automation
  using GitHub action workflows to improve maintenance of GitHub project.

  More information can be found in the infra repo: https://github.com/conda/infra

* Removed unused continuous integration platform config files.

Contributors:
-------------

* @dholth
* @conda-bot
* @chenghlee
* @analog-cbarber
* @chrisburr
* @vz-x
* @jezdez


2021-04-12 1.7.3:
==================

Enhancements:
-------------

* Python tar extraction now used as a fallback if libarchive fails

Bug fixes:
----------

* Fix binsort's mangling of symlinks
* Fix #71, larger directories fail to extract using libarchive
* When testing that exceptions are raised or archives containing abs paths, first check that such a "broken" archive was created during test setup... otherwise skip the test.
* api.create now raises an error correctly if archive creation failed or extension is not supported.
* Travis CI issue now resolved, mock added as dependency for conda test environments and system dependencies
* Fixed bug where extract parser cli failed due to not having ``out_folder`` attribute.

Contributors:
-------------

* @mingwandroid
* @leej3
* @beckermr
* @seemethere



2020-10-16 1.7.2:
==================

Enhancements:
-------------

* add --force to transmute

Bug fixes:
----------

* Do not report symlinks as missing files
* Fixes for --process and --out-folder  #68
* --out-folder: Normalise, expand user-ify and ensure it ends with os.sep

Contributors:
-------------

* @mingwandroid
* @nehaljwani

2019-09-20 1.6.0:
==================

Enhancements:
-------------

* add a "prefix" keyword argument to the api.extract function.  When combined with dest_dir, the prefix is the base directory, and the dest_dir is the folder name.  dest_dir alone as an abspath is both the base directory and the folder name.

Bug fixes:
----------

* provide a non-ProcessPoolExecutor path when number of processes is 1
* open files to be added to archives in binary mode.  On Windows, the implicit default was text mode, which was corrupting newline data and putting in null characters.
* extraction prefix defaults to the folder containing the specified archive.  This is a behavior change from 1.3.x, which extracted into the CWD by default.

Contributors:
-------------

* @msarahan
* @jjhelmus


2019-08-31 1.5.0:
==================

Contributors:
-------------

* @msarahan
* @jjhelmus


2019-08-04 1.4.1:
==================

Enhancements:
-------------

* several small error fixes from bad copypasta

Contributors:
-------------

* @msarahan


2019-08-02 1.4.0:
==================

Bug fixes:
----------

* provide fallback to built-in tarfile if libarchive fails to import.  Won't support new .conda format (obviously)
* tmpdir created in output folder (defaults to cwd, but not always cwd)

Contributors:
-------------

* @msarahan


2019-07-11 1.3.11:
==================

Bug fixes:
----------

* fix BadZipFile exception handling on py27

Contributors:
-------------

* @msarahan


2019-06-24 1.3.10:
==================

Contributors:
-------------

* @msarahan


2019-06-14 1.3.9:
==================

Bug fixes:
----------

* put temporary files in CWD/.cph_tmp(random) instead of default temp dir.  Hope that this fixes the permission problems seen on appveyor and azure.

Contributors:
-------------

* @msarahan


2019-06-13 1.3.8:
==================

Bug fixes:
----------

* Write output files to output path directly, rather than any temporary.  Hope that this fixes permission errors on appveyor/azure

Contributors:
-------------

* @msarahan


2019-06-12 1.3.7:
==================

Bug fixes:
----------

* Don't print message for every skipped file that already exists.  Don't even look at files that match the target conversion pattern.

Contributors:
-------------

* @msarahan


2019-06-12 1.3.6:
==================

Contributors:
-------------



2019-06-12 1.3.5:
==================

Bug fixes:
----------

* fix recursion issue with TemporaryDirectory

Contributors:
-------------

* @msarahan


2019-06-11 1.3.4:
==================

Bug fixes:
----------

* fix setup.cfg path issue with versioneer
* try copying temporary artifact to final location instead of moving it, in hopes of avoiding permission errors

Contributors:
-------------

* @msarahan


2019-06-11 1.3.3:
==================

Bug fixes:
----------

* add .gitattributes file to fix versioneer not working

Contributors:
-------------

* @msarahan


2019-06-11 1.3.2:
==================

Bug fixes:
----------

* port rm_rf functionality from conda, to better handle permissions errors being observed on Azure and Appveyor windows hosts (but not on local machines)

Contributors:
-------------

* @msarahan


2019-06-11 1.3.1:
==================

Bug fixes:
----------

* try to wrap tempdir cleanup so that it never exits violently.  Add warning message.

Contributors:
-------------

* @msarahan


2019-06-10 1.3.0:
==================

Enhancements:
-------------

* add a cph-specific exception, so that downstream consumers of cph don't have to handle libarchive exceptions

Contributors:
-------------

* @msarahan


2019-06-08 1.2.0:
==================

Enhancements:
-------------

* add get_default_extracted_folder api function that returns the folder location where a file would be extracted to by default (no dest folder specified) 
* add --processes flag to cph t, to limit number of processes spawned.  Defaults to number of CPUs if not set.

Contributors:
-------------

* @msarahan


2019-05-21 1.1.5:
==================

Bug fixes:
----------

* generate symlink tests rather than including file layout, to avoid issues on win

Contributors:
-------------

* @msarahan


2019-05-21 1.1.4:
==================

Enhancements:
-------------

* moved conda_package_handling into src (src layout)

Contributors:
-------------

* @msarahan


2019-05-20 1.1.3:
==================

Bug fixes:
----------

* improve tests of symlink and other file contents

Contributors:
-------------

* @msarahan


2019-05-20 1.1.2:
==================

Bug fixes:
----------

* fix creation dropping symlinks and things that are not otherwise "files"

Contributors:
-------------

* @msarahan


2019-05-14 1.1.1:
==================

Bug fixes:
----------

* fix path join bug, where an absolute path for out_fn was causing file writing problems

Contributors:
-------------

* @msarahan


2019-05-10 1.1.0:
==================

Bug fixes:
----------

* simplify .conda package info, to work with conda/conda#8639 and conda/conda-build#3500
* add missing six dep
* fix reference in cli.py to incorrect API function (how was this working?)
* Wrap calls to shutil.move in try, because of windows permission errors observed on Appveyor

Contributors:
-------------

* @msarahan
* @nehaljwani


2019-02-13 1.0.4:
==================

Enhancements:
-------------

* new api-only function, ``get_pkg_details`` that returns package size and checksum info in dictionary form
* add version info output to the CLI

Contributors:
-------------

* @msarahan


2019-02-04 1.0.3:
==================

Bug fixes:
----------

* fix support for python 2.7

Contributors:
-------------

* @msarahan


2019-02-04 1.0.2:
==================

Contributors:
-------------

* @msarahan


2019-02-04 1.0.1:
==================

Contributors:
-------------
