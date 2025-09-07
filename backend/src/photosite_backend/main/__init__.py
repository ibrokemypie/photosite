import argparse
import pathlib
from importlib.metadata import version
from pprint import pprint

from photosite_backend.image import get_images
from photosite_backend.manifest import generate_manifest


def return_hi():
    return "hi!"


def main():
    parser = argparse.ArgumentParser(
        prog="photosite-backend",
        description="Generator of manifests for my photography website",
    )
    parser.add_argument(
        "-i",
        "--input-dir",
        type=pathlib.Path,
        help="Path to the directory containing the photos to import",
        required=True,
    )
    parser.add_argument(
        "-o",
        "--output-dir",
        type=pathlib.Path,
        help="Path to the directory the manifest and sanitized images will be written to.",
        default="./",
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=version("photosite_backend")),
    )

    args = parser.parse_args()
    print(pprint(generate_manifest(get_images(args.input_dir))))


if __name__ == "__main__":
    main()
