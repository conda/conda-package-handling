import io
from contextlib import redirect_stdout
from pathlib import Path
from urllib.request import urlretrieve

import pytest

import conda_package_handling.cli as cli

from .test_api import data_dir, test_package_name


def test_cli(tmpdir, mocker):
    """
    Code coverage for the cli.
    """
    for command in [
        ["x", str(Path(data_dir, test_package_name + ".tar.bz2")), f"--prefix={tmpdir}"],
        [
            "x",
            str(Path(data_dir, test_package_name + ".conda")),
            "--info",
            f"--prefix={tmpdir}",
        ],
        ["c", str(Path(tmpdir, test_package_name)), ".tar.bz2", f"--out-folder={tmpdir}"],
    ]:
        cli.main(args=command)

    # XXX difficult to get to this error handling code through the actual CLI;
    # for example, a .tar.bz2 that can't be extracted raises OSError instead of
    # returning errors. Designed for .tar.bz2 -> .conda conversions that somehow
    # omit files?
    mocker.patch(
        "conda_package_handling.api.transmute", return_value=set("that is why you fail".split())
    )
    with pytest.raises(SystemExit):
        command = [
            "t",
            str(Path(data_dir, test_package_name + ".tar.bz2")),
            ".conda",
            f"--out-folder={tmpdir}",
        ]
        cli.main(args=command)


def test_import_main():
    """
    e.g. python -m conda_package_handling
    """
    with pytest.raises(SystemExit):
        import conda_package_handling.__main__  # noqa


@pytest.mark.parametrize(
    "url,n_files",
    [
        ("https://conda.anaconda.org/conda-forge/noarch/conda-package-handling-2.2.0-pyh38be061_0.conda", 51),
        ("https://conda.anaconda.org/conda-forge/linux-64/conda-package-handling-1.9.0-py311hd4cff14_1.tar.bz2", 81),
    ]
)
def test_list(tmp_path, url, n_files):
    "Integration test to ensure `cph list` works correctly."
    localpath = tmp_path / url.split("/")[-1]
    urlretrieve(url, localpath)
    memfile = io.StringIO()
    with redirect_stdout(memfile):
        cli.main(["list", str(localpath)])
    memfile.seek(0)
    assert n_files == sum(1 for line in memfile.readlines() if line.strip())
