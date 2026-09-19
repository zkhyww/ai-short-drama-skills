#!/usr/bin/env python3
"""Export an offline, read-only view of explicitly selected production records."""
from __future__ import annotations

import argparse
import base64
import csv
from datetime import datetime, timezone
import hashlib
import html
import io
import json
import os
from pathlib import Path
import re
import sys
import tempfile


TEXT_EXTENSIONS = {'.md', '.txt', '.json', '.csv'}


def _safe_path_text(value):
    text = str(value)
    normalized = text.replace('\\', '/')
    if not text or any(ord(c) < 32 for c in text) or normalized.startswith('//'):
        raise ValueError('Network, device or empty paths are not permitted')
    # Allow a local drive prefix, not a URI scheme or Windows alternate stream.
    rest = normalized[2:] if re.match(r'^[A-Za-z]:/', normalized) else normalized
    if ':' in rest or re.match(r'^[A-Za-z]:[^/]', normalized):
        raise ValueError('Only local filesystem paths are permitted')
    for part in normalized.split('/'):
        name = part.lower()
        if not name or name in {'.', '..'} or re.fullmatch('[a-z]:', name):
            continue
        if part.endswith((' ', '.')) or re.fullmatch(r'(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?', name):
            raise ValueError('Device or ambiguous paths are not permitted')
        if (name in {'.git', '.ssh', '.aws', '.azure', '.env', 'local-config.json'}
                or name.startswith('.env.') or name.endswith(('.local.json', '.pem', '.key', '.p12', '.pfx'))
                or re.search(r'(^|[_.-])(credentials?|cookies?|secrets?|tokens?|auth)([_.-]|$)', name)):
            raise ValueError('Credential/configuration paths are not permitted')
    return text


def _root_path(value):
    path = Path(_safe_path_text(value)).resolve()
    if not path.is_dir():
        raise ValueError(f'Root directory is unavailable: {path}')
    return path


def resolve_source(root, value, *, allowed_roots=(), must_exist=True):
    """Resolve against the project, then test containment, never string prefixes."""
    root = _root_path(root)
    permitted = [root, *(_root_path(p) for p in allowed_roots)]
    path = Path(_safe_path_text(value))
    path = (path if path.is_absolute() else root / path).resolve()
    _safe_path_text(path)
    if not any(path == parent or parent in path.parents for parent in permitted):
        raise ValueError(f'Path is outside explicitly allowed roots: {value}')
    if path.exists() and not path.is_file():
        raise ValueError(f'Expected a file: {value}')
    if must_exist and not path.is_file():
        raise ValueError(f'Source file is unavailable: {value}')
    return path


def read_source(root, value):
    path = resolve_source(root, value)
    if path.suffix.lower() not in TEXT_EXTENSIONS:
        raise ValueError(f'Unsupported text type: {path.suffix}')
    try:
        for _ in range(2):
            before = path.stat()
            raw = path.read_bytes()
            after = path.stat()
            signature = lambda stat: (stat.st_mtime_ns, stat.st_size, stat.st_ino)
            if signature(before) == signature(after) and len(raw) == after.st_size:
                return {'path': str(path), 'text': raw.decode('utf-8-sig'),
                        'sha256': hashlib.sha256(raw).hexdigest(), 'mtime_ns': after.st_mtime_ns}
    except (OSError, UnicodeError) as exc:
        raise ValueError(f'Cannot read UTF-8 source {path}: {exc}') from exc
    raise ValueError(f'Source changed during snapshot: {path}')


def select_prompt(source, *, kind, start_line=None, end_line=None):
    if kind not in {'image', 'video'}:
        raise ValueError('Prompt kind must be image or video')
    text = source['text']
    if (start_line is None) != (end_line is None):
        raise ValueError('Both line bounds are required')
    if start_line is not None:
        lines = text.splitlines(keepends=True)
        if (type(start_line) is not int or type(end_line) is not int
                or not 1 <= start_line <= end_line <= len(lines)):
            raise ValueError('Invalid prompt line range')
        text = ''.join(lines[start_line - 1:end_line])
    if not text.strip():
        raise ValueError('Prompt selection is empty')
    return {'kind': kind, 'source_path': source['path'], 'text': text,
            'sha256': hashlib.sha256(text.encode('utf-8')).hexdigest(),
            'selection': [start_line, end_line]}


