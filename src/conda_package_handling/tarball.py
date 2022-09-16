from errno import ELOOP
import os
import re
import subprocess
import sys
import tarfile
from tempfile import NamedTemporaryFile
import logging

libarchive_enabled = False

from . import utils, streaming
from .interface import AbstractBaseFormat
from .exceptions import CaseInsensitiveFileSystemError, InvalidArchiveError

LOG = logging.getLogger(__file__)

def _sort_file_order(prefix, files):
    """Sort by filesize or by binsort, to optimize compression"""
    info_slash = "info" +  os.path.sep
    def order(f):
        # we don't care about empty files so send them back via 100000
        fsize = os.lstat(os.path.join(prefix, f)).st_size or 100000
        # info/* records will be False == 0, others will be 1.
        info_order = int(not f.startswith(info_slash))
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
        # Binsort does not handle symlinks gracefully. It will follow them. We must correct that.
        s1 = set(files)
        s2 = set(files_list)
        followed = s2 - s1
        for f in followed:
            files_list.remove(f)
        s2 = set(files_list)
        if len(s1) > len(s2):
            files_list.extend(s1 - s2)
        # move info/ to front, otherwise preserving current order fi[0]
        # (Python's sort algorithm is guaranteed to be stable, maintains
        # existing order of items with the same sort key)
        files_list = list(sorted(files, key=lambda f: not f.startswith(info_slash)))
    else:
        files_list = list(sorted(files, key=order))
    return files_list


def _create_no_libarchive(fullpath, files):
    with tarfile.open(fullpath, 'w:bz2') as t:
        for f in files:
            t.add(f)


def create_compressed_tarball(prefix, files, tmpdir, basename,
                              ext, compression_filter, filter_opts=''):
    tmp_path = os.path.join(tmpdir, basename)
    files = _sort_file_order(prefix, files)

    # add files in order of a) in info directory, b) increasing size so
    # we can access small manifest or json files without decompressing
    # possible large binary or data files
    fullpath = tmp_path + ext
    with utils.tmp_chdir(prefix):
            _create_no_libarchive(fullpath, files)
    return fullpath


class CondaTarBZ2(AbstractBaseFormat):

    @staticmethod
    def supported(fn):
        return fn.endswith('.tar.bz2')

    @staticmethod
    def extract(fn, dest_dir, **kw):
        if not os.path.isdir(dest_dir):
            os.makedirs(dest_dir)
        if not os.path.isabs(fn):
            fn = os.path.normpath(os.path.join(os.getcwd(), fn))

        streaming._extract(str(fn), str(dest_dir), components=["pkg"])

    @staticmethod
    def create(prefix, file_list, out_fn, out_folder=os.getcwd(), **kw):
        if os.path.isabs(out_fn):
            out_folder = os.path.dirname(out_fn)
        out_file = create_compressed_tarball(prefix, file_list, out_folder,
                                             os.path.basename(out_fn).replace('.tar.bz2', ''),
                                             '.tar.bz2', 'bzip2')
        return out_file

    @staticmethod
    def get_pkg_details(in_file):
        stat_result = os.stat(in_file)
        size = stat_result.st_size
        md5, sha256 = utils.checksums(in_file, ('md5', 'sha256'))
        return {"size": size, "md5": md5, "sha256": sha256}
