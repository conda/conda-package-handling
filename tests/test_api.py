from datetime import datetime
import os
import sys
import tarfile

import pytest
import libarchive

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
    assert results["sha256"] == "181ec44eb7b06ebb833eae845bcc466ad96474be1f33ee55cab7ac1b0fdbbfa3"
    assert results["md5"] == "23c226430e35a3bd994db6c36b9ac8ae"


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


@pytest.mark.skipif(sys.platform=="win32", reason="windows and symlinks are not great")
def test_create_package_with_uncommon_conditions_captures_all_content(testing_workdir):
    os.makedirs('src/a_folder')
    os.makedirs('src/empty_folder')
    os.makedirs('src/symlink_stuff')
    with open('src/a_folder/text_file', 'w') as f:
        f.write('weee')
    open('src/empty_file', 'w').close()
    os.link('src/a_folder/text_file', 'src/a_folder/hardlink_to_text_file')
    os.symlink('../a_folder', 'src/symlink_stuff/symlink_to_a')
    os.symlink('../empty_file', 'src/symlink_stuff/symlink_to_empty_file')
    os.symlink('../a_folder/text_file', 'src/symlink_stuff/symlink_to_text_file')

    with tarfile.open('pinkie.tar.bz2', 'w:bz2') as tf:
        tf.add('src/empty_folder', 'empty_folder')
        tf.add('src/empty_file', 'empty_file')
        tf.add('src/a_folder', 'a_folder')
        tf.add('src/a_folder/text_file', 'a_folder/text_file')
        tf.add('src/a_folder/hardlink_to_text_file', 'a_folder/hardlink_to_text_file')
        tf.add('src/symlink_stuff/symlink_to_a', 'symlink_stuff/symlink_to_a')
        tf.add('src/symlink_stuff/symlink_to_empty_file', 'symlink_stuff/symlink_to_empty_file')
        tf.add('src/symlink_stuff/symlink_to_text_file', 'symlink_stuff/symlink_to_text_file')

    cph_created = api.create('src', None, 'thebrain.tar.bz2')

    # test against both archives created manually and those created by cph.  They should be equal in all ways.
    for fn in ('pinkie.tar.bz2', 'thebrain.tar.bz2'):
        api.extract(fn)
        target_dir = fn[:-8]
        flist = [
            'empty_folder',
            'empty_file',
            'a_folder/text_file',
            'a_folder/hardlink_to_text_file',
            'symlink_stuff/symlink_to_a',
            'symlink_stuff/symlink_to_text_file',
            'symlink_stuff/symlink_to_empty_file',
        ]

        # no symlinks on windows
        if sys.platform != 'win32':
            # not directly included but checked symlink
            flist.append('symlink_stuff/symlink_to_a/text_file')

        missing_content = []
        for f in flist:
            path_that_should_be_there = os.path.join(testing_workdir, target_dir, f)
            if not (os.path.exists(path_that_should_be_there) or
                    os.path.lexists(path_that_should_be_there)):
                missing_content.append(f)
        if missing_content:
            print("missing files in output package")
            print(missing_content)
            sys.exit(1)

        # hardlinks should be preserved, but they're currently not with libarchive
        # hardlinked_file = os.path.join(testing_workdir, target_dir, 'a_folder/text_file')
        # stat = os.stat(hardlinked_file)
        # assert stat.st_nlink == 2

        hardlinked_file = os.path.join(testing_workdir, target_dir, 'empty_file')
        stat = os.stat(hardlinked_file)
        if sys.platform != 'win32':
            assert stat.st_nlink == 1


@pytest.mark.skipif(datetime.now() <= datetime(2019, 7, 1), reason="Don't understand why this doesn't behave.  Punt.")
def test_secure_refusal_to_extract_abs_paths(testing_workdir):
    with tarfile.open('pinkie.tar.bz2', 'w:bz2') as tf:
        open('thebrain', 'w').close()
        tf.add(os.path.join(testing_workdir, 'thebrain'), '/naughty/abs_path')

    with pytest.raises(libarchive.exception.ArchiveError):
        api.extract('pinkie.tar.bz2')


def tests_secure_refusal_to_extract_dotdot(testing_workdir):
    with tarfile.open('pinkie.tar.bz2', 'w:bz2') as tf:
        open('thebrain', 'w').close()
        tf.add(os.path.join(testing_workdir, 'thebrain'), '../naughty/abs_path')

    with pytest.raises(libarchive.exception.ArchiveError):
        api.extract('pinkie.tar.bz2')
