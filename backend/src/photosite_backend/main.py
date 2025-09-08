import argparse
import logging
import pathlib
from importlib.metadata import version

from photosite_backend.image import get_images, write_image
from photosite_backend.manifest import generate_manifest, write_manifest

logging.basicConfig(level=logging.INFO)


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

    write_output(args.input_dir, args.output_dir)


def write_output(input_path: pathlib.Path, output_dir: pathlib.Path):
    """
    Reads the images contained within input_dir, writes them, with their EXIF
    sanitized, into the output dir named after the hash of their image contents,
    alongside a manifest file.
    """

    image_paths = get_images(input_path)

    written_files = set()
    manifest = generate_manifest(image_paths)

    for image_path in image_paths:
        output_path = write_image(output_dir, image_path)
        written_files.add(output_path)
        logging.info("Wrote image `%s` to `%s`", image_path.name, output_path)

    manifest_path = write_manifest(output_dir, manifest)
    written_files.add(manifest_path)
    logging.info("Wrote manifest to `%s`", manifest_path)

    return written_files


if __name__ == "__main__":
    main()
