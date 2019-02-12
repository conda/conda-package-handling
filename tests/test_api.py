import os

from conda_package_handling import api

this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, "data")
test_package_name = "mock-2.0.0-py37_1000"


def test_api_extract_tarball_implicit_path(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.tar.bz2')
    api.extract(tarfile)
    assert os.path.isfile(os.path.join(testing_workdir, test_package_name, 'info', 'index.json'))


def test_api_tarball_details(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.tar.bz2')
    results = api.get_pkg_details(tarfile)
    assert results["size"] == 106576
    assert results["md5"] == "0f9cce120a73803a70abb14bd4d4900b"
    assert results["sha256"] == "34c659b0fdc53d28ae721fd5717446fb8abebb1016794bd61e25937853f4c29c"


def test_api_conda_v2_details(testing_workdir):
    condafile = os.path.join(data_dir, test_package_name + '.conda')
    results = api.get_pkg_details(condafile)
    assert results["size"] == 113421
    assert results["inner_sha256"] == "c9c3042f7ce1c304a5aa4baa0bfd1b23e0fbb16e17e203fd3a16ade20beb5ee5"
    assert results["outer_sha256"] == "181ec44eb7b06ebb833eae845bcc466ad96474be1f33ee55cab7ac1b0fdbbfa3"


def test_api_extract_tarball_explicit_path(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.tar.bz2')
    api.extract(tarfile, 'manual_path')
    assert os.path.isfile(os.path.join(testing_workdir, 'manual_path', 'info', 'index.json'))


def test_api_extract_conda_v2_implicit_path(testing_workdir):
    condafile = os.path.join(data_dir, test_package_name + '.conda')
    api.extract(condafile)
    assert os.path.isfile(os.path.join(testing_workdir, test_package_name, 'info', 'index.json'))


def test_api_extract_conda_v2_explicit_path(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.conda')
    api.extract(tarfile, 'manual_path')
    assert os.path.isfile(os.path.join(testing_workdir, 'manual_path', 'info', 'index.json'))


def test_api_extract_info_conda_v2(testing_workdir):
    condafile = os.path.join(data_dir, test_package_name + '.conda')
    api.extract(condafile, 'manual_path', components='info')
    assert os.path.isfile(os.path.join(testing_workdir, 'manual_path', 'info', 'index.json'))
    assert not os.path.isdir(os.path.join(testing_workdir, 'manual_path', 'lib'))


def test_api_transmute_tarball_to_conda_v2(testing_workdir):
    tarfile = os.path.join(data_dir, test_package_name + '.tar.bz2')
    api.transmute(tarfile, '.conda', testing_workdir)
    assert os.path.isfile(os.path.join(testing_workdir, test_package_name + '.conda'))


def test_api_transmute_conda_v2_to_tarball(testing_workdir):
    condafile = os.path.join(data_dir, test_package_name + '.conda')
    api.transmute(condafile, '.tar.bz2', testing_workdir)
    assert os.path.isfile(os.path.join(testing_workdir, test_package_name + '.tar.bz2'))


def test_warning_when_bundling_no_metadata(testing_workdir):
    pass