ALIASES = {
    'id': ('id', 'asset_id', 'char_id', 'scene_id', 'prop_id'),
    'file': ('file', 'path', 'file_path'),
    'name': ('name', '名称', '姓名', '场景名', '道具名'),
}
ASSET_FIELDS = ('id', 'name', 'type', 'file', 'panel', 'decision', 'readiness',
                'usage_status', 'version', 'purpose', 'clips', 'dependencies',
                'next_action', 'file_action')
FILE_ACTIONS = {'reuse', 'generate', 'rework'}


def _identity_warnings(rows, *, across_sources=False):
    groups, warnings = {}, []
    for number, row in enumerate(rows, 1):
        if isinstance(row.get('id'), str) and row['id']:
            groups.setdefault(row['id'], []).append((number, row))
    for identity, group in groups.items():
        if across_sources and len({row.get('_source_path') for _, row in group}) < 2:
            continue
        for field in ('type', 'name'):
            specified = [(number, row) for number, row in group if row.get(field) not in (None, '')]
            if specified and any(row[field] != specified[0][1][field] for _, row in specified[1:]):
                details = '；'.join(f'{row.get("_source_path", "原记录")} '
                                    f'条目 {row.get("_source_row", number)}: {row[field]!r}'
                                    for number, row in specified)
                warnings.append(f'身份 ID {identity} 的 {field} 跨条目冲突，未合并原记录：{details}')
    return warnings


def _unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f'Duplicate JSON key: {key}')
        result[key] = value
    return result


def normalize_assets(data):
    """Project common existing layouts without changing or dropping source data."""
    rows, warnings, unparsed = [], [], {}
    if isinstance(data, list):
        entries = [(None, item) for item in data]
    elif isinstance(data, dict) and any(key in data for key in ('assets', 'rows')):
        keys = [key for key in ('assets', 'rows') if key in data]
        if len(keys) != 1 or not isinstance(data[keys[0]], list):
            return {'rows': [], 'warnings': ['资产容器不明确，保留原记录'], 'unparsed': data}
        entries = [(None, item) for item in data[keys[0]]]
        unparsed = {key: value for key, value in data.items() if key != keys[0]}
    elif isinstance(data, dict):
        entries = [(key, item) for key, item in data.items() if isinstance(item, dict)]
        unparsed = {key: item for key, item in data.items() if not isinstance(item, dict)}
    else:
        return {'rows': [], 'warnings': ['未知资产结构，保留原记录'], 'unparsed': data}
    rejected = []
    for number, (map_id, record) in enumerate(entries, 1):
        if not isinstance(record, dict):
            rejected.append(record)
            warnings.append(f'条目 {number} 不是资产对象')
            continue
        row = {'raw': record}
        for field in ASSET_FIELDS:
            values = [record[key] for key in ALIASES.get(field, (field,))
                      if record.get(key) is not None and record[key] != '']
            if field == 'id' and map_id is not None:
                values.append(map_id)
            if values and any(value != values[0] for value in values[1:]):
                warnings.append(f'条目 {number} 的 {field} 同义键冲突，未选择任意一个')
                row[field] = None
            else:
                row[field] = values[0] if values else None
            if field in ('id', 'file', 'name') and row[field] is not None and not isinstance(row[field], str):
                warnings.append(f'条目 {number} 的 {field} 应为文本，原值保留')
                row[field] = None
        if row['id'] is None:
            warnings.append(f'条目 {number} 未明确身份 ID')
        if row['file_action'] is not None and row['file_action'] not in ('reuse', 'generate', 'rework'):
            warnings.append(f'条目 {number} 的文件作业类型未知，未推断')
            row['file_action'] = None
        rows.append(row)
    if rejected:
        unparsed = {'extra': unparsed, 'entries': rejected}
    if unparsed:
        warnings.append('有未投影内容，见原记录；不能把未解析视为无工作')
    warnings.extend(_identity_warnings(rows))
    return {'rows': rows, 'warnings': warnings, 'unparsed': unparsed}


