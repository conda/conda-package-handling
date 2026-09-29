"""Shared package fixtures used by the tests and their HTTP server."""

from pathlib import Path

DATA_DIR = Path(__file__).parent / "data"
MOCK_PACKAGE = "mock-2.0.0-py37_1000"
CPH_TEST_DATA_PACKAGE = "cph_test_data-0.0.1-0"
TEST_CONDA = DATA_DIR / f"{MOCK_PACKAGE}.conda"
TEST_TARBZ = DATA_DIR / f"{MOCK_PACKAGE}.tar.bz2"
