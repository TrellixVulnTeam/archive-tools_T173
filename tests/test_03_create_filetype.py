"""Tests related to the type of files while creating archives.
"""

import os
from pathlib import Path
import socket
import pytest
from archive import Archive
from archive.exception import ArchiveInvalidTypeError
from conftest import setup_testdata, check_manifest


# Setup a directory with some test data to be put into an archive.
# Make sure that we have all kind of different things in there.
testdata = {
    "dirs": [
        (Path("base"), 0o755),
        (Path("base", "data"), 0o750),
        (Path("base", "empty"), 0o755),
    ],
    "files": [
        (Path("base", "msg.txt"), 0o644),
        (Path("base", "data", "rnd.dat"), 0o600),
    ],
    "symlinks": [
        (Path("base", "s.dat"), Path("data", "rnd.dat")),
    ]
}

@pytest.fixture(scope="module")
def test_dir(tmpdir):
    setup_testdata(tmpdir, **testdata)
    return tmpdir

class tmp_socket():
    """A context manager temporarily creating a unix socket.
    """
    def __init__(self, path):
        self.path = path
        self.socket = socket.socket(socket.AF_UNIX)
        self.socket.bind(str(self.path))
    def __enter__(self):
        return self.socket
    def __exit__(self, type, value, tb):
        self.socket.close()
        self.path.unlink()

class tmp_fifo():
    """A context manager temporarily creating a FIFO.
    """
    def __init__(self, path):
        self.path = path
        os.mkfifo(str(self.path))
    def __enter__(self):
        return self.path
    def __exit__(self, type, value, tb):
        self.path.unlink()

@pytest.mark.xfail(raises=ArchiveInvalidTypeError, reason="Issue #34")
def test_create_invalid_file_socket(test_dir, archive_name, monkeypatch):
    """Create an archive from a directory containing a socket.
    """
    monkeypatch.chdir(str(test_dir))
    p = Path("base")
    with tmp_socket(p / "socket"):
        Archive().create(archive_name, "", [p])
    with Archive().open(archive_name) as archive:
        assert archive.basedir == Path("base")
        check_manifest(archive.manifest, **testdata)
        archive.verify()

@pytest.mark.xfail(raises=ArchiveInvalidTypeError, reason="Issue #34")
def test_create_invalid_file_fifo(test_dir, archive_name, monkeypatch):
    """Create an archive from a directory containing a FIFO.
    """
    monkeypatch.chdir(str(test_dir))
    p = Path("base")
    with tmp_fifo(p / "fifo"):
        Archive().create(archive_name, "", [p])
    with Archive().open(archive_name) as archive:
        assert archive.basedir == Path("base")
        check_manifest(archive.manifest, **testdata)
        archive.verify()