def summarize_assets(rows):
    groups, identities = {}, set()
    unknown_without_file = 0
    incomplete = bool(_identity_warnings(rows))
    for row in rows:
        identity = row.get('id')
        if isinstance(identity, str) and identity:
            identities.add(identity)
        else:
            incomplete = True
        file = row.get('file')
        if isinstance(file, str) and file:
            groups.setdefault(os.path.normcase(os.path.normpath(file)), []).append(row)
        else:
            unknown_without_file += 1
            incomplete = True
    reused, planned, unknown = 0, 0, unknown_without_file
    for group in groups.values():
        actions = [row.get('file_action') for row in group]
        action = actions[0]
        if action not in ('reuse', 'generate', 'rework') or any(item != action for item in actions):
            unknown += 1
            incomplete = True
        elif action in {'generate', 'rework'}:
            planned += 1
        elif all(row.get('readiness') == 'file_ready' and row.get('file_exists') is True
                 and not row.get('file_issue') for row in group):
            reused += 1
        else:
            incomplete = True
        if any(row.get('readiness') not in ('prompt_only', 'file_ready', 'external_mount_plan') for row in group):
            incomplete = True
    return {'reference_count': len(identities), 'referenced_file_count': len(groups),
            'reused_file_count': reused, 'planned_new_file_count': planned,
            'unknown_file_action_count': unknown, 'incomplete': incomplete}


def _image_uri(path):
    with path.open('rb') as stream:
        head = stream.read(16)
    matches = {'.png': head.startswith(b'\x89PNG\r\n\x1a\n'),
               '.jpg': head.startswith(b'\xff\xd8\xff'),
               '.jpeg': head.startswith(b'\xff\xd8\xff'),
               '.gif': head.startswith((b'GIF87a', b'GIF89a')),
               '.webp': head.startswith(b'RIFF') and head[8:12] == b'WEBP'}
    if not matches.get(path.suffix.lower(), False):
        raise ValueError('仅预览扩展名与文件签名相符的 PNG/JPEG/WebP/GIF')
    return path.as_uri()


def _display(value):
    if value is None or value == '' or value == []:
        return '未记录'
    if isinstance(value, (dict, list)):
        value = json.dumps(value, ensure_ascii=False, indent=2)
    return html.escape(str(value), quote=True)


def _dependency_status(value):
    if isinstance(value, dict):
        if value.get('status') in ('pending', 'unresolved', 'blocked'):
            return '未决（按来源记录）'
        return '状态未记录' if 'status' not in value else f"来源状态：{_display(value['status'])}"
    if isinstance(value, list):
        return '；'.join(_dependency_status(item) for item in value) or '状态未记录'
    return '状态未记录'


CSS = '''
:root{color-scheme:light;--ink:#1e2926;--muted:#53665d;--line:#d5ded7;--paper:#f2f5f1;--accent:#155e4b}
*{box-sizing:border-box}body{margin:0;background:var(--paper);color:var(--ink);font:16px/1.65 system-ui,"Microsoft YaHei",sans-serif}
main{max-width:1120px;margin:auto;padding:32px 24px 70px}h1{font-size:clamp(26px,4vw,40px);margin:0 0 12px}h2{font-size:24px;margin:36px 0 14px}h3{margin:0 0 10px;font-size:19px}
p{margin:8px 0}.eyebrow{font-size:13px;letter-spacing:.12em;color:var(--accent)}.muted,small{color:var(--muted)}nav{display:flex;gap:20px;flex-wrap:wrap;margin-top:20px}a{color:var(--accent)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));gap:18px}.card,details{background:white;border:1px solid var(--line);border-radius:12px;padding:20px;min-width:0;margin-bottom:14px}
.stats{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:12px}.stat{border-top:2px solid var(--accent);padding:12px 0}.stat strong{display:block;font-size:28px}
.notice{border-left:4px solid #8b6324;padding:12px 18px;background:#fff7e8}.tag{font-size:13px;border:1px solid var(--line);border-radius:5px;padding:2px 8px;display:inline-block}
dl{display:grid;grid-template-columns:110px minmax(0,1fr);gap:7px 12px;margin:12px 0}dt{color:var(--muted)}dd{margin:0;white-space:pre-wrap}pre,dd,small,p,summary,a{overflow-wrap:anywhere;word-break:normal}
pre{white-space:pre-wrap;font:14px/1.7 ui-monospace,Consolas,monospace;max-height:440px;overflow:auto;background:#f6f8f5;border-radius:8px;padding:14px;margin:12px 0}img{display:block;width:100%;height:auto;max-height:420px;object-fit:contain;background:#e8ede8;border-radius:8px}img[hidden]{display:none}
button{background:var(--accent);color:white;border:0;border-radius:7px;padding:10px 16px;font:inherit;cursor:pointer;min-height:44px}button:hover{background:#0d4738}button:focus-visible,a:focus-visible,summary:focus-visible,pre:focus-visible,textarea:focus-visible{outline:3px solid #b06919;outline-offset:4px}
summary{cursor:pointer}textarea{display:block;width:100%;min-height:160px;margin-top:12px;font:14px/1.5 monospace}li{overflow-wrap:anywhere;margin:6px 0}article{min-width:0}.responsibility{border-top:1px solid var(--line);padding-top:12px;margin-top:16px}
@media(max-width:500px){main{padding:22px 14px 40px}.card,details{padding:14px}dl{grid-template-columns:1fr;gap:2px}dd{margin-bottom:8px}.stats{grid-template-columns:1fr 1fr}}
'''

