#!/usr/bin/env python3
"""Normalize generated clips and assemble a production MP4 with ffmpeg."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
from typing import Sequence


def _run(command: Sequence[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            list(command),
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
        )
    except subprocess.CalledProcessError as exc:
        detail = exc.stderr.strip() or exc.stdout.strip() or "no ffmpeg output"
        raise RuntimeError(f"media command failed: {detail}") from exc


def _require_binary(binary: str) -> str:
    resolved = shutil.which(binary)
    if not resolved:
        raise RuntimeError(f"required executable not found: {binary}")
    return resolved


def probe_media(path: str | Path, ffprobe_bin: str = "ffprobe") -> dict:
    source = Path(path).expanduser().resolve()
    if not source.is_file():
        raise ValueError(f"media file does not exist: {source}")
    ffprobe = _require_binary(ffprobe_bin)
    result = _run(
        [
            ffprobe,
            "-v",
            "error",
            "-show_streams",
            "-show_format",
            "-of",
            "json",
            str(source),
        ]
    )
    return json.loads(result.stdout)


def _has_stream(probe: dict, kind: str) -> bool:
    return any(stream.get("codec_type") == kind for stream in probe.get("streams", []))


def _concat_manifest_path(path: Path) -> str:
    escaped = path.resolve().as_posix().replace("'", "'\\''")
    return f"file '{escaped}'"


def _normalize_clip(
    source: Path,
    destination: Path,
    *,
    width: int,
    height: int,
    fps: int,
    ffmpeg: str,
    ffprobe_bin: str,
) -> None:
    probe = probe_media(source, ffprobe_bin)
    if not _has_stream(probe, "video"):
        raise ValueError(f"clip has no video stream: {source}")
    video_filter = (
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,fps={fps},format=yuv420p"
    )
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-i", str(source)]
    if _has_stream(probe, "audio"):
        command.extend(
            [
                "-filter_complex",
                f"[0:v:0]{video_filter}[v];[0:a:0]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad[a]",
                "-map",
                "[v]",
                "-map",
                "[a]",
            ]
        )
    else:
        command.extend(
            [
                "-f",
                "lavfi",
                "-i",
                "anullsrc=r=48000:cl=stereo",
                "-filter_complex",
                f"[0:v:0]{video_filter}[v]",
                "-map",
                "[v]",
                "-map",
                "1:a:0",
            ]
        )
    command.extend(
        [
            "-c:v",
            "libx264",
            "-preset",
            "medium",
            "-crf",
            "18",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-ar",
            "48000",
            "-ac",
            "2",
            "-shortest",
            "-movflags",
            "+faststart",
            str(destination),
        ]
    )
    _run(command)


def assemble_timeline(
    *,
    clips: Sequence[str | Path],
    output: str | Path,
    width: int = 1080,
    height: int = 1920,
    fps: int = 30,
    external_audio: str | Path | None = None,
    audio_mode: str = "replace",
    overwrite: bool = False,
    ffmpeg_bin: str = "ffmpeg",
    ffprobe_bin: str = "ffprobe",
) -> dict:
    """Normalize and concatenate clips, optionally replacing or mixing audio."""
    if not clips:
        raise ValueError("at least one clip is required")
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise ValueError("width and height must be positive even integers")
    if fps <= 0:
        raise ValueError("fps must be positive")
    if audio_mode not in {"replace", "mix"}:
        raise ValueError("audio_mode must be replace or mix")

    ffmpeg = _require_binary(ffmpeg_bin)
    ffprobe = _require_binary(ffprobe_bin)
    sources = [Path(path).expanduser().resolve() for path in clips]
    for source in sources:
        if not source.is_file():
            raise ValueError(f"clip does not exist: {source}")

    target = Path(output).expanduser().resolve()
    if target.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {target}")
    target.parent.mkdir(parents=True, exist_ok=True)

    fallback = None
    if external_audio is not None:
        fallback = Path(external_audio).expanduser().resolve()
        if not fallback.is_file():
            raise ValueError(f"external audio does not exist: {fallback}")
        if not _has_stream(probe_media(fallback, ffprobe), "audio"):
            raise ValueError(f"external audio has no audio stream: {fallback}")

    with tempfile.TemporaryDirectory(prefix="drama-studio-assemble-") as temp_dir:
        temp_root = Path(temp_dir)
        normalized: list[Path] = []
        for index, source in enumerate(sources, start=1):
            destination = temp_root / f"normalized_{index:04d}.mp4"
            _normalize_clip(
                source,
                destination,
                width=width,
                height=height,
                fps=fps,
                ffmpeg=ffmpeg,
                ffprobe_bin=ffprobe,
            )
            normalized.append(destination)

        manifest = temp_root / "concat.txt"
        manifest.write_text(
            "\n".join(_concat_manifest_path(path) for path in normalized) + "\n",
            encoding="utf-8",
        )
        joined = temp_root / "joined.mp4"
        _run(
            [
                ffmpeg,
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "concat",
                "-safe",
                "0",
                "-i",
                str(manifest),
                "-c",
                "copy",
                "-movflags",
                "+faststart",
                str(joined),
            ]
        )

        if fallback is None:
            shutil.copy2(joined, target)
        elif audio_mode == "replace":
            _run(
                [
                    ffmpeg,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-i",
                    str(joined),
                    "-i",
                    str(fallback),
                    "-filter_complex",
                    "[1:a:0]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad[a]",
                    "-map",
                    "0:v:0",
                    "-map",
                    "[a]",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-shortest",
                    "-movflags",
                    "+faststart",
                    str(target),
                ]
            )
        else:
            _run(
                [
                    ffmpeg,
                    "-hide_banner",
                    "-loglevel",
                    "error",
                    "-y",
                    "-i",
                    str(joined),
                    "-i",
                    str(fallback),
                    "-filter_complex",
                    "[0:a:0]aresample=48000[base];[1:a:0]aresample=48000,aformat=sample_fmts=fltp:channel_layouts=stereo,apad[extra];[base][extra]amix=inputs=2:duration=first:dropout_transition=0:normalize=0[a]",
                    "-map",
                    "0:v:0",
                    "-map",
                    "[a]",
                    "-c:v",
                    "copy",
                    "-c:a",
                    "aac",
                    "-b:a",
                    "192k",
                    "-shortest",
                    "-movflags",
                    "+faststart",
                    str(target),
                ]
            )

    result = probe_media(target, ffprobe)
    video_streams = [stream for stream in result.get("streams", []) if stream.get("codec_type") == "video"]
    if not video_streams or not _has_stream(result, "audio"):
        raise RuntimeError("assembled output must contain video and audio streams")
    video = video_streams[0]
    if (video.get("width"), video.get("height")) != (width, height):
        raise RuntimeError("assembled output dimensions do not match the requested target")
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--clip", action="append", required=True, help="ordered input clip; repeat as needed")
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=1080)
    parser.add_argument("--height", type=int, default=1920)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--external-audio")
    parser.add_argument("--audio-mode", choices=("replace", "mix"), default="replace")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    result = assemble_timeline(
        clips=args.clip,
        output=args.output,
        width=args.width,
        height=args.height,
        fps=args.fps,
        external_audio=args.external_audio,
        audio_mode=args.audio_mode,
        overwrite=args.overwrite,
    )
    print(json.dumps({"output": str(Path(args.output).resolve()), "probe": result}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
