import os
from tempfile import TemporaryDirectory

from conda_package_handling import api


def write_package_dir(prefix: str, files: dict[str, str]):
    """Write a package directory tree under ``prefix``.

    ``files`` maps archive-relative paths to file contents. Parent directories
    are created as needed.
    """
    for relpath, content in files.items():
        path = prefix / relpath
        parent = path.parent
        if parent:
            parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")


def component_member_paths(conda_path: str, component: str):
    """Return member paths from one .conda inner tarball.

    Extracts only ``component`` (``"info"`` or ``"pkg"``) from ``conda_path``
    into a temp dir and returns the archive-relative paths of regular files.
    """
    with TemporaryDirectory() as root:
        api.extract(conda_path, root, components=component)
        paths = set()
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                relpath = os.path.relpath(os.path.join(dirpath, filename), root)
                paths.add(relpath.replace("\\", "/"))
        return paths
