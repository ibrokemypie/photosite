"""
This file contains the functions that will generate the manifest file from
the parsed image metadata.
"""

import json
import pathlib
from typing import Iterable, TypedDict

from photosite_backend.image import (
    hash_image,
    read_tags,
)

MANIFEST_VERSION = 2


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
    created_date: str | None
    keyword_tags: list[str]


def generate_manifest_entry(image_path: pathlib.Path):
    image_hash = hash_image(image_path)
    image_tags = read_tags(image_path)

    # in order of preference, check all these tags for the date
    possible_date_tags = ["EXIF:DateTimeOriginal", "EXIF:CreateDate"]
    created_date = None
    for tag in possible_date_tags:
        if not created_date and tag in image_tags:
            created_date = image_tags[tag]

    keywords = []
    possible_keyword_tags = ["IPTC:Keywords", "XMP:Subject", "XMP:HierarchicalSubject"]
    for tag in possible_keyword_tags:
        if not keywords and tag in image_tags:
            keywords = image_tags[tag]

    # deduplicate
    keywords = list(set(keywords))

    return ManifestEntry(
        filename=f"{image_hash}{image_path.suffix}",
        created_date=created_date,
        keyword_tags=sorted(keywords),
    )


def write_manifest(output_dir: pathlib.Path, manifest_contents: dict):
    manifest_path = output_dir / "manifest.json"

    with manifest_path.open("w") as file:
        json.dump(manifest_contents, file)

    return manifest_path