JS = '''
document.querySelectorAll('img[data-src]').forEach(img => {
  const status = img.parentElement.querySelector('[data-image-status]');
  img.addEventListener('error', () => {
    img.hidden = true;
    status.textContent = '图片未加载：文件可能已移动、不可解码或被浏览器限制。请核原路径；不改变来源状态。';
  });
  img.addEventListener('load', () => {
    status.textContent = '本地图片已显示；不代表内容审核通过或已采用。';
  });
  img.src = img.dataset.src;
});
document.addEventListener('click', async event => {
  const button = event.target.closest('button[data-copy]');
  if (!button) return;
  const region = button.closest('[data-prompt-utf8]');
  const bytes = Uint8Array.from(atob(region.dataset.promptUtf8), c => c.charCodeAt(0));
  const text = new TextDecoder('utf-8', {fatal:true}).decode(bytes);
  const status = region.querySelector('[role="status"]');
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = '已复制提示词原文；不包含状态说明。';
  } catch {
    let field = region.querySelector('textarea');
    if (!field) {
      field = document.createElement('textarea');
      field.readOnly = true;
      field.setAttribute('aria-label', '提示词原文手动复制');
      region.appendChild(field);
    }
    field.value = text;
    field.focus();
    field.select();
    status.textContent = '自动复制不可用，请手动复制已选原文（浏览器可能规范化换行）。';
  }
});
'''


def _prompt_region(prompt):
    payload = base64.b64encode(prompt['text'].encode('utf-8')).decode('ascii')
    label = '图片提示词' if prompt['kind'] == 'image' else '视频提示词'
    return (f'<section class="card" data-prompt-utf8="{payload}"><h3>{label}</h3>'
            f'<p class="muted">来源：{_display(prompt["source_path"])} · 行范围：{_display(prompt["selection"])}</p>'
            f'<button type="button" data-copy>复制{label}原文</button>'
            f'<pre tabindex="0">{_display(prompt["text"])}</pre>'
            '<p role="status" aria-live="polite"></p></section>')


def _row_region(row):
    labels = {'id':'身份 ID', 'name':'名称', 'type':'类型', 'panel':'Panel / 区域',
              'decision':'身份／状态决策', 'file_action':'文件作业', 'readiness':'文件就绪（来源）',
              'usage_status':'使用状态（来源）', 'version':'版本', 'purpose':'用途 / 控制职责',
              'clips':'覆盖片段', 'dependencies':'依赖原记录', 'next_action':'下一动作'}
    fields = ''.join(f'<dt>{label}</dt><dd>{_display(row.get(key))}</dd>' for key, label in labels.items())
    return (f'<section class="responsibility"><dl>{fields}</dl>'
            f'<p class="muted">依赖：{_dependency_status(row.get("dependencies"))}；不据此自动排队。</p>'
            f'<details><summary>完整来源条目（含未投影字段）</summary><pre>{_display(row["raw"])}</pre></details></section>')


