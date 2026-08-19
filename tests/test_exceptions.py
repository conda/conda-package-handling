import pickle

import pytest

from conda_package_handling.exceptions import (
    CaseInsensitiveFileSystemError,
    ConversionError,
    InvalidArchiveError,
)


@pytest.mark.parametrize(
    ("error_type", "constructor_args"),
    (
        (InvalidArchiveError, ("archive.conda", "invalid archive")),
        (CaseInsensitiveFileSystemError, ("archive.conda", "destination")),
        (ConversionError, (["missing"], ["mismatched"], "extra context")),
    ),
    ids=(
        "InvalidArchiveError",
        "CaseInsensitiveFileSystemError",
        "ConversionError",
    ),
)
def test_exception_pickle_round_trip(mocker, error_type, constructor_args):
    error = error_type(*constructor_args)
    error.extra_state = {"preserved": True}
    init = mocker.spy(error_type, "__init__")

    restored = pickle.loads(pickle.dumps(error))

    init.assert_called_once_with(restored, *constructor_args)
    assert type(restored) is type(error)
    assert restored.args == error.args
    assert str(restored) == str(error)
    assert vars(restored) == vars(error)
