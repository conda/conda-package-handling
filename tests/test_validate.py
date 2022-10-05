from pathlib import Path

from conda_package_handling.validate import validate_converted_files_match_streaming

from .test_api import data_dir, test_package_name, test_package_name_2


def test_validate_streaming():
    assert (
        validate_converted_files_match_streaming(
            Path(data_dir, test_package_name + ".conda"),
            Path(data_dir, test_package_name + ".tar.bz2"),
        )
        is None
    )

    assert validate_converted_files_match_streaming(
        Path(data_dir, test_package_name_2 + ".tar.bz2"),
        Path(data_dir, test_package_name + ".conda"),
    ) == (
        Path(data_dir, test_package_name_2 + ".tar.bz2"),
        ["files are missing"],
        ["sizes are mismatched"],
    )
