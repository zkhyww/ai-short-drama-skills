#!/usr/bin/env python3
"""Build validated official Dreamina CLI commands without submitting them."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Iterable, Sequence


VIDEO_RATIOS = {"1:1", "3:4", "16:9", "4:3", "9:16", "21:9"}
IMAGE_RATIOS = {"21:9", "16:9", "3:2", "4:3", "1:1", "3:4", "2:3", "9:16"}
# The short-clip default is resolved below; individual clips over 15s use 2.5.
DEFAULT_VIDEO_MODEL = "seedance2.0fast_vip"
SEEDANCE_20_MODELS = {
    "seedance2.0",
    "seedance2.0fast",
    "seedance2.0_vip",
    "seedance2.0fast_vip",
    "seedance2.0mini",
}
VIDEO_MODELS = SEEDANCE_20_MODELS | {"seedance2.5"}
IMAGE_MODELS = {"3.0", "3.1", "4.0", "4.1", "4.5", "4.6", "4.7", "5.0", "5.0Pro"}


def _flag(name: str, value: object) -> str:
    return f"--{name}={value}"


def _require_prompt(prompt: str) -> str:
    prompt = prompt.strip()
    if not prompt:
        raise ValueError("prompt must not be empty")
    return prompt


IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


def _existing_paths(paths: Iterable[str | Path], label: str) -> list[Path]:
    resolved: list[Path] = []
    for raw_path in paths:
        path = Path(raw_path).expanduser().resolve()
        if not path.is_file():
            raise ValueError(f"{label} does not exist or is not a file: {path}")
        resolved.append(path)
    return resolved


def _image_paths(paths: Iterable[str | Path], label: str) -> list[Path]:
    resolved = _existing_paths(paths, label)
    for path in resolved:
        if path.suffix.lower() not in IMAGE_EXTENSIONS:
            raise ValueError(f"{label} must be an image file {sorted(IMAGE_EXTENSIONS)}, got: {path.suffix or '(no extension)'} {path}")
    return resolved


def _video_duration_range(model_version: str, route: str) -> tuple[int, int]:
    if model_version == "seedance2.5":
        return 4, 30
    if model_version in SEEDANCE_20_MODELS:
        return 4, 15
    if route == "image2video" and model_version == "seedance1.0fast":
        return 5, 10
    if route in {"image2video", "frames2video"} and model_version == "seedance1.5pro":
        return 5, 12
    raise ValueError(f"model {model_version!r} is not supported by dreamina {route}")


def _validate_video_resolution(model_version: str, resolution: str) -> None:
    if model_version == "seedance2.5":
        allowed = {"480p", "720p", "1080p"}
    elif model_version == "seedance2.0_vip":
        allowed = {"720p", "1080p", "4k"}
    else:
        allowed = {"720p"}
    if resolution not in allowed:
        choices = ", ".join(sorted(allowed))
        raise ValueError(f"model {model_version} supports video_resolution: {choices}")


def build_video_command(
    *,
    prompt: str,
    model_version: str | None = None,
    duration: int,
    video_resolution: str = "720p",
    ratio: str = "16:9",
    first_frame: str | Path | None = None,
    last_frame: str | Path | None = None,
    reference_images: Sequence[str | Path] = (),
    reference_videos: Sequence[str | Path] = (),
    reference_audios: Sequence[str | Path] = (),
) -> list[str]:
    """Return the official Dreamina command for one video request."""
    prompt = _require_prompt(prompt)
    if ratio not in VIDEO_RATIOS:
        raise ValueError(f"unsupported video ratio: {ratio}")

    images = _image_paths(reference_images, "reference image")
    videos = _existing_paths(reference_videos, "reference video")
    audios = _existing_paths(reference_audios, "reference audio")
    first = _image_paths([first_frame], "first frame")[0] if first_frame else None
    last = _image_paths([last_frame], "last frame")[0] if last_frame else None

    if last is not None and first is None:
        raise ValueError("last_frame requires first_frame")
    if (first or last) and (images or videos or audios):
        raise ValueError("first/last frames cannot be mixed with multimodal references")

    if last is not None:
        route = "frames2video"
        allowed_models = VIDEO_MODELS | {"seedance1.5pro"}
    elif first is not None:
        route = "image2video"
        allowed_models = VIDEO_MODELS | {"seedance1.0fast", "seedance1.5pro"}
    elif images or videos or audios:
        route = "multimodal2video"
        allowed_models = VIDEO_MODELS
    else:
        route = "text2video"
        allowed_models = VIDEO_MODELS

    if model_version is None:
        model_version = DEFAULT_VIDEO_MODEL if duration <= 15 else "seedance2.5"
    if model_version not in allowed_models:
        raise ValueError(f"model {model_version!r} is not supported by dreamina {route}")
    minimum, maximum = _video_duration_range(model_version, route)
    if not minimum <= duration <= maximum:
        raise ValueError(f"{model_version} duration must be {minimum}-{maximum} seconds for {route}")
    _validate_video_resolution(model_version, video_resolution)

    if route == "multimodal2video":
        total = len(images) + len(videos) + len(audios)
        if model_version == "seedance2.5":
            if len(images) > 30 or len(videos) > 10 or len(audios) > 10 or total > 50:
                raise ValueError("seedance2.5 multimodal limits: image<=30, video<=10, audio<=10, total<=50")
        else:
            if not images and not videos:
                raise ValueError("Seedance 2.0 multimodal mode requires at least one image or video")
            if len(images) > 9 or len(videos) > 3 or len(audios) > 3 or total > 12:
                raise ValueError("Seedance 2.0 multimodal limits: image<=9, video<=3, audio<=3, total<=12")

    command = [
        "dreamina",
        route,
        _flag("prompt", prompt),
        _flag("model_version", model_version),
        _flag("duration", duration),
        _flag("video_resolution", video_resolution),
    ]
    if route in {"text2video", "multimodal2video"}:
        command.append(_flag("ratio", ratio))
    if route == "image2video":
        command.append(_flag("image", first))
    elif route == "frames2video":
        command.extend([_flag("first", first), _flag("last", last)])
    elif route == "multimodal2video":
        command.extend(_flag("image", path) for path in images)
        command.extend(_flag("video", path) for path in videos)
        command.extend(_flag("audio", path) for path in audios)
    return command


def build_image_command(
    *,
    prompt: str,
    model_version: str | None = None,
    resolution_type: str | None = None,
    ratio: str | None = None,
    generate_num: int = 1,
    reference_images: Sequence[str | Path] = (),
    require_reference: bool = False,
) -> list[str]:
    """Preview an image request using settings resolved from the asset task."""
    prompt = _require_prompt(prompt)
    references = _image_paths(reference_images, "reference image")
    if not model_version or not resolution_type or not ratio:
        raise ValueError("explicit image settings required: model_version, resolution_type, ratio")
    if require_reference and not references:
        raise ValueError("this image task requires an approved reference; text2image fallback is not allowed")
    if model_version not in IMAGE_MODELS:
        raise ValueError(f"unsupported Dreamina image model: {model_version}")
    if ratio not in IMAGE_RATIOS:
        raise ValueError(f"unsupported image ratio: {ratio}")
    if not 1 <= generate_num <= 10:
        raise ValueError("generate_num must be 1-10")
    if model_version in {"3.0", "3.1"}:
        allowed_resolutions = {"1k", "2k"}
    elif model_version == "5.0Pro":
        allowed_resolutions = {"1.5k", "2k", "4k"}
    else:
        allowed_resolutions = {"2k", "4k"}
    if resolution_type not in allowed_resolutions:
        choices = ", ".join(sorted(allowed_resolutions))
        raise ValueError(f"model {model_version} supports resolution_type: {choices}")

    if len(references) > 10:
        raise ValueError("dreamina image2image accepts at most 10 images")
    if references and model_version in {"3.0", "3.1"}:
        raise ValueError("dreamina image2image does not support models 3.0 or 3.1")

    route = "image2image" if references else "text2image"
    command = [
        "dreamina",
        route,
        _flag("prompt", prompt),
        _flag("model_version", model_version),
        _flag("resolution_type", resolution_type),
        _flag("ratio", ratio),
        _flag("generate_num", generate_num),
    ]
    command.extend(_flag("images", path) for path in references)
    return command


def inspect_image_output(
    path: str | Path,
    *,
    expected_format: str,
    expected_ratio: str | None = None,
    require_opaque: bool = False,
) -> dict[str, object]:
    """Read actual image bytes; technical success never certifies visual content."""
    from PIL import Image

    expected_format = expected_format.upper()
    if expected_format not in {"JPEG", "PNG", "WEBP"}:
        raise ValueError("expected_format must be JPEG, PNG or WEBP")
    if expected_ratio is not None and expected_ratio not in IMAGE_RATIOS:
        raise ValueError(f"unsupported expected image ratio: {expected_ratio}")
    path = Path(path).expanduser().resolve()
    result: dict[str, object] = {
        "path": str(path), "technical_pass": False, "semantic_review": "not_performed",
        "expected_format": expected_format, "expected_ratio": expected_ratio,
        "require_opaque": require_opaque, "issues": [],
    }
    try:
        with Image.open(path) as picture:
            picture.load()
            width, height = picture.size
            actual_format = picture.format
            alpha = picture.convert("RGBA").getchannel("A").getextrema()
            result.update(actual_format=actual_format, width=width, height=height,
                          mode=picture.mode, alpha_extrema=alpha)
    except (OSError, SyntaxError, ValueError) as error:
        result.update(issues=["unreadable_image"], error=str(error))
        return result

    issues: list[str] = []
    if actual_format != expected_format:
        issues.append("format_mismatch")
    extension_formats = {".jpg": "JPEG", ".jpeg": "JPEG", ".png": "PNG", ".webp": "WEBP"}
    if path.suffix.lower() in extension_formats and extension_formats[path.suffix.lower()] != actual_format:
        issues.append("extension_mismatch")
    if require_opaque and alpha[0] < 255:
        issues.append("unexpected_transparency")
    if expected_ratio is not None:
        ratio_width, ratio_height = map(int, expected_ratio.split(":"))
        # Allow integer-pixel rounding, not a different layout or orientation.
        if abs(width * ratio_height - height * ratio_width) > max(ratio_width, ratio_height):
            issues.append("ratio_mismatch")
    result.update(issues=issues, technical_pass=not issues)
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="kind", required=True)

    video = subparsers.add_parser("video", help="preview a Dreamina video command")
    video.add_argument("--prompt", required=True)
    video.add_argument("--model", help="default: 2.0fast_vip for 4-15s, 2.5 for >15-30s")
    video.add_argument("--duration", required=True, type=int)
    video.add_argument("--resolution", default="720p")
    video.add_argument("--ratio", default="16:9")
    video.add_argument("--first-frame")
    video.add_argument("--last-frame")
    video.add_argument("--image", action="append", default=[])
    video.add_argument("--video", action="append", default=[])
    video.add_argument("--audio", action="append", default=[])

    image = subparsers.add_parser("image", help="preview a Dreamina image command")
    image.add_argument("--prompt", required=True)
    image.add_argument("--model", required=True, help="resolved image model; never inherit video defaults")
    image.add_argument("--resolution", required=True, help="resolved image resolution")
    image.add_argument("--ratio", required=True, help="asset canvas ratio, not automatically the video ratio")
    image.add_argument("--count", type=int, default=1)
    image.add_argument("--reference", action="append", default=[])
    image.add_argument("--require-reference", action="store_true", help="reject missing continuity/edit references")

    check = subparsers.add_parser("check-image", help="read-only technical image check; requires Pillow")
    check.add_argument("--path", required=True)
    check.add_argument("--format", required=True, choices=["JPEG", "PNG", "WEBP"])
    check.add_argument("--ratio", choices=sorted(IMAGE_RATIOS))
    check.add_argument("--opaque", action="store_true")
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = _parser().parse_args()
    if args.kind == "check-image":
        result = inspect_image_output(args.path, expected_format=args.format,
                                      expected_ratio=args.ratio, require_opaque=args.opaque)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result["technical_pass"] else 1
    if args.kind == "video":
        command = build_video_command(
            prompt=args.prompt,
            model_version=args.model,
            duration=args.duration,
            video_resolution=args.resolution,
            ratio=args.ratio,
            first_frame=args.first_frame,
            last_frame=args.last_frame,
            reference_images=args.image,
            reference_videos=args.video,
            reference_audios=args.audio,
        )
    else:
        command = build_image_command(
            prompt=args.prompt,
            model_version=args.model,
            resolution_type=args.resolution,
            ratio=args.ratio,
            generate_num=args.count,
            reference_images=args.reference,
            require_reference=args.require_reference,
        )
    print(json.dumps({"mode": "preview_only", "command": command}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
