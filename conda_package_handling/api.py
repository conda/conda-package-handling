import os as _os

from six import string_types as _string_types
import tqdm

from conda_package_handling.tarball import CondaTarBZ2 as _CondaTarBZ2
from conda_package_handling.conda_fmt import CondaFormat_v2 as _CondaFormat_v2
from conda_package_handling.utils import TemporaryDirectory as _TemporaryDirectory

SUPPORTED_EXTENSIONS = {'.tar.bz2': _CondaTarBZ2,
                        '.conda': _CondaFormat_v2}


def _collect_paths(prefix):
    dir_paths, file_paths = [], []
    for dp, dn, filenames in _os.walk(prefix):
        for f in filenames:
            file_paths.append(_os.path.relpath(_os.path.join(dp, f), prefix))
        dir_paths.extend(_os.path.relpath(_os.path.join(dp, _), prefix) for _ in dn)
    file_list = file_paths + [dp for dp in dir_paths
                              if not any(f.startswith(dp) for f in file_paths)]
    return file_list


def extract(fn, dest_dir=None, components=None):
    if dest_dir:
        if not _os.path.isabs(dest_dir):
            dest_dir = _os.path.normpath(_os.path.join(_os.getcwd(), dest_dir))
        if not _os.path.isdir(dest_dir):
            _os.makedirs(dest_dir)
    for ext in SUPPORTED_EXTENSIONS:
        if fn.endswith(ext):
            SUPPORTED_EXTENSIONS[ext].extract(fn, dest_dir, components=components)
            break
    else:
        raise ValueError("Didn't recognize extension for file '{}'.  Supported extensions are: {}"
                         .format(fn, list(SUPPORTED_EXTENSIONS.keys())))


def create(prefix, file_list, out_fn, out_folder=None, **kw):
    if not out_folder:
        out_folder = _os.getcwd()
    if file_list is None:
        file_list = _collect_paths(prefix)

    elif isinstance(file_list, _string_types):
        try:
            with open(file_list) as f:
                data = f.readlines()
            file_list = [_.strip() for _ in data]
        except:
            raise

    for ext in SUPPORTED_EXTENSIONS:
        if out_fn.endswith(ext):
            out = SUPPORTED_EXTENSIONS[ext].create(prefix, file_list, out_fn, out_folder, **kw)
    return out


def _convert(fn, out_ext, out_folder, **kw):
    basename = None
    for ext in SUPPORTED_EXTENSIONS:
        if fn.endswith(ext):
            basename = _os.path.basename(fn).replace(ext, '')
    if not basename:
        print("Input file %s doesn't have a supported extension (%s), skipping it"
                % (fn, SUPPORTED_EXTENSIONS))
        return
    out_fn = _os.path.join(out_folder, basename + out_ext)
    if _os.path.lexists(out_fn):
        print("Skipping %s because %s already exists" % (fn, out_fn))
    else:
        with _TemporaryDirectory() as tmp:
            extract(fn, dest_dir=tmp)
            file_list = _collect_paths(tmp)
            create(tmp, file_list, _os.path.basename(out_fn), out_folder=out_folder, **kw)
    return fn


def transmute(in_file, out_ext, out_folder=None, **kw):
    from glob import glob
    from concurrent.futures import ProcessPoolExecutor, as_completed
    if not out_folder:
        out_folder = _os.path.dirname(in_file) or _os.getcwd()

    flist = glob(in_file)
    with tqdm.tqdm(total=len(flist)) as t:
        with ProcessPoolExecutor() as executor:
            futures = (executor.submit(_convert, fn, out_ext, out_folder, **kw) for fn in flist)
            for future in as_completed(futures):
                fn = future.result()
                t.set_description("Converted: %s" % fn)
                t.update()


def get_pkg_details(in_file):
    """For the new pkg format, we return the size and hashes of the inner pkg part of the file"""
    for ext in SUPPORTED_EXTENSIONS:
        if in_file.endswith(ext):
            details = SUPPORTED_EXTENSIONS[ext].get_pkg_details(in_file)
            break
    else:
        raise ValueError("Don't know what to do with file {}".format(in_file))
    return details
