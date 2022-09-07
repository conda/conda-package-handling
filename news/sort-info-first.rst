Enhancements:
-------------

* Support setting the zstd compression level on the cli. (#114)

Bug fixes:
----------

* Include tested fix for "``info/`` sorts first in ``.tar.bz2``" feature, useful
  for streaming ``.tar.bz2``. (#102)
* Fix extracting ``.conda`` given as relative path. (#116)
* Gracefully handle missing subcommands. (#105)