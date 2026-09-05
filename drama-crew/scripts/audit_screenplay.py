#!/usr/bin/env python3
"""Read-only deterministic checks for drama-crew production/submission Markdown."""

from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
import json
from pathlib import Path
import re
import sys
from typing import Literal, Sequence
import unicodedata


Severity = Literal["error", "warning"]

EPISODE_HEADING_RE = re.compile(
    r"^#{1,3}[ \t]*(?:第[ \t]*(\d+)[ \t]*集|E(\d{1,3})(?:\b|（|\())[^\r\n]*",
    re.MULTILINE | re.IGNORECASE,
)
OUTLINE_ENTRY_RE = re.compile(
    r"^[ \t]*(?:[-*+][ \t]*)?(?:#{1,6}[ \t]*)?第[ \t]*(\d+)[ \t]*集"
    r"[ \t]*(?:[:：][ \t]*)?(.*)$",
    re.MULTILINE,
)
DIALOGUE_RE = re.compile(r"^(?P<speaker>[^#∆【（(*|>\-\s][^：\n]{0,40})：(?P<content>.*)$")
PERSON_LINE_RE = re.compile(r"^\*\*人物：(.+?)\*\*\s*$")
SCENE_LINE_RE = re.compile(r"^\*\*场(\d+)-(\d+)\s+(?:日|夜)\s+(?:内|外)\s+\S.*?\*\*\s*$")
FLASHBACK_ACTION_RE = re.compile(r"^（画面闪回：∆(.*?)）\s*$")
SPEAKER_ANNOTATION_RE = re.compile(r"^([^#∆【*|>\-\s][^：\n]{0,30})（([^）]+)）：")
LEADING_HINT_RE = re.compile(r"^\s*（([^）]*)）\s*")
NON_SPOKEN_SPEAKER_HINTS = ("写字", "打字", "举牌", "字幕", "手语")
VISIBLE_ACTION_HINT_RE = re.compile(
    r"盯|看向|看着|回头|转身|靠近|走|跑|抬(?:手|头|眼)|低头|点头|摇头|"
    r"推(?:门|开)|拉(?:门|开)|拿起|放下|拔|坐下|站起|起身|伸手|握住|"
    r"松开|踢|打(?:人|脸|耳光|拳)|写(?:字|下)|敲(?:门|桌)|指向|拧干|凑近"
)
INTERNAL_FIELD_RE = re.compile(
    r"(?:^|\s)(?:project_id|script_rev|review_state|romance_axis|carrier|"
    r"source_locator|质检节奏|唯一内容真源)\s*(?::|：|=)",
    re.IGNORECASE,
)
PRODUCTION_BEAT_RESIDUE_RE = re.compile(
    r"【动作节拍】|\bBeat\b|[^\n]{0,80}→[^\n]{0,80}→|"
    r"情绪(?:强度)?\s*(?::|：)?\s*(?:10|[1-9])(?:\s*/\s*10)?",
    re.IGNORECASE,
)
INSTITUTIONAL_TERMS = (
    "记录",
    "复核",
    "授权",
    "封存",
    "程序",
    "确认",
    "待核",
    "结算",
    "原始记录",
    "退出程序",
)
REQUIRED_SUBMISSION_SECTIONS = (
    "一句话卖点",
    "故事梗概",
    "主要人物",
    "粗纲",
    "逐集集纲",
    "正文",
)


@dataclass(frozen=True)
class Finding:
    severity: Severity
    code: str
    line: int
    message: str


@dataclass
class AuditResult:
    findings: list[Finding]
    metrics: dict[str, object]

    @property
    def blocking(self) -> bool:
        return any(item.severity == "error" for item in self.findings)


