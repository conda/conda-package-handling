"""
Test format classes.

(Some of their code is unreachable through api.py)
"""

import os
from pathlib import Path

import pytest

import conda_package_handling.conda_fmt as conda_fmt
from conda_package_handling.conda_fmt import CondaFormat_v2
from conda_package_handling.tarball import CondaTarBZ2

from .test_api import data_dir, test_package_name

TEST_CONDA = Path(data_dir, test_package_name + ".conda")
TEST_TARBZ = Path(data_dir, test_package_name + ".tar.bz2")


def test_extract_create(tmpdir):
    for format, infile, outfile in (
        (CondaFormat_v2, TEST_CONDA, "newmock.conda"),
        (CondaTarBZ2, TEST_TARBZ, "newmock.tar.bz2"),
    ):
        both_path = Path(tmpdir, f"mkdirs-{outfile.split('.', 1)[-1]}")

        # these old APIs don't guarantee Path-like's
        format.extract(infile, str(both_path))
        assert sorted(os.listdir(both_path)) == sorted(["lib", "info"])

        if format == CondaFormat_v2:
            info_path = Path(tmpdir, "info-only")
            format.extract_info(TEST_CONDA, str(info_path))  # type: ignore
            assert os.listdir(info_path) == ["info"]

        filelist = [str(p.relative_to(both_path)) for p in both_path.rglob("*")]
        format.create(
            both_path,
            filelist,
            tmpdir / outfile,
            # compression_tuple is for libarchive compatibility. Instead, pass
            # compressor=(compressor factory function)
            compression_tuple=(".tar.zst", "zstd", "zstd:compression-level=1"),
        )

        assert (tmpdir / outfile).exists()

        with pytest.raises(ValueError):
            CondaFormat_v2.create(
                "",
                [],
                "",
                compressor=True,
                compression_tuple=("1", "2", "3"),  # type: ignore
            )


@pytest.mark.parametrize(
    ("level", "threads", "cpu_count", "expected"),
    [
        (None, None, 7, (19, 1)),
        (1, 1, 7, (1, 1)),
        (None, -1, 7, (19, 7)),
        (None, -1, None, (19, 1)),
    ],
)
def test_zstd_level_threads(monkeypatch, level, threads, cpu_count, expected):
    monkeypatch.setattr(conda_fmt.os, "cpu_count", lambda: cpu_count)
    assert conda_fmt._translate_zstd_level_threads(level, threads) == expected


def test_list_contents_dispatches_to_subclass(monkeypatch):
    class CustomCondaFormat(CondaFormat_v2):
        @staticmethod
        def _list_remote_contents(url, verbose=False, components=("info", "pkg")):
            return url, verbose, components

    monkeypatch.setattr(
        CondaFormat_v2,
        "_list_remote_contents",
        staticmethod(lambda *args, **kwargs: "base"),
    )
    url = "https://example.invalid/package.conda"
    assert CustomCondaFormat.list_contents(url) == (url, False, ("info", "pkg"))
