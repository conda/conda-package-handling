import os

from conda_package_handling import api

this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, "data")
test_package_name = "mock-2.0.0-py37_1000"


def test_api_extract_tarball_implicit_path(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.tar.bz2')
    api.extract(tarfile)
    assert os.path.isfile(os.path.join(testing_workdir, test_package_name, 'info', 'index.json'))


def test_api_extract_tarball_explicit_path(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.tar.bz2')
    api.extract(tarfile, 'manual_path')
    assert os.path.isfile(os.path.join(testing_workdir, 'manual_path', 'info', 'index.json'))


def test_api_extract_conda_v2_implicit_path(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.conda')
    api.extract(tarfile)
    assert os.path.isfile(os.path.join(testing_workdir, test_package_name, 'info', 'index.json'))


def test_api_extract_conda_v2_explicit_path(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.conda')
    api.extract(tarfile, 'manual_path')
    assert os.path.isfile(os.path.join(testing_workdir, 'manual_path', 'info', 'index.json'))


def test_api_extract_info_conda_v2(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.conda')
    api.extract(tarfile, 'manual_path', components='info')
    assert os.path.isfile(os.path.join(testing_workdir, 'manual_path', 'info', 'index.json'))
    assert not os.path.isdir(os.path.join(testing_workdir, 'manual_path', 'lib'))


def test_api_convert_tarball_to_conda_v2(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.tar.bz2')
    api.convert(tarfile, '.conda')


def test_api_convert_conda_v2_to_tarball(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.conda')
    api.convert(tarfile, '.tar.bz2')


def test_warning_when_bundling_no_metadata(testing_workdir):
    pass
