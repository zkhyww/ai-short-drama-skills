#!/usr/bin/env python3
"""Normalize generated clips and assemble a production MP4 with ffmpeg."""

from __future__ import annotations

import argparse
import json
import math
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


def _cut_time(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite non-negative number of seconds")
    try:
        seconds = float(value)
    except OverflowError as exc:
        raise ValueError(f"{label} must be finite") from exc
    if not math.isfinite(seconds) or seconds < 0:
        raise ValueError(f"{label} must be a finite non-negative number of seconds")
    return seconds


def _read_timeline(path: Path) -> list[tuple[Path, float, float | None]]:
    if not path.is_file():
        raise ValueError(f"timeline does not exist: {path}")
    data = json.loads(path.read_text(encoding="utf-8-sig"))
    entries = data.get("clips") if isinstance(data, dict) else None
    if not isinstance(entries, list) or not entries:
        raise ValueError("timeline must contain a non-empty clips array")
    selections = []
    for index, entry in enumerate(entries, start=1):
        label = f"timeline clip {index}"
        if not isinstance(entry, dict) or not isinstance(entry.get("path"), str) or not entry["path"].strip():
            raise ValueError(f"{label} requires a non-empty path string")
        source = Path(entry["path"]).expanduser()
        if not source.is_absolute():
            source = path.parent / source
        start = _cut_time(entry.get("in", 0), f"{label} in")
        end = _cut_time(entry["out"], f"{label} out") if "out" in entry else None
        selections.append((source.resolve(), start, end))
    return selections


def _video_duration(probe: dict, source: Path, ffprobe: str) -> float:
    video = next((stream for stream in probe.get("streams", []) if stream.get("codec_type") == "video"), None)
    if video is None:
        raise ValueError(f"clip has no video stream: {source}")
    try:
        duration = float(video.get("duration"))
    except (TypeError, ValueError):
        duration = math.nan
    if math.isfinite(duration) and duration > 0:
        return duration

    # Container duration can include timestamp offsets and longer audio tracks.
    # When stream duration is absent, measure only this video's packet extent.
    result = _run([
        ffprobe, "-v", "error", "-select_streams", "v:0", "-show_packets",
        "-show_entries", "packet=pts_time,duration_time", "-of", "json", str(source),
    ])
    packets = json.loads(result.stdout).get("packets", [])
    extents = []
    for packet in packets:
        try:
            start = float(packet["pts_time"])
            length = float(packet["duration_time"])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"clip has no reliable video duration: {source}") from exc
        if not math.isfinite(start) or not math.isfinite(length) or length <= 0:
            raise ValueError(f"clip has no reliable video duration: {source}")
        extents.append((start, start + length))
    if not extents:
        raise ValueError(f"clip has no reliable video duration: {source}")
    return max(end for _, end in extents) - min(start for start, _ in extents)


