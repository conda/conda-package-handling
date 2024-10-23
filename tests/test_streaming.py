"""
Test streaming module.
"""

import pytest
from conda_package_handling.streaming import _stream_components
from conda_package_handling.exceptions import InvalidArchiveError

def test__stream_components(tmp_path):
    test_file = tmp_path / "hello.conda"
    test_file.write_text("hello")
    with pytest.raises(InvalidArchiveError):
        list(_stream_components(test_file, ["pkg"]))
