import os
import shutil
import sys
from pathlib import Path
from textwrap import dedent

import pytest
from xprocess import ProcessStarter


@pytest.fixture(scope="function")
def testing_workdir(tmpdir, request):
    """Create a workdir in a safe temporary folder; cd into dir above before test, cd out after

    :param tmpdir: py.test fixture, will be injected
    :param request: py.test fixture-related, will be injected (see pytest docs)
    """

    saved_path = os.getcwd()

    tmpdir.chdir()
    # temporary folder for profiling output, if any
    tmpdir.mkdir("prof")

    def return_to_saved_path():
        if os.path.isdir(os.path.join(saved_path, "prof")):
            profdir = tmpdir.join("prof")
            files = profdir.listdir("*.prof") if profdir.isdir() else []

            for f in files:
                shutil.copy(str(f), os.path.join(saved_path, "prof", f.basename))
        os.chdir(saved_path)

    request.addfinalizer(return_to_saved_path)

    return str(tmpdir)


@pytest.fixture(scope="session")
def localserver(xprocess):
    port = 8000
    datadir = Path(__file__).parent / "data"

    class Starter(ProcessStarter):
        pattern = "Hit Ctrl-C to quit."
        terminate_on_interrupt = True
        timeout = 10
        args = [
            sys.executable,
            "-u",  # unbuffered
            "-c",
            # Adapted from conda-package-streaming/tests/server.py
            dedent(
                f"""
                from bottle import route, run, static_file

                @route("/<filename>", "GET")
                def serve_file(filename):
                    mimetype = "auto"
                    # from https://repo.anaconda.com/ behavior:
                    if filename.endswith(".tar.bz2"):
                        mimetype = "application/x-tar"
                    elif filename.endswith(".conda"):
                        mimetype = "binary/octet-stream"
                    return static_file(filename, root="{datadir.as_posix()}", mimetype=mimetype)

                run(port={port})
                """
            ),
        ]

    pid, logfile = xprocess.ensure("bottle.server", Starter)
    print("Logfile at", str(logfile))
    yield f"http://localhost:{port}"
    xprocess.getinfo("bottle.server").terminate()
