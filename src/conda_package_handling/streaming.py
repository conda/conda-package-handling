"""
Exception-compatible adapter from conda_package_streaming.
"""

from __future__ import annotations

import os
import os.path
from tarfile import TarError
from zipfile import BadZipFile

from conda_package_streaming.extract import exceptions as cps_exceptions
from conda_package_streaming.extract import extract_stream, package_streaming

from . import exceptions


def _extract(fn: str, dest_dir: str, components: list[str]):
    """
    Extract .conda or .tar.bz2 package to dest_dir.

    If it's a conda package, components may be ["pkg", "info"]

    If it's a .tar.bz2 package, components must equal ["pkg"]

    Internal. Skip directly to conda-package-streaming if you don't need
    exception compatibility.
    """
    file_name = os.path.basename(fn)

    if str(fn).endswith(".tar.bz2"):
        assert components == ["pkg"]

    try:
        with open(fn, "rb") as fileobj:
            for component in components:
                # will parse zipfile twice
                stream = package_streaming.stream_conda_component(
                    file_name, fileobj, component=component
                )
                extract_stream(stream, dest_dir)
    except cps_exceptions.CaseInsensitiveFileSystemError as e:
        raise exceptions.CaseInsensitiveFileSystemError(fn, dest_dir) from e
    except (IOError, TarError, BadZipFile) as e:
        raise exceptions.InvalidArchiveError(
            fn, "failed with error: {}".format(str(e))
        ) from e
