import logging
import os
import re
import shutil
import subprocess
import sys
from tempfile import NamedTemporaryFile

import libarchive

from conda_package_handling import utils
from conda_package_handling.interface import AbstractBaseFormat
from conda_package_handling.utils import TemporaryDirectory


def _sort_file_order(prefix, files):
    """Sort by filesize or by binsort, to optimize compression"""
    def order(f):
        # we don't care about empty files so send them back via 100000
        fsize = os.stat(os.path.join(prefix, f)).st_size or 100000
        # info/* records will be False == 0, others will be 1.
        info_order = int(os.path.dirname(f) != 'info')
        if info_order:
            _, ext = os.path.splitext(f)
            # Strip any .dylib.* and .so.* and rename .dylib to .so
            ext = re.sub(r'(\.dylib|\.so).*$', r'.so', ext)
            if not ext:
                # Files without extensions should be sorted by dirname
                info_order = 1 + hash(os.path.dirname(f)) % (10 ** 8)
            else:
                info_order = 1 + abs(hash(ext)) % (10 ** 8)
        return info_order, fsize

    binsort = os.path.join(sys.prefix, 'bin', 'binsort')
    if os.path.exists(binsort):
        with NamedTemporaryFile(mode='w', suffix='.filelist', delete=False) as fl:
            with utils.tmp_chdir(prefix):
                fl.writelines(map(lambda x: '.' + os.sep + x + '\n', files))
                fl.close()
                cmd = binsort + ' -t 1 -q -d -o 1000 {}'.format(fl.name)
                out, _ = subprocess.Popen(cmd, shell=True,
                                            stdout=subprocess.PIPE).communicate()
                files_list = out.decode('utf-8').strip().split('\n')
                # binsort returns the absolute paths.
                files_list = [f.split(prefix + os.sep, 1)[-1]
                                for f in files_list]
                os.unlink(fl.name)
    else:
        files_list = list(f for f in sorted(files, key=order))
    return files_list


def create_compressed_tarball(prefix, files, tmpdir, basename,
                              ext, compression_filter, filter_opts=''):
    tmp_path = os.path.join(tmpdir, basename)
    files = _sort_file_order(prefix, files)

    # add files in order of a) in info directory, b) increasing size so
    # we can access small manifest or json files without decompressing
    # possible large binary or data files
    fullpath = tmp_path + ext
    with utils.tmp_chdir(prefix):
        with libarchive.file_writer(fullpath, 'gnutar', filter_name=compression_filter,
                                    options=filter_opts) as archive:
            archive.add_files(*files)
    return fullpath


def _tar_xf(tarball, dir_path):
    flags = libarchive.extract.EXTRACT_TIME | \
            libarchive.extract.EXTRACT_PERM | \
            libarchive.extract.EXTRACT_SECURE_NODOTDOT | \
            libarchive.extract.EXTRACT_SECURE_SYMLINKS | \
            libarchive.extract.EXTRACT_SECURE_NOABSOLUTEPATHS
    if not os.path.isabs(tarball):
        tarball = os.path.join(os.getcwd(), tarball)
    with utils.tmp_chdir(dir_path):
        libarchive.extract_file(tarball, flags)


class CondaTarBZ2(AbstractBaseFormat):

    @staticmethod
    def extract(fn, dest_dir=None, **kw):
        file_id = os.path.basename(fn).replace('.tar.bz2', '')
        if not dest_dir:
            dest_dir = os.path.join(os.getcwd(), file_id)
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        # if kw.get('components'):
        #     print("Warning: ignoring request for components - .tar.bz2 files can't "
        #           "be partially extracted")
        if not os.path.isabs(fn):
            fn = os.path.normpath(os.path.join(os.getcwd(), fn))
        _tar_xf(fn, dest_dir)

    @staticmethod
    def create(prefix, file_list, out_fn, out_folder=os.getcwd(), **kw):
        with TemporaryDirectory() as tmpdir:
            out_file = create_compressed_tarball(prefix, file_list, tmpdir,
                                                 os.path.basename(out_fn).replace('.tar.bz2', ''),
                                                 '.tar.bz2', 'bzip2')
            final_path = os.path.join(out_folder, os.path.basename(out_file))
            if out_file != final_path:
                try:
                    shutil.move(out_file, final_path)
                except OSError as e:
                    logging.getLogger(__name__).info("Moving temporary "
                        "package from {} to {} had some issues.  Error "
                        "message was: {}".format(out_file, final_path, repr(e)))
        return final_path

    @staticmethod
    def get_pkg_details(in_file):
        stat_result = os.lstat(in_file)
        size = stat_result.st_size
        # open the file twice because we need to start from the beginning each time
        with open(in_file, 'rb') as f:
            md5 = utils.md5_checksum(f)
        with open(in_file, 'rb') as f:
            sha256 = utils.sha256_checksum(f)
        return {"size": size, "md5": md5, "sha256": sha256}
