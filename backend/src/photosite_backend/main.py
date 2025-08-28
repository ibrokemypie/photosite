import argparse
import pathlib
from importlib.metadata import version


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
        required=True,
    )
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version="%(prog)s {version}".format(version=version("photosite_backend")),
    )

    args = parser.parse_args()
    print(args)


if __name__ == "__main__":
    main()
