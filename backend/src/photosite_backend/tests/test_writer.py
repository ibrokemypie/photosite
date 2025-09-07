import json

from photosite_backend.writer import write_manifest


def test_write_manifest(tmpdir):
    manifest = {
        "version": 1,
        "images": {"asdf": {"foo": "bar"}, "hjkl": {"baz": "qux"}},
    }

    manifest_path = write_manifest(tmpdir, manifest)

    with manifest_path.open("r") as file:
        assert json.load(file) == manifest
