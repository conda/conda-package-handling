from pathlib import Path

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
