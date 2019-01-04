"""The 'new' conda format, introduced in late 2018/early 2019.  Spec at
https://anaconda.atlassian.net/wiki/spaces/AD/pages/90210540/Conda+package+format+v2"""

import json
import os
import shutil
from tempfile import TemporaryDirectory
import zipfile

from conda_package_handling import utils
from conda_package_handling.tarball import create_compressed_tarball
from conda_package_handling.interface import AbstractBaseFormat
from conda_package_handling.tarball import create_compressed_tarball, _tar_xf

CONDA_PACKAGE_FORMAT_VERSION = 2
DEFAULT_COMPRESSION_TUPLE = ('.tar.zst', 'zstd', 'zstd:compression-level=22')


def _write_conda_pkg_version_spec(tmpdir):
    metadata_file = os.path.join(tmpdir, 'metadata.json')
    pkg_metadata = {'conda_pkg_format_version': CONDA_PACKAGE_FORMAT_VERSION}
    with open(metadata_file, 'w') as f:
        json.dump(pkg_metadata, f)


def _extract_component(fn, component_name, dest_dir=None):
    file_id = os.path.basename(fn).replace('.conda', '')
    if not dest_dir:
        dest_dir = os.path.join(os.getcwd(), file_id)
    with TemporaryDirectory() as tmp:
        with utils.tmp_chdir(tmp.name):
            with zipfile.ZipFile(fn, compression=zipfile.ZIP_STORED) as zf:
                contents = zf.namelist()
                component_filename_without_ext = '-'.join((component_name, file_id))
                component_filename = [_ for _ in contents if
                                        _.startswith(component_filename_without_ext)]
                if not component_filename:
                    raise RuntimeError("didn't find {} in {}".format(
                        component_filename_without_ext, fn))
                component_filename = component_filename[0]
                zf.extract(component_filename)
                _tar_xf(component_filename, dest_dir)


class CondaFormat_v2(AbstractBaseFormat):
    """If there's another conda format or breaking changes, please create a new class and keep this
    one, so that handling of v2 stays working."""

    @staticmethod
    def extract(fn, dest_dir=None):
        _extract_component(fn, 'info', dest_dir)
        _extract_component(fn, 'pkg', dest_dir)

    def extract_info(fn, dest_dir=None):
        _extract_component(fn, 'info', dest_dir)

    def create(prefix, file_list, out_fn, out_folder=os.getcwd(), **kw):
        tmp = TemporaryDirectory()
        out_fn = out_fn.replace('.conda', '')
        conda_pkg_fn = os.path.join(tmp.name, out_fn) + '.conda'
        pkg_files = utils.filter_info_files(file_list, prefix)
        info_files = set(file_list) - set(pkg_files)
        ext, comp_filter, filter_opts = kw.get('compression_tuple') or DEFAULT_COMPRESSION_TUPLE

        info_tarball = create_compressed_tarball(prefix, info_files, tmp, 'info-' + out_fn,
                                                 ext, comp_filter, filter_opts)
        pkg_tarball = create_compressed_tarball(prefix, pkg_files, tmp, 'pkg-' + out_fn,
                                                 ext, comp_filter, filter_opts)

        _write_conda_pkg_version_spec(tmp.name)

        with utils.tmp_chdir(tmp.name):
            with zipfile.ZipFile(conda_pkg_fn, 'w', compression=zipfile.ZIP_STORED) as zf:
                for pkg in (info_tarball, pkg_tarball):
                    zf.write(os.path.basename(pkg))
                zf.write('metadata.json')
        final_path = os.path.join(out_folder, os.path.basename(conda_pkg_fn))
        shutil.rename(conda_pkg_fn, final_path)
        return final_path
