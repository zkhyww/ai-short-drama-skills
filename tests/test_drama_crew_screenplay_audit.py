from __future__ import annotations

import importlib.util
import io
from pathlib import Path
import sys
import tempfile
import unittest
from contextlib import redirect_stdout


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "drama-crew" / "scripts" / "audit_screenplay.py"
SPEC = importlib.util.spec_from_file_location("audit_screenplay", MODULE_PATH)
if SPEC is None or SPEC.loader is None:
    raise ImportError(f"Cannot load screenplay auditor from {MODULE_PATH}")
AUDIT = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = AUDIT
SPEC.loader.exec_module(AUDIT)


def submission(body: str, *, outline: str = "- 第1集：甲拒绝签字，门外警报响起。") -> str:
    return f"""# 《测试剧》

## 一句话卖点
一个普通人必须在一分钟内作出选择。

## 故事梗概
甲在压力下拒绝签字，并承担后果。

## 主要人物
甲：坚持事实的人。

## 粗纲
第一阶段：甲发现问题并拒绝合作。

## 逐集集纲
{outline}

## 正文
{body}
"""


VALID_SUBMISSION = submission(
    """# 第 1 集
**场1-1 夜 内 值班室**
**人物：甲 乙**
∆警报灯亮起，甲把签字笔推回去。
甲：（低声）我不同意。
乙：那你就留下。
"""
)

VALID_MASTER = """project_id: test
script_rev: 1
review_state: reviewed
romance_axis=off

## 正文
# 第 1 集
【场景设定】夜，值班室。
甲：我不同意。
"""


