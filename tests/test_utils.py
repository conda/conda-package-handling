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


@pytest.mark.parametrize(
    "path",
    [
        "info",
        "info/index.json",
        "info/files",
        "info/paths.json",
        "info/about.json",
        "info/has_prefix",
        "info/hash_input_files",
        "info/hash_input.json",
        "info/run_exports.yaml",
        "info/run_exports.json",
        "info/git",
        "info/recipe/meta.yaml",
        "info/recipe_log.json",
        "info/recipe.tar",
        "info/test/run_test.py",
        "info/LICENSE",
        "info/LICENSE.txt",
        "info/licenses/LICENSE",
        "info/requires",
        "info/meta",
        "info/platform",
        "info/no_link",
        "info/link.json",
        "info/icon.png",
        "info\\licenses\\LICENSE",
        "info\\index.json",
    ],
)
def test_is_info_member_path(path):
    assert utils.is_info_member_path(path)


@pytest.mark.parametrize(
    "path",
    [
        "bin/foo",
        "lib/python3.10/site-packages/foo",
        "information/foo",
        "notinfo/foo",
        "infofoo/bar",
        "prefix/info/index.json",
    ],
)
def test_is_info_member_path_false(path):
    assert not utils.is_info_member_path(path)
