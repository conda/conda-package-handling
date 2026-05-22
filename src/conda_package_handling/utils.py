import contextlib
import hashlib
import logging
import os
import re
import sys
from concurrent.futures import Executor, ProcessPoolExecutor, ThreadPoolExecutor

on_win = sys.platform == "win32"
log = logging.getLogger(__name__)


class DummyExecutor(Executor):
    def map(self, func, *iterables):
        for iterable in iterables:
            for thing in iterable:
                yield func(thing)


def get_executor(processes):
    return DummyExecutor() if processes == 1 else ProcessPoolExecutor(max_workers=processes)


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


def is_info_member_path(path):
    """Return True if ``path`` belongs in the ``info-*`` component (CEP 35)."""
    normalized = path.replace("\\", "/")
    return normalized == "info" or normalized.startswith("info/")


def filter_info_files(files_list, prefix):
    """Return packages files from files list that belong to the ``pkg-*`` component (CEP 35).

    Returns files that go into the ``pkg-*`` component or in other words filter OUT
    files that go into the ``info-*`` component.
    """
    return [f for f in filter_files(files_list, prefix) if not is_info_member_path(f)]


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