class ScreenplayAuditTests(unittest.TestCase):
    def test_submission_rejects_empty_episode_outline_and_internal_fields(self) -> None:
        invalid = submission(
            """# 第 1 集
script_rev: 7
**场1-1 夜 内 值班室**
**人物：甲**
甲：我不同意。
""",
            outline="",
        )

        result = AUDIT.audit_submission(invalid, expected_episodes=1)

        codes = {item.code for item in result.findings if item.severity == "error"}
        self.assertIn("EMPTY_EPISODE_OUTLINE", codes)
        self.assertIn("INTERNAL_FIELD_IN_SUBMISSION", codes)

    def test_submission_rejects_an_individually_empty_episode_outline_entry(self) -> None:
        invalid = submission(
            """# 第 1 集
**场1-1 夜 内 值班室**
**人物：甲**
甲：我不同意。
# 第 2 集
**场2-1 日 内 值班室**
**人物：甲**
甲：我还是不同意。
""",
            outline="- 第1集：\n- 第2集：甲继续拒绝签字。",
        )

        result = AUDIT.audit_submission(invalid, expected_episodes=2)

        self.assertTrue(
            any(item.code == "EMPTY_EPISODE_OUTLINE_ENTRY" for item in result.findings)
        )

    def test_submission_rejects_beat_markup_duplicate_people_and_visible_action_hint(self) -> None:
        invalid = submission(
            """# 第 1 集
**场1-1 夜 内 值班室**
**人物：甲 甲 乙**
【动作节拍】甲→推门→盯住乙；情绪7
甲：（盯着屏幕）我不同意。
"""
        )

        result = AUDIT.audit_submission(invalid, expected_episodes=1)

        codes = {item.code for item in result.findings if item.severity == "error"}
        self.assertTrue(
            {
                "PRODUCTION_BEAT_IN_SUBMISSION",
                "DUPLICATE_PERSON",
                "VISIBLE_ACTION_IN_DIALOGUE_HINT",
            }.issubset(codes)
        )

    def test_submission_rejects_speaker_side_annotation(self) -> None:
        invalid = submission(
            """# 第 1 集
**场1-1 夜 内 值班室**
**人物：林衡**
林衡（回放）：门没有打开。
"""
        )

        result = AUDIT.audit_submission(invalid, expected_episodes=1)

        self.assertTrue(
            any(item.code == "NONSTANDARD_SPEAKER_ANNOTATION" for item in result.findings)
        )

    def test_master_rejects_invalid_romance_axis(self) -> None:
        result = AUDIT.audit_master(
            "romance_axis=weak\n## 正文\n# 第 1 集\n甲：我不同意。",
            expected_episodes=1,
        )

        self.assertTrue(any(item.code == "INVALID_ROMANCE_AXIS" for item in result.findings))

    def test_master_rejects_empty_numeric_or_chinese_romance_axis(self) -> None:
        for value in ("", "1", "无"):
            with self.subTest(value=value):
                result = AUDIT.audit_master(
                    f"romance_axis={value}\n## 正文\n# 第 1 集\n甲：我不同意。",
                    expected_episodes=1,
                )
                self.assertTrue(
                    any(item.code == "INVALID_ROMANCE_AXIS" for item in result.findings)
                )

    def test_non_spoken_writing_action_is_not_counted_as_dialogue(self) -> None:
        sample = submission(
            """# 第 1 集
**场1-1 日 内 会议室**
**人物：甲 老人**
老人（写字）：我签。
甲：我不同意。
"""
        )

        result = AUDIT.audit_submission(sample, expected_episodes=1)

        self.assertEqual(4, result.metrics["spoken_chars"])

    def test_long_dialogue_run_and_repeated_action_are_diagnostics(self) -> None:
        episodes: list[str] = []
        for episode in range(1, 4):
            lines = [
                f"# 第 {episode} 集",
                f"**场{episode}-1 夜 内 值班室**",
                "**人物：甲 乙**",
                "∆夜01:05，头灯从门缝斜切进去。",
            ]
            lines.extend(f"甲：第{i}句话。" for i in range(1, 11))
            episodes.append("\n".join(lines))
        sample = submission(
            "\n".join(episodes),
            outline="\n".join(f"- 第{i}集：继续对峙。" for i in range(1, 4)),
        )

        result = AUDIT.audit_submission(sample, expected_episodes=3)

        warning_codes = {item.code for item in result.findings if item.severity == "warning"}
        self.assertIn("LONG_DIALOGUE_RUN", warning_codes)
        self.assertIn("REPEATED_ACTION_LINE", warning_codes)
        self.assertFalse(result.blocking)

    def test_valid_pair_passes_and_reports_only_spoken_time_range(self) -> None:
        result = AUDIT.audit_pair(VALID_MASTER, VALID_SUBMISSION, expected_episodes=1)

        self.assertFalse(result.blocking)
        self.assertGreaterEqual(
            result.metrics["spoken_seconds_at_3_5_cps"],
            result.metrics["spoken_seconds_at_4_5_cps"],
        )
        self.assertNotIn("estimated_total_runtime", result.metrics)

    def test_cli_returns_zero_for_valid_pair_and_one_for_invalid_submission(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp = Path(tmp_dir)
            master = tmp / "master.md"
            valid = tmp / "valid.md"
            invalid = tmp / "invalid.md"
            master.write_text(VALID_MASTER, encoding="utf-8")
            valid.write_text(VALID_SUBMISSION, encoding="utf-8")
            invalid.write_text(submission("# 第 1 集\nscript_rev: 2", outline=""), encoding="utf-8")

            with redirect_stdout(io.StringIO()):
                valid_exit = AUDIT.main(
                    [
                        "--master",
                        str(master),
                        "--submission",
                        str(valid),
                        "--expected-episodes",
                        "1",
                    ]
                )
                invalid_exit = AUDIT.main(
                    [
                        "--master",
                        str(master),
                        "--submission",
                        str(invalid),
                        "--expected-episodes",
                        "1",
                    ]
                )
            self.assertEqual(0, valid_exit)
            self.assertEqual(1, invalid_exit)

    def test_cli_rejects_identical_master_and_submission_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp_dir:
            shared = Path(tmp_dir) / "shared.md"
            shared.write_text(VALID_MASTER, encoding="utf-8")
            output = io.StringIO()

            with redirect_stdout(output):
                exit_code = AUDIT.main(
                    [
                        "--master",
                        str(shared),
                        "--submission",
                        str(shared),
                        "--expected-episodes",
                        "1",
                    ]
                )

            self.assertEqual(1, exit_code)
            self.assertIn("IDENTICAL_DELIVERABLE_PATH", output.getvalue())


if __name__ == "__main__":
    unittest.main()
