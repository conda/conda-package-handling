"""The 'new' conda format, introduced in late 2018/early 2019.  Spec at
https://anaconda.atlassian.net/wiki/spaces/AD/pages/90210540/Conda+package+format+v2"""

import json
import os
import shutil
import zipfile

from conda_package_handling import utils
from conda_package_handling.interface import AbstractBaseFormat
from conda_package_handling.tarball import create_compressed_tarball, _tar_xf
from conda_package_handling.utils import TemporaryDirectory

CONDA_PACKAGE_FORMAT_VERSION = 2
DEFAULT_COMPRESSION_TUPLE = ('.tar.zst', 'zstd', 'zstd:compression-level=22')


def _write_conda_pkg_version_spec(tmpdir):
    metadata_file = os.path.join(tmpdir, 'metadata.json')
    pkg_metadata = {'conda_pkg_format_version': CONDA_PACKAGE_FORMAT_VERSION}
    with open(metadata_file, 'w') as f:
        json.dump(pkg_metadata, f)


def _lookup_component_filename(zf, file_id, component_name):
    contents = zf.namelist()
    component_filename_without_ext = '-'.join((component_name, file_id))
    component_filename = [_ for _ in contents if
                            _.startswith(component_filename_without_ext)]
    return component_filename

def _extract_component(fn, file_id, component_name, dest_dir=None):
    with TemporaryDirectory() as tmp:
        with utils.tmp_chdir(tmp):
            with zipfile.ZipFile(fn, compression=zipfile.ZIP_STORED) as zf:
                component_filename = _lookup_component_filename(zf, file_id, component_name)
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
    def extract(fn, dest_dir=None, **kw):
        components = utils.ensure_list(kw.get('components')) or ('info', 'pkg')
        file_id = os.path.basename(fn).replace('.conda', '')
        if not dest_dir:
            dest_dir = os.path.join(os.getcwd(), file_id)
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
    def create(prefix, file_list, out_fn, out_folder=os.getcwd(), gpg_wrapper=None, **kw):
        with TemporaryDirectory() as tmp:
            out_fn = out_fn.replace('.conda', '')
            conda_pkg_fn = os.path.join(tmp, out_fn) + '.conda'
            pkg_files = utils.filter_info_files(file_list, prefix)
            info_files = set(file_list) - set(pkg_files)
            ext, comp_filter, filter_opts = kw.get('compression_tuple') or DEFAULT_COMPRESSION_TUPLE

            info_tarball = create_compressed_tarball(prefix, info_files, tmp, 'info-' + out_fn,
                                                    ext, comp_filter, filter_opts)
            pkg_tarball = create_compressed_tarball(prefix, pkg_files, tmp, 'pkg-' + out_fn,
                                                    ext, comp_filter, filter_opts)

            _write_conda_pkg_version_spec(tmp)

            with utils.tmp_chdir(tmp):
                with zipfile.ZipFile(conda_pkg_fn, 'w', compression=zipfile.ZIP_STORED) as zf:
                    for pkg in (info_tarball, pkg_tarball):
                        zf.write(os.path.basename(pkg))
                    zf.write('metadata.json')
                    # This should always be done at the end
                    if gpg_wrapper:
                      _signature_file = 'signature.asc'
                      gpg_wrapper.sign(artifacts=zf.namelist(), output='signature.asc')
                      zf.write(_signature_file)

            final_path = os.path.join(out_folder, os.path.basename(conda_pkg_fn))
            shutil.move(conda_pkg_fn, final_path)
        return final_path

    @staticmethod
    def get_pkg_details(in_file):
        # the thing of interest with the new format is the inner pkg-* file, not the package as a whole.
        file_id = os.path.basename(in_file).replace('.conda', '')
        stat_result = os.lstat(in_file)
        size = stat_result.st_size
        with zipfile.ZipFile(in_file, compression=zipfile.ZIP_STORED) as zf:
            component_filename = _lookup_component_filename(zf, file_id, 'pkg')
            if not component_filename:
                raise RuntimeError("didn't find {} in {}".format(
                    component_filename_without_ext, in_file))
            else:
                component_filename = component_filename[0]
            pkg_file = zf.open(component_filename, 'r')
            inner_sha256 = utils.sha256_checksum(pkg_file)
        with open(in_file, 'rb') as fd:
            outer_sha256 = utils.sha256_checksum(fd)
        return {"size": size, "inner_sha256": inner_sha256, "outer_sha256": outer_sha256}

    @staticmethod
    def gpg_sign(fn, gpg_wrapper=None, out_folder=os.getcwd()):
        assert gpg_wrapper

        final_fn = os.path.join(out_folder, os.path.basename(fn))
        with TemporaryDirectory() as tmp:
            with utils.tmp_chdir(tmp):
                with zipfile.ZipFile(fn, 'r', compression=zipfile.ZIP_STORED) as zf:
                    zf.extractall()
                    content = utils.ensure_list(zf.namelist())
                signature_file = 'signature.asc'
                try:
                    content.remove(signature_file)
                except ValueError:
                    pass
                with zipfile.ZipFile(final_fn, 'w', compression=zipfile.ZIP_STORED) as zf:
                    gpg_wrapper.sign(artifacts=content,
                                     output=signature_file)
                    for zn in content:
                        zf.write(zn)
                    zf.write(signature_file)

            shutil.move(fn, final_fn)

    @staticmethod
    def gpg_verify(fn, gpg_wrapper=None):
        assert gpg_wrapper

        with TemporaryDirectory() as tmp:
            with utils.tmp_chdir(tmp):
                with zipfile.ZipFile(fn, compression=zipfile.ZIP_STORED) as zf:
                    zf.extractall()
                    content = utils.ensure_list(zf.namelist())
                    content.remove('signature.asc')
                    gpg_wrapper.verify(artifacts=content,
                                       signature="signature.asc")
