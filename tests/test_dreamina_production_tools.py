import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


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
                "python",
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
