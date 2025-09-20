import json
import logging
from pathlib import Path
from unittest import mock

import pytest

from photosite_backend.main import add, hash, remove, sync
from photosite_backend.manifest import Manifest
from photosite_backend.tests import create_test_datafile


class TestHashCommand:
    def test_no_file(self):
        path = Path("no_file")
        with pytest.raises(FileNotFoundError):
            hash(path)

    def test_with_file(self, tmp_path: Path, caplog):
        path = create_test_datafile(tmp_path, "photo_1.jpg")

        caplog.set_level(logging.INFO)

        hash(path)
        assert (
            "Hash of `photo_1.jpg`: `f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24`"
            in caplog.text
        )


class TestSync:
    def test_no_sources(self, tmp_path):
        in_path = tmp_path / "in"
        out_path = tmp_path / "out"
        in_path.mkdir()
        out_path.mkdir()

        sync(in_path, out_path)

        expected_manifest_path = out_path / "manifest.json"
        assert list(out_path.glob("*")) == [expected_manifest_path]

        with expected_manifest_path.open() as file:
            manifest_contents: Manifest = json.load(file)

        assert manifest_contents["images"] == {}

    def test_with_sources(self, tmp_path):
        in_path = tmp_path / "in"
        out_path = tmp_path / "out"
        in_path.mkdir()
        out_path.mkdir()

        files = ["photo_1.jpg", "photo_2.jpg", "photo_3.jpg"]
        for file in files:
            create_test_datafile(in_path, file)

        sync(in_path, out_path)

        with (out_path / "manifest.json").open() as file:
            manifest_contents: Manifest = json.load(file)

        manifest_images = list(manifest_contents["images"].keys())
        assert len(manifest_images) == len(files)

        expected_files = [
            out_path / "manifest.json",
            *[out_path / (hash + ".jpg") for hash in manifest_images],
        ]
        assert sorted(list(out_path.glob("*"))) == sorted(expected_files)


class TestAddCommand:
    def test_no_manifest(self, tmp_path):
        in_path = tmp_path / "in"
        out_path = tmp_path / "out"
        in_path.mkdir()
        out_path.mkdir()

        create_test_datafile(in_path, "photo_1.jpg")

        image_path = in_path / "photo_1.jpg"
        add(out_path, image_path)

        with (out_path / "manifest.json").open() as file:
            manifest_contents: Manifest = json.load(file)

        manifest_images = list(manifest_contents["images"].keys())
        assert manifest_images == [
            "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24"
        ]

        assert sorted(list(out_path.glob("*"))) == sorted(
            [
                out_path / "manifest.json",
                out_path
                / "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24.jpg",
            ]
        )

    def test_existing_manifest(self, tmp_path):
        in_path = tmp_path / "in"
        out_path = tmp_path / "out"
        in_path.mkdir()
        out_path.mkdir()

        create_test_datafile(in_path, "photo_1.jpg")
        create_test_datafile(in_path, "photo_2.jpg")

        add(out_path, in_path / "photo_1.jpg")
        add(out_path, in_path / "photo_2.jpg")

        with (out_path / "manifest.json").open() as file:
            manifest_contents: Manifest = json.load(file)

        manifest_images = list(manifest_contents["images"].keys())
        assert manifest_images == [
            "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24",
            "c6e9ec51b31e15299990d475ac83e70ebde470f5a66e6ddfb0fce341caaff6ea",
        ]

        assert sorted(list(out_path.glob("*"))) == sorted(
            [
                out_path / "manifest.json",
                out_path
                / "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24.jpg",
                out_path
                / "c6e9ec51b31e15299990d475ac83e70ebde470f5a66e6ddfb0fce341caaff6ea.jpg",
            ]
        )


class TestRemoveCommand:
    def test_remove_no_manifest(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            remove(tmp_path, "asdf")

    def test_remove_missing(self, tmp_path, caplog):
        in_path = tmp_path / "in"
        out_path = tmp_path / "out"
        in_path.mkdir()
        out_path.mkdir()

        image_path = create_test_datafile(in_path, "photo_1.jpg")
        add(out_path, image_path)

        def fake_exit(code):
            raise Exception(code)

        with (
            pytest.raises(Exception),
            mock.patch("photosite_backend.main.exit", fake_exit),
        ):
            remove(out_path, "asdf")

        assert "Provided hash `asdf` not found in the manifest!" in caplog.text

    def test_remove_existing(self, tmp_path):
        in_path = tmp_path / "in"
        out_path = tmp_path / "out"
        in_path.mkdir()
        out_path.mkdir()

        image_path = create_test_datafile(in_path, "photo_1.jpg")
        add(out_path, image_path)

        hash = "f85e656b84e9bd44354f02bd224b7eb9140f8a09e144ad469b1222b968082b24"

        remove(out_path, hash)

        assert list(out_path.glob("*")) == [out_path / "manifest.json"]

        with (out_path / "manifest.json").open() as file:
            manifest_contents: Manifest = json.load(file)

        manifest_images = list(manifest_contents["images"].keys())
        assert manifest_images == []