def _normalize_clip(
    source: Path,
    destination: Path,
    *,
    width: int,
    height: int,
    fps: int,
    ffmpeg: str,
    probe: dict,
    start: float,
    end: float,
) -> None:
    # Cuts are elapsed time from the source start, even with non-zero source PTS.
    video = next(stream for stream in probe["streams"] if stream.get("codec_type") == "video")
    video_start = float(video.get("start_time", 0))
    video_filter = (
        f"setpts=PTS-STARTPTS,trim=start={start}:end={end},setpts=PTS-STARTPTS,"
        f"scale={width}:{height}:force_original_aspect_ratio=decrease,"
        f"pad={width}:{height}:(ow-iw)/2:(oh-ih)/2:color=black,"
        f"setsar=1,fps={fps},format=yuv420p"
    )
    command = [ffmpeg, "-hide_banner", "-loglevel", "error", "-y", "-copyts", "-i", str(source)]
    if _has_stream(probe, "audio"):
        command.extend(
            [
                "-filter_complex",
                f"[0:v:0]{video_filter}[v];"
                # Preserve delayed audio relative to video; pad before trimming so
                # a selection beyond the audio end still produces finite silence.
                f"[0:a:0]asetpts=PTS-{video_start}/TB,aresample=48000:async=1:first_pts=0,"
                "aformat=sample_fmts=fltp:channel_layouts=stereo,apad,"
                f"atrim=start={start}:end={end},asetpts=PTS-STARTPTS[a]",
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
    clips: Sequence[str | Path] | None = None,
    timeline: str | Path | None = None,
    output: str | Path,
    width: int = 720,
    height: int = 1280,
    fps: int = 30,
    external_audio: str | Path | None = None,
    audio_mode: str = "replace",
    overwrite: bool = False,
    ffmpeg_bin: str = "ffmpeg",
    ffprobe_bin: str = "ffprobe",
) -> dict:
    """Assemble full clips or JSON-selected ranges, optionally replacing/mixing audio."""
    if (clips is None) == (timeline is None):
        raise ValueError("provide either clips or timeline (mutually exclusive)")
    if clips is not None and not clips:
        raise ValueError("at least one clip is required")
    if width <= 0 or height <= 0 or width % 2 or height % 2:
        raise ValueError("width and height must be positive even integers")
    if fps <= 0:
        raise ValueError("fps must be positive")
    if audio_mode not in {"replace", "mix"}:
        raise ValueError("audio_mode must be replace or mix")

    ffmpeg = _require_binary(ffmpeg_bin)
    ffprobe = _require_binary(ffprobe_bin)
    timeline_path = Path(timeline).expanduser().resolve() if timeline is not None else None
    selections = _read_timeline(timeline_path) if timeline_path is not None else [
        (Path(path).expanduser().resolve(), 0.0, None) for path in clips
    ]
    sources = [source for source, _, _ in selections]
    for source in sources:
        if not source.is_file():
            raise ValueError(f"clip does not exist: {source}")

    target = Path(output).expanduser().resolve()
    fallback = Path(external_audio).expanduser().resolve() if external_audio is not None else None
    protected = [*sources, *([fallback] if fallback is not None else []),
                 *([timeline_path] if timeline_path is not None else [])]
    for source in protected:
        if target == source or (target.exists() and source.exists() and target.samefile(source)):
            raise ValueError(f"output must not overwrite input media: {source}")
    if target.exists() and not overwrite:
        raise FileExistsError(f"output already exists: {target}")

    # Validate every selected range before any normalization/render begins.
    validated = []
    for source, start, end in selections:
        probe = probe_media(source, ffprobe)
        duration = _video_duration(probe, source, ffprobe)
        end = duration if end is None else end
        if not 0 <= start < end <= duration:
            raise ValueError(f"clip cuts require 0 <= in < out <= source duration ({duration}): {source}")
        validated.append((source, start, end, probe))

    if fallback is not None:
        if not fallback.is_file():
            raise ValueError(f"external audio does not exist: {fallback}")
        if not _has_stream(probe_media(fallback, ffprobe), "audio"):
            raise ValueError(f"external audio has no audio stream: {fallback}")

    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="drama-studio-assemble-") as temp_dir:
        temp_root = Path(temp_dir)
        normalized: list[Path] = []
        for index, (source, start, end, probe) in enumerate(validated, start=1):
            destination = temp_root / f"normalized_{index:04d}.mp4"
            _normalize_clip(
                source,
                destination,
                width=width,
                height=height,
                fps=fps,
                ffmpeg=ffmpeg,
                probe=probe,
                start=start,
                end=end,
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
    inputs = parser.add_mutually_exclusive_group(required=True)
    inputs.add_argument("--clip", action="append", help="ordered input clip; repeat as needed")
    inputs.add_argument("--timeline", help="JSON clips with path and optional in/out seconds")
    parser.add_argument("--output", required=True)
    parser.add_argument("--width", type=int, default=720)
    parser.add_argument("--height", type=int, default=1280)
    parser.add_argument("--fps", type=int, default=30)
    parser.add_argument("--external-audio")
    parser.add_argument("--audio-mode", choices=("replace", "mix"), default="replace")
    parser.add_argument("--overwrite", action="store_true")
    return parser


def main() -> int:
    args = _parser().parse_args()
    result = assemble_timeline(
        clips=args.clip,
        timeline=args.timeline,
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
