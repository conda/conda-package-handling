# current developments
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
