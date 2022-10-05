import os
import hashlib

from .utils import TemporaryDirectory

from conda_package_streaming import package_streaming


def validate_converted_files_match(src_file_or_folder, subject, reference_ext=""):
    from .api import extract

    with TemporaryDirectory() as tmpdir:
        if os.path.isdir(src_file_or_folder):
            src_folder = src_file_or_folder
        else:
            extract(
                src_file_or_folder + reference_ext, dest_dir=os.path.join(tmpdir, "src")
            )
            src_folder = os.path.join(tmpdir, "src")

        converted_folder = os.path.join(tmpdir, "converted")
        extract(subject, dest_dir=converted_folder)

        missing_files = set()
        mismatch_size = set()
        for root, dirs, files in os.walk(src_folder):
            for f in files:
                absfile = os.path.join(root, f)
                rp = os.path.relpath(absfile, src_folder)
                destpath = os.path.join(converted_folder, rp)
                if not os.path.islink(destpath):
                    if not os.path.isfile(destpath):
                        missing_files.add(rp)
                    elif os.stat(absfile).st_size != os.stat(destpath).st_size:
                        mismatch_size.add(rp)
    return src_file_or_folder, missing_files, mismatch_size


def hash_fn():
    return hashlib.blake2b()


def validate_converted_files_match_streaming(src_file, reference_file):
    source_set = set()
    reference_set = set()

    def get_fileset(filename):
        fileset = set()
        components = ["info", "pkg"] if str(filename).endswith(".conda") else ["pkg"]
        with open(filename, "rb") as conda_file:
            for component in components:
                for tar, member in package_streaming.stream_conda_component(
                    filename, conda_file, component
                ):
                    hasher = hash_fn()
                    if member.isfile():
                        fd = tar.extractfile(member)
                        assert fd is not None
                        for block in iter(lambda: fd.read(1 << 18), b""):  # type: ignore
                            hasher.update(block)

                    fileset.add((member.name, hasher.digest()))

                # TODO symlinks, permissions

        return fileset

    source_set = get_fileset(src_file)
    reference_set = get_fileset(reference_file)
    if source_set != reference_set:
        return src_file, ["files are missing"], ["sizes are mismatched"]
