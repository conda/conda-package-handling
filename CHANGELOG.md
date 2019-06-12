# current developments
2019-06-12 1.3.7:
------------------

Bug fixes:
----------

* Don't print message for every skipped file that already exists.  Don't even look at files that match the target conversion pattern.

Contributors:
-------------

* @msarahan


2019-06-12 1.3.6:
------------------

Contributors:
-------------



2019-06-12 1.3.5:
------------------

Bug fixes:
----------

* fix recursion issue with TemporaryDirectory

Contributors:
-------------

* @msarahan


2019-06-11 1.3.4:
------------------

Bug fixes:
----------

* fix setup.cfg path issue with versioneer
* try copying temporary artifact to final location instead of moving it, in hopes of avoiding permission errors

Contributors:
-------------

* @msarahan


2019-06-11 1.3.3:
------------------

Bug fixes:
----------

* add .gitattributes file to fix versioneer not working

Contributors:
-------------

* @msarahan


2019-06-11 1.3.2:
------------------

Bug fixes:
----------

* port rm_rf functionality from conda, to better handle permissions errors being observed on Azure and Appveyor windows hosts (but not on local machines)

Contributors:
-------------

* @msarahan


2019-06-11 1.3.1:
------------------

Bug fixes:
----------

* try to wrap tempdir cleanup so that it never exits violently.  Add warning message.

Contributors:
-------------

* @msarahan


2019-06-10 1.3.0:
------------------

Enhancements:
-------------

* add a cph-specific exception, so that downstream consumers of cph don't have to handle libarchive exceptions

Contributors:
-------------

* @msarahan


2019-06-08 1.2.0:
------------------

Enhancements:
-------------

* add get_default_extracted_folder api function that returns the folder location where a file would be extracted to by default (no dest folder specified) 
* add --processes flag to cph t, to limit number of processes spawned.  Defaults to number of CPUs if not set.

Contributors:
-------------

* @msarahan


2019-05-21 1.1.5:
------------------

Bug fixes:
----------

* generate symlink tests rather than including file layout, to avoid issues on win

Contributors:
-------------

* @msarahan


2019-05-21 1.1.4:
------------------

Enhancements:
-------------

* moved conda_package_handling into src (src layout)

Contributors:
-------------

* @msarahan


2019-05-20 1.1.3:
------------------

Bug fixes:
----------

* improve tests of symlink and other file contents

Contributors:
-------------

* @msarahan


2019-05-20 1.1.2:
------------------

Bug fixes:
----------

* fix creation dropping symlinks and things that are not otherwise "files"

Contributors:
-------------

* @msarahan


2019-05-14 1.1.1:
------------------

Bug fixes:
----------

* fix path join bug, where an absolute path for out_fn was causing file writing problems

Contributors:
-------------

* @msarahan


2019-05-10 1.1.0:
------------------

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
------------------

Enhancements:
-------------

* new api-only function, ``get_pkg_details`` that returns package size and checksum info in dictionary form
* add version info output to the CLI

Contributors:
-------------

* @msarahan


2019-02-04 1.0.3:
------------------

Bug fixes:
----------

* fix support for python 2.7

Contributors:
-------------

* @msarahan


2019-02-04 1.0.2:
------------------

Contributors:
-------------

* @msarahan


2019-02-04 1.0.1:
------------------

Contributors:
-------------




## 1.0.0

Initial release
