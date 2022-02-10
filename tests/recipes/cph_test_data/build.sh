cd "${PREFIX}"
umask 022

mkdir -p bin lib libexec share/terminfo

echo -e '#/bin/sh\necho hello world' > bin/hello-1.0
chmod 755 bin/hello-1.0

echo -n "" >share/terminfo/xterm.dat
chmod 644 share/terminfo/xterm.dat


# Tests for symlink...
pushd bin >/dev/null
ln -sn hello-1.0 hello                  # ...to file in same dir
popd >/dev/null

pushd libexec >/dev/null
ln -sn ../bin/hello greetings           # ...to file in another dir
popd >/dev/null

pushd share >/dev/null
ln -sn terminfo termcap                 # ...to subdir in same dir
popd >/dev/null

pushd lib >/dev/null
ln -sn ../share/terminfo terminfo       # ...to subdir of another dir
ln -sn libdangle.lib.1 libdangle.lib    # ...dangling link
popd >/dev/null
