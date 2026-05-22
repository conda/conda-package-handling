import os
from collections.abc import Mapping
from tempfile import TemporaryDirectory

from conda_package_handling import api


def write_package_dir(prefix, files: Mapping[str, str | bytes]):
    """Write a package directory tree under ``prefix``.

    ``files`` maps archive-relative paths to file contents. Parent directories
    are created as needed.
    """
    for relpath, content in files.items():
        path = os.path.join(prefix, relpath)
        parent = os.path.dirname(path)
        if parent:
            os.makedirs(parent, exist_ok=True)
        if isinstance(content, bytes):
            with open(path, "wb") as f:
                f.write(content)
        else:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)


def component_member_paths(conda_path, component):
    """Return member paths from one .conda inner tarball.

    Extracts only ``component`` (``"info"`` or ``"pkg"``) from ``conda_path``
    into a temp dir and returns the archive-relative paths of regular files.
    """
    with TemporaryDirectory() as root:
        api.extract(conda_path, root, components=component)
        paths = set()
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                paths.add(os.path.relpath(os.path.join(dirpath, filename), root))
        return paths
