#!/usr/bin/env python3
"""Convert HEIC/HEIF photos in a folder to JPG, PNG, or WebP.

Install dependencies:
    conda create -n heic-convert -c conda-forge python=3.11 pillow pillow-heif
    conda activate heic-convert

Examples:
    python convert_heic.py photo/summer26europe
    python convert_heic.py photo/summer26europe --format png
    python convert_heic.py photo/summer26europe --format webp
    python convert_heic.py photo/summer26europe --format webp --lossless
    python convert_heic.py photo/summer26europe --recursive --quality 90
"""

import argparse
import sys
from pathlib import Path


SUPPORTED_EXTENSIONS = {".heic", ".heif"}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Convert HEIC/HEIF images in a folder to JPG, PNG, or WebP."
    )
    parser.add_argument(
        "folder",
        type=Path,
        help="Folder containing HEIC/HEIF images.",
    )
    parser.add_argument(
        "-f",
        "--format",
        choices=("jpg", "png", "webp"),
        default="png",
        help="Output image format. Default: png.",
    )
    parser.add_argument(
        "-q",
        "--quality",
        type=int,
        default=95,
        help="Output quality from 1 to 100. Applies to JPG and lossy WebP. Default: 95.",
    )
    parser.add_argument(
        "-r",
        "--recursive",
        action="store_true",
        help="Also convert images in subfolders.",
    )
    parser.add_argument(
        "--overwrite",
        action="store_true",
        help="Replace existing output files.",
    )
    parser.add_argument(
        "--lossless",
        action="store_true",
        help="Use lossless WebP. Only applies when --format webp.",
    )
    return parser.parse_args()


def iter_heic_files(folder: Path, recursive: bool) -> list[Path]:
    pattern = "**/*" if recursive else "*"
    return sorted(
        path
        for path in folder.glob(pattern)
        if path.is_file() and path.suffix.lower() in SUPPORTED_EXTENSIONS
    )


def build_save_options(image, output_format: str, quality: int, lossless: bool) -> dict:
    save_options = {}

    if "icc_profile" in image.info:
        save_options["icc_profile"] = image.info["icc_profile"]
    if "exif" in image.info:
        save_options["exif"] = image.info["exif"]

    if output_format == "jpg":
        save_options.update(
            quality=quality,
            subsampling=0,
            optimize=True,
        )
    elif output_format == "png":
        save_options["optimize"] = True
    elif lossless:
        save_options.update(
            lossless=True,
            quality=100,
        )
    else:
        save_options["quality"] = quality

    return save_options


def convert_image(
    source: Path,
    output_format: str,
    quality: int,
    overwrite: bool,
    lossless: bool,
) -> str:
    from PIL import Image
    from pillow_heif import register_heif_opener

    register_heif_opener()

    target_suffixes = {
        "jpg": ".jpg",
        "png": ".png",
        "webp": ".webp",
    }
    save_formats = {
        "jpg": "JPEG",
        "png": "PNG",
        "webp": "WEBP",
    }
    target_suffix = target_suffixes[output_format]
    target = source.with_suffix(target_suffix)

    if target.exists() and not overwrite:
        return f"Skipped existing: {target}"

    with Image.open(source) as image:
        save_options = build_save_options(image, output_format, quality, lossless)
        converted = image.convert("RGB")
        converted.save(target, save_formats[output_format], **save_options)

    return f"Converted: {source} -> {target}"


def main() -> int:
    args = parse_args()

    if not args.folder.is_dir():
        print(f"Error: folder does not exist: {args.folder}", file=sys.stderr)
        return 1

    if not 1 <= args.quality <= 100:
        print("Error: --quality must be between 1 and 100.", file=sys.stderr)
        return 1

    if args.lossless and args.format != "webp":
        print("Error: --lossless only applies when --format webp.", file=sys.stderr)
        return 1

    try:
        import PIL  # noqa: F401
        import pillow_heif  # noqa: F401
    except ImportError:
        print(
            "Error: missing dependencies. Install them with:\n"
            "  conda install -c conda-forge pillow pillow-heif",
            file=sys.stderr,
        )
        return 1

    files = iter_heic_files(args.folder, args.recursive)
    if not files:
        print(f"No HEIC/HEIF files found in: {args.folder}")
        return 0

    for source in files:
        try:
            print(
                convert_image(
                    source,
                    args.format,
                    args.quality,
                    args.overwrite,
                    args.lossless,
                )
            )
        except Exception as exc:
            print(f"Failed: {source}: {exc}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
