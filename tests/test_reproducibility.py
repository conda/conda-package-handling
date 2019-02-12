import os

from conda_package_handling import api

this_dir = os.path.dirname(__file__)
data_dir = os.path.join(this_dir, "data")
test_package_name = "mock-2.0.0-py37_1000"

def test_api_create_tarball_is_reproducible(testing_workdir):
    pkg_dir = os.path.join(data_dir, test_package_name)
    api.create(pkg_dir, None, 'out_pkg.tar.bz2', out_folder=testing_workdir)
    results = api.get_pkg_details(os.path.join(testing_workdir, "out_pkg.tar.bz2"))
    assert results["size"] == 106976
    assert results["md5"] == "0f9cce120a73803a70abb14bd4d4900b"
    assert results["sha256"] == "34c659b0fdc53d28ae721fd5717446fb8abebb1016794bd61e25937853f4c29c"


def test_api_create_conda_v2_is_reproducible(testing_workdir):
    pkg_dir = os.path.join(data_dir, test_package_name)
    api.create(pkg_dir, None, 'out_pkg.conda', out_folder=testing_workdir)
    results = api.get_pkg_details(os.path.join(testing_workdir, "out_pkg.conda"))
    assert results["size"] == 112059
    assert results["inner_sha256"] == "c9c3042f7ce1c304a5aa4baa0bfd1b23e0fbb16e17e203fd3a16ade20beb5ee5"
    assert results["outer_sha256"] == "181ec44eb7b06ebb833eae845bcc466ad96474be1f33ee55cab7ac1b0fdbbfa3"


def test_sort_file_order():
    from conda_package_handling.tarball import _sort_file_order
    prefix = os.path.join(data_dir, test_package_name)
    file_list = [os.path.relpath(os.path.join(dp, f), prefix)
                 for dp, dn, filenames in os.walk(prefix)
                 for f in filenames]
    # TODO: come up with a good reference sort order.  The file referenced here doesn't exist yet.
    with open(os.path.join(data_dir, 'reference_sort_order_binsort.txt')) as f:
        reference_order = f.readlines()
    assert reference_order == _sort_file_order(prefix, file_list)
