import copy
import json
import hashlib
import os
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
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(value, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def write_prompt(self, local_root: Path, case: dict, body: str) -> Path:
        prompt_path = local_root / Path(case["prompt"]["local_relative_path"])
        prompt_path.parent.mkdir(parents=True, exist_ok=True)
        prompt_path.write_text(body, encoding="utf-8")
        return prompt_path

    def write_config(
        self,
        path: Path,
        metadata_path: Path,
        local_root: Path,
        local_view: Path,
    ) -> None:
        self.write_json(
            path,
            {
                "canonical_metadata": str(metadata_path),
                "local_root": str(local_root),
                "local_view": str(local_view),
            },
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
            self.assertIn("## 动作与打斗", local_text)
            self.assertIn("action / spatial-continuity", local_text)
            self.assertIn("Example Model（author_claimed）", local_text)
            self.assertIn(
                "complete；缺输入：未记录缺项（非输入齐备证明）", local_text
            )
            self.assertIn("author_post_unverified", local_text)
            self.assertIn("媒体 not_reviewed；许可 unknown", local_text)

    def test_build_rejects_overlapping_file_identities_without_modifying_files(self) -> None:
        scenarios = ("same_metadata", "dotdot_alias", "shared_views", "hardlink_alias")
        for scenario in scenarios:
            with self.subTest(scenario=scenario), tempfile.TemporaryDirectory() as temp_dir:
                temp = Path(temp_dir)
                metadata_path = temp / "canonical" / "metadata.json"
                public_view = temp / "README.md"
                local_view = temp / "开始这里.md"
                local_root = temp / "案例库"
                metadata = valid_metadata()
                self.write_json(metadata_path, metadata)
                self.write_prompt(local_root, metadata["cases"][0], "third-party prompt body")
                public_view.write_text("public sentinel\n", encoding="utf-8")
                local_view.write_text("local sentinel\n", encoding="utf-8")

                if scenario == "same_metadata":
                    public_argument = metadata_path
                    local_argument = local_view
                elif scenario == "dotdot_alias":
                    (metadata_path.parent / "child").mkdir()
                    public_argument = metadata_path.parent / "child" / ".." / "metadata.json"
                    local_argument = local_view
                elif scenario == "shared_views":
                    public_argument = public_view
                    local_argument = public_view
                else:
                    public_view.unlink()
                    os.link(metadata_path, public_view)
                    public_argument = public_view
                    local_argument = local_view

                protected = {
                    metadata_path: metadata_path.read_bytes(),
                    public_view: public_view.read_bytes(),
                    local_view: local_view.read_bytes(),
                }
                result = self.run_cli(
                    "build",
                    "--metadata",
                    str(metadata_path),
                    "--public-view",
                    str(public_argument),
                    "--local-root",
                    str(local_root),
                    "--local-view",
                    str(local_argument),
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("must be distinct", result.stderr)
                for path, content in protected.items():
                    self.assertEqual(path.read_bytes(), content)

    def test_add_rejects_dotdot_output_alias_without_modifying_bundle(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "canonical" / "metadata.json"
            (metadata_path.parent / "child").mkdir(parents=True)
            public_alias = metadata_path.parent / "child" / ".." / "metadata.json"
            local_root = temp / "案例库"
            local_view = temp / "开始这里.md"
            record_path = temp / "record.json"
            metadata = valid_metadata()
            self.write_json(metadata_path, metadata)
            self.write_prompt(local_root, metadata["cases"][0], "third-party prompt body")
            local_view.write_text("local sentinel\n", encoding="utf-8")
            self.write_json(record_path, {"id": "ACT-001"})
            before_metadata = metadata_path.read_bytes()
            before_local = local_view.read_bytes()

            result = self.run_cli(
                "add",
                "--metadata",
                str(metadata_path),
                "--record",
                str(record_path),
                "--public-view",
                str(public_alias),
                "--local-root",
                str(local_root),
                "--local-view",
                str(local_view),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("must be distinct", result.stderr)
            self.assertEqual(metadata_path.read_bytes(), before_metadata)
            self.assertEqual(local_view.read_bytes(), before_local)

    def test_add_keeps_distinct_ids_on_same_post_and_fill_only_patch_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "metadata.json"
            public_path = temp / "README.md"
            local_view = temp / "开始这里.md"
            local_root = temp / "案例库"
            add_path = temp / "add.json"
            patch_path = temp / "patch.json"
            metadata = valid_metadata()
            self.write_json(metadata_path, metadata)
            self.write_prompt(local_root, metadata["cases"][0], "third-party prompt body")

            added = copy.deepcopy(valid_metadata()["cases"][0])
            added["id"] = "CAM-002"
            added["title"] = "Example camera move"
            added["prompt"] = {
                **added["prompt"],
                "local_relative_path": "提示词/镜头与空间运动/CAM-002_Example.txt",
                "content_fingerprint": hashlib.sha256(
                    "differentpromptbody".encode("utf-8")
                ).hexdigest(),
            }
            self.write_prompt(local_root, added, "different prompt body")
            self.write_json(add_path, added)
            result = self.run_cli(
                "add",
                "--metadata",
                str(metadata_path),
                "--record",
                str(add_path),
                "--local-root",
                str(local_root),
                "--local-view",
                str(local_view),
                "--public-view",
                str(public_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            after_add = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(
                [item["id"] for item in after_add["cases"]],
                ["ACT-001", "CAM-002"],
            )
            self.assertEqual(after_add["snapshot"]["original_case_count"], 1)
            self.assertEqual(
                after_add["cases"][0]["source"]["post_url"],
                after_add["cases"][1]["source"]["post_url"],
            )

            self.write_json(
                patch_path,
                {
                    "id": "CAM-002",
                    "source": {"post_url": "https://example.com/post/1"},
                },
            )
            result = self.run_cli(
                "add",
                "--metadata",
                str(metadata_path),
                "--record",
                str(patch_path),
                "--local-root",
                str(local_root),
                "--local-view",
                str(local_view),
                "--public-view",
                str(public_path),
            )
            self.assertEqual(result.returncode, 0, result.stderr)

            updated = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual([item["id"] for item in updated["cases"]], ["ACT-001", "CAM-002"])
            self.assertEqual(updated["snapshot"]["original_case_count"], 1)
            self.assertEqual(updated["cases"][1]["source"]["post_url"], "https://example.com/post/1")

            self.write_json(
                patch_path,
                {"id": "CAM-002", "source": {"post_url": "https://example.com/post/2"}},
            )
            before = metadata_path.read_bytes()
            result = self.run_cli(
                "add",
                "--metadata",
                str(metadata_path),
                "--record",
                str(patch_path),
                "--local-root",
                str(local_root),
                "--local-view",
                str(local_view),
                "--public-view",
                str(public_path),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("conflicting non-empty value", result.stderr)
            self.assertEqual(metadata_path.read_bytes(), before)

    def test_add_rejects_new_id_for_the_same_normalized_prompt(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "metadata.json"
            add_path = temp / "add.json"
            local_root = temp / "案例库"
            local_view = temp / "开始这里.md"
            public_view = temp / "README.md"
            metadata = valid_metadata()
            self.write_json(metadata_path, metadata)
            self.write_prompt(local_root, metadata["cases"][0], "third-party prompt body")
            duplicate_prompt = copy.deepcopy(valid_metadata()["cases"][0])
            duplicate_prompt["id"] = "CAM-099"
            duplicate_prompt["title"] = "Same prompt under a new id"
            duplicate_prompt["prompt"] = {
                **duplicate_prompt["prompt"],
                "local_relative_path": "提示词/镜头与空间运动/CAM-099_Same.txt",
            }
            self.write_prompt(local_root, duplicate_prompt, "third-party prompt body")
            self.write_json(add_path, duplicate_prompt)

            result = self.run_cli(
                "add",
                "--metadata",
                str(metadata_path),
                "--record",
                str(add_path),
                "--local-root",
                str(local_root),
                "--local-view",
                str(local_view),
                "--public-view",
                str(public_view),
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

    def test_validation_rejects_windows_drive_relative_and_unc_local_paths(self) -> None:
        mutations = (
            (
                "prompt drive relative",
                lambda value: value["cases"][0]["prompt"].update(
                    {"local_relative_path": "C:example.txt"}
                ),
            ),
            (
                "locator drive relative",
                lambda value: value["cases"][0]["source"].update(
                    {
                        "local_locators": [
                            {
                                "label": "source",
                                "kind": "source",
                                "relative_path": "C:example.txt",
                            }
                        ]
                    }
                ),
            ),
            (
                "locator UNC",
                lambda value: value["cases"][0]["source"].update(
                    {
                        "local_locators": [
                            {
                                "label": "source",
                                "kind": "source",
                                "relative_path": "//server/share/example.txt",
                            }
                        ]
                    }
                ),
            ),
        )
        for name, mutate in mutations:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp_dir:
                metadata_path = Path(temp_dir) / "metadata.json"
                metadata = valid_metadata()
                mutate(metadata)
                self.write_json(metadata_path, metadata)

                result = self.run_cli("validate", "--metadata", str(metadata_path))

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("relative_path:", result.stderr)

    def test_build_rejects_embedded_machine_paths_but_keeps_urls_and_relative_text(self) -> None:
        for embedded_path in (
            "Evidence at C:/synthetic-private/example.txt",
            "Evidence at /home/synthetic-private/example.txt",
        ):
            with self.subTest(embedded_path=embedded_path), tempfile.TemporaryDirectory() as temp_dir:
                temp = Path(temp_dir)
                metadata_path = temp / "metadata.json"
                public_view = temp / "README.md"
                metadata = valid_metadata()
                metadata["cases"][0]["summary"] = embedded_path
                self.write_json(metadata_path, metadata)
                public_view.write_text("public sentinel\n", encoding="utf-8")
                before = public_view.read_bytes()

                result = self.run_cli(
                    "build",
                    "--metadata",
                    str(metadata_path),
                    "--public-view",
                    str(public_view),
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("not publishable", result.stderr)
                self.assertEqual(public_view.read_bytes(), before)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "metadata.json"
            public_view = temp / "README.md"
            metadata = valid_metadata()
            metadata["cases"][0]["summary"] = (
                "参见 https://example.com/reference 与 提示词/中文原文.txt。"
            )
            self.write_json(metadata_path, metadata)

            result = self.run_cli(
                "build",
                "--metadata",
                str(metadata_path),
                "--public-view",
                str(public_view),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(metadata["cases"][0]["summary"], public_view.read_text(encoding="utf-8"))

    def test_build_scans_machine_paths_after_url_boundaries(self) -> None:
        unsafe_summaries = (
            "参见 https://example.com/reference，证据在/home/private/example.txt",
            "参见 https://example.com/reference，证据在C:/private/example.txt",
            r"参见 https://example.com/reference，证据在\\server\share\example.txt",
            "参见 https://example.com/reference,证据在/home/private/example.txt",
            "参见 https://example.com/reference:证据在C:/private/example.txt",
            r"参见 https://example.com/reference证据在\\server\share\example.txt",
            "参见 https://example.com/reference证据在/home/private/example.txt",
            "证据：/home/private/example.txt",
            "source=/home/private/example.txt",
            "source=(/home/private/example.txt)",
            "evidence:/home/private/example.txt",
            "relative/C:/private/example.txt",
        )
        for summary in unsafe_summaries:
            with self.subTest(summary=summary), tempfile.TemporaryDirectory() as temp_dir:
                temp = Path(temp_dir)
                metadata_path = temp / "metadata.json"
                public_view = temp / "README.md"
                metadata = valid_metadata()
                metadata["cases"][0]["summary"] = summary
                self.write_json(metadata_path, metadata)
                public_view.write_text("public sentinel\n", encoding="utf-8")
                before = public_view.read_bytes()

                result = self.run_cli(
                    "build",
                    "--metadata",
                    str(metadata_path),
                    "--public-view",
                    str(public_view),
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn("not publishable", result.stderr)
                self.assertEqual(public_view.read_bytes(), before)

        safe_summaries = (
            "参见 https://example.com/reference",
            "参见 https://example.com/a/b?next=/home/private&win=C:/private#part-1",
            "参见 https://example.com/a/b?next=%2Fhome%2Fprivate&label=C%3A%2Fprivate#part-1",
            "参见 https://example.com/reference，另见提示词/中文原文.txt",
            "素材/home/example.txt",
            "素材 files/home/example.txt",
            "docs/tmp/example.txt",
            "archive/Users/example.txt",
        )
        for summary in safe_summaries:
            with self.subTest(summary=summary), tempfile.TemporaryDirectory() as temp_dir:
                temp = Path(temp_dir)
                metadata_path = temp / "metadata.json"
                public_view = temp / "README.md"
                metadata = valid_metadata()
                metadata["cases"][0]["summary"] = summary
                self.write_json(metadata_path, metadata)

                result = self.run_cli(
                    "build",
                    "--metadata",
                    str(metadata_path),
                    "--public-view",
                    str(public_view),
                )

                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn(summary, public_view.read_text(encoding="utf-8"))

    def test_validation_rejects_local_symlink_that_resolves_outside_approved_root(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            local_root = temp / "案例库"
            outside_root = temp / "outside"
            outside_root.mkdir()
            (outside_root / "source.md").write_text("outside source", encoding="utf-8")
            (outside_root / "prompt.txt").write_text("third-party prompt body", encoding="utf-8")
            local_root.mkdir()
            escape = local_root / "escape"
            if os.name == "nt":
                junction = subprocess.run(
                    ["cmd", "/c", "mklink", "/J", str(escape), str(outside_root)],
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    capture_output=True,
                    check=False,
                )
                self.assertEqual(junction.returncode, 0, junction.stderr)
            else:
                escape.symlink_to(outside_root, target_is_directory=True)
            metadata_path = temp / "metadata.json"
            metadata = valid_metadata()
            metadata["cases"][0]["source"]["local_locators"] = [
                {"label": "source", "kind": "source", "relative_path": "escape/source.md"}
            ]
            metadata["cases"][0]["prompt"].update(
                {"local_relative_path": "escape/prompt.txt"}
            )
            self.write_json(metadata_path, metadata)

            result = self.run_cli(
                "validate",
                "--metadata",
                str(metadata_path),
                "--local-root",
                str(local_root),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("outside local root", result.stderr)

    def test_config_binds_canonical_metadata_and_explicit_arguments_override_it(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            canonical_path = temp / "canonical" / "metadata.json"
            explicit_path = temp / "explicit" / "metadata.json"
            local_root = temp / "案例库"
            local_view = temp / "开始这里.md"
            config_path = temp / "local-config.json"

            canonical = valid_metadata()
            canonical["cases"][0]["title"] = "Canonical title"
            explicit = valid_metadata()
            explicit["cases"][0]["title"] = "Explicit title"
            self.write_json(canonical_path, canonical)
            self.write_json(explicit_path, explicit)
            self.write_prompt(local_root, canonical["cases"][0], "third-party prompt body")
            self.write_config(config_path, canonical_path, local_root, local_view)

            result = self.run_cli("build", "--config", str(config_path))
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn(
                "Canonical title",
                (canonical_path.parent / "README.md").read_text(encoding="utf-8"),
            )
            self.assertIn("Canonical title", local_view.read_text(encoding="utf-8"))

            explicit_public = temp / "explicit-public.md"
            explicit_local = temp / "explicit-local.md"
            result = self.run_cli(
                "build",
                "--config",
                str(config_path),
                "--metadata",
                str(explicit_path),
                "--public-view",
                str(explicit_public),
                "--local-view",
                str(explicit_local),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Explicit title", explicit_public.read_text(encoding="utf-8"))
            self.assertIn("Explicit title", explicit_local.read_text(encoding="utf-8"))

    def test_broken_canonical_binding_fails_without_falling_back_to_packaged_snapshot(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            missing_metadata = temp / "missing" / "metadata.json"
            local_root = temp / "案例库"
            local_view = temp / "开始这里.md"
            config_path = temp / "local-config.json"
            self.write_config(config_path, missing_metadata, local_root, local_view)

            result = self.run_cli("validate", "--config", str(config_path))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(str(missing_metadata), result.stderr)
            self.assertIn("cannot read JSON", result.stderr)

    def test_add_accepts_new_author_validates_local_files_and_refreshes_both_views(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "canonical" / "metadata.json"
            public_view = metadata_path.parent / "README.md"
            local_root = temp / "案例库"
            local_view = local_root / "开始这里.md"
            config_path = temp / "local-config.json"
            record_path = temp / "case.json"
            author_path = temp / "author.json"

            metadata = valid_metadata()
            self.write_json(metadata_path, metadata)
            self.write_prompt(local_root, metadata["cases"][0], "third-party prompt body")
            self.write_config(config_path, metadata_path, local_root, local_view)

            new_case = copy.deepcopy(metadata["cases"][0])
            new_case.update(
                {
                    "id": "CAM-002",
                    "title": "New author camera case",
                    "category": "镜头与空间运动",
                    "author_id": "author-new",
                    "task_tags": ["camera", "tracking"],
                }
            )
            new_case["source"] = {
                "post_url": "https://example.com/post/new",
                "attribution_status": "author_post_unverified",
                "attribution_note": "author supplied",
                "status_note": "media not reviewed",
                "local_locators": [
                    {
                        "label": "来源记录",
                        "kind": "source",
                        "relative_path": "来源/CAM-002.md",
                    }
                ],
            }
            new_case["prompt"] = {
                **new_case["prompt"],
                "local_relative_path": "提示词/镜头与空间运动/CAM-002_New.txt",
                "content_fingerprint": hashlib.sha256(
                    "newpromptbody".encode("utf-8")
                ).hexdigest(),
            }
            self.write_prompt(local_root, new_case, "new prompt body")
            source_path = local_root / "来源" / "CAM-002.md"
            source_path.parent.mkdir(parents=True)
            source_path.write_text("local source record", encoding="utf-8")
            self.write_json(record_path, new_case)
            self.write_json(
                author_path,
                {
                    "id": "author-new",
                    "display_name": "New Author",
                    "handle": "@new",
                    "profile_url": "https://example.com/new",
                    "public_numeric_id": None,
                },
            )

            result = self.run_cli(
                "add",
                "--config",
                str(config_path),
                "--record",
                str(record_path),
                "--author-record",
                str(author_path),
            )

            self.assertEqual(result.returncode, 0, result.stderr)
            updated = json.loads(metadata_path.read_text(encoding="utf-8"))
            self.assertEqual(updated["authors"][-1]["id"], "author-new")
            self.assertEqual(updated["cases"][-1]["id"], "CAM-002")
            self.assertIn("New author camera case", public_view.read_text(encoding="utf-8"))
            local_text = local_view.read_text(encoding="utf-8")
            self.assertIn("## 镜头与空间运动", local_text)
            self.assertIn(str(source_path), local_text)

    def test_add_validation_failure_leaves_metadata_and_views_byte_identical(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "canonical" / "metadata.json"
            public_view = metadata_path.parent / "README.md"
            local_root = temp / "案例库"
            local_view = local_root / "开始这里.md"
            config_path = temp / "local-config.json"
            record_path = temp / "case.json"

            metadata = valid_metadata()
            self.write_json(metadata_path, metadata)
            self.write_prompt(local_root, metadata["cases"][0], "third-party prompt body")
            self.write_config(config_path, metadata_path, local_root, local_view)
            built = self.run_cli("build", "--config", str(config_path))
            self.assertEqual(built.returncode, 0, built.stderr)
            before = {
                path: path.read_bytes()
                for path in (metadata_path, public_view, local_view)
            }

            missing_case = copy.deepcopy(metadata["cases"][0])
            missing_case["id"] = "CAM-003"
            missing_case["title"] = "Missing local TXT"
            missing_case["prompt"] = {
                **missing_case["prompt"],
                "local_relative_path": "提示词/镜头与空间运动/CAM-003_Missing.txt",
                "content_fingerprint": hashlib.sha256(b"missing").hexdigest(),
            }
            self.write_json(record_path, missing_case)

            result = self.run_cli(
                "add",
                "--config",
                str(config_path),
                "--record",
                str(record_path),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("missing local TXT", result.stderr)
            for path, content in before.items():
                self.assertEqual(path.read_bytes(), content)

    def test_add_fills_only_empty_values_and_rejects_nonempty_conflicts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "metadata.json"
            public_view = temp / "README.md"
            local_root = temp / "案例库"
            local_view = temp / "开始这里.md"
            record_path = temp / "patch.json"
            metadata = valid_metadata()
            metadata["cases"][0]["source"]["post_url"] = None
            self.write_json(metadata_path, metadata)
            self.write_prompt(local_root, metadata["cases"][0], "third-party prompt body")

            patch = {"id": "ACT-001", "source": {"post_url": "https://example.com/post/filled"}}
            self.write_json(record_path, patch)
            args = (
                "add",
                "--metadata",
                str(metadata_path),
                "--record",
                str(record_path),
                "--local-root",
                str(local_root),
                "--local-view",
                str(local_view),
                "--public-view",
                str(public_view),
            )
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(
                json.loads(metadata_path.read_text(encoding="utf-8"))["cases"][0]["source"]["post_url"],
                "https://example.com/post/filled",
            )
            first_bytes = metadata_path.read_bytes()
            result = self.run_cli(*args)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(metadata_path.read_bytes(), first_bytes)

            self.write_json(
                record_path,
                {"id": "ACT-001", "source": {"post_url": "https://example.com/post/conflict"}},
            )
            result = self.run_cli(*args)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("conflicting non-empty value", result.stderr)
            self.assertEqual(metadata_path.read_bytes(), first_bytes)

    def test_validation_rejects_unknown_fields_empty_tags_and_bad_array_members(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp = Path(temp_dir)
            metadata_path = temp / "metadata.json"
            base = valid_metadata()
            base["cases"][0]["source"].update(
                {"attribution_note": "allowed note", "status_note": "allowed status"}
            )
            base["cases"][0]["source"]["local_locators"] = [
                {"label": "source", "kind": "source", "relative_path": "来源/ACT-001.md"}
            ]
            base["aliases"] = [{"legacy_id": "OLD-ACT-001", "case_id": "ACT-001"}]
            self.write_json(metadata_path, base)
            allowed = self.run_cli("validate", "--metadata", str(metadata_path))
            self.assertEqual(allowed.returncode, 0, allowed.stderr)

            mutations = [
                ("top-level", lambda value: value.update({"prompt_body": "private"})),
                ("snapshot", lambda value: value["snapshot"].update({"qa": {}})),
                ("author", lambda value: value["authors"][0].update({"raw_response": {}})),
                ("case", lambda value: value["cases"][0].update({"qa": {}})),
                ("model", lambda value: value["cases"][0]["model_claim"].update({"raw": {}})),
                ("source", lambda value: value["cases"][0]["source"].update({"raw_response": {}})),
                ("locator", lambda value: value["cases"][0]["source"]["local_locators"][0].update({"absolute_path": "private"})),
                ("prompt", lambda value: value["cases"][0]["prompt"].update({"prompt_body": "private"})),
                ("license", lambda value: value["cases"][0]["license"].update({"qa": {}})),
                ("alias", lambda value: value["aliases"][0].update({"note": "private"})),
                ("empty tags", lambda value: value["cases"][0].update({"task_tags": []})),
                ("bad missing input", lambda value: value["cases"][0]["prompt"].update({"missing_inputs": [1]})),
                ("bad author member", lambda value: value.update({"authors": ["bad"]})),
                ("bad case member", lambda value: value.update({"cases": ["bad"]})),
                ("bad alias member", lambda value: value.update({"aliases": ["bad"]})),
            ]
            for name, mutate in mutations:
                with self.subTest(name=name):
                    value = copy.deepcopy(base)
                    mutate(value)
                    self.write_json(metadata_path, value)
                    result = self.run_cli("validate", "--metadata", str(metadata_path))
                    self.assertNotEqual(result.returncode, 0, name)

    def test_validation_rejects_boolean_schema_version_and_untyped_author_reference(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            metadata_path = Path(temp_dir) / "metadata.json"

            boolean_version = valid_metadata()
            boolean_version["schema_version"] = True
            self.write_json(metadata_path, boolean_version)
            result = self.run_cli("validate", "--metadata", str(metadata_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("metadata.schema_version: expected integer 1", result.stderr)

            untyped_author = valid_metadata()
            untyped_author["cases"][0]["author_id"] = []
            self.write_json(metadata_path, untyped_author)
            result = self.run_cli("validate", "--metadata", str(metadata_path))
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("author_id: expected non-empty text", result.stderr)
            self.assertNotIn("Traceback", result.stderr)

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
