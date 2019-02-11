import contextlib
import hashlib
import os
import re
import shutil
import warnings as _warnings

from six import string_types

try:
    from tempfile import TemporaryDirectory
except ImportError:
    from tempfile import mkdtemp

    class TemporaryDirectory(object):
        """Create and return a temporary directory.  This has the same
        behavior as mkdtemp but can be used as a context manager.  For
        example:

            with TemporaryDirectory() as tmpdir:
                ...

        Upon exiting the context, the directory and everything contained
        in it are removed.
        """

        # Handle mkdtemp raising an exception
        name = None
        _closed = False

        def __init__(self, suffix="", prefix='tmp', dir=None):
            self.name = mkdtemp(suffix, prefix, dir)

        def __repr__(self):
            return "<{} {!r}>".format(self.__class__.__name__, self.name)

        def __enter__(self):
            return self.name

        def cleanup(self, _warn=False, _warnings=_warnings):
            if self.name and not self._closed:
                try:
                    shutil.rmtree(self.name)
                except (TypeError, AttributeError) as ex:
                    if "None" not in '%s' % (ex,):
                        raise
                    shutil.rmtree(self.name)
                self._closed = True
                if _warn and _warnings.warn:
                    _warnings.warn("Implicitly cleaning up {!r}".format(self),
                                    _warnings.ResourceWarning)

        def __exit__(self, exc, value, tb):
            self.cleanup()

        def __del__(self):
            # Issue a ResourceWarning if implicit cleanup needed
            self.cleanup(_warn=True)


@contextlib.contextmanager
def tmp_chdir(dest):
    curdir = os.getcwd()
    try:
        os.chdir(dest)
        yield
    finally:
        os.chdir(curdir)


def ensure_list(arg):
    if (isinstance(arg, string_types) or not hasattr(arg, '__iter__')):
        if arg is not None:
            arg = [arg]
        else:
            arg = []
    return arg


def filter_files(files_list, prefix, filter_patterns=(r'(.*[\\\\/])?\.git[\\\\/].*',
                                                      r'(.*[\\\\/])?\.git$',
                                                      r'(.*)?\.DS_Store.*',
                                                      r'.*\.la$',
                                                      r'conda-meta.*')):
    """Remove things like the .git directory from the list of files to be copied"""
    for pattern in filter_patterns:
        r = re.compile(pattern)
        files_list = set(files_list) - set(filter(r.match, files_list))
    return [f for f in files_list if not os.path.isdir(os.path.join(prefix, f))]


def filter_info_files(files_list, prefix):
    return filter_files(files_list, prefix, filter_patterns=(
                    'info[\\\\/]index.json',
                    'info[\\\\/]files',
                    'info[\\\\/]paths.json',
                    'info[\\\\/]about.json',
                    'info[\\\\/]has_prefix',
                    'info[\\\\/]hash_input_files',   # legacy, not used anymore
                    'info[\\\\/]hash_input.json',
                    'info[\\\\/]run_exports.yaml',   # legacy
                    'info[\\\\/]run_exports.json',   # current
                    'info[\\\\/]git',
                    'info[\\\\/]recipe[\\\\/].*',
                    'info[\\\\/]recipe_log.json',
                    'info[\\\\/]recipe.tar',
                    'info[\\\\/]test[\\\\/].*',
                    'info[\\\\/]LICENSE.txt',
                    'info[\\\\/]requires',
                    'info[\\\\/]meta',
                    'info[\\\\/]platform',
                    'info[\\\\/]no_link',
                    'info[\\\\/]link.json',
                    'info[\\\\/]icon.png',
            ))


def _checksum(fd, algorithm, buffersize=65536):
    fd.seek(0)
    hash_impl = getattr(hashlib, algorithm)
    if not hash_impl:
        raise ValueError("Unrecognized hash algorithm: {}".format(algorithm))
    else:
        hash_impl = hash_impl()
    for block in iter(lambda: fd.read(buffersize), b''):
        hash_impl.update(block)
    return hash_impl.hexdigest()


def sha256_checksum(fd):
    return _checksum(fd, 'sha256')


def md5_checksum(fd):
    return _checksum(fd, 'md5')
