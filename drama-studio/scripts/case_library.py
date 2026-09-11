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
SOURCE_FIELDS = {"post_url", "attribution_status", "local_locators"}
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
WINDOWS_ABSOLUTE_RE = re.compile(r"^[A-Za-z]:[\\/]")
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


class ValidationError(ValueError):
    pass


def read_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValidationError(f"cannot read JSON {path}: {exc}") from exc


def require_fields(value: Any, fields: set[str], location: str) -> None:
    if not isinstance(value, dict):
        raise ValidationError(f"{location}: expected object")
    missing = fields - value.keys()
    if missing:
        raise ValidationError(
            f"{location}: missing field(s): {', '.join(sorted(missing))}"
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
    if WINDOWS_ABSOLUTE_RE.match(value) or "\\" in value:
        raise ValidationError(f"{location}: expected safe POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValidationError(f"{location}: expected safe relative path")
    if path.suffix.lower() != ".txt":
        raise ValidationError(f"{location}: local prompt path must end in .txt")


def validate_local_locator(value: Any, location: str) -> None:
    require_fields(value, LOCAL_LOCATOR_FIELDS, location)
    require_text(value["label"], f"{location}.label")
    if value["kind"] not in {"media", "source"}:
        raise ValidationError(f"{location}.kind: expected media or source")
    relative_path = value["relative_path"]
    require_text(relative_path, f"{location}.relative_path")
    if WINDOWS_ABSOLUTE_RE.match(relative_path) or "\\" in relative_path:
        raise ValidationError(f"{location}.relative_path: expected safe POSIX relative path")
    path = PurePosixPath(relative_path)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        raise ValidationError(f"{location}.relative_path: expected safe relative path")


def normalized_prompt_fingerprint(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    normalized = re.sub(r"\s+", "", text)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def reject_embedded_absolute_paths(value: Any, location: str = "metadata") -> None:
    if isinstance(value, dict):
        for key, child in value.items():
            reject_embedded_absolute_paths(child, f"{location}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_embedded_absolute_paths(child, f"{location}[{index}]")
    elif isinstance(value, str) and WINDOWS_ABSOLUTE_RE.match(value):
        raise ValidationError(f"{location}: absolute machine path is not publishable")


def validate_metadata(metadata: Any, local_root: Path | None = None) -> dict[str, Any]:
    require_fields(metadata, TOP_LEVEL_FIELDS, "metadata")
    if metadata["schema_version"] != 1:
        raise ValidationError("metadata.schema_version: expected 1")
    require_text(metadata["library_id"], "metadata.library_id")
    require_fields(metadata["snapshot"], SNAPSHOT_FIELDS, "metadata.snapshot")
    if not isinstance(metadata["snapshot"]["original_case_count"], int):
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
        validate_url(author["profile_url"], f"{location}.profile_url")
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
        if not isinstance(case["task_tags"], list) or not all(
            isinstance(tag, str) and tag.strip() for tag in case["task_tags"]
        ):
            raise ValidationError(f"{location}.task_tags: expected non-empty text array")
        if case["author_id"] not in author_ids:
            raise ValidationError(f"{location}.author_id: unknown author id")

        require_fields(case["source"], SOURCE_FIELDS, f"{location}.source")
        validate_url(case["source"]["post_url"], f"{location}.source.post_url")
        require_text(
            case["source"]["attribution_status"],
            f"{location}.source.attribution_status",
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
                locator_path = local_root / Path(locator["relative_path"])
                if not locator_path.exists():
                    raise ValidationError(
                        f"{locator_location}.relative_path: missing local item {locator_path}"
                    )
        require_fields(case["prompt"], PROMPT_FIELDS, f"{location}.prompt")
        require_text(case["prompt"]["completeness"], f"{location}.prompt.completeness")
        if not isinstance(case["prompt"]["missing_inputs"], list):
            raise ValidationError(f"{location}.prompt.missing_inputs: expected array")
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
            prompt_path = local_root / Path(case["prompt"]["local_relative_path"])
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
        "逐条缺输入、归属提醒与原始状态说明保存在唯一真源 [metadata.json](metadata.json) 的同 ID 记录中。公开可读不等于取得原文再发布许可。",
        "",
        "## 本地绑定与维护",
        "",
        "本地根只通过调用参数传入，不写进 Skill。示例：",
        "",
        "```powershell",
        "python drama-studio/scripts/case_library.py validate --metadata drama-studio/references/case-library/metadata.json",
        "python drama-studio/scripts/case_library.py build --metadata drama-studio/references/case-library/metadata.json --public-view drama-studio/references/case-library/README.md --local-root '<本地案例根>' --local-view '<忽略的本地阅读索引.md>'",
        "python drama-studio/scripts/case_library.py add --metadata drama-studio/references/case-library/metadata.json --record '<新增或补缺记录.json>'",
        "```",
        "",
        "`add` 遇到新 ID 才追加；同 ID 按字段补缺并保持原位置。标准化原文 SHA-256 相同却另分配新 ID 时拒绝；同一帖子含多段不同原文时按不同指纹保留。每次写入后都执行完整 schema、重复 ID/原文指纹、别名目标与相对路径校验。新增外部材料先是入库候选；经过项目适配、相称核验并获得持久化/升格授权后，才可能进入正式规则。",
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
    lines = [
        "# 本地案例阅读索引",
        "",
        "> 本页由公共 metadata 真源与调用时提供的本地根机械生成，不应提交到 Git。原文与媒体仍留在本地，读取不改变授权状态。",
        "",
    ]
    for case in metadata["cases"]:
        prompt_path = local_root / Path(case["prompt"]["local_relative_path"])
        lines.append(f"- {case['id']} {case['title']} — [{prompt_path.name}]({prompt_path})")
        for locator in case["source"]["local_locators"]:
            locator_path = local_root / Path(locator["relative_path"])
            lines.append(
                f"  - {locator['kind']}：[{locator['label']}]({locator_path})"
            )
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


def deep_merge(original: dict[str, Any], patch: dict[str, Any]) -> dict[str, Any]:
    merged = copy.deepcopy(original)
    for key, value in patch.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = deep_merge(merged[key], value)
        else:
            merged[key] = copy.deepcopy(value)
    return merged


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
    for label, target in MARKDOWN_LINK_RE.findall(source_cell):
        if target.startswith(("http://", "https://")):
            continue
        target_path = Path(target)
        if not target_path.is_absolute():
            target_path = (source_index.parent / target_path).resolve()
        try:
            relative_path = target_path.relative_to(local_root).as_posix()
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
        source_path = local_root / Path(locator["relative_path"])
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
        source_path = Path(case_match.group("path"))
        try:
            relative_path = source_path.relative_to(args.local_root).as_posix()
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
    metadata = read_json(args.metadata)
    validate_metadata(metadata, args.local_root)
    print(f"valid: {len(metadata['cases'])} cases, {len(metadata['aliases'])} aliases")


def command_build(args: argparse.Namespace) -> None:
    if (args.local_root is None) != (args.local_view is None):
        raise ValidationError("--local-root and --local-view must be provided together")
    metadata = read_json(args.metadata)
    validate_metadata(metadata, args.local_root)
    write_text(args.public_view, render_public(metadata))
    if args.local_root is not None:
        write_text(args.local_view, render_local(metadata, args.local_root))
    print(f"built: {len(metadata['cases'])} cases")


def command_add(args: argparse.Namespace) -> None:
    metadata = read_json(args.metadata)
    validate_metadata(metadata)
    record = read_json(args.record)
    if not isinstance(record, dict):
        raise ValidationError("record: expected object")
    require_text(record.get("id"), "record.id")
    case_ids = [case["id"] for case in metadata["cases"]]
    if record["id"] in case_ids:
        index = case_ids.index(record["id"])
        metadata["cases"][index] = deep_merge(metadata["cases"][index], record)
        action = "updated"
    else:
        metadata["cases"].append(record)
        action = "added"
    validate_metadata(metadata)
    write_json_atomic(args.metadata, metadata)
    print(f"{action}: {record['id']}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate = subparsers.add_parser("validate")
    validate.add_argument("--metadata", type=Path, required=True)
    validate.add_argument("--local-root", type=Path)
    validate.set_defaults(handler=command_validate)

    build = subparsers.add_parser("build")
    build.add_argument("--metadata", type=Path, required=True)
    build.add_argument("--public-view", type=Path, required=True)
    build.add_argument("--local-root", type=Path)
    build.add_argument("--local-view", type=Path)
    build.set_defaults(handler=command_build)

    add = subparsers.add_parser("add")
    add.add_argument("--metadata", type=Path, required=True)
    add.add_argument("--record", type=Path, required=True)
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
