"""
Test conda-package-handling can work in `.tar.bz2`-only mode if zstandard is not
available. (Giving the user a chance to immediately install zstandard.)
"""

import importlib
import sys


def test_degraded():
    try:
        sys.modules["zstandard"] = None  # type: ignore
        sys.modules["conda_package_handling.conda_fmt"] = None  # type: ignore

        # this is only testing conda_package_handling's code, and does not test
        # that conda_package_streaming works without zstandard.

        import conda_package_handling.api

        importlib.reload(conda_package_handling.api)

        assert conda_package_handling.api.libarchive_enabled == False

    finally:
        sys.modules.pop("zstandard", None)
        sys.modules.pop("conda_package_handling.conda_fmt", None)
        import conda_package_handling.api

        importlib.reload(conda_package_handling.api)

        assert conda_package_handling.api.libarchive_enabled == True
