"""
This file contains the functions that will generate the manifest file from
the parsed image metadata.
"""

import json
import pathlib
from typing import Any, Iterable, TypedDict

from photosite_backend.image import (
    filter_tags,
    hash_image,
    read_tags,
)

MANIFEST_VERSION = 1


def generate_manifest(image_paths: Iterable[pathlib.Path]):
    return {
        "version": MANIFEST_VERSION,
        "images": {
            hash_image(image_path): generate_manifest_entry(image_path)
            for image_path in image_paths
        },
    }


class ManifestEntry(TypedDict):
    filename: str
    tags: dict[str, Any]


def generate_manifest_entry(image_path: pathlib.Path):
    image_hash = hash_image(image_path)
    image_tags = read_tags(image_path)
    filtered_tags = filter_tags(image_tags)

    return ManifestEntry(
        filename=f"{image_hash}{image_path.suffix}",
        tags=filtered_tags,
    )


def write_manifest(output_dir: pathlib.Path, manifest_contents: dict):
    manifest_path = output_dir / "manifest.json"

    with manifest_path.open("w") as file:
        json.dump(manifest_contents, file)

    return manifest_path
