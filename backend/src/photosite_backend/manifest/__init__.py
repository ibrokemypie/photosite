"""
This file contains the functions that will generate the manifest file from
the parsed image metadata.
"""

import pathlib
from typing import Iterable

from photosite_backend.reader import hash_image, read_tags

MANIFEST_VERSION = 1


def generate_manifest(image_paths: Iterable[pathlib.Path]):
    return {
        "version": MANIFEST_VERSION,
        "images": {
            hash_image(image_path): generate_manifest_entry(image_path)
            for image_path in image_paths
        },
    }


def generate_manifest_entry(image_path: pathlib.Path):
    image_hash = hash_image(image_path)
    image_tags = read_tags(image_path)

    return {"filename": f"{image_hash}{image_path.suffix}", "tags": image_tags}
