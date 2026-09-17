import importlib.util
from functools import partial
import json
import math
from pathlib import Path
import shutil
import struct
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "drama-studio" / "scripts"


def load_script(name: str):
    path = SCRIPTS / f"{name}.py"
    if not path.is_file():
        raise AssertionError(f"production script is missing: {path}")
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load production script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DreaminaRouteTests(unittest.TestCase):
    def test_image_generation_rejects_video_disguised_as_reference_image(self) -> None:
        route = load_script("dreamina_route")
        with tempfile.TemporaryDirectory() as temp_dir:
            video = Path(temp_dir) / "clip.mp4"
            video.write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError, "must be an image file"):
                route.build_image_command(prompt="建立人物", reference_images=[video])

    def test_precise_frame_and_mother_voice_cannot_silently_drop_each_other(self) -> None:
        route = load_script("dreamina_route")
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first.png"
            voice = Path(temp_dir) / "voice.wav"
            first.write_bytes(b"fixture")
            voice.write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError, "cannot be mixed"):
                route.build_video_command(
                    prompt="母音色对白", model_version="seedance2.5", duration=8,
                    video_resolution="720p", first_frame=first, reference_audios=[voice],
                )
    def test_text_only_seedance_25_uses_official_text2video(self) -> None:
        route = load_script("dreamina_route")

        command = route.build_video_command(
            prompt="雨夜里，她回头看见追兵",
            model_version="seedance2.5",
            duration=16,
            video_resolution="1080p",
            ratio="9:16",
        )

        self.assertEqual(
            [
                "dreamina",
                "text2video",
                "--prompt=雨夜里，她回头看见追兵",
                "--model_version=seedance2.5",
                "--duration=16",
                "--video_resolution=1080p",
                "--ratio=9:16",
            ],
            command,
        )

    def test_first_frame_uses_image2video_and_infers_ratio(self) -> None:
        route = load_script("dreamina_route")
        with tempfile.TemporaryDirectory() as temp_dir:
            first_frame = Path(temp_dir) / "首帧.png"
            first_frame.write_bytes(b"fixture")

            command = route.build_video_command(
                prompt="镜头缓慢推近",
                model_version="seedance2.0_vip",
                duration=10,
                video_resolution="1080p",
                ratio="9:16",
                first_frame=first_frame,
            )

        self.assertEqual("dreamina", command[0])
        self.assertEqual("image2video", command[1])
        self.assertIn(f"--image={first_frame.resolve()}", command)
        self.assertNotIn("--ratio=9:16", command)

    def test_mixed_references_use_multimodal2video(self) -> None:
        route = load_script("dreamina_route")
        with tempfile.TemporaryDirectory() as temp_dir:
            image = Path(temp_dir) / "character.png"
            audio = Path(temp_dir) / "voice.wav"
            image.write_bytes(b"fixture")
            audio.write_bytes(b"fixture")

            command = route.build_video_command(
                prompt="保持人物与声线连续",
                model_version="seedance2.5",
                duration=20,
                video_resolution="1080p",
                ratio="9:16",
                reference_images=[image],
                reference_audios=[audio],
            )

        self.assertEqual(["dreamina", "multimodal2video"], command[:2])
        self.assertIn(f"--image={image.resolve()}", command)
        self.assertIn(f"--audio={audio.resolve()}", command)
        self.assertIn("--ratio=9:16", command)
        self.assertFalse(any("jimeng" in token or "xmst" in token for token in command))

    def test_first_and_last_frames_use_frames2video(self) -> None:
        route = load_script("dreamina_route")
        with tempfile.TemporaryDirectory() as temp_dir:
            first = Path(temp_dir) / "first.png"
            last = Path(temp_dir) / "last.png"
            first.write_bytes(b"fixture")
            last.write_bytes(b"fixture")

            command = route.build_video_command(
                prompt="从警惕变为释然",
                model_version="seedance2.0",
                duration=8,
                video_resolution="720p",
                first_frame=first,
                last_frame=last,
            )

        self.assertEqual(["dreamina", "frames2video"], command[:2])
        self.assertIn(f"--first={first.resolve()}", command)
        self.assertIn(f"--last={last.resolve()}", command)

    def test_seedance_20_rejects_sixteen_second_request(self) -> None:
        route = load_script("dreamina_route")

        with self.assertRaisesRegex(ValueError, "4-15"):
            route.build_video_command(
                prompt="超长镜头",
                model_version="seedance2.0",
                duration=16,
                video_resolution="720p",
            )

    def test_unspecified_model_and_resolution_follow_individual_clip_duration(self) -> None:
        route = load_script("dreamina_route")
        self.assertEqual("seedance2.0fast_vip", route.DEFAULT_VIDEO_MODEL)
        for duration, model in ((4, "seedance2.0fast_vip"), (15, "seedance2.0fast_vip"),
                                (16, "seedance2.5"), (30, "seedance2.5")):
            with self.subTest(duration=duration):
                command = route.build_video_command(prompt="人物转身", duration=duration)
                self.assertIn(f"--model_version={model}", command)
                self.assertIn("--video_resolution=720p", command)
                self.assertIn(f"--duration={duration}", command)

    def test_explicit_short_clip_model_and_resolution_override_defaults(self) -> None:
        route = load_script("dreamina_route")
        command = route.build_video_command(
            prompt="人物转身", duration=12, model_version="seedance2.5", video_resolution="1080p",
        )
        self.assertIn("--model_version=seedance2.5", command)
        self.assertIn("--video_resolution=1080p", command)
        with self.assertRaisesRegex(ValueError, "video_resolution"):
            route.build_video_command(prompt="人物转身", duration=12, video_resolution="1080p")

    def test_unsupported_duration_is_rejected_without_splitting(self) -> None:
        route = load_script("dreamina_route")
        for duration in (3, 31):
            with self.subTest(duration=duration), self.assertRaisesRegex(ValueError, "duration"):
                route.build_video_command(prompt="人物转身", duration=duration)

    def test_cli_resolves_omitted_model_without_submitting(self) -> None:
        for duration, model in ((15, "seedance2.0fast_vip"), (16, "seedance2.5"), (30, "seedance2.5")):
            with self.subTest(duration=duration):
                result = subprocess.run(
                    [sys.executable, "-X", "utf8", str(SCRIPTS / "dreamina_route.py"), "video",
                     "--prompt", "人物转身", "--duration", str(duration)],
                    check=True, capture_output=True, text=True, encoding="utf-8",
                )
                payload = json.loads(result.stdout)
                self.assertEqual("preview_only", payload["mode"])
                self.assertIn(f"--model_version={model}", payload["command"])
                self.assertIn("--video_resolution=720p", payload["command"])

    def test_video_route_rejects_non_image_first_frame_and_references(self) -> None:
        # v1.13.5 复核补丁：首帧/尾帧/多模态 --image 必须是图片文件，防整段视频被当首帧喂给 image2video
        route = load_script("dreamina_route")
        with tempfile.TemporaryDirectory() as temp_dir:
            not_image = Path(temp_dir) / "clip.mp4"
            not_image.write_bytes(b"fixture")

            with self.assertRaisesRegex(ValueError, "must be an image file"):
                route.build_video_command(
                    prompt="女主推门",
                    model_version="seedance2.0",
                    duration=5,
                    video_resolution="720p",
                    first_frame=not_image,
                )
            # --video 参考（真正的视频文件）必须放行——mp4 走 _existing_paths 合法
            command = route.build_video_command(
                prompt="动作迁移参考",
                model_version="seedance2.5",
                duration=8,
                video_resolution="1080p",
                reference_videos=[not_image],
            )
            self.assertIn("multimodal2video", command)
        # 音频参考走 _existing_paths 不受图片校验影响
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_ref = Path(temp_dir) / "voice.wav"
            audio_ref.write_bytes(b"fixture")
            with self.assertRaisesRegex(ValueError, "requires at least one image or video"):
                route.build_video_command(
                    prompt="音色参考",
                    model_version="seedance2.0",
                    duration=8,
                    video_resolution="720p",
                    reference_audios=[audio_ref],
                )

    def test_image_reference_routes_to_official_image2image(self) -> None:
        route = load_script("dreamina_route")
        with tempfile.TemporaryDirectory() as temp_dir:
            reference = Path(temp_dir) / "character.png"
            reference.write_bytes(b"fixture")

            command = route.build_image_command(
                prompt="保持人物身份，生成全身定妆照",
                model_version="5.0",
                resolution_type="2k",
                ratio="9:16",
                reference_images=[reference],
            )

        self.assertEqual(["dreamina", "image2image"], command[:2])
        self.assertIn(f"--images={reference.resolve()}", command)

    def test_preview_cli_outputs_json_without_submitting(self) -> None:
        script = SCRIPTS / "dreamina_route.py"
        self.assertTrue(script.is_file(), f"production script is missing: {script}")

        result = subprocess.run(
            [
                sys.executable,
                "-X",
                "utf8",
                str(script),
                "video",
                "--prompt",
                "人物转身",
                "--model",
                "seedance2.5",
                "--duration",
                "6",
                "--resolution",
                "720p",
                "--ratio",
                "9:16",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        payload = json.loads(result.stdout)

        self.assertEqual("preview_only", payload["mode"])
        self.assertEqual(["dreamina", "text2video"], payload["command"][:2])


@unittest.skipUnless(shutil.which("ffmpeg") and shutil.which("ffprobe"), "ffmpeg/ffprobe required")
class TimelineAssemblerIntegrationTests(unittest.TestCase):
    def setUp(self) -> None:
        # Exercise real subprocesses, but bound each media invocation during tests.
        guard = patch.object(subprocess, "run", new=partial(subprocess.run, timeout=30))
        guard.start()
        self.addCleanup(guard.stop)

    @staticmethod
    def make_color_clip(path: Path, colors: tuple[str, str], rate: int, frequency: int,
                        timestamp_offset: int = 0) -> None:
        # Each source changes color and tone at one second, so assertions detect
        # ignored in/out points as well as reversed source order.
        subprocess.run(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
             "-f", "lavfi", "-i", f"color=c={colors[0]}:s=160x120:r={rate}:d=1",
             "-f", "lavfi", "-i", f"color=c={colors[1]}:s=160x120:r={rate}:d=1",
             "-f", "lavfi", "-i", f"sine=frequency={frequency}:sample_rate=48000:duration=1",
             "-f", "lavfi", "-i", f"sine=frequency={frequency * 2}:sample_rate=48000:duration=1",
             "-filter_complex", "[0:v][1:v]concat=n=2:v=1:a=0[v];[2:a][3:a]concat=n=2:v=0:a=1[a]",
             "-map", "[v]", "-map", "[a]", "-c:v", "libx264", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-output_ts_offset", str(timestamp_offset), str(path)],
            check=True, capture_output=True,
        )

    @staticmethod
    def pixel_at(path: Path, seconds: float) -> tuple[int, int, int]:
        result = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", str(seconds), "-i", str(path),
             "-frames:v", "1", "-vf", "crop=2:2:(iw-2)/2:(ih-2)/2,scale=1:1",
             "-f", "rawvideo", "-pix_fmt", "rgb24", "pipe:1"],
            check=True, capture_output=True,
        )
        return tuple(result.stdout[:3])

    @staticmethod
    def tone_at(path: Path, seconds: float) -> float:
        result = subprocess.run(
            ["ffmpeg", "-v", "error", "-ss", str(seconds), "-i", str(path), "-t", "0.2",
             "-vn", "-ac", "1", "-ar", "8000", "-f", "s16le", "pipe:1"],
            check=True, capture_output=True,
        )
        samples = struct.unpack(f"<{len(result.stdout) // 2}h", result.stdout)
        if not samples or max(abs(value) for value in samples) < 100:
            return 0.0
        crossings = sum(left <= 0 < right for left, right in zip(samples, samples[1:]))
        return crossings * 8000 / len(samples)

    def test_timeline_selects_ordered_ranges_with_native_audio_and_reset_timestamps(self) -> None:
        assembler = load_script("assemble_timeline")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first.mp4"
            second = root / "second.mp4"
            self.make_color_clip(first, ("red", "blue"), 24, 440, timestamp_offset=5)
            self.make_color_clip(second, ("lime", "yellow"), 15, 330)
            originals = {path: path.read_bytes() for path in (first, second)}
            timeline = root / "edit.json"
            timeline.write_text(json.dumps({"clips": [
                {"path": "second.mp4", "in": 0.2, "out": 0.8},
                {"path": str(first), "in": 1.2, "out": 1.8},
            ]}), encoding="utf-8")
            output = root / "assembled.mp4"
            probe = assembler.assemble_timeline(timeline=timeline, output=output, width=180, height=320)
            video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
            self.assertEqual((180, 320, "yuv420p", "30/1"),
                             (video["width"], video["height"], video["pix_fmt"], video["r_frame_rate"]))
            self.assertAlmostEqual(1.2, float(probe["format"]["duration"]), delta=0.12)
            self.assertLess(abs(float(video["start_time"])), 0.05)
            for time, color in ((0.25, (0, 255, 0)), (0.85, (0, 0, 255))):
                actual = self.pixel_at(output, time)
                self.assertEqual(3, len(actual))
                self.assertTrue(all(abs(a - b) < 15 for a, b in zip(actual, color)), actual)
            self.assertAlmostEqual(330, self.tone_at(output, 0.2), delta=15)
            self.assertAlmostEqual(880, self.tone_at(output, 0.85), delta=15)
            for path, original in originals.items():
                self.assertEqual(original, path.read_bytes())

    def test_timeline_cli_defaults_to_720p_and_omitted_cuts_use_full_source(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.mp4"
            self.make_clip(source, "160x120", 24, 0.3, with_audio=True)
            timeline = root / "edit.json"
            timeline.write_text(json.dumps({"clips": [{"path": "source.mp4"}]}), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, "-X", "utf8", str(SCRIPTS / "assemble_timeline.py"), "--timeline", str(timeline),
                 "--output", str(root / "assembled.mp4")],
                check=True, capture_output=True, text=True, encoding="utf-8",
            )
            probe = json.loads(result.stdout)["probe"]
            video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
            self.assertEqual((720, 1280), (video["width"], video["height"]))
            self.assertAlmostEqual(1 / 3, float(probe["format"]["duration"]), delta=0.1)

    def test_selected_native_audio_keeps_its_delay_and_silent_tail(self) -> None:
        assembler = load_script("assemble_timeline")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "delayed.mp4"
            subprocess.run(
                ["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                 "color=c=red:s=160x120:r=30:d=1.2", "-itsoffset", "0.4",
                 "-f", "lavfi", "-i", "sine=frequency=440:sample_rate=48000:duration=0.4",
                 "-c:v", "libx264", "-c:a", "aac", str(source)],
                check=True, capture_output=True,
            )
            timeline = root / "edit.json"
            timeline.write_text(json.dumps({"clips": [
                {"path": "delayed.mp4", "in": 0.1, "out": 1.1},
                {"path": "delayed.mp4", "in": 0.9},
            ]}), encoding="utf-8")
            output = root / "assembled.mp4"
            probe = assembler.assemble_timeline(timeline=timeline, output=output, width=160, height=120)
            self.assertAlmostEqual(1.3, float(probe["format"]["duration"]), delta=0.12)
            self.assertEqual(0, self.tone_at(output, 0.05))
            self.assertAlmostEqual(440, self.tone_at(output, 0.4), delta=15)
            self.assertEqual(0, self.tone_at(output, 0.8))
            self.assertEqual(0, self.tone_at(output, 1.05))

    def test_legacy_repeatable_clip_cli_keeps_order_and_explicit_dimensions(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first, second, output = (root / name for name in ("first.mp4", "second.mp4", "out.mp4"))
            self.make_color_clip(first, ("red", "blue"), 24, 440)
            self.make_color_clip(second, ("lime", "yellow"), 15, 330)
            subprocess.run(
                [sys.executable, "-X", "utf8", str(SCRIPTS / "assemble_timeline.py"),
                 "--clip", str(first), "--clip", str(second), "--output", str(output),
                 "--width", "160", "--height", "120"],
                check=True, capture_output=True,
            )
            self.assertGreater(self.pixel_at(output, 0.3)[0], 240)
            self.assertGreater(self.pixel_at(output, 2.3)[1], 240)

    def test_invalid_timeline_is_rejected_before_any_clip_is_rendered(self) -> None:
        assembler = load_script("assemble_timeline")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.mp4"
            self.make_clip(source, "160x120", 24, 0.5, with_audio=True)
            timeline = root / "edit.json"
            output = root / "assembled.mp4"
            original = source.read_bytes()
            malformed = ["{", "[]", "{}", '{"clips": []}', '{"clips": "source.mp4"}']
            invalid_entries = [None, {}, {"path": 7}, {"path": ""},
                               {"path": "missing.mp4"}, {"path": "source.mp4", "in": -0.1},
                               {"path": "source.mp4", "in": 0.3, "out": 0.2},
                               {"path": "source.mp4", "in": 0.2, "out": 0.2},
                               {"path": "source.mp4", "out": 8},
                               {"path": "source.mp4", "in": 8},
                               {"path": "source.mp4", "out": None}]
            for value in (True, "0.1", math.nan, math.inf, -math.inf):
                for field in ("in", "out"):
                    invalid_entries.append({"path": "source.mp4", field: value})
            malformed += [json.dumps({"clips": [{"path": "source.mp4"}, entry]})
                          for entry in invalid_entries]
            with patch.object(assembler, "_normalize_clip") as render:
                for content in malformed:
                    with self.subTest(content=content):
                        timeline.write_text(content, encoding="utf-8")
                        with self.assertRaises(ValueError):
                            assembler.assemble_timeline(timeline=timeline, output=output)
                        render.assert_not_called()
                        self.assertFalse(output.exists())
            self.assertEqual(original, source.read_bytes())

    def test_timeline_cannot_overwrite_source_or_edit_record(self) -> None:
        assembler = load_script("assemble_timeline")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            source = root / "source.mp4"
            self.make_clip(source, "160x120", 24, 0.3, with_audio=True)
            timeline = root / "edit.json"
            timeline.write_text(json.dumps({"clips": [{"path": "source.mp4"}]}), encoding="utf-8")
            for target in (source, timeline):
                with self.subTest(target=target):
                    original = target.read_bytes()
                    with self.assertRaisesRegex(ValueError, "output must not overwrite input"):
                        assembler.assemble_timeline(timeline=timeline, output=target, overwrite=True)
                    self.assertEqual(original, target.read_bytes())

    def test_cli_and_python_reject_ambiguous_clip_and_timeline(self) -> None:
        assembler = load_script("assemble_timeline")
        with self.assertRaisesRegex(ValueError, "either|mutually exclusive"):
            assembler.assemble_timeline(clips=["source.mp4"], timeline="edit.json", output="out.mp4")
        result = subprocess.run(
            [sys.executable, "-X", "utf8", str(SCRIPTS / "assemble_timeline.py"), "--clip", "source.mp4",
             "--timeline", "edit.json", "--output", "out.mp4"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(2, result.returncode)
        self.assertIn("not allowed with argument", result.stderr)

    def test_overwrite_permission_never_allows_replacing_input_media(self) -> None:
        assembler = load_script("assemble_timeline")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            clip = root / "source.mp4"
            fallback = root / "voice.wav"
            self.make_clip(clip, "160x120", 24, 0.3, with_audio=True)
            self.make_audio(fallback, 0.3)
            for target in (clip, fallback):
                with self.subTest(target=target):
                    original = target.read_bytes()
                    with self.assertRaisesRegex(ValueError, "output must not overwrite input"):
                        assembler.assemble_timeline(
                            clips=[clip], output=target, external_audio=fallback,
                            width=160, height=120, overwrite=True,
                        )
                    self.assertEqual(original, target.read_bytes())

    @staticmethod
    def make_clip(path: Path, size: str, rate: int, duration: float, with_audio: bool) -> None:
        command = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-f",
            "lavfi",
            "-i",
            f"testsrc2=size={size}:rate={rate}:duration={duration}",
        ]
        if with_audio:
            command.extend(
                [
                    "-f",
                    "lavfi",
                    "-i",
                    f"sine=frequency=440:sample_rate=48000:duration={duration}",
                ]
            )
        command.extend(["-c:v", "libx264", "-pix_fmt", "yuv420p"])
        if with_audio:
            command.extend(["-c:a", "aac", "-shortest"])
        command.append(str(path))
        subprocess.run(command, check=True, capture_output=True)

    @staticmethod
    def make_audio(path: Path, duration: float) -> None:
        subprocess.run(
            [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"sine=frequency=880:sample_rate=48000:duration={duration}",
                str(path),
            ],
            check=True,
            capture_output=True,
        )

    def test_normalizes_heterogeneous_clips_and_preserves_complete_audio_timeline(self) -> None:
        assembler = load_script("assemble_timeline")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            first = root / "first.mp4"
            second = root / "second.mp4"
            output = root / "assembled.mp4"
            self.make_clip(first, "160x120", 24, 0.6, with_audio=True)
            self.make_clip(second, "320x180", 15, 0.5, with_audio=False)

            assembler.assemble_timeline(
                clips=[first, second],
                output=output,
                width=180,
                height=320,
                fps=30,
            )
            probe = assembler.probe_media(output)

            video = next(stream for stream in probe["streams"] if stream["codec_type"] == "video")
            audio = next(stream for stream in probe["streams"] if stream["codec_type"] == "audio")
            self.assertEqual((180, 320), (video["width"], video["height"]))
            self.assertEqual("aac", audio["codec_name"])
            self.assertGreater(float(probe["format"]["duration"]), 0.9)

    def test_external_fallback_audio_can_replace_native_mix(self) -> None:
        assembler = load_script("assemble_timeline")
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            clip = root / "clip.mp4"
            fallback = root / "fallback.wav"
            output = root / "revoiced.mp4"
            self.make_clip(clip, "160x120", 24, 0.7, with_audio=True)
            self.make_audio(fallback, 0.3)

            assembler.assemble_timeline(
                clips=[clip],
                output=output,
                width=180,
                height=320,
                fps=30,
                external_audio=fallback,
                audio_mode="replace",
            )
            probe = assembler.probe_media(output)

            self.assertTrue(any(stream["codec_type"] == "audio" for stream in probe["streams"]))
            self.assertGreater(float(probe["format"]["duration"]), 0.6)


if __name__ == "__main__":
    unittest.main()
