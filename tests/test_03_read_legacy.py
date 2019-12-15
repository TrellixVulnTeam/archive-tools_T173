"""Test reading archives from legacy versions.
"""

import datetime
from pathlib import Path
import pytest
from archive import Archive
from conftest import *


testdata = [
    TestDataDir(Path("base"), 0o755),
    TestDataDir(Path("base", "data"), 0o750),
    TestDataDir(Path("base", "empty"), 0o755),
    TestDataFile(Path("base", "msg.txt"), 0o644),
    TestDataFile(Path("base", "data", "rnd.dat"), 0o600),
    TestDataSymLink(Path("base", "s.dat"), Path("data", "rnd.dat")),
]

@pytest.fixture(scope="module")
def legacy_1_0_archive():
    return gettestdata("legacy-1_0.tar.gz")

def test_1_0_check_manifest(legacy_1_0_archive):
    with Archive().open(legacy_1_0_archive) as archive:
        assert archive.manifest.version == "1.0"
        assert isinstance(archive.manifest.date, datetime.datetime)
        assert len(archive.manifest.checksums) > 0
        manifest_path = archive.basedir / ".manifest.yaml"
        assert archive.manifest.metadata == (str(manifest_path),)

def test_1_0_verify(legacy_1_0_archive):
    with Archive().open(legacy_1_0_archive) as archive:
        archive.verify()
