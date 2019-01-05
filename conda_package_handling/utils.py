import contextlib
import os
import re

from six import string_types


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
