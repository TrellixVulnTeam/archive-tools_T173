"""Test error conditions during verifying an archive.
"""

import os
from pathlib import Path
import shutil
import stat
import tarfile
import time
import pytest
from archive import Archive
from archive.exception import ArchiveVerifyError
from archive.manifest import Manifest
from conftest import tmpdir, archive_name, setup_testdata


# Setup a directory with some test data to be put into an archive.
# Make sure that we have all kind if different things in there.
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

@pytest.fixture(scope="function")
def test_data(tmpdir, monkeypatch):
    monkeypatch.chdir(str(tmpdir))
    shutil.rmtree("base", ignore_errors=True)
    setup_testdata(tmpdir, **testdata)
    manifest = Manifest(paths=[Path("base")])
    with open("manifest.yaml", "wb") as f:
        manifest.write(f)
    return tmpdir

def create_archive(archive_path):
    with tarfile.open(archive_path, "w") as tarf:
        with open("manifest.yaml", "rb") as f:
            manifest_info = tarf.gettarinfo(arcname="base/.manifest.yaml", 
                                            fileobj=f)
            manifest_info.mode = stat.S_IFREG | 0o444
            tarf.addfile(manifest_info, f)
        tarf.add("base")

def test_verify_missing(test_data, archive_name):
    path = Path("base", "msg.txt")
    mtime_parent = os.stat(str(path.parent)).st_mtime
    path.unlink()
    os.utime(str(path.parent), times=(mtime_parent, mtime_parent))
    create_archive(archive_name)
    archive = Archive(archive_name, mode="r")
    with pytest.raises(ArchiveVerifyError) as err:
        archive.verify()
    assert "%s: missing" % path in str(err.value)

def test_verify_wrong_mode_file(test_data, archive_name):
    path = Path("base", "data", "rnd.dat")
    path.chmod(0o644)
    create_archive(archive_name)
    archive = Archive(archive_name, mode="r")
    with pytest.raises(ArchiveVerifyError) as err:
        archive.verify()
    assert "%s: wrong mode" % path in str(err.value)

def test_verify_wrong_mode_dir(test_data, archive_name):
    path = Path("base", "data")
    path.chmod(0o755)
    create_archive(archive_name)
    archive = Archive(archive_name, mode="r")
    with pytest.raises(ArchiveVerifyError) as err:
        archive.verify()
    assert "%s: wrong mode" % path in str(err.value)

def test_verify_wrong_mtime(test_data, archive_name):
    path = Path("base", "msg.txt")
    hour_ago = time.time() - 3600
    os.utime(str(path), times=(hour_ago, hour_ago))
    create_archive(archive_name)
    archive = Archive(archive_name, mode="r")
    with pytest.raises(ArchiveVerifyError) as err:
        archive.verify()
    assert "%s: wrong modification time" % path in str(err.value)

def test_verify_wrong_type(test_data, archive_name):
    path = Path("base", "msg.txt")
    mode = os.stat(str(path)).st_mode
    mtime = os.stat(str(path)).st_mtime
    mtime_parent = os.stat(str(path.parent)).st_mtime
    path.unlink()
    path.mkdir()
    path.chmod(mode)
    os.utime(str(path), times=(mtime, mtime))
    os.utime(str(path.parent), times=(mtime_parent, mtime_parent))
    create_archive(archive_name)
    archive = Archive(archive_name, mode="r")
    with pytest.raises(ArchiveVerifyError) as err:
        archive.verify()
    assert "%s: wrong type" % path in str(err.value)

def test_verify_wrong_checksum(test_data, archive_name):
    path = Path("base", "data", "rnd.dat")
    stat = os.stat(str(path))
    mode = stat.st_mode
    mtime = stat.st_mtime
    size = stat.st_size
    with path.open("wb") as f:
        f.write(b'0' * size)
    path.chmod(mode)
    os.utime(str(path), times=(mtime, mtime))
    create_archive(archive_name)
    archive = Archive(archive_name, mode="r")
    with pytest.raises(ArchiveVerifyError) as err:
        archive.verify()
    assert "%s: checksum" % path in str(err.value)

def test_verify_ok(test_data, archive_name):
    create_archive(archive_name)
    archive = Archive(archive_name, mode="r")
    archive.verify()