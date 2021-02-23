Enhancements:
-------------

* Python tar extraction now used as a fallback if libarchive fails

Bug fixes:
----------

* Fix #71, larger directories fail to extract using libarchive
* When testing that exceptions are raised or archives containing abs paths, first check that such a "broken" archive was created during test setup... otherwise skip the test.
* api.create now raises an error correctly if archive creation failed or extension is not supported.
* Travis CI issue now resolved (pytest from outside conda env was being used)

Deprecations:
-------------

* <news item>

Docs:
-----

* <news item>

Other:
------

* <news item>

