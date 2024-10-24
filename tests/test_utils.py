import pytest

from conda_package_handling import utils


def test_checksum(tmp_path):
    tmp_file = tmp_path / "file"
    tmp_file.write_text("file")
    with tmp_file.open("rb") as f:
        with pytest.raises(ValueError):
            utils._checksum(f, "chicken")
        utils.sha256_checksum(f)
        utils.md5_checksum(f)
