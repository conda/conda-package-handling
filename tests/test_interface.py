"""
Test format classes.

(Some of their code is unreachable through api.py)
"""

import os

from pathlib import Path

from conda_package_handling.conda_fmt import *
from conda_package_handling.tarball import *

from .test_api import data_dir, test_package_name

TEST_CONDA = Path(data_dir, test_package_name + ".conda")


def test_extract_create(tmpdir):
    both_path = Path(tmpdir, "mkdirs")

    # these old APIs don't guarantee Path-like's
    CondaFormat_v2.extract(TEST_CONDA, str(both_path))
    assert sorted(os.listdir(both_path)) == sorted(["lib", "info"])

    info_path = Path(tmpdir, "info-only")
    CondaFormat_v2.extract_info(TEST_CONDA, str(info_path))
    assert os.listdir(info_path) == ["info"]

    filelist = [str(p.relative_to(both_path)) for p in both_path.rglob("*")]
    CondaFormat_v2.create(
        both_path,
        filelist,
        tmpdir / "newmock.conda",
        # compression_tuple is for libarchive compatibility. Instead, pass
        # compressor=(compressor factory function)
        compression_tuple=(".tar.zst", "zstd", "zstd:compression-level=1"),
    )

    assert (tmpdir / "newmock.conda").exists()
