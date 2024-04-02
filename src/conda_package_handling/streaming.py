"""
Exception-compatible adapter from conda_package_streaming.
"""

from __future__ import annotations

import io
from contextlib import redirect_stdout
from tarfile import TarError, TarFile, TarInfo
from zipfile import BadZipFile
from typing import Generator

from conda_package_streaming.extract import exceptions as cps_exceptions
from conda_package_streaming.extract import extract_stream, package_streaming

from . import exceptions

def _stream_components(
    filename: str, components: list[str]
) -> Generator[tuple[TarFile, TarInfo], None, None]:
    if str(filename).endswith(".tar.bz2"):
        assert components == ["pkg"]

    try:
        with open(filename, "rb") as fileobj:
            for component in components:
                # will parse zipfile twice
                yield package_streaming.stream_conda_component(
                    filename, fileobj, component=component
                )
    except (OSError, TarError, BadZipFile) as e:
        raise exceptions.InvalidArchiveError(filename, f"failed with error: {str(e)}") from e
    

def _extract(filename: str, dest_dir: str, components: list[str]):
    """
    Extract .conda or .tar.bz2 package to dest_dir.

    If it's a conda package, components may be ["pkg", "info"]

    If it's a .tar.bz2 package, components must equal ["pkg"]

    Internal. Skip directly to conda-package-streaming if you don't need
    exception compatibility.
    """
    try:
        for stream in _stream_components(filename, components):
            extract_stream(stream, dest_dir)
    except cps_exceptions.CaseInsensitiveFileSystemError as e:
        raise exceptions.CaseInsensitiveFileSystemError(filename, dest_dir) from e
    

def _list(filename: str, components: list[str], verbose=True):
    memfile = io.StringIO()
    for component in _stream_components(filename, components):
        for tar, _ in component:
            with redirect_stdout(memfile):
                tar.list(verbose=verbose)
            component.close()
    memfile.seek(0)
    lines = sorted(memfile.readlines(), key=lambda line: line.split(None, 5)[-1])
    print("".join(lines))
