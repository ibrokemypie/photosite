from pathlib import Path

from photosite_backend.manifest import generate_manifest_entry
from photosite_backend.tests import create_test_datafile


def test_generate_manifest_entry(tmp_path: Path):
    create_test_datafile(tmp_path, "photo_1.jpg")

    manifest_entry = generate_manifest_entry(tmp_path / "photo_1.jpg")

    assert manifest_entry == {
        "filename": "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24.jpg",
        "tags": {
            "Make": "OLYMPUS CORPORATION",
            "Model": "E-M10MarkII",
            "DateTime": "2019:10:22 18:00:27",
        },
    }