def _line_number(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def _find_section(text: str, title: str) -> re.Match[str] | None:
    return re.search(rf"^##\s*{re.escape(title)}\s*$", text, re.MULTILINE)


def _section_content(text: str, title: str) -> tuple[str, int] | None:
    match = _find_section(text, title)
    if match is None:
        return None
    start = match.end()
    next_heading = re.search(r"^##\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end], _line_number(text, start)


def _after_section(text: str, title: str) -> tuple[str, int]:
    match = _find_section(text, title)
    if match is None:
        return "", 1
    start = match.end()
    return text[start:], _line_number(text, start)


def _episode_numbers(text: str) -> list[int]:
    numbers: list[int] = []
    for match in EPISODE_HEADING_RE.finditer(text):
        raw = match.group(1) or match.group(2)
        numbers.append(int(raw))
    return numbers


def _episode_blocks(body: str, line_offset: int = 1) -> list[tuple[int, str, int]]:
    headings = list(EPISODE_HEADING_RE.finditer(body))
    return [
        (
            int(heading.group(1) or heading.group(2)),
            body[heading.end():headings[index + 1].start() if index + 1 < len(headings) else len(body)],
            line_offset + _line_number(body, heading.end()) - 1,
        )
        for index, heading in enumerate(headings)
    ]


def _check_episode_count(
    body: str,
    line_offset: int,
    expected_episodes: int | None,
) -> tuple[list[Finding], list[int]]:
    episodes = _episode_numbers(body)
    findings: list[Finding] = []
    unique = sorted(set(episodes))
    if expected_episodes is not None:
        expected = list(range(1, expected_episodes + 1))
        if unique != expected:
            findings.append(
                Finding(
                    "error",
                    "EPISODE_COUNT_MISMATCH",
                    line_offset,
                    f"正文集号应为 1-{expected_episodes}，实际为 {unique or '空'}。",
                )
            )
    if not episodes:
        findings.append(Finding("error", "MISSING_EPISODE", line_offset, "正文没有集标题。"))
    if len(episodes) != len(unique):
        findings.append(
            Finding("error", "DUPLICATE_EPISODE_HEADING", line_offset, "正文存在重复集号。")
        )
    if episodes != sorted(episodes):
        findings.append(Finding("error", "EPISODE_ORDER_MISMATCH", line_offset, "正文集号不按顺序排列。"))
    return findings, unique


def _check_scenes(body: str, body_line: int) -> list[Finding]:
    findings: list[Finding] = []
    for episode, block, start_line in _episode_blocks(body, body_line):
        lines = block.splitlines()
        starts = [index for index, line in enumerate(lines) if line.strip().startswith("**场")]
        if not starts:
            findings.append(Finding("error", "MISSING_SCENE", start_line, f"第 {episode} 集缺少场次行。"))
        for ordinal, start in enumerate(starts, 1):
            line_number = start_line + start
            match = SCENE_LINE_RE.match(lines[start].strip())
            if not match:
                findings.append(Finding("error", "INVALID_SCENE_HEADING", line_number, "场次行应含场号、日/夜、内/外和地点。"))
            elif (int(match[1]), int(match[2])) != (episode, ordinal):
                findings.append(Finding("error", "SCENE_NUMBER_MISMATCH", line_number, f"此处应为场{episode}-{ordinal}。"))
            end = starts[ordinal] if ordinal < len(starts) else len(lines)
            scene_lines = [line.strip() for line in lines[start + 1:end] if line.strip()]
            if not scene_lines or not PERSON_LINE_RE.match(scene_lines[0]):
                findings.append(Finding("error", "MISSING_PERSON_LINE", line_number, "场次行后缺少人物行；无人空镜可标“无（空镜）”。"))
            if not any(
                (line.startswith("∆") and line[1:].strip())
                or ((dialogue := DIALOGUE_RE.match(line)) and _strip_hint(dialogue["content"])[1].strip())
                or ((flashback := FLASHBACK_ACTION_RE.match(line)) and flashback[1].strip())
                for line in scene_lines
            ):
                findings.append(Finding("error", "EMPTY_SCENE", line_number, "场内没有动作或台词，不能以标题代替正文。"))
    return findings


def _check_episode_outline(
    outline_text: str,
    line_offset: int,
    expected_episodes: int | None,
) -> list[Finding]:
    findings: list[Finding] = []
    entries = list(OUTLINE_ENTRY_RE.finditer(outline_text))
    outlined = sorted({int(match.group(1)) for match in entries})

    if expected_episodes is not None and outlined != list(range(1, expected_episodes + 1)):
        findings.append(
            Finding(
                "error",
                "INCOMPLETE_EPISODE_OUTLINE",
                line_offset,
                f"逐集集纲应覆盖 1-{expected_episodes} 集，实际为 {outlined or '空'}。",
            )
        )

    for index, match in enumerate(entries):
        next_start = entries[index + 1].start() if index + 1 < len(entries) else len(outline_text)
        entry_content = f"{match.group(2)}\n{outline_text[match.end():next_start]}"
        if not entry_content.strip(" \t\r\n|-"):
            findings.append(
                Finding(
                    "error",
                    "EMPTY_EPISODE_OUTLINE_ENTRY",
                    line_offset + outline_text.count("\n", 0, match.start()),
                    f"第 {int(match.group(1))} 集集纲没有核心事件与结尾卡点。",
                )
            )
    return findings


def _strip_hint(content: str) -> tuple[str, str]:
    hints: list[str] = []
    remaining = content
    while True:
        match = LEADING_HINT_RE.match(remaining)
        if match is None:
            break
        hints.append(match.group(1))
        remaining = remaining[match.end() :]
    return "，".join(hints), remaining


def _spoken_character_count(content: str) -> int:
    return sum(
        1
        for character in content
        if not character.isspace()
        and not unicodedata.category(character).startswith(("P", "S"))
    )


def _dialogue_parts(line: str) -> tuple[str, str, str] | None:
    match = DIALOGUE_RE.match(line.strip())
    if match is None:
        return None
    speaker = match.group("speaker").strip()
    content = match.group("content").strip()
    speaker_hint_match = re.fullmatch(r"(.+?)（([^）]+)）", speaker)
    speaker_hint = speaker_hint_match.group(2) if speaker_hint_match else ""
    if speaker_hint_match:
        speaker = speaker_hint_match.group(1).strip()
    content_hint, spoken = _strip_hint(content)
    hints = "，".join(filter(None, (speaker_hint, content_hint)))
    if any(marker in hints for marker in NON_SPOKEN_SPEAKER_HINTS):
        return speaker, hints, ""
    return speaker, hints, spoken


def _audio_kind(hints: str) -> str:
    tokens = re.split(r"[，,\s/／、;；:：|｜]+", hints.upper())
    for kind in ("OS", "VO"):
        if kind in tokens:
            return kind
    return "dialogue"


def _dialogue_metrics(body: str) -> dict[str, object]:
    spoken_chars = 0
    dialogue_lines = 0
    os_lines = 0
    vo_lines = 0
    action_lines = 0
    institutional_counts: Counter[str] = Counter()

    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line.startswith("∆"):
            action_lines += 1
            continue
        match = DIALOGUE_RE.match(line)
        if match is None:
            continue
        parts = _dialogue_parts(line)
        if parts is None:
            continue
        _, speaker_hint, spoken = parts
        if not _spoken_character_count(spoken):
            continue
        dialogue_lines += 1
        os_lines += _audio_kind(speaker_hint) == "OS"
        vo_lines += _audio_kind(speaker_hint) == "VO"
        spoken_chars += _spoken_character_count(spoken)
        for term in INSTITUTIONAL_TERMS:
            institutional_counts[term] += spoken.count(term)

    return {
        "spoken_chars": spoken_chars,
        "dialogue_lines": dialogue_lines,
        "action_lines": action_lines,
        "os_lines": os_lines,
        "vo_lines": vo_lines,
        "spoken_seconds_at_3_5_cps": round(spoken_chars / 3.5, 2),
        "spoken_seconds_at_4_5_cps": round(spoken_chars / 4.5, 2),
        "institutional_term_counts": dict(institutional_counts),
    }


def _runtime_metrics(body: str) -> dict[str, object]:
    metrics = _dialogue_metrics(body)
    metrics["per_episode"] = [
        {"episode": episode, **_dialogue_metrics(block)}
        for episode, block, _ in _episode_blocks(body)
    ]
    metrics["timing_basis"] = "text_estimate_only; excludes acting, pauses, transitions and overlapping audio"
    return metrics


def _spoken_sequence(body: str) -> list[tuple[int, str, str, str]]:
    sequence: list[tuple[int, str, str, str]] = []
    for episode, block, _ in _episode_blocks(body):
        for line in block.splitlines():
            parts = _dialogue_parts(line)
            if parts and parts[2]:
                speaker, hints, spoken = parts
                sequence.append((episode, speaker, _audio_kind(hints), re.sub(r"\s+", "", spoken)))
    return sequence


def _format_findings(text: str, body: str, body_line: int) -> list[Finding]:
    findings: list[Finding] = []

    for match in INTERNAL_FIELD_RE.finditer(text):
        findings.append(
            Finding(
                "error",
                "INTERNAL_FIELD_IN_SUBMISSION",
                _line_number(text, match.start()),
                "投稿稿含制作侧内部字段。",
            )
        )

    for match in PRODUCTION_BEAT_RESIDUE_RE.finditer(body):
        findings.append(
            Finding(
                "error",
                "PRODUCTION_BEAT_IN_SUBMISSION",
                body_line + _line_number(body, match.start()) - 1,
                "投稿正文含动作节拍、箭头链、Beat 或情绪数字。",
            )
        )

    for index, raw_line in enumerate(body.splitlines(), start=body_line):
        line = raw_line.strip()
        person_match = PERSON_LINE_RE.match(line)
        if person_match:
            names = [name for name in re.split(r"[、,，\s]+", person_match.group(1)) if name]
            duplicates = sorted(name for name, count in Counter(names).items() if count > 1)
            if duplicates:
                findings.append(
                    Finding(
                        "error",
                        "DUPLICATE_PERSON",
                        index,
                        f"人物行重复：{'、'.join(duplicates)}。",
                    )
                )

        if SPEAKER_ANNOTATION_RE.match(line):
            findings.append(
                Finding(
                    "error",
                    "NONSTANDARD_SPEAKER_ANNOTATION",
                    index,
                    "提示写在人物名一侧；应改为“人物名：（提示）台词”或独立动作行。",
                )
            )

        dialogue_match = DIALOGUE_RE.match(line)
        if dialogue_match:
            hints, _ = _strip_hint(dialogue_match.group("content"))
            if VISIBLE_ACTION_HINT_RE.search(hints):
                findings.append(
                    Finding(
                        "error",
                        "VISIBLE_ACTION_IN_DIALOGUE_HINT",
                        index,
                        "台词括号含可见动作；动作应另写为 ∆ 行。",
                    )
                )
    return findings


def _diagnostic_findings(body: str, body_line: int) -> list[Finding]:
    findings: list[Finding] = []
    dialogue_run = 0
    run_start = 0
    warned_run = False
    current_episode: int | None = None
    action_occurrences: defaultdict[str, list[tuple[int | None, int]]] = defaultdict(list)

    for index, raw_line in enumerate(body.splitlines(), start=body_line):
        line = raw_line.strip()
        heading = EPISODE_HEADING_RE.match(line)
        if heading:
            current_episode = int(heading.group(1) or heading.group(2))
            dialogue_run = 0
            warned_run = False
            continue
        if not line:
            continue
        if line.startswith("∆"):
            normalized = re.sub(r"\s+", "", line)
            action_occurrences[normalized].append((current_episode, index))
            dialogue_run = 0
            warned_run = False
            continue
        if DIALOGUE_RE.match(line):
            if dialogue_run == 0:
                run_start = index
            dialogue_run += 1
            if dialogue_run >= 10 and not warned_run:
                findings.append(
                    Finding(
                        "warning",
                        "LONG_DIALOGUE_RUN",
                        run_start,
                        "连续至少 10 行对白没有新的动作行；需人工判断场面是否静止。",
                    )
                )
                warned_run = True
            continue
        if not line.startswith(("**人物：",)):
            dialogue_run = 0
            warned_run = False

    for normalized, occurrences in action_occurrences.items():
        episodes = {episode for episode, _ in occurrences if episode is not None}
        if len(episodes) >= 3:
            findings.append(
                Finding(
                    "warning",
                    "REPEATED_ACTION_LINE",
                    occurrences[0][1],
                    f"同一动作行跨 {len(episodes)} 集重复；需结合账本核对时间与状态推进。",
                )
            )

    metrics = _dialogue_metrics(body)
    institutional_total = sum(metrics["institutional_term_counts"].values())
    dialogue_lines = int(metrics["dialogue_lines"])
    if dialogue_lines and institutional_total >= 5 and institutional_total / dialogue_lines >= 0.25:
        findings.append(
            Finding(
                "warning",
                "INSTITUTIONAL_LANGUAGE_DENSITY",
                body_line,
                "制度词相对对白行偏密；只作语义复核提示，不据此自动删改。",
            )
        )
    return findings


def audit_submission(
    text: str, expected_episodes: int | None = None, *, submission_scope: str = "full",
) -> AuditResult:
    if submission_scope not in {"full", "body-only"}:
        raise ValueError("submission_scope must be full or body-only")
    findings: list[Finding] = []

    for title in REQUIRED_SUBMISSION_SECTIONS if submission_scope == "full" else ():
        section = _section_content(text, title)
        if section is None:
            findings.append(Finding("error", "MISSING_REQUIRED_SECTION", 1, f"缺少“{title}”节。"))
        elif not section[0].strip():
            code = "EMPTY_EPISODE_OUTLINE" if title == "逐集集纲" else "EMPTY_REQUIRED_SECTION"
            findings.append(Finding("error", code, section[1], f'“{title}”节为空。'))

    outline = _section_content(text, "逐集集纲")
    if outline and outline[0].strip():
        findings.extend(_check_episode_outline(outline[0], outline[1], expected_episodes))

    body, body_line = _after_section(text, "正文")
    if submission_scope == "body-only" and _find_section(text, "正文") is None:
        body, body_line = text, 1
    count_findings, episodes = _check_episode_count(body, body_line, expected_episodes)
    findings.extend(count_findings)
    findings.extend(_check_scenes(body, body_line))
    findings.extend(_format_findings(text, body, body_line))
    findings.extend(_diagnostic_findings(body, body_line))
    metrics = _runtime_metrics(body)
    metrics["episode_count"] = len(episodes)
    return AuditResult(findings=findings, metrics=metrics)


def audit_master(text: str, expected_episodes: int | None = None) -> AuditResult:
    findings: list[Finding] = []
    for match in re.finditer(
        r"^\s*romance_axis\s*(?::|=)[ \t]*([^\r\n]*)$",
        text,
        re.IGNORECASE | re.MULTILINE,
    ):
        value = match.group(1).strip().lower()
        if value not in {"on", "off"}:
            findings.append(
                Finding(
                    "error",
                    "INVALID_ROMANCE_AXIS",
                    _line_number(text, match.start()),
                    f"romance_axis 只能为 on|off，实际为 {value}。",
                )
            )
    body, body_line = _after_section(text, "正文")
    if not body.strip():
        body = text
        body_line = 1
    count_findings, episodes = _check_episode_count(body, body_line, expected_episodes)
    findings.extend(count_findings)
    metrics = _runtime_metrics(body)
    metrics["episode_count"] = len(episodes)
    return AuditResult(findings=findings, metrics=metrics)


def audit_pair(
    master_text: str,
    submission_text: str,
    expected_episodes: int | None = None,
    *,
    submission_scope: str = "full",
) -> AuditResult:
    master = audit_master(master_text, expected_episodes)
    submission = audit_submission(submission_text, expected_episodes, submission_scope=submission_scope)
    findings = list(master.findings) + list(submission.findings)
    master_body = _after_section(master_text, "正文")[0] if _find_section(master_text, "正文") else master_text
    submission_body = _after_section(submission_text, "正文")[0] if _find_section(submission_text, "正文") else submission_text
    if _spoken_sequence(master_body) != _spoken_sequence(submission_body):
        findings.append(Finding("error", "PAIR_SPOKEN_TEXT_MISMATCH", 1, "两稿逐集发声顺序、人物、OS/VO 类型或台词正文不一致；内容修改须先回母稿。"))
    master_count = int(master.metrics.get("episode_count", 0))
    submission_count = int(submission.metrics.get("episode_count", 0))
    if master_count != submission_count:
        findings.append(
            Finding(
                "error",
                "PAIR_EPISODE_COUNT_MISMATCH",
                1,
                f"制作母稿 {master_count} 集，投稿稿 {submission_count} 集。",
            )
        )
    metrics = dict(submission.metrics)
    metrics["master_episode_count"] = master_count
    metrics["pair_comparison_scope"] = "spoken_text_only; action facts require manual comparison"
    return AuditResult(findings=findings, metrics=metrics)


def _result_payload(result: AuditResult) -> dict[str, object]:
    return {
        "status": "FAIL" if result.blocking else "PASS",
        "blocking": result.blocking,
        "findings": [asdict(item) for item in result.findings],
        "metrics": result.metrics,
    }


def _print_human(result: AuditResult) -> None:
    print(f"Screenplay audit: {'FAIL' if result.blocking else 'PASS'}")
    for finding in result.findings:
        print(
            f"[{finding.severity.upper()}] {finding.code} "
            f"line {finding.line}: {finding.message}"
        )
    print(json.dumps(result.metrics, ensure_ascii=False, indent=2, sort_keys=True))


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--master", type=Path, help="完整制作母稿 Markdown")
    parser.add_argument("--submission", type=Path, help="标准投稿阅读稿 Markdown")
    parser.add_argument("--expected-episodes", type=int)
    parser.add_argument("--submission-scope", choices=("full", "body-only"), default="full",
                        help="仅接收方明确只收正文时使用 body-only；仍核场次与双稿台词")
    parser.add_argument("--json", action="store_true", help="以 JSON 输出")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    if args.expected_episodes is not None and args.expected_episodes <= 0:
        _parser().error("--expected-episodes 必须为正整数")
    if args.master is None and args.submission is None:
        _parser().error("至少提供 --master 或 --submission")

    if (
        args.master is not None
        and args.submission is not None
        and args.master.resolve() == args.submission.resolve()
    ):
        result = AuditResult(
            findings=[
                Finding(
                    "error",
                    "IDENTICAL_DELIVERABLE_PATH",
                    1,
                    "完整制作母稿与标准投稿阅读稿必须使用两个不同文件路径。",
                )
            ],
            metrics={},
        )
    else:
        master_text = args.master.read_text(encoding="utf-8") if args.master else None
        submission_text = args.submission.read_text(encoding="utf-8") if args.submission else None
        if master_text is not None and submission_text is not None:
            result = audit_pair(master_text, submission_text, args.expected_episodes, submission_scope=args.submission_scope)
        elif master_text is not None:
            result = audit_master(master_text, args.expected_episodes)
        else:
            result = audit_submission(submission_text or "", args.expected_episodes, submission_scope=args.submission_scope)

    if args.json:
        print(json.dumps(_result_payload(result), ensure_ascii=False, indent=2, sort_keys=True))
    else:
        _print_human(result)
    return 1 if result.blocking else 0


if __name__ == "__main__":
    sys.exit(main())
