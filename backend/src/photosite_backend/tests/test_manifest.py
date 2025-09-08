import json
from pathlib import Path

from photosite_backend.manifest import generate_manifest_entry, write_manifest
from photosite_backend.tests import create_test_datafile


def test_generate_manifest_entry(tmp_path: Path):
    create_test_datafile(tmp_path, "photo_1.jpg")

    manifest_entry = generate_manifest_entry(tmp_path / "photo_1.jpg")

    assert (
        manifest_entry["filename"]
        == "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24.jpg"
    )

    expected_tags = {
        "EXIF:Make": "OLYMPUS CORPORATION",
        "EXIF:Model": "E-M10MarkII",
        "EXIF:DateTimeOriginal": "2017:01:06 11:05:48",
        "IPTC:DateCreated": "2017:01:06",
        "Composite:DigitalCreationDateTime": "2017:01:06 11:05:48",
        "Photoshop:IPTCDigest": "eb27960dc5edfa1c57448a87db5f2f2a",
    }
    expected = set(expected_tags.items())
    actual = set(manifest_entry["tags"].items())

    assert expected.issubset(actual)

    assert expected_tags.items() <= manifest_entry["tags"].items()


def test_write_manifest(tmpdir):
    manifest = {
        "version": 1,
        "images": {"asdf": {"foo": "bar"}, "hjkl": {"baz": "qux"}},
    }

    manifest_path = write_manifest(tmpdir, manifest)

    with manifest_path.open("r") as file:
        assert json.load(file) == manifest
