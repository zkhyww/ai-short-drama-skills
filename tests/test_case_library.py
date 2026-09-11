import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "drama-studio" / "scripts" / "case_library.py"
REPO_METADATA = (
    ROOT
    / "drama-studio"
    / "references"
    / "case-library"
    / "metadata.json"
)


def valid_metadata() -> dict:
    return {
        "schema_version": 1,
        "library_id": "test-case-library",
        "snapshot": {
            "as_of": "2026-09-12",
            "original_case_count": 1,
            "prompt_policy": "metadata_only_unless_redistribution_permitted",
        },
        "authors": [
            {
                "id": "author-example",
                "display_name": "Example Author",
                "handle": "@example",
                "profile_url": "https://example.com/author",
                "public_numeric_id": None,
            }
        ],
        "cases": [
            {
                "id": "ACT-001",
                "title": "Example action",
                "category": "动作与打斗",
                "summary": "研究动作的空间关系。",
                "model_claim": {
                    "name": "Example Model",
                    "basis": "author_claimed",
                },
                "task_tags": ["action", "spatial-continuity"],
                "author_id": "author-example",
                "source": {
                    "post_url": "https://example.com/post/1",
                    "attribution_status": "author_post_unverified",
                    "local_locators": [],
                },
                "prompt": {
                    "completeness": "complete",
                    "missing_inputs": [],
                    "local_relative_path": "提示词/动作与打斗/ACT-001_Example.txt",
                    "content_fingerprint": hashlib.sha256(
                        "third-partypromptbody".encode("utf-8")
                    ).hexdigest(),
                    "publication": "metadata_only",
                },
                "media_verification": "not_reviewed",
                "license": {
                    "status": "unknown",
                    "prompt_redistribution": "not_permitted",
                },
            }
        ],
        "aliases": [],
    }


