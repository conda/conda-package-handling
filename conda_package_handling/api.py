import os as _os
from tempfile import TemporaryDirectory as _TemporaryDirectory

from six import string_types as _string_types
import tqdm

from conda_package_handling.tarball import CondaTarBZ2 as _CondaTarBZ2
from conda_package_handling.conda_fmt import CondaFormat_v2 as _CondaFormat_v2

SUPPORTED_EXTENSIONS = {'.tar.bz2': _CondaTarBZ2,
                        '.conda': _CondaFormat_v2}


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
        file_list = [_os.path.relpath(_os.path.join(dp, f), prefix)
                     for dp, dn, filenames in _os.walk(prefix)
                     for f in filenames]
    elif isinstance(file_list, _string_types):
        try:
            with open(file_list) as f:
                data = f.readlines()
            file_list = [_.strip() for _ in data]
        except:
            raise

    for ext in SUPPORTED_EXTENSIONS:
        if out_fn.endswith(ext):
            SUPPORTED_EXTENSIONS[ext].create(prefix, file_list, out_fn, out_folder, **kw)


def transmute(in_file, out_ext, out_folder=None, **kw):
    from glob import glob
    if not out_folder:
        out_folder = _os.path.dirname(in_file) or _os.getcwd()

    def _convert(fn):
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
                file_list = [_os.path.relpath(_os.path.join(dp, f), tmp)
                            for dp, dn, filenames in _os.walk(tmp)
                            for f in filenames]
                create(tmp, file_list, _os.path.basename(out_fn), out_folder=out_folder, **kw)

    # TODO: parallelize?  Maybe this is better left to the terminal (xargs?)
    flist = glob(in_file)
    with tqdm.tqdm(total=len(flist)) as t:
        for fn in flist:
            t.set_description("Converting: %s" % fn)
            t.update()
            _convert(fn)
