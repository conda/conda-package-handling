#!/usr/bin/env python
# Create pkg_with_unicode.tar.bz2 with files which contain unicode names
import os
import tarfile
import tempfile


with tempfile.TemporaryDirectory() as tmpdirname:
    curdir = os.getcwd()
    os.chdir(tmpdirname)
    # root directory
    with open('simple_file', 'w') as f:
        f.write("simple text")
    with open('❤', 'w') as f:
        f.write("unicode ❤ text")
    with open('❤.bat', 'w') as f:
        f.write("more unicode ❤ text")
    # directory with unicode
    dirname1 = 'dir_with_λ_unicode'
    os.mkdir(dirname1)
    with open(os.path.join(dirname1, 'a_file'), 'w') as f:
        f.write("blah❤")
    # another directory with unicode
    dirname2 = 'λλλ_another_dir_λλλ'
    os.mkdir(dirname2)
    with open(os.path.join(dirname2, 'another_λ'), 'w') as f:
        f.write("blah")
    with open(os.path.join(dirname2, 'λλλ_third'), 'w') as f:
        f.write("blah")
    # create a tarball with the above files
    tarball_path = os.path.join(curdir, 'pkg_with_unicode.tar.bz2')
    with tarfile.open(tarball_path, "w|bz2") as tarball:
        tarball.add('simple_file')
        tarball.add('❤')
        tarball.add('❤.bat')
        tarball.add(dirname1)
        tarball.add(dirname2)
    os.chdir(curdir)