class CaseLibraryCliTests(unittest.TestCase):
    def run_cli(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=ROOT,
            text=True,
            encoding="utf-8",
            errors="replace",
            capture_output=True,
            check=False,
        )

    def write_json(self, path: Path, value: dict) -> None:
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_validate_and_build_separate_public_and_local_views(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "metadata.json"
            public_path = temp / "README.md"
            local_path = temp / "local-index.md"
            local_root = temp / "private-cases"
            prompt_path = local_root / "提示词" / "动作与打斗" / "ACT-001_Example.txt"
            prompt_path.parent.mkdir(parents=True)
            prompt_path.write_text("third-party prompt body", encoding="utf-8")
            self.write_json(metadata_path, valid_metadata())

            result = self.run_cli(
                "build",
                "--metadata",
                str(metadata_path),
                "--public-view",
                str(public_path),
                "--local-root",
                str(local_root),
                "--local-view",
                str(local_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            public_text = public_path.read_text(encoding="utf-8")
            local_text = local_path.read_text(encoding="utf-8")
            self.assertIn("ACT-001", public_text)
            self.assertIn("metadata_only", public_text)
            self.assertNotIn(str(local_root), public_text)
            self.assertNotIn("ACT-001_Example.txt", public_text)
            self.assertNotIn("third-party prompt body", public_text)
            self.assertIn(str(prompt_path), local_text)
            self.assertIn("ACT-001_Example.txt", local_text)

    def test_add_keeps_distinct_ids_on_same_post_and_patch_does_not_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "metadata.json"
            add_path = temp / "add.json"
            patch_path = temp / "patch.json"
            self.write_json(metadata_path, valid_metadata())

            added = valid_metadata()["cases"][0].copy()
            added["id"] = "CAM-002"
            added["title"] = "Example camera move"
            added["prompt"] = {
                **added["prompt"],
                "local_relative_path": "提示词/镜头与空间运动/CAM-002_Example.txt",
                "content_fingerprint": hashlib.sha256(
                    "different prompt body".encode("utf-8")
                ).hexdigest(),
            }
            self.write_json(add_path, added)
            result = self.run_cli(
                "add", "--metadata", str(metadata_path), "--record", str(add_path)
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            after_add = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(
                [item["id"] for item in after_add["cases"]],
                ["ACT-001", "CAM-002"],
            )
            self.assertEqual(
                after_add["cases"][0]["source"]["post_url"],
                after_add["cases"][1]["source"]["post_url"],
            )

            self.write_json(
                patch_path,
                {
                    "id": "CAM-002",
                    "source": {"post_url": "https://example.com/post/2"},
                },
            )
            result = self.run_cli(
                "add", "--metadata", str(metadata_path), "--record", str(patch_path)
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            updated = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual([item["id"] for item in updated["cases"]], ["ACT-001", "CAM-002"])
            self.assertEqual(updated["cases"][1]["source"]["post_url"], "https://example.com/post/2")

    def test_add_rejects_new_id_for_the_same_normalized_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "metadata.json"
            add_path = temp / "add.json"
            self.write_json(metadata_path, valid_metadata())
            duplicate_prompt = valid_metadata()["cases"][0].copy()
            duplicate_prompt["id"] = "CAM-099"
            duplicate_prompt["title"] = "Same prompt under a new id"
            duplicate_prompt["prompt"] = {
                **duplicate_prompt["prompt"],
                "local_relative_path": "提示词/镜头与空间运动/CAM-099_Same.txt",
            }
            self.write_json(add_path, duplicate_prompt)

            result = self.run_cli(
                "add", "--metadata", str(metadata_path), "--record", str(add_path)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate prompt fingerprint", result.stderr)
            unchanged = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual([item["id"] for item in unchanged["cases"]], ["ACT-001"])

    def test_validation_rejects_duplicate_ids_bad_paths_and_missing_schema(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "metadata.json"

            duplicate = valid_metadata()
            duplicate["cases"].append(duplicate["cases"][0].copy())
            self.write_json(metadata_path, duplicate)
            result = self.run_cli("validate", "--metadata", str(metadata_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("duplicate case id", result.stderr)

            bad_path = valid_metadata()
            bad_path["cases"][0]["prompt"]["local_relative_path"] = "../secret.txt"
            self.write_json(metadata_path, bad_path)
            result = self.run_cli("validate", "--metadata", str(metadata_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("relative path", result.stderr)

            missing_schema = valid_metadata()
            del missing_schema["cases"][0]["license"]
            self.write_json(metadata_path, missing_schema)
            result = self.run_cli("validate", "--metadata", str(metadata_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing field", result.stderr)

    def test_repository_snapshot_has_original_inventory_and_aliases_without_public_prompts(self) -> None:
        result = self.run_cli("validate", "--metadata", str(REPO_METADATA))
        self.assertEqual(result.returncode, 0, result.stderr)

        metadata = json.loads(REPO_METADATA.read_text(encoding="utf-8"))
        case_ids = [item["id"] for item in metadata["cases"]]
        aliases = {item["legacy_id"]: item["case_id"] for item in metadata["aliases"]}
        self.assertGreaterEqual(len(case_ids), 71)
        self.assertEqual(len(case_ids), len(set(case_ids)))
        self.assertEqual(
            aliases,
            {
                "P03男性四视图": "REF-002",
                "P03女性四视图": "REF-001",
                "P03手机随行跟拍待补全": "CAM-001",
                "P02御剑群战": "ACT-001",
                "P01玄幻双人重击": "ACT-004",
                "P03双角色替换": "EDT-005",
                "P03庭院人物场景": "ART-002",
            },
        )
        self.assertTrue(
            all(item["prompt"]["publication"] == "metadata_only" for item in metadata["cases"])
        )

    def test_migrate_reads_multi_author_row_without_copying_prompt_body(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            local_root = temp / "案例库"
            prompt_path = local_root / "提示词" / "镜头" / "CAM-008_Test.txt"
            source_note = local_root / "来源" / "CAM-008.md"
            prompt_path.parent.mkdir(parents=True)
            source_note.parent.mkdir(parents=True)
            prompt_path.write_text("unlicensed prompt body", encoding="utf-8")
            source_note.write_text("local source note", encoding="utf-8")
            source_index = temp / "索引.md"
            source_index.write_text(
                "# 索引\n\n"
                "## 镜头与空间运动\n\n"
                "| 编号·独立提示词 | 模型／步骤 | 交叉用途 | 作者 | 素材与来源 | 完整性与缺项 |\n"
                "|---|---|---|---|---|---|\n"
                f"| [CAM-008 Test]({prompt_path.as_posix()}) | Example Model · 视频 | 稳定机位／空间结构 | "
                "[@first](https://example.com/first)、[@second](https://example.com/second) | "
                f"[来源]({source_note.as_posix()}) | 原文完整；媒体未验收 |\n",
                encoding="utf-8",
            )
            author_index = temp / "作者.md"
            author_index.write_text(
                "| 作者／handle | 公开数字ID | 主页 | 可复查的方向 | 代表帖 | 身份记录来源 |\n"
                "|---|---|---|---|---|---|\n"
                "| First／@first | `123` | [主页](https://example.com/first) | 镜头 | "
                "[原帖](https://example.com/post/8) | 本地记录 |\n",
                encoding="utf-8",
            )
            metadata_path = temp / "metadata.json"

            result = self.run_cli(
                "migrate",
                "--source-index",
                str(source_index),
                "--author-index",
                str(author_index),
                "--local-root",
                str(local_root),
                "--metadata",
                str(metadata_path),
                "--as-of",
                "2026-09-12",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual([item["id"] for item in metadata["cases"]], ["CAM-008"])
            self.assertEqual(metadata["cases"][0]["author_id"], "first")
            self.assertIn("@second", metadata["cases"][0]["source"]["attribution_note"])
            self.assertNotIn("unlicensed prompt body", metadata_path.read_text(encoding="utf-8"))

            outside_source = temp / "outside.md"
            outside_source.write_text("must not be bound", encoding="utf-8")
            source_index.write_text(
                source_index.read_text(encoding="utf-8").replace(
                    source_note.as_posix(), outside_source.as_posix()
                ),
                encoding="utf-8",
            )
            result = self.run_cli(
                "migrate",
                "--source-index",
                str(source_index),
                "--author-index",
                str(author_index),
                "--local-root",
                str(local_root),
                "--metadata",
                str(metadata_path),
                "--as-of",
                "2026-09-12",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("outside local root", result.stderr)

    def test_migrate_preserves_local_source_locators_and_recovers_exact_post(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            local_root = temp / "案例库"
            prompt_path = local_root / "提示词" / "动作" / "ACT-008_Test.txt"
            media_path = local_root / "素材" / "2098370471414677906_1.mp4"
            source_path = local_root / "来源" / "案例.md"
            prompt_path.parent.mkdir(parents=True)
            media_path.parent.mkdir(parents=True)
            source_path.parent.mkdir(parents=True)
            prompt_path.write_text("unlicensed prompt body", encoding="utf-8")
            media_path.write_bytes(b"local media stays private")
            source_path.write_text(
                "来源：https://x.com/example/status/2098370471414677906\n",
                encoding="utf-8",
            )
            source_index = temp / "索引.md"
            source_index.write_text(
                "# 索引\n\n"
                "## 动作与打斗\n\n"
                "| 编号·独立提示词 | 模型／步骤 | 交叉用途 | 作者 | 素材与来源 | 完整性与缺项 |\n"
                "|---|---|---|---|---|---|\n"
                f"| [ACT-008 Test]({prompt_path.as_posix()}) | Example Model · 视频 | 接触 | "
                "[@example](https://x.com/example) | "
                f"[平台成品视频]({media_path.as_posix()}) · [来源与全部素材]({source_path.as_posix()}) | "
                "提示词末段完整；image 1 与 image 2 未取到；未观看验收 |\n",
                encoding="utf-8",
            )
            author_index = temp / "作者.md"
            author_index.write_text(
                "| 作者／handle | 公开数字ID | 主页 | 可复查的方向 | 代表帖 | 身份记录来源 |\n"
                "|---|---|---|---|---|---|\n"
                "| Example／@example | `123` | [主页](https://x.com/example) | 动作 | "
                "[原帖](https://x.com/example/status/2098370471414677906) | 本地记录 |\n",
                encoding="utf-8",
            )
            metadata_path = temp / "metadata.json"
            local_view = temp / "local-index.md"

            result = self.run_cli(
                "migrate",
                "--source-index",
                str(source_index),
                "--author-index",
                str(author_index),
                "--local-root",
                str(local_root),
                "--metadata",
                str(metadata_path),
                "--as-of",
                "2026-09-12",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            case = metadata["cases"][0]
            self.assertEqual(
                case["source"]["post_url"],
                "https://x.com/example/status/2098370471414677906",
            )
            self.assertEqual(
                case["source"]["local_locators"],
                [
                    {
                        "label": "平台成品视频",
                        "kind": "media",
                        "relative_path": "素材/2098370471414677906_1.mp4",
                    },
                    {
                        "label": "来源与全部素材",
                        "kind": "source",
                        "relative_path": "来源/案例.md",
                    },
                ],
            )
            self.assertEqual(case["prompt"]["missing_inputs"], ["see_status_note"])

            result = self.run_cli(
                "build",
                "--metadata",
                str(metadata_path),
                "--public-view",
                str(temp / "README.md"),
                "--local-root",
                str(local_root),
                "--local-view",
                str(local_view),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            local_text = local_view.read_text(encoding="utf-8")
            self.assertIn(str(media_path), local_text)
            self.assertIn(str(source_path), local_text)

    def test_migrate_uses_unique_recorded_source_when_media_id_differs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            local_root = temp / "案例库"
            prompt_path = local_root / "提示词" / "镜头" / "CAM-001_Test.txt"
            media_path = local_root / "素材" / "2097698712978087966_1.jpg"
            source_path = local_root / "来源" / "案例.md"
            prompt_path.parent.mkdir(parents=True)
            media_path.parent.mkdir(parents=True)
            source_path.parent.mkdir(parents=True)
            prompt_path.write_text("prompt", encoding="utf-8")
            media_path.write_bytes(b"local asset")
            source_path.write_text(
                "[在线来源](https://x.com/example/status/2097698694296686623)\n",
                encoding="utf-8",
            )
            source_index = temp / "索引.md"
            source_index.write_text(
                "## 镜头与空间运动\n\n"
                "| 编号·独立提示词 | 模型／步骤 | 交叉用途 | 作者 | 素材与来源 | 完整性与缺项 |\n"
                "|---|---|---|---|---|---|\n"
                f"| [CAM-001 Test]({prompt_path.as_posix()}) | Model · 视频 | 跟拍 | "
                "[@example](https://x.com/example) | "
                f"[参考图]({media_path.as_posix()}) · [来源与全部素材]({source_path.as_posix()}) | "
                "缺尾 |\n",
                encoding="utf-8",
            )
            author_index = temp / "作者.md"
            author_index.write_text(
                "| 作者／handle | 公开数字ID | 主页 | 可复查的方向 | 代表帖 | 身份记录来源 |\n"
                "|---|---|---|---|---|---|\n"
                "| Example／@example | `123` | [主页](https://x.com/example) | 镜头 | 无 | 本地记录 |\n",
                encoding="utf-8",
            )
            metadata_path = temp / "metadata.json"

            result = self.run_cli(
                "migrate",
                "--source-index",
                str(source_index),
                "--author-index",
                str(author_index),
                "--local-root",
                str(local_root),
                "--metadata",
                str(metadata_path),
                "--as-of",
                "2026-09-12",
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(
                metadata["cases"][0]["source"]["post_url"],
                "https://x.com/example/status/2097698694296686623",
            )


if __name__ == "__main__":
    unittest.main()
