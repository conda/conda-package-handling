"""
Test streaming module.
"""

from pathlib import Path

import pytest
from conda_package_streaming.exceptions import (
    CaseInsensitiveFileSystemError as CPSCaseInsensitiveFileSystemError,
)
from pytest_mock import MockerFixture
from pytest_mock.plugin import _mocker

from conda_package_handling.exceptions import CaseInsensitiveFileSystemError, InvalidArchiveError
from conda_package_handling.streaming import _extract, _stream_components

from .test_interface import TEST_CONDA


def test__stream_components(tmp_path: Path, mocker: MockerFixture):
    """
    Execute two error handling paths in _stream_components
    """
    test_file = tmp_path / "hello.conda"
    test_file.write_text("hello")
    with pytest.raises(InvalidArchiveError):
        list(_stream_components(test_file, ["pkg"]))

    # translates their exception to our exception of the same name
    mocker.patch(
        "conda_package_streaming.package_streaming.stream_conda_component",
        side_effect=CPSCaseInsensitiveFileSystemError(),
    )

    with pytest.raises(CaseInsensitiveFileSystemError):
        list(_stream_components(test_file, ["pkg"]))


def test__extract(tmp_path: Path, mocker: MockerFixture):
    # translates their exception to our exception of the same name
    # Curiously a side effect on extract_stream doesn't work? compared to the more likely to be called accidentally realpath.
    mocker.patch(
        "conda_package_handling.streaming.extract_stream",
        side_effect=CPSCaseInsensitiveFileSystemError(),
    )

    with pytest.raises(CaseInsensitiveFileSystemError):
        _extract(str(TEST_CONDA), str(tmp_path), ["pkg", "info"])
