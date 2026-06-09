"""
Test conda-package-handling can work in `.tar.bz2`-only mode if zstd support is
not available.
"""

import importlib
import subprocess
import sys
import warnings


def test_degraded():
    try:
        sys.modules["backports.zstd"] = None  # type: ignore
        sys.modules["compression.zstd"] = None  # type: ignore
        sys.modules["conda_package_streaming.transmute"] = None  # type: ignore
        sys.modules["conda_package_handling.conda_fmt"] = None  # type: ignore

        # this is only testing conda_package_handling's code, and does not test
        # that conda_package_streaming works without zstd.

        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Ensure warnings are sent
            import conda_package_handling.api

            importlib.reload(conda_package_handling.api)

            # Filter for warnings related to conda_package_handling
            cph_warnings = [
                warning
                for warning in w
                if "backports.zstd" in str(warning.message)
                or "Python 3.14" in str(warning.message)
            ]
            assert len(cph_warnings) >= 1
            assert any(issubclass(w.category, UserWarning) for w in cph_warnings)
            assert conda_package_handling.api.libarchive_enabled is False

    finally:
        sys.modules.pop("compression.zstd", None)
        sys.modules.pop("backports.zstd", None)
        sys.modules.pop("conda_package_handling.conda_fmt", None)
        sys.modules.pop("conda_package_streaming.transmute", None)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")  # Ensure warnings are sent
            import conda_package_handling.api

            importlib.reload(conda_package_handling.api)
            assert len(w) == 0
            assert conda_package_handling.api.libarchive_enabled is True


def test_degraded_subprocess():
    """
    More reliable way to mock 'zstd not available'
    """
    subprocess.check_call(
        [
            sys.executable,
            "-c",
            "import sys; sys.modules['backports.zstd'] = None; sys.modules['compression.zstd'] = None; import conda_package_handling.api",
        ]
    )
