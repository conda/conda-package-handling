"""The 'new' conda format, introduced in late 2018/early 2019.  Spec at
https://anaconda.atlassian.net/wiki/spaces/AD/pages/90210540/Conda+package+format+v2"""

import json
import os
from tempfile import NamedTemporaryFile

try:
    from zipfile import ZipFile, BadZipFile, ZIP_STORED
except ImportError:
    # py27 compat
    from zipfile import ZipFile, ZIP_STORED, BadZipfile as BadZipFile

from . import utils
from .exceptions import InvalidArchiveError
from .interface import AbstractBaseFormat
from .tarball import create_compressed_tarball, _tar_xf

CONDA_PACKAGE_FORMAT_VERSION = 2
DEFAULT_COMPRESSION_TUPLE = ('.tar.zst', 'zstd', 'zstd:compression-level=22')


def _lookup_component_filename(zf, file_id, component_name):
    contents = zf.namelist()
    component_filename_without_ext = '-'.join((component_name, file_id))
    component_filename = [_ for _ in contents if
                            _.startswith(component_filename_without_ext)]
    return component_filename


def _extract_component(fn, file_id, component_name, dest_dir=os.getcwd()):
    try:
        with ZipFile(fn, compression=ZIP_STORED) as zf:
            with utils.TemporaryDirectory(prefix=dest_dir) as tmpdir:
                with utils.tmp_chdir(tmpdir):
                    component_filename = _lookup_component_filename(zf, file_id, component_name)
                    if not component_filename:
                        raise RuntimeError("didn't find {} component in {}"
                                           .format(component_name, fn))
                    component_filename = component_filename[0]
                    zf.extract(component_filename)
                    _tar_xf(component_filename, dest_dir)
    except BadZipFile as e:
        raise InvalidArchiveError(fn, str(e))


class CondaFormat_v2(AbstractBaseFormat):
    """If there's another conda format or breaking changes, please create a new class and keep this
    one, so that handling of v2 stays working."""

    @staticmethod
    def extract(fn, dest_dir, **kw):
        components = utils.ensure_list(kw.get('components')) or ('info', 'pkg')
        file_id = os.path.basename(fn).replace('.conda', '')
        if not os.path.isabs(fn):
            fn = os.path.normpath(os.path.join(os.getcwd(), fn))
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        for component in components:
            _extract_component(fn, file_id, component, dest_dir)

    @staticmethod
    def extract_info(fn, dest_dir=None):
        return CondaFormat_v2.extract(fn, dest_dir, components=['info'])

    @staticmethod
    def create(prefix, file_list, out_fn, out_folder=os.getcwd(), **kw):
        if os.path.isabs(out_fn):
            out_folder = os.path.dirname(out_fn)
            out_fn = os.path.basename(out_fn)
        conda_pkg_fn = os.path.join(out_folder, out_fn)
        out_fn = out_fn.replace('.conda', '')
        pkg_files = utils.filter_info_files(file_list, prefix)
        info_files = set(file_list) - set(pkg_files)
        ext, comp_filter, filter_opts = kw.get('compression_tuple') or DEFAULT_COMPRESSION_TUPLE

        with utils.TemporaryDirectory(prefix=out_folder) as tmpdir:
            info_fn = 'info-' + out_fn
            info_tarball = create_compressed_tarball(prefix, info_files, tmpdir, info_fn,
                                                    ext, comp_filter, filter_opts)
            with open(info_tarball, 'rb') as f:
                info_tarball_sha256 = utils.sha256_checksum(f)
            info_tarball_size = os.lstat(info_tarball).st_size

            pkg_fn = 'pkg-' + out_fn
            pkg_tarball = create_compressed_tarball(prefix, pkg_files, tmpdir, pkg_fn,
                                                    ext, comp_filter, filter_opts)
            with open(pkg_tarball, 'rb') as f:
                pkg_tarball_sha256 = utils.sha256_checksum(f)
            pkg_tarball_size = os.lstat(pkg_tarball).st_size

            pkg_metadata = {
                "conda_pkg_format_version": CONDA_PACKAGE_FORMAT_VERSION,
                "schema_version": 1,
                "pkg": {
                    "fn": pkg_fn,
                    "sha256": pkg_tarball_sha256,
                    "size": pkg_tarball_size,
                },
                "info": {
                    "fn": info_fn,
                    "sha256": info_tarball_sha256,
                    "size": info_tarball_size,
                },
            }

            with ZipFile(conda_pkg_fn, 'w', compression=ZIP_STORED) as zf:
                with NamedTemporaryFile(mode='w') as tf:
                    tf.write(utils.json_dumps_compact(pkg_metadata))
                    zf.write(tf.name, 'metadata.json')
                    for pkg in (info_tarball, pkg_tarball):
                        zf.write(pkg, os.path.basename(pkg))
        return conda_pkg_fn

    @staticmethod
    def get_pkg_details(in_file):
        stat_result = os.stat(in_file)
        size = stat_result.st_size
        # open the file twice because we need to start from the beginning each time
        with open(in_file, 'rb') as f:
            md5 = utils.md5_checksum(f)
        with open(in_file, 'rb') as f:
            sha256 = utils.sha256_checksum(f)
        return {"size": size, "md5": md5, "sha256": sha256}
