import pytest

from conda_package_handling import utils


def test_checksum(tmp_path):
    tmp_file = tmp_path / "file"
    tmp_file.write_text("file")
    with tmp_file.open("rb") as f:
        with pytest.raises(ValueError):
            utils._checksum(f, "chicken")
        assert (
            utils.sha256_checksum(f)
            == "3b9c358f36f0a31b6ad3e14f309c7cf198ac9246e8316f9ce543d5b19ac02b80"
        )
        assert utils.md5_checksum(f) == "d41d8cd98f00b204e9800998ecf8427e"
