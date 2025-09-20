import json
from pathlib import Path

from photosite_backend.backends import get_fs
from photosite_backend.manifest import (
    Manifest,
    ManifestEntry,
    generate_manifest_entry,
    write_manifest,
)
from photosite_backend.tests import create_test_datafile


def test_generate_manifest_entry(tmp_path: Path):
    create_test_datafile(tmp_path, "photo_6.jpg")

    manifest_entry = generate_manifest_entry(tmp_path / "photo_6.jpg")

    expected = ManifestEntry(
        filename="c4f25abf6a3fdfa308a2f4b0027666e54dc8562f8d60ec8ae69dec75525225e0.jpg",
        created_date="2025:09:11 16:30:37",
        keyword_tags=["animal", "cat"],
    )

    assert manifest_entry == expected


def test_write_manifest(tmpdir):
    manifest = Manifest(
        version=1,
        images={
            "asdf": {"filename": "bar", "created_date": "", "keyword_tags": []},
            "hjkl": {"filename": "qux", "created_date": "", "keyword_tags": []},
        },
    )

    dest_fs = get_fs(str(tmpdir), "dir")

    write_manifest(dest_fs, manifest)

    with dest_fs.open("manifest.json", "rb") as file:
        assert json.load(file) == manifest