def build_board(project_root, *, asset_files=(), record_files=(), prompts=(), image_roots=(), generated_at=None):
    root = _root_path(project_root)
    image_roots = tuple(_root_path(p) for p in image_roots)
    if not (asset_files or record_files or prompts):
        raise ValueError('At least one explicit text source is required')
    sources, rows, warnings, unparsed, records, selected = {}, [], [], [], [], []
    input_paths = set()

    def source_for(value):
        path = str(resolve_source(root, value))
        if path not in sources:
            sources[path] = read_source(root, value)
        input_paths.add(path)
        return sources[path]

    for value in asset_files:
        source = source_for(value)
        suffix = Path(source['path']).suffix.lower()
        try:
            if suffix == '.json':
                data = json.loads(source['text'], object_pairs_hook=_unique_object)
            elif suffix == '.csv':
                reader = csv.DictReader(io.StringIO(source['text']))
                headers = reader.fieldnames or []
                if len(headers) != len(set(headers)):
                    raise ValueError('Duplicate CSV headers; no column was selected or discarded')
                data = list(reader)
            else:
                data = source['text']
        except (ValueError, csv.Error) as exc:
            raise ValueError(f'Invalid asset source {source["path"]}: {exc}') from exc
        projection = normalize_assets(data)
        for number, row in enumerate(projection['rows'], 1):
            row['_source_path'], row['_source_row'] = source['path'], number
        rows.extend(projection['rows'])
        warnings.extend(f'{source["path"]}: {warning}' for warning in projection['warnings'])
        if projection['unparsed']:
            unparsed.append({'source':source['path'], 'content':projection['unparsed']})
    warnings.extend(_identity_warnings(rows, across_sources=True))
    for value in record_files:
        records.append(source_for(value))
    for spec in prompts:
        selected.append(select_prompt(source_for(spec['path']), kind=spec['kind'],
                                      start_line=spec.get('start_line'), end_line=spec.get('end_line')))

    previews, groups = {}, {}
    for number, row in enumerate(rows):
        row['file_exists'] = None
        file = row.get('file')
        issue, uri = '未记录文件路径', None
        key = f'unmapped-{number}'
        if file:
            key = file
            try:
                path = resolve_source(root, file, allowed_roots=image_roots, must_exist=False)
                row['file'] = str(path)
                key = os.path.normcase(str(path))
                input_paths.add(str(path))
                if key not in previews:
                    exists = path.is_file()
                    try:
                        uri = _image_uri(path) if exists else None
                        issue = None if exists else '文件尚不存在'
                    except (OSError, ValueError) as exc:
                        issue = str(exc)
                    previews[key] = (exists, uri, issue)
                row['file_exists'], uri, issue = previews[key]
            except (ValueError, OSError) as exc:
                issue = str(exc)
        row['file_issue'] = issue
        if issue:
            warnings.append(f'{file or row.get("id")}: 未预览 — {issue}')
        group = groups.setdefault(key, {'file':row.get('file'), 'uri':uri, 'issue':issue, 'rows':[]})
        group['rows'].append(row)
    summary = summarize_assets(rows)
    if not asset_files:
        warnings.append('未提供结构化资产，数量未核；请读取原作业记录，不把显示的已识别零项当作全项目零项')
    if unparsed or warnings:
        summary['incomplete'] = True
    for group in groups.values():
        actions = [row.get('file_action') for row in group['rows']]
        if actions and any(action != actions[0] for action in actions[1:]):
            warnings.append(f'{group["file"]}: 同文件作业冲突，未计入复用或新制')

    stamp = generated_at or datetime.now(timezone.utc).isoformat(timespec='seconds')
    stats = [('参考身份', 'reference_count'), ('记录文件（含计划）', 'referenced_file_count'),
             ('来源标为复用、路径存在（解码未核）', 'reused_file_count'), ('记录计划新制／返修', 'planned_new_file_count'),
             ('文件作业未明确', 'unknown_file_action_count')]
    body = ['<main><header><p class="eyebrow">STUDIO / LOCAL DELIVERY</p><h1>制作资产与提示词</h1>',
            f'<p>只读快照 · {_display(stamp)}</p><p class="muted">来源改变后需重新导出。本页不生成媒体、不改源记录，也不认证画面质量。</p>',
            '<nav aria-label="页面导航"><a href="#assets">资产图册</a><a href="#prompts">提示词原文</a><a href="#sources">来源与未决项</a></nav></header>',
            '<h2>本批工作概览</h2><div class="stats">']
    body.extend(f'<div class="stat"><strong>{summary[key]}</strong>{label}</div>' for label, key in stats)
    body.append('</div><p class="notice">' + ('统计不完整：未知项没有当作零或已完成。' if summary['incomplete'] else '统计仅依据明确记录与本次路径核验，不是内容验收。') + '</p>')
    body.append('<h2 id="assets">资产图册</h2><div class="grid">')
    for group in groups.values():
        body.append(f'<article class="card"><h3>{_display(Path(group["file"]).name if group["file"] else "待明确文件")}</h3>')
        if group['uri']:
            uri = html.escape(group['uri'], quote=True)
            body.append(f'<div><img data-src="{uri}" alt="资产参考预览"><p data-image-status class="muted">等待加载本地图片；失败时显示未加载。</p></div>'
                        f'<p><a href="{uri}" target="_blank" rel="noopener">查看原图</a></p>')
        else:
            body.append(f'<p class="notice">未预览：{_display(group["issue"])}</p>')
        body.append(f'<small>{_display(group["file"])}</small>')
        body.extend(_row_region(row) for row in group['rows'])
        body.append('</article>')
    body.append('</div><h2 id="prompts">提示词原文</h2><p class="muted">复制仅包含所选正文；清单、来源、状态说明不进入提示词。未指定图片与词的对应关系时不猜关联。</p>')
    body.extend(_prompt_region(prompt) for prompt in selected)
    body.append('<h2 id="sources">来源与未决项</h2>')
    if warnings:
        body.append('<div class="notice"><ul>' + ''.join(f'<li>{_display(w)}</li>' for w in warnings) + '</ul></div>')
    for record in records:
        body.append(f'<details open><summary>作业／记录：{_display(record["path"])}</summary><pre>{_display(record["text"])}</pre></details>')
    for value in unparsed:
        body.append(f'<details open><summary>未投影原记录</summary><pre>{_display(value)}</pre></details>')
    source_metadata = [{key:source[key] for key in ('path','sha256','mtime_ns')} for source in sources.values()]
    body.append(f'<details><summary>来源指纹与读取时刻（非实时状态）</summary><pre>{_display(source_metadata)}</pre></details></main>')
    digest = lambda value: base64.b64encode(hashlib.sha256(value.encode('utf-8')).digest()).decode('ascii')
    csp = (f"default-src 'none'; script-src 'sha256-{digest(JS)}'; style-src 'sha256-{digest(CSS)}'; "
           "img-src file:; connect-src 'none'; object-src 'none'; frame-src 'none'; base-uri 'none'; form-action 'none'")
    page = ('<!doctype html><html lang="zh-CN"><head><meta charset="utf-8">'
            f'<meta http-equiv="Content-Security-Policy" content="{html.escape(csp, quote=True)}">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>制作资产与提示词 · 只读快照</title><style>{CSS}</style></head><body>'
            + ''.join(body) + f'<script>{JS}</script></body></html>')
    return {'html':page, 'sources':source_metadata, 'warnings':warnings, 'summary':summary,
            'input_paths':sorted(input_paths)}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', required=True)
    parser.add_argument('--output', required=True)
    for name in ('assets', 'record', 'image-prompt', 'video-prompt', 'image-root'):
        parser.add_argument('--' + name, action='append', default=[])
    parser.add_argument('--prompt-range', nargs=4, action='append', default=[], metavar=('KIND','FILE','START','END'))
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args(argv)
    try:
        root = _root_path(args.root)
        output = resolve_source(root, args.output, must_exist=False)
        if output.suffix.lower() != '.html' or not output.parent.is_dir():
            raise ValueError('Output must be an .html file in an existing project directory')
        if output.exists() and not args.overwrite:
            raise ValueError('Output exists; use --overwrite only for this derived snapshot')
        prompts = ([{'path':p,'kind':'image'} for p in args.image_prompt]
                   + [{'path':p,'kind':'video'} for p in args.video_prompt])
        prompts.extend({'kind':kind,'path':path,'start_line':int(start),'end_line':int(end)}
                       for kind,path,start,end in args.prompt_range)
        result = build_board(root, asset_files=args.assets, record_files=args.record,
                             prompts=prompts, image_roots=args.image_root)
        if str(output) in result['input_paths']:
            raise ValueError('Output must not overwrite any referenced source')
        data = result['html'].encode('utf-8')
        if args.overwrite:
            descriptor, temp_path = tempfile.mkstemp(prefix='.board-', suffix='.tmp', dir=output.parent)
            try:
                with os.fdopen(descriptor, 'wb') as stream:
                    stream.write(data)
                os.replace(temp_path, output)
            finally:
                if os.path.exists(temp_path):
                    os.unlink(temp_path)
        else:
            created = False
            try:
                with output.open('xb') as stream:
                    created = True
                    stream.write(data)
            except OSError:
                if created:
                    output.unlink(missing_ok=True)
                raise
        for warning in result['warnings']:
            print(f'Warning: {warning}', file=sys.stderr)
        print(str(output))
        return 0
    except (OSError, ValueError) as exc:
        print(f'Error: {exc}', file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
