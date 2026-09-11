#!/usr/bin/env python3
"""Validate and render the shared, metadata-only drama case library."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
import os
import re
import sys
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any


TOP_LEVEL_FIELDS = {
    "schema_version",
    "library_id",
    "snapshot",
    "authors",
    "cases",
    "aliases",
}
CONFIG_FIELDS = {"canonical_metadata", "local_root", "local_view"}
SNAPSHOT_FIELDS = {"as_of", "original_case_count", "prompt_policy"}
AUTHOR_FIELDS = {
    "id",
    "display_name",
    "handle",
    "profile_url",
    "public_numeric_id",
}
CASE_FIELDS = {
    "id",
    "title",
    "category",
    "summary",
    "model_claim",
    "task_tags",
    "author_id",
    "source",
    "prompt",
    "media_verification",
    "license",
}
MODEL_FIELDS = {"name", "basis"}
SOURCE_REQUIRED_FIELDS = {"post_url", "attribution_status", "local_locators"}
SOURCE_FIELDS = SOURCE_REQUIRED_FIELDS | {"attribution_note", "status_note"}
LOCAL_LOCATOR_FIELDS = {"label", "kind", "relative_path"}
PROMPT_FIELDS = {
    "completeness",
    "missing_inputs",
    "local_relative_path",
    "content_fingerprint",
    "publication",
}
LICENSE_FIELDS = {"status", "prompt_redistribution"}
ALIAS_FIELDS = {"legacy_id", "case_id"}
WINDOWS_DRIVE_RE = re.compile(r"^[A-Za-z]:")
EMBEDDED_WINDOWS_PATH_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:[A-Za-z]:[\\/]|\\\\[^\\/\s]+[\\/][^\\/\s]+)"
)
EMBEDDED_UNC_PATH_RE = re.compile(r"(?:^|[\s(\[{'\"=：:])//[^/\s]+/[^/\s]+")
EMBEDDED_POSIX_PATH_RE = re.compile(r"(?:^|(?<=[\s(\[{'\"=：:]))/(?![/\s])")
HTTP_URL_RE = re.compile(r"https?://[^\s<>\[\]()\"']+")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
CASE_LINK_RE = re.compile(
    r"^\[(?P<id>[A-Z]+-\d+) (?P<title>[^\]]+)\]\((?P<path>[^)]+)\)$"
)
MARKDOWN_LINK_RE = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
SOCIAL_POST_URL_RE = re.compile(
    r"https?://(?:www\.)?(?:x\.com|twitter\.com)/[^/\s\"')\]]+/status/(\d+)"
)
MEDIA_SUFFIXES = {
    ".aac",
    ".avi",
    ".flac",
    ".gif",
    ".jpeg",
    ".jpg",
    ".m4a",
    ".mov",
    ".mp3",
    ".mp4",
    ".png",
    ".wav",
    ".webm",
    ".webp",
}
TEXT_SOURCE_SUFFIXES = {".html", ".json", ".md", ".txt"}
LEGACY_ALIASES = {
    "P03男性四视图": "REF-002",
    "P03女性四视图": "REF-001",
    "P03手机随行跟拍待补全": "CAM-001",
    "P02御剑群战": "ACT-001",
    "P01玄幻双人重击": "ACT-004",
    "P03双角色替换": "EDT-005",
    "P03庭院人物场景": "ART-002",
}
PACKAGED_METADATA = (
    Path(__file__).resolve().parents[1]
    / "references"
    / "case-library"
    / "metadata.json"
)
PACKAGED_CONFIG = PACKAGED_METADATA.parent / "local-config.json"


class ValidationError(ValueError):
    pass


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON {path}: {exc}") from exc


def config_path_value(value: Any, key: str, config_path: Path) -> Path:
    require_text(value, f"config.{key}")
    path = Path(value)
    if not path.is_absolute():
        path = config_path.parent / path
    return path


def resolve_bindings(args: argparse.Namespace) -> tuple[Path, Path, Path | None, Path | None]:
    config_path = getattr(args, "config", None)
    if config_path is None and getattr(args, "metadata", None) is None:
        if PACKAGED_CONFIG.is_file():
            config_path = PACKAGED_CONFIG

    config: dict[str, Any] | None = None
    if config_path is not None:
        config = read_json(config_path)
        require_fields(config, CONFIG_FIELDS, "config")

    metadata = getattr(args, "metadata", None)
    if metadata is None:
        metadata = (
            config_path_value(config["canonical_metadata"], "canonical_metadata", config_path)
            if config is not None
            else PACKAGED_METADATA
        )

    local_root = getattr(args, "local_root", None)
    if local_root is None and config is not None:
        local_root = config_path_value(config["local_root"], "local_root", config_path)

    local_view = getattr(args, "local_view", None)
    if local_view is None and config is not None:
        local_view = config_path_value(config["local_view"], "local_view", config_path)

    public_view = getattr(args, "public_view", None)
    if public_view is None:
        public_view = metadata.parent / "README.md"
    return metadata, public_view, local_root, local_view


def require_fields(
    value: Any,
    fields: set[str],
    location: str,
    allowed_fields: set[str] | None = None,
) -> None:
    if not isinstance(value, dict):
        raise ValidationError(f"{location}: expected object")
    missing = fields - value.keys()
    if missing:
        raise ValidationError(
            f"{location}: missing field(s): {', '.join(sorted(missing))}"
        )
    unexpected = value.keys() - (allowed_fields or fields)
    if unexpected:
        raise ValidationError(
            f"{location}: unknown field(s): {', '.join(sorted(unexpected))}"
        )


def require_text(value: Any, location: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(f"{location}: expected non-empty text")


def validate_url(value: Any, location: str) -> None:
    if value is None:
        return
    require_text(value, location)
    if not value.startswith(("https://", "http://")):
        raise ValidationError(f"{location}: expected http(s) URL or null")


def validate_relative_path(value: Any, location: str) -> None:
    require_text(value, location)
    if WINDOWS_DRIVE_RE.match(value) or "\\" in value:
        raise ValidationError(f"{location}: expected safe POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValidationError(f"{location}: expected safe relative path")
    if path.suffix.lower() != ".txt":
        raise ValidationError(f"{location}: local prompt path must end in .txt")


def validate_local_locator(value: Any, location: str) -> None:
    require_fields(value, LOCAL_LOCATOR_FIELDS, location)
    require_text(value["label"], f"{location}.label")
    if not isinstance(value["kind"], str) or value["kind"] not in {"media", "source"}:
        raise ValidationError(f"{location}.kind: expected media or source")
    relative_path = value["relative_path"]
    require_text(relative_path, f"{location}.relative_path")
    if WINDOWS_DRIVE_RE.match(relative_path) or "\\" in relative_path:
        raise ValidationError(f"{location}.relative_path: expected safe POSIX relative path")
    path = PurePosixPath(relative_path)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValidationError(f"{location}.relative_path: expected safe relative path")


def normalized_prompt_fingerprint(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = re.sub(r"\s+", "", text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def resolve_local_path(local_root: Path, relative_path: str, location: str) -> Path:
    approved_root = local_root.resolve()
    resolved_path = (approved_root / Path(relative_path)).resolve()
    try:
        resolved_path.relative_to(approved_root)
    except ValueError as exc:
        raise ValidationError(f"{location}: resolved path is outside local root") from exc
    return resolved_path


def reject_embedded_absolute_paths(value: Any, location: str = "metadata") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            reject_embedded_absolute_paths(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_embedded_absolute_paths(child, f"{location}[{index}]")
    elif isinstance(value, str):
        publishable_text = HTTP_URL_RE.sub("", value)
        if (
            EMBEDDED_WINDOWS_PATH_RE.search(publishable_text)
            or EMBEDDED_UNC_PATH_RE.search(publishable_text)
            or EMBEDDED_POSIX_PATH_RE.search(publishable_text)
        ):
            raise ValidationError(f"{location}: absolute machine path is not publishable")


def validate_metadata(metadata: Any, local_root: Path | None = None) -> dict[str, Any]:
    require_fields(metadata, TOP_LEVEL_FIELDS, "metadata")
    if type(metadata["schema_version"]) is not int or metadata["schema_version"] != 1:
        raise ValidationError("metadata.schema_version: expected integer 1")
    require_text(metadata["library_id"], "metadata.library_id")
    require_fields(metadata["snapshot"], SNAPSHOT_FIELDS, "metadata.snapshot")
    require_text(metadata["snapshot"]["as_of"], "metadata.snapshot.as_of")
    require_text(
        metadata["snapshot"]["prompt_policy"], "metadata.snapshot.prompt_policy"
    )
    if isinstance(metadata["snapshot"]["original_case_count"], bool) or not isinstance(
        metadata["snapshot"]["original_case_count"], int
    ):
        raise ValidationError("metadata.snapshot.original_case_count: expected integer")
    reject_embedded_absolute_paths(metadata)

    authors = metadata["authors"]
    if not isinstance(authors, list):
        raise ValidationError("metadata.authors: expected array")
    author_ids: set[str] = set()
    for index, author in enumerate(authors):
        location = f"metadata.authors[{index}]"
        require_fields(author, AUTHOR_FIELDS, location)
        require_text(author["id"], f"{location}.id")
        require_text(author["display_name"], f"{location}.display_name")
        if author["handle"] is not None:
            require_text(author["handle"], f"{location}.handle")
        validate_url(author["profile_url"], f"{location}.profile_url")
        if author["public_numeric_id"] is not None:
            require_text(author["public_numeric_id"], f"{location}.public_numeric_id")
        if author["id"] in author_ids:
            raise ValidationError(f"duplicate author id: {author['id']}")
        author_ids.add(author["id"])

    cases = metadata["cases"]
    if not isinstance(cases, list):
        raise ValidationError("metadata.cases: expected array")
    case_ids: set[str] = set()
    local_paths: set[str] = set()
    prompt_fingerprints: set[str] = set()
    for index, case in enumerate(cases):
        location = f"metadata.cases[{index}]"
        require_fields(case, CASE_FIELDS, location)
        for field in ("id", "title", "category", "summary", "media_verification"):
            require_text(case[field], f"{location}.{field}")
        if case["id"] in case_ids:
            raise ValidationError(f"duplicate case id: {case['id']}")
        case_ids.add(case["id"])

        require_fields(case["model_claim"], MODEL_FIELDS, f"{location}.model_claim")
        require_text(case["model_claim"]["name"], f"{location}.model_claim.name")
        require_text(case["model_claim"]["basis"], f"{location}.model_claim.basis")
        if not isinstance(case["task_tags"], list) or not case["task_tags"] or not all(
            isinstance(tag, str) and tag.strip() for tag in case["task_tags"]
        ):
            raise ValidationError(f"{location}.task_tags: expected non-empty text array")
        require_text(case["author_id"], f"{location}.author_id")
        if case["author_id"] not in author_ids:
            raise ValidationError(f"{location}.author_id: unknown author id")

        require_fields(
            case["source"],
            SOURCE_REQUIRED_FIELDS,
            f"{location}.source",
            SOURCE_FIELDS,
        )
        validate_url(case["source"]["post_url"], f"{location}.source.post_url")
        require_text(
            case["source"]["attribution_status"],
            f"{location}.source.attribution_status",
        )
        for optional_note in ("attribution_note", "status_note"):
            if optional_note in case["source"]:
                require_text(
                    case["source"][optional_note],
                    f"{location}.source.{optional_note}",
                )
        local_locators = case["source"]["local_locators"]
        if not isinstance(local_locators, list):
            raise ValidationError(f"{location}.source.local_locators: expected array")
        for locator_index, locator in enumerate(local_locators):
            locator_location = (
                f"{location}.source.local_locators[{locator_index}]"
            )
            validate_local_locator(locator, locator_location)
            if local_root is not None:
                locator_path = resolve_local_path(
                    local_root, locator["relative_path"], f"{locator_location}.relative_path"
                )
                if not locator_path.exists():
                    raise ValidationError(
                        f"{locator_location}.relative_path: missing local item {locator_path}"
                    )
        require_fields(case["prompt"], PROMPT_FIELDS, f"{location}.prompt")
        require_text(case["prompt"]["completeness"], f"{location}.prompt.completeness")
        if not isinstance(case["prompt"]["missing_inputs"], list) or not all(
            isinstance(item, str) and item.strip()
            for item in case["prompt"]["missing_inputs"]
        ):
            raise ValidationError(
                f"{location}.prompt.missing_inputs: expected text array"
            )
        validate_relative_path(
            case["prompt"]["local_relative_path"],
            f"{location}.prompt.local_relative_path",
        )
        fingerprint = case["prompt"]["content_fingerprint"]
        if not isinstance(fingerprint, str) or not SHA256_RE.fullmatch(fingerprint):
            raise ValidationError(
                f"{location}.prompt.content_fingerprint: expected lowercase SHA-256"
            )
        if fingerprint in prompt_fingerprints:
            raise ValidationError(f"duplicate prompt fingerprint: {fingerprint}")
        prompt_fingerprints.add(fingerprint)
        if case["prompt"]["local_relative_path"] in local_paths:
            raise ValidationError(
                f"duplicate local prompt path: {case['prompt']['local_relative_path']}"
            )
        local_paths.add(case["prompt"]["local_relative_path"])
        if case["prompt"]["publication"] != "metadata_only":
            raise ValidationError(
                f"{location}.prompt.publication: current library permits metadata_only only"
            )

        require_fields(case["license"], LICENSE_FIELDS, f"{location}.license")
        require_text(case["license"]["status"], f"{location}.license.status")
        if case["license"]["prompt_redistribution"] != "not_permitted":
            raise ValidationError(
                f"{location}.license.prompt_redistribution: expected not_permitted"
            )

        if local_root is not None:
            prompt_path = resolve_local_path(
                local_root,
                case["prompt"]["local_relative_path"],
                f"{location}.prompt.local_relative_path",
            )
            if not prompt_path.is_file():
                raise ValidationError(
                    f"{location}.prompt.local_relative_path: missing local TXT {prompt_path}"
                )
            actual_fingerprint = normalized_prompt_fingerprint(prompt_path)
            if actual_fingerprint != fingerprint:
                raise ValidationError(
                    f"{location}.prompt.content_fingerprint: local TXT content mismatch"
                )

    aliases = metadata["aliases"]
    if not isinstance(aliases, list):
        raise ValidationError("metadata.aliases: expected array")
    legacy_ids: set[str] = set()
    for index, alias in enumerate(aliases):
        location = f"metadata.aliases[{index}]"
        require_fields(alias, ALIAS_FIELDS, location)
        require_text(alias["legacy_id"], f"{location}.legacy_id")
        require_text(alias["case_id"], f"{location}.case_id")
        if alias["legacy_id"] in legacy_ids:
            raise ValidationError(f"duplicate legacy alias: {alias['legacy_id']}")
        if alias["case_id"] not in case_ids:
            raise ValidationError(
                f"{location}.case_id: alias target does not exist: {alias['case_id']}"
            )
        legacy_ids.add(alias["legacy_id"])

    return metadata


def author_label(author: dict[str, Any]) -> str:
    label = author["handle"] or author["display_name"]
    if author["profile_url"]:
        return f"[{label}]({author['profile_url']})"
    return label


def render_public(metadata: dict[str, Any]) -> str:
    authors = {author["id"]: author for author in metadata["authors"]}
    lines = [
        "# 公共案例索引",
        "",
        "> 本页由 `metadata.json` 机械生成。它只发布来源元数据与原创中性简述，不发布第三方提示词全文、媒体、本机路径，也不授予再发布许可。模型与效果状态均按来源记录，未复现不等于可复现；案例不得新增或改写项目正典事实。",
        "",
        "使用时按当前创作、对白或制作问题匹配用途标签，只读命中单条。需要原提示词时，必须在获准且已绑定的本地案例根中读取；本页没有本地原文时，使用现有规则做原创设计，不伪称读过案例。",
        "",
        "逐条缺输入、归属提醒与原始状态说明保存在生成本页所用的 [metadata.json](metadata.json) 同 ID 记录中；私有绑定可把维护命令指向唯一 canonical metadata，包内文件只作发布快照。公开可读不等于取得原文再发布许可。",
        "",
        "## 本地绑定与维护",
        "",
        "私有绑定写入同目录且已被 Git 忽略的 `local-config.json`，只含 `canonical_metadata`、`local_root`、`local_view`。安装副本中的 metadata 是发布快照；存在绑定时，`validate`、`build`、`add` 都使用 canonical metadata，绑定失效会明确失败，不会静默回退快照。没有绑定时仍可读取和生成包内公共视图。可用 `--config` 显式选择配置；同次调用中的路径参数逐项覆盖该配置。只显式传 `--metadata` 而不传 `--config` 时视为独立上下文，不自动混用私有绑定。",
        "",
        "```powershell",
        "python drama-studio/scripts/case_library.py validate",
        "python drama-studio/scripts/case_library.py build",
        "python drama-studio/scripts/case_library.py add --record '<新增或补缺记录.json>' --author-record '<可选的新作者记录.json>'",
        "python drama-studio/scripts/case_library.py build --metadata '<显式metadata.json>' --public-view '<显式公共README.md>' --local-root '<显式本地案例根>' --local-view '<显式本地入口.md>'",
        "```",
        "",
        "正常新增或同 ID 补缺必须走 `add`，不得改历史 `snapshot.original_case_count`。`add` 可在同一事务加入一个新作者与一个案例：先核作者、真实 TXT/locator、标准化 SHA-256、完整 schema、重复 ID/指纹及别名，再一起刷新 metadata、公共视图和本地 `开始这里.md`；任一步失败都不改这三份文件。新 ID 才追加；同 ID 只填 `null`、空字符串/数组/对象，完全相同的值幂等，非空冲突拒绝。只有经批准的非空事实更正才直接编辑 canonical metadata，保留可审查 diff，再运行 `validate` 与 `build`。每条取得的第三方原文独立保存为纯原文 TXT，只保留真实原文；来源、授权与取得状态写对应 metadata，现有字段不足时写同 ID 本地来源旁档；我方归纳另存并标明，成果以稳定 ID 与 locator 回指唯一原文，不造第二份混合真源。同一帖子含多段不同原文时按不同指纹保留。新增外部材料先是入库候选；经过项目适配、相称核验并获得持久化/升格授权后，才可能进入正式规则。",
        "",
    ]
    categories: dict[str, list[dict[str, Any]]] = {}
    for case in metadata["cases"]:
        categories.setdefault(case["category"], []).append(case)
    for category, cases in categories.items():
        lines.extend(
            [
                f"## {category}",
                "",
                "| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |",
                "|---|---|---|---|---|---|",
            ]
        )
        for case in cases:
            source_url = case["source"]["post_url"]
            source = author_label(authors[case["author_id"]])
            if source_url:
                source += f" / [原帖]({source_url})"
            prompt_status = (
                f"{case['prompt']['publication']}；{case['prompt']['completeness']}；"
                f"媒体 {case['media_verification']}；许可 {case['license']['status']}"
            )
            lines.append(
                "| {id} | {title}：{summary} | {tags} | {model}（{basis}） | "
                "{source} | {status} |".format(
                    id=case["id"],
                    title=case["title"],
                    summary=case["summary"],
                    tags=" / ".join(case["task_tags"]),
                    model=case["model_claim"]["name"],
                    basis=case["model_claim"]["basis"],
                    source=source,
                    status=prompt_status,
                )
            )
        lines.append("")

    lines.extend(
        [
            "## 历史别名",
            "",
            "这批别名只用于定位原有本地 TXT，不计作新增来源；原文件保留。",
            "",
            "| 历史别名 | 稳定 ID |",
            "|---|---|",
        ]
    )
    lines.extend(
        f"| {alias['legacy_id']} | {alias['case_id']} |" for alias in metadata["aliases"]
    )
    lines.append("")
    return "\n".join(lines)


def render_local(metadata: dict[str, Any], local_root: Path) -> str:
    authors = {author["id"]: author for author in metadata["authors"]}
    lines = [
        "# 本地案例阅读索引",
        "",
        "> 本页由 canonical metadata（未绑定时为包内发布快照）与本地根机械生成，不应提交到 Git。原文与媒体仍留在本地，读取不改变授权状态。",
        "",
    ]
    categories: dict[str, list[dict[str, Any]]] = {}
    for case in metadata["cases"]:
        categories.setdefault(case["category"], []).append(case)
    for category, cases in categories.items():
        lines.extend([f"## {category}", ""])
        for case in cases:
            prompt_path = local_root / Path(case["prompt"]["local_relative_path"])
            author = author_label(authors[case["author_id"]])
            if case["source"]["post_url"]:
                author += f" / [原帖]({case['source']['post_url']})"
            missing = " / ".join(case["prompt"]["missing_inputs"]) or "未记录缺项（非输入齐备证明）"
            attribution = case["source"]["attribution_status"]
            if case["source"].get("attribution_note"):
                attribution += f"；{case['source']['attribution_note']}"
            if case["source"].get("status_note"):
                attribution += f"；{case['source']['status_note']}"
            lines.extend(
                [
                    f"### {case['id']} {case['title']}",
                    "",
                    f"- 用途标签：{' / '.join(case['task_tags'])}",
                    f"- 作者/来源：{author}",
                    f"- 模型声称：{case['model_claim']['name']}（{case['model_claim']['basis']}）",
                    f"- 完整性：{case['prompt']['completeness']}；缺输入：{missing}",
                    f"- 归属/状态：{attribution}",
                    f"- 验证/许可：媒体 {case['media_verification']}；许可 {case['license']['status']}；提示词再发布 {case['license']['prompt_redistribution']}",
                    f"- 本地提示词：[{prompt_path.name}]({prompt_path})",
                ]
            )
            for locator in case["source"]["local_locators"]:
                locator_path = local_root / Path(locator["relative_path"])
                lines.append(
                    f"  - {locator['kind']}：[{locator['label']}]({locator_path})"
                )
            lines.append("")
    lines.extend(["", "## 历史别名", ""])
    lines.extend(
        f"- {alias['legacy_id']} → {alias['case_id']}" for alias in metadata["aliases"]
    )
    lines.append("")
    return "\n".join(lines)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8", newline="\n")


def write_json_atomic(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(handle, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, ensure_ascii=False, indent=2)
            stream.write("\n")
        os.replace(temporary_name, path)
    finally:
        temporary_path = Path(temporary_name)
        if temporary_path.exists():
            temporary_path.unlink()


def json_text(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def stage_bytes(path: Path, content: bytes) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    handle, temporary_name = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(handle, "wb") as stream:
            stream.write(content)
    except Exception:
        Path(temporary_name).unlink(missing_ok=True)
        raise
    return Path(temporary_name)


def write_bundle_atomic(payloads: list[tuple[Path, str]]) -> None:
    paths = [path for path, _ in payloads]
    require_distinct_file_paths(paths)
    originals: dict[Path, bytes | None] = {}
    staged: dict[Path, Path] = {}
    try:
        for path, text in payloads:
            originals[path] = path.read_bytes() if path.exists() else None
            staged[path] = stage_bytes(path, text.encode("utf-8"))
        for path in paths:
            os.replace(staged.pop(path), path)
    except OSError as exc:
        rollback_errors: list[str] = []
        for path, original in originals.items():
            try:
                if original is None:
                    if path.exists():
                        path.unlink()
                else:
                    rollback = stage_bytes(path, original)
                    os.replace(rollback, path)
            except OSError as rollback_exc:
                rollback_errors.append(f"{path}: {rollback_exc}")
        detail = f"; rollback failed for {', '.join(rollback_errors)}" if rollback_errors else ""
        raise ValidationError(f"cannot update case library transaction: {exc}{detail}") from exc
    finally:
        for temporary_path in staged.values():
            temporary_path.unlink(missing_ok=True)


def require_distinct_file_paths(paths: list[Path]) -> None:
    resolved_paths = [path.resolve() for path in paths]
    for index, path in enumerate(paths):
        for other_index in range(index):
            other = paths[other_index]
            same_identity = resolved_paths[index] == resolved_paths[other_index]
            if not same_identity and path.exists() and other.exists():
                try:
                    same_identity = path.samefile(other)
                except OSError:
                    same_identity = False
            if same_identity:
                raise ValidationError("metadata and derived view paths must be distinct")


def is_empty_value(value: Any) -> bool:
    return value is None or value == "" or value == [] or value == {}


def fill_missing(original: Any, patch: Any, location: str) -> Any:
    if isinstance(original, dict) and isinstance(patch, dict):
        merged = copy.deepcopy(original)
        for key, value in patch.items():
            child_location = f"{location}.{key}"
            if key not in merged or is_empty_value(merged[key]):
                merged[key] = copy.deepcopy(value)
            elif isinstance(merged[key], dict) and isinstance(value, dict):
                merged[key] = fill_missing(merged[key], value, child_location)
            elif merged[key] != value:
                raise ValidationError(
                    f"{child_location}: conflicting non-empty value"
                )
        return merged
    if is_empty_value(original):
        return copy.deepcopy(patch)
    if original != patch:
        raise ValidationError(f"{location}: conflicting non-empty value")
    return copy.deepcopy(original)


def markdown_cells(line: str) -> list[str]:
    return [cell.strip() for cell in line.strip().strip("|").split("|")]


def author_id_from_label(label: str) -> str:
    if label.startswith("@"):
        return label[1:].lower()
    slug = re.sub(r"[^a-z0-9]+", "-", label.lower()).strip("-")
    return slug or "unknown-source"


def parse_author_index(path: Path) -> dict[str, dict[str, Any]]:
    authors: dict[str, dict[str, Any]] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = markdown_cells(line)
        if len(cells) < 3 or "／@" not in cells[0]:
            continue
        display_name, handle = cells[0].rsplit("／", 1)
        links = [link for link in MARKDOWN_LINK_RE.findall(cells[2]) if link[1].startswith(("http://", "https://"))]
        if not links:
            continue
        numeric_id = cells[1].strip("`") or None
        author_id = author_id_from_label(handle)
        authors[handle.lower()] = {
            "id": author_id,
            "display_name": display_name.strip(),
            "handle": handle,
            "profile_url": links[0][1],
            "public_numeric_id": numeric_id,
        }
    return authors


def split_tags(value: str) -> list[str]:
    tags = [tag.strip() for tag in re.split(r"[·・／/]", value) if tag.strip()]
    return tags or ["待分类"]


def prompt_completeness(status: str) -> str:
    if any(word in status for word in ("缺尾", "中断", "截断", "不完整")):
        return "partial"
    if "完整" in status:
        return "complete_as_recorded"
    return "unknown"


def missing_inputs(status: str) -> list[str]:
    if any(
        word in status
        for word in ("未取得", "未取到", "缺", "未提供", "不齐", "错配", "未声明")
    ):
        return ["see_status_note"]
    return []


def local_locators_from_cell(
    source_cell: str, local_root: Path, source_index: Path
) -> list[dict[str, str]]:
    locators: list[dict[str, str]] = []
    approved_root = local_root.resolve()
    for label, target in MARKDOWN_LINK_RE.findall(source_cell):
        if target.startswith(("http://", "https://")):
            continue
        target_path = Path(target)
        if not target_path.is_absolute():
            target_path = source_index.parent / target_path
        target_path = target_path.resolve()
        try:
            relative_path = target_path.relative_to(approved_root).as_posix()
        except ValueError as exc:
            raise ValidationError(
                f"source locator is outside local root: {target_path}"
            ) from exc
        kind = "media" if target_path.suffix.lower() in MEDIA_SUFFIXES else "source"
        locators.append(
            {
                "label": label,
                "kind": kind,
                "relative_path": relative_path,
            }
        )
    return locators


def discover_post_url(
    source_cell: str,
    local_locators: list[dict[str, str]],
    local_root: Path,
) -> str | None:
    direct_urls = [
        target
        for _, target in MARKDOWN_LINK_RE.findall(source_cell)
        if target.startswith(("http://", "https://"))
    ]
    if direct_urls:
        return direct_urls[0]

    post_ids = {
        match
        for locator in local_locators
        for match in re.findall(r"(?<!\d)(\d{18,20})(?!\d)", locator["relative_path"])
    }
    candidates: list[tuple[str, str]] = []
    fallback_urls: list[str] = []
    media_names = {
        Path(locator["relative_path"]).name
        for locator in local_locators
        if locator["kind"] == "media"
    }
    for locator in local_locators:
        if locator["kind"] != "source":
            continue
        source_path = resolve_local_path(
            local_root, locator["relative_path"], "source locator.relative_path"
        )
        if source_path.suffix.lower() not in TEXT_SOURCE_SUFFIXES or not source_path.is_file():
            continue
        try:
            source_text = source_path.read_text(encoding="utf-8")
        except (OSError, UnicodeDecodeError):
            continue
        for line in source_text.splitlines():
            if media_names and not any(name in line for name in media_names):
                continue
            line_urls = [
                target
                for _, target in MARKDOWN_LINK_RE.findall(line)
                if target.startswith(("http://", "https://"))
                and ("/status/" in target or "/blog/" in target)
            ]
            if line_urls:
                return line_urls[0]
        candidates.extend(
            (match.group(0), match.group(1))
            for match in SOCIAL_POST_URL_RE.finditer(source_text)
        )
        fallback_urls.extend(
            target
            for _, target in MARKDOWN_LINK_RE.findall(source_text)
            if target.startswith(("http://", "https://"))
            and ("/status/" in target or "/blog/" in target)
        )
    for post_url, post_id in candidates:
        if post_id in post_ids:
            return post_url
    unique_fallbacks = list(dict.fromkeys(fallback_urls))
    if len(unique_fallbacks) == 1:
        return unique_fallbacks[0]
    return None


def media_status(status: str) -> str:
    if any(word in status for word in ("未观看", "未验收", "未验证", "未复现")):
        return "not_reviewed_or_reproduced"
    return "not_independently_verified"


def attribution_status(author_cell: str, status: str) -> str:
    if any(word in status for word in ("归属异议", "转用", "冒用")) or "、" in author_cell:
        return "attribution_warning"
    return "source_recorded_not_independently_verified"


def command_migrate(args: argparse.Namespace) -> None:
    indexed_authors = parse_author_index(args.author_index)
    authors: dict[str, dict[str, Any]] = {}
    cases: list[dict[str, Any]] = []
    category = ""
    for line in args.source_index.read_text(encoding="utf-8").splitlines():
        if line.startswith("## "):
            category = line[3:].strip()
            continue
        if not line.startswith("| ["):
            continue
        cells = markdown_cells(line)
        if len(cells) != 6:
            continue
        case_match = CASE_LINK_RE.match(cells[0])
        if not case_match:
            continue
        if not category:
            raise ValidationError(f"case {case_match.group('id')}: missing category heading")
        author_links = MARKDOWN_LINK_RE.findall(cells[3])
        if not author_links:
            raise ValidationError(f"case {case_match.group('id')}: missing author link")
        primary_label, primary_url = author_links[0]
        author_id = author_id_from_label(primary_label)
        indexed = indexed_authors.get(primary_label.lower())
        authors.setdefault(
            author_id,
            indexed
            or {
                "id": author_id,
                "display_name": primary_label.lstrip("@"),
                "handle": primary_label if primary_label.startswith("@") else None,
                "profile_url": primary_url,
                "public_numeric_id": None,
            },
        )
        approved_root = args.local_root.resolve()
        source_path = Path(case_match.group("path")).resolve()
        try:
            relative_path = source_path.relative_to(approved_root).as_posix()
        except ValueError as exc:
            raise ValidationError(
                f"case {case_match.group('id')}: prompt path is outside local root"
            ) from exc
        local_locators = local_locators_from_cell(
            cells[4], args.local_root, args.source_index
        )
        source_post_url = discover_post_url(cells[4], local_locators, args.local_root)
        status = cells[5]
        secondary = [label for label, _ in author_links[1:]]
        attribution_note = (
            f"also credited or republished by {', '.join(secondary)}; see status note"
            if secondary
            else "see status note"
        )
        cases.append(
            {
                "id": case_match.group("id"),
                "title": case_match.group("title"),
                "category": category,
                "summary": f"用于研究{'、'.join(split_tags(cells[2]))}。",
                "model_claim": {
                    "name": cells[1],
                    "basis": "author_or_source_claim_unverified",
                },
                "task_tags": split_tags(cells[2]),
                "author_id": author_id,
                "source": {
                    "post_url": source_post_url,
                    "attribution_status": attribution_status(cells[3], status),
                    "attribution_note": attribution_note,
                    "status_note": status,
                    "local_locators": local_locators,
                },
                "prompt": {
                    "completeness": prompt_completeness(status),
                    "missing_inputs": missing_inputs(status),
                    "local_relative_path": relative_path,
                    "content_fingerprint": normalized_prompt_fingerprint(source_path),
                    "publication": "metadata_only",
                },
                "media_verification": media_status(status),
                "license": {
                    "status": "unknown",
                    "prompt_redistribution": "not_permitted",
                },
            }
        )

    if not cases:
        raise ValidationError("source index: no case rows found")
    case_ids = {case["id"] for case in cases}
    metadata = {
        "schema_version": 1,
        "library_id": "drama-studio-case-library",
        "snapshot": {
            "as_of": args.as_of,
            "original_case_count": len(cases),
            "prompt_policy": "metadata_only_unless_redistribution_permitted",
        },
        "authors": list(authors.values()),
        "cases": cases,
        "aliases": [
            {"legacy_id": legacy_id, "case_id": case_id}
            for legacy_id, case_id in LEGACY_ALIASES.items()
            if case_id in case_ids
        ],
    }
    validate_metadata(metadata, args.local_root)
    write_json_atomic(args.metadata, metadata)
    print(f"migrated: {len(cases)} cases")


def command_validate(args: argparse.Namespace) -> None:
    metadata_path, _, local_root, _ = resolve_bindings(args)
    metadata = read_json(metadata_path)
    validate_metadata(metadata, local_root)
    print(f"valid: {len(metadata['cases'])} cases, {len(metadata['aliases'])} aliases")


def command_build(args: argparse.Namespace) -> None:
    metadata_path, public_view, local_root, local_view = resolve_bindings(args)
    if (local_root is None) != (local_view is None):
        raise ValidationError("--local-root and --local-view must be provided together")
    require_distinct_file_paths(
        [metadata_path, public_view] + ([local_view] if local_view is not None else [])
    )
    metadata = read_json(metadata_path)
    validate_metadata(metadata, local_root)
    write_text(public_view, render_public(metadata))
    if local_root is not None:
        write_text(local_view, render_local(metadata, local_root))
    print(f"built: {len(metadata['cases'])} cases")


def command_add(args: argparse.Namespace) -> None:
    metadata_path, public_view, local_root, local_view = resolve_bindings(args)
    if local_root is None or local_view is None:
        raise ValidationError(
            "add requires --local-root and --local-view or a complete local binding"
        )
    require_distinct_file_paths([metadata_path, public_view, local_view])
    metadata = read_json(metadata_path)
    validate_metadata(metadata, local_root)

    if args.author_record is not None:
        author_record = read_json(args.author_record)
        require_fields(author_record, AUTHOR_FIELDS, "author record")
        require_text(author_record["id"], "author record.id")
        author_ids = [author["id"] for author in metadata["authors"]]
        if author_record["id"] in author_ids:
            index = author_ids.index(author_record["id"])
            metadata["authors"][index] = fill_missing(
                metadata["authors"][index], author_record, "author record"
            )
        else:
            metadata["authors"].append(author_record)

    record = read_json(args.record)
    if not isinstance(record, dict):
        raise ValidationError("record: expected object")
    require_text(record.get("id"), "record.id")
    case_ids = [case["id"] for case in metadata["cases"]]
    if record["id"] in case_ids:
        index = case_ids.index(record["id"])
        metadata["cases"][index] = fill_missing(
            metadata["cases"][index], record, "record"
        )
        action = "updated"
    else:
        metadata["cases"].append(record)
        action = "added"
    validate_metadata(metadata, local_root)
    public_text = render_public(metadata)
    local_text = render_local(metadata, local_root)
    write_bundle_atomic(
        [
            (metadata_path, json_text(metadata)),
            (public_view, public_text),
            (local_view, local_text),
        ]
    )
    print(f"{action}: {record['id']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--config", type=Path)
    validate.add_argument("--metadata", type=Path)
    validate.add_argument("--local-root", type=Path)
    validate.set_defaults(handler=command_validate)

    build = subparsers.add_parser("build")
    build.add_argument("--config", type=Path)
    build.add_argument("--metadata", type=Path)
    build.add_argument("--public-view", type=Path)
    build.add_argument("--local-root", type=Path)
    build.add_argument("--local-view", type=Path)
    build.set_defaults(handler=command_build)

    add = subparsers.add_parser("add")
    add.add_argument("--config", type=Path)
    add.add_argument("--metadata", type=Path)
    add.add_argument("--record", type=Path, required=True)
    add.add_argument("--author-record", type=Path)
    add.add_argument("--public-view", type=Path)
    add.add_argument("--local-root", type=Path)
    add.add_argument("--local-view", type=Path)
    add.set_defaults(handler=command_add)

    migrate = subparsers.add_parser("migrate")
    migrate.add_argument("--source-index", type=Path, required=True)
    migrate.add_argument("--author-index", type=Path, required=True)
    migrate.add_argument("--local-root", type=Path, required=True)
    migrate.add_argument("--metadata", type=Path, required=True)
    migrate.add_argument("--as-of", required=True)
    migrate.set_defaults(handler=command_migrate)
    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    try:
        args.handler(args)
    except ValidationError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
