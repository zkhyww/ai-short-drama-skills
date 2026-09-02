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
    model_version: str,
    duration: int,
    video_resolution: str,
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
    model_version: str = "5.0",
    resolution_type: str = "2k",
    ratio: str = "9:16",
    generate_num: int = 1,
    reference_images: Sequence[str | Path] = (),
) -> list[str]:
    """Return a text2image or image2image command for Dreamina."""
    prompt = _require_prompt(prompt)
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

    references = _existing_paths(reference_images, "reference image")
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


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="kind", required=True)

    video = subparsers.add_parser("video", help="preview a Dreamina video command")
    video.add_argument("--prompt", required=True)
    video.add_argument("--model", required=True)
    video.add_argument("--duration", required=True, type=int)
    video.add_argument("--resolution", required=True)
    video.add_argument("--ratio", default="16:9")
    video.add_argument("--first-frame")
    video.add_argument("--last-frame")
    video.add_argument("--image", action="append", default=[])
    video.add_argument("--video", action="append", default=[])
    video.add_argument("--audio", action="append", default=[])

    image = subparsers.add_parser("image", help="preview a Dreamina image command")
    image.add_argument("--prompt", required=True)
    image.add_argument("--model", default="5.0")
    image.add_argument("--resolution", default="2k")
    image.add_argument("--ratio", default="9:16")
    image.add_argument("--count", type=int, default=1)
    image.add_argument("--reference", action="append", default=[])
    return parser


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    args = _parser().parse_args()
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
        )
    print(json.dumps({"mode": "preview_only", "command": command}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
