import json
from pathlib import Path

from photosite_backend.manifest import (
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
    manifest = {
        "version": 1,
        "images": {"asdf": {"foo": "bar"}, "hjkl": {"baz": "qux"}},
    }

    manifest_path = write_manifest(tmpdir, manifest)

    with manifest_path.open("r") as file:
        assert json.load(file) == manifest
