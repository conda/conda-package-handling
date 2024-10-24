import contextlib
import hashlib
import logging
import os
import re
import sys
import warnings as _warnings
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor
from tempfile import mkdtemp

on_win = sys.platform == "win32"
log = logging.getLogger(__name__)


class DummyExecutor(Executor):
    def map(self, func, *iterables):
        for iterable in iterables:
            for thing in iterable:
                yield func(thing)


def get_executor(processes):
    return DummyExecutor() if processes == 1 else ProcessPoolExecutor(max_workers=processes)


# we have our own TemporaryDirectory class because it's faster and handles disk issues better.
class TemporaryDirectory:
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

    def __init__(self, suffix="", prefix=".cph_tmp", dir=os.getcwd()):
        self.name = mkdtemp(suffix, prefix, dir)

    def __repr__(self):
        return f"<{self.__class__.__name__} {self.name!r}>"

    def __enter__(self):
        return self.name

    def cleanup(self, _warn=False, _warnings=_warnings):
        if self.name and not self._closed:
            try:
                rm_rf(self.name)
            except:
                _warnings.warn(
                    'Conda-package-handling says: "I tried to clean up, '
                    "but I could not.  There is a mess in %s that you might "
                    'want to clean up yourself.  Sorry..."' % self.name
                )
            self._closed = True
            if _warn and _warnings.warn:
                _warnings.warn(
                    f"Implicitly cleaning up {self!r}",
                    _warnings.ResourceWarning,
                )

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
    if isinstance(arg, str) or not hasattr(arg, "__iter__"):
        if arg is not None:
            arg = [arg]
        else:
            arg = []
    return arg


def filter_files(
    files_list,
    prefix,
    filter_patterns=(
        r"(.*[\\\\/])?\.git[\\\\/].*",
        r"(.*[\\\\/])?\.git$",
        r"(.*)?\.DS_Store.*",
        r".*\.la$",
        r"conda-meta.*",
    ),
):
    """Remove things like the .git directory from the list of files to be copied"""
    for pattern in filter_patterns:
        r = re.compile(pattern)
        files_list = set(files_list) - set(filter(r.match, files_list))
    return [
        f
        for f in files_list
        if
        # `islink` prevents symlinks to directories from being removed
        os.path.islink(os.path.join(prefix, f)) or not os.path.isdir(os.path.join(prefix, f))
    ]


def filter_info_files(files_list, prefix):
    return filter_files(
        files_list,
        prefix,
        filter_patterns=(
            "info[\\\\/]index\\.json",
            "info[\\\\/]files",
            "info[\\\\/]paths\\.json",
            "info[\\\\/]about\\.json",
            "info[\\\\/]has_prefix",
            "info[\\\\/]hash_input_files",  # legacy, not used anymore
            "info[\\\\/]hash_input\\.json",
            "info[\\\\/]run_exports\\.yaml",  # legacy
            "info[\\\\/]run_exports\\.json",  # current
            "info[\\\\/]git",
            "info[\\\\/]recipe[\\\\/].*",
            "info[\\\\/]recipe_log.json",
            "info[\\\\/]recipe.tar",
            "info[\\\\/]test[\\\\/].*",
            "info[\\\\/]LICENSE.*",
            "info[\\\\/]requires",
            "info[\\\\/]meta",
            "info[\\\\/]platform",
            "info[\\\\/]no_link",
            "info[\\\\/]link\\.json",
            "info[\\\\/]icon\\.png",
        ),
    )


def _checksum(fd, algorithm, buffersize=65536):
    hash_impl = hashlib.new(algorithm)
    for block in iter(lambda: fd.read(buffersize), b""):
        hash_impl.update(block)
    return hash_impl.hexdigest()


def sha256_checksum(fd):
    return _checksum(fd, "sha256")


def md5_checksum(fd):
    return _checksum(fd, "md5")


def checksum(fn, algorithm, buffersize=1 << 18):
    """
    Calculate a checksum for a filename (not an open file).
    """
    with open(fn, "rb") as fd:
        return _checksum(fd, algorithm, buffersize)


def checksums(fn, algorithms, buffersize=1 << 18):
    """
    Calculate multiple checksums for a filename in parallel.
    """
    with ThreadPoolExecutor(max_workers=len(algorithms)) as e:
        # take care not to share hash_impl between threads
        results = [e.submit(checksum, fn, algorithm, buffersize) for algorithm in algorithms]
    return [result.result() for result in results]


def anonymize_tarinfo(tarinfo):
    """
    Remove user id, name from tarinfo.
    """
    # also remove timestamps?
    tarinfo.uid = 0
    tarinfo.uname = ""
    tarinfo.gid = 0
    tarinfo.gname = ""
    return tarinfo
