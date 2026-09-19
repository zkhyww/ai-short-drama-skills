# 资产作业清单、可视图册与只读看板 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox syntax for tracking.

**Goal:** 在保留本机最新版的前提下，补齐同源资产作业清单、可视图册及可选离线看板，验证、同步安装后推送并合并 GitHub main。

**Architecture:** 制作职责沿现有剧本、资产索引和复用说明识别本批工作；一个标准库展示工具只读取明确输入，导出静态 HTML。它不生成媒体、不改源记录、不依赖尚未实现的提示词检查器。图片词和视频词各自引用、各自复制，状态说明不进入正文。

**Tech Stack:** Python 标准库、HTML/CSS/JavaScript、unittest、宿主浏览器测试工具、Git；不新增服务、数据库或产品依赖。

**Spec:** [已确认设计](../specs/2026-09-19-local-baseline-production-enhancement-design.md) §7–§9。用户最新要求“请修改并上传推送合并”确认书面设计并授权验证后的发布。此计划原位替换旧看板计划，不依赖 [检查器与方法计划](2026-09-19-production-checks-and-methods.md)；后者仍为独立待审事项。本计划待用户审阅并选择执行方式，当前没有产品实现或验收结论。

## Global Constraints

- 以本机最新版为基线，保留现有改动，再补；补完之后再同步合并最新的 main。
- 不付费生成媒体，不安装外部 Skill，不修改用户剧本，不把创作样本放进 Skill，不清理其他任务文件。
- 本批清单在已有索引／复用说明和交付入口中呈现，不另建一份人工维护的 JSON 台账。
- 身份决策沿用 reuse/new_variant/new_asset/unresolved；文件就绪沿用 prompt_only/file_ready/external_mount_plan，另保留原有候选／采用状态。
- 保留一人一份独立参考、完整全身三视图、按实际出镜故事角色配板、总表 Panel 可承担场景／道具职责、英文项目适配和八段视频格式。
- 简单资产请求不需要整剧清单、分镜、总表或 HTML。
- 不从文件名或提示词子串猜关联；输入适配在工具内完成，不能为出看板批量迁移资产索引。
- 复制保持源正文，不带来源、清单、案例说明、状态徽标或检查报告。
- 只读取明确指定的文本输入和其中明确引用、落在已声明允许目录内的本地图片，不递归扫描目录、不读取凭据、不自动下载或上传。
- 预览仅加载实际本地栅格图片，不执行 SVG／HTML 等活动内容，不复制图片、不把媒体打包为 Base64。
- 图片展示也不构成新的内容验收；看板只展示真实状态，不生成图片、不排队付费任务、不替代内容审核。
- 本轮授权包含验证后的推送与 main 合并，不强推、不自动暂存原工作区已有案例改动；敏感内容检查仍是发布前置。

## Review Focus

1. 一个文件承载多个资产 Panel，同一身份补细节但仍为 reuse：不能按身份判词算新图或重复算文件。任务 2。
2. 中文／英文 Prompt 含 CRLF、emoji、引号、HTML、说明性标题；一份文件含多条提示词：显式选择正文范围，原文复制，不猜边界。任务 1、3。
3. Windows 中文路径、相似前缀目录、UNC／设备路径、符号链接、外部资产目录和脚本式链接：只有明确输入且实际落在允许范围内才读取／预览。任务 1、3。
4. 本地图片无法加载、源文件被移动、剪贴板受限、旧快照和窄屏：有真实失败反馈，不能只凭生成 HTML 或状态标签宣称可用。任务 3、5。
5. 安装版或 main 并发变化、旧测试只认过时措辞、私有案例绑定或本机路径：保留有效行为和现场，发布逐文件核验。任务 1、4、5。

## 文件与接口总图

| 文件 | 职责 |
|---|---|
| drama-studio/scripts/build_production_board.py（新增） | 有界输入、资产视图、原文载荷、图片预览与 HTML/CLI |
| tests/test_production_board.py（新增） | 输入、状态、统计、原文、安全、只读及 CLI 回归 |
| tests/test_asset_delivery_contracts.py（新增） | 运行时规则入口、两轴状态、按需展示与现有默认的合同检查 |
| drama-studio/references/asset-library.md | 原 §1、§4、§5 的作业记录与缺口选图 |
| drama-studio/references/role-cards.md | 丹青原职责、交付与派单的实际落点 |
| drama-studio/references/file-management.md | 原 §0–§4 的源数据、派生视图和版本边界 |
| drama-studio/SKILL.md | 原工具表、透明化、资产产出与最终交付入口 |
| 两包 references/startup-guide.md | 共用功能导航，Crew 为维护真源，Studio 为相同内容副本 |
| README.md、CHANGELOG.md | 验证后的真实功能、版本及使用方法 |

仅新增一个可单独运行的展示脚本，不新增检查器、通用调度平台或项目 manifest。下面的 Python dict 是工具内存视图，不是要求用户另存的 Schema。内部函数和 CLI 的最小合同在各任务定义，后续任务不得另起一套同义接口。

### Task 1: 保全本机基线并实现有界文本输入

**Files:** 当前两包可发布文件的逐文件合并；新增展示脚本和 tests/test_production_board.py。基线副本及行为证据只留本机受保护任务目录，不进发布包。

**Interfaces:**

- resolve_source(root: Path, value: str | Path, *, allowed_roots: Sequence[Path] = (), must_exist: bool = True) -> Path：限制实际解析路径。文本输入只在 root 内；allowed_roots 只用于后续图片预览。
- read_source(root: Path, value: str | Path) -> dict：返回 path、text、sha256、mtime_ns；UTF-8/UTF-8 BOM 解码，保留换行。不得写源文件。
- select_prompt(source: dict, *, kind: str, start_line: int | None = None, end_line: int | None = None) -> dict：kind 仅 image/video；返回 kind、source_path、text、sha256、selection。行号从 1 起，含端点；一端缺失或越界拒绝。未给行号表示调用者明确指定整个文件为一条纯 Prompt。
- 通用 record 输入只展示，不提供 Prompt 复制；调用者未能确认纯正文时必须传 record，不能用八段标题猜测切片。行范围采用 splitlines(keepends=True)，不 strip、不重排。

- [ ] **Step 1: 使用 using-git-worktrees 保全现场并核基线。**

先读取适用 AGENTS.md，确认目标是 ai-short-drama-skills，不在上级控制仓库建立产品分支。原工作区两份案例文件保持原位，记录哈希，不自动 stash、暂存或清理。按实际工具能力与用户选择设置隔离工作区；原生工具不能指向此子仓库时才使用 Git fallback。没有用户的隔离偏好时与本计划执行方式一并确认。

~~~powershell
git rev-parse --show-toplevel
git rev-parse --git-dir
git rev-parse --git-common-dir
git rev-parse --show-superproject-working-tree
git status --short --branch
git remote -v
python -B -m unittest discover -s tests -v
~~~

读取正式安装版路径由用户目录定位，不从旧源码反向覆盖：

~~~powershell
$installedCrew = Join-Path $env:USERPROFILE '.codex/skills/drama-crew'
$installedStudio = Join-Path $env:USERPROFILE '.codex/skills/drama-studio'
Get-Content -LiteralPath (Join-Path $installedStudio 'SKILL.md') -TotalCount 9
Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $installedStudio 'SKILL.md')
~~~

只读比较本机与仓库的相对路径及内容，逐文件保留本机 1.21.9 生图规则和 main 独有的有效脚本修复。将可发布规则、必要跨包依赖、脚本合入隔离分支；不整包复制私有案例绑定、原始案例 TXT、媒体、缓存或项目内容。原始安装文件先逐文件备份。基线引入的旧措辞测试失败须查明具体行为差异，不直接删除测试。真实既有失败向用户披露，不把未通过基线冒充可发布。

保全可发布基线形成单独提交；明确这些是原有本机成果，不是本轮新增。新工具 RED 测试在这个基线上运行。

- [ ] **Step 2: 写并运行输入边界失败测试。**

~~~python
from pathlib import Path
import tempfile
import unittest
from tests.test_dreamina_production_tools import load_script

class BoardSourceTests(unittest.TestCase):
    def test_source_and_selection_preserve_text(self):
        board = load_script("build_production_board")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            path = root / "对白.txt"
            raw = "说明\r\n英文台词 🎬 <b>literal</b>\r\n尾注\r\n"
            path.write_bytes(raw.encode("utf-8"))
            before = path.read_bytes()
            source = board.read_source(root, path)
            prompt = board.select_prompt(
                source, kind="video", start_line=2, end_line=2)
            self.assertEqual("英文台词 🎬 <b>literal</b>\r\n", prompt["text"])
            self.assertEqual(before, path.read_bytes())

    def test_sibling_with_same_prefix_is_rejected(self):
        board = load_script("build_production_board")
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder)
            root = parent / "project"
            sibling = parent / "project-private"
            root.mkdir()
            sibling.mkdir()
            path = sibling / "private.txt"
            path.write_text("outside", encoding="utf-8")
            with self.assertRaises(ValueError):
                board.resolve_source(root, path)
~~~

~~~powershell
python -B -m unittest tests.test_production_board -v
~~~

预期是缺少脚本／目标函数造成 RED，不是临时目录权限或导入环境错误。继续增加明确测试：根路径不存在、输入为目录、越界 ../、UNC、设备路径、javascript/data/http URL、凭据名、无效 UTF-8、半个行范围、倒序／越界行范围、源 bytes 不变；路径测试不读取任何真实密钥。符号链接测试只创建临时范围内的无敏感夹具，无法建立时明确记录 skip，Windows 发布前补实际核验。

- [ ] **Step 3: 最小实现并运行 GREEN。**

路径使用 Path.resolve 后的 relative_to，禁止字符串前缀判断。先拒绝网络／设备／脚本式值和明确凭据路径，再验证文件类型。显式文本输入只接受 .md/.txt/.json/.csv；不因扩展名识别出 Prompt 身份。读取一次 bytes，哈希与解码来自同一批 bytes；读取前后 stat 变化则重试一次，仍变化报来源不稳定，不生成伪一致快照。

~~~python
import hashlib
from pathlib import Path

def is_inside(path, roots):
    return any(path == root or root in path.parents for root in roots)

def select_prompt(source, *, kind, start_line=None, end_line=None):
    if kind not in {"image", "video"}:
        raise ValueError("prompt kind must be image or video")
    text = source["text"]
    if (start_line is None) != (end_line is None):
        raise ValueError("both line bounds are required")
    if start_line is not None:
        lines = text.splitlines(keepends=True)
        if not 1 <= start_line <= end_line <= len(lines):
            raise ValueError("invalid prompt line range")
        text = "".join(lines[start_line - 1:end_line])
    if not text.strip():
        raise ValueError("prompt selection is empty")
    return {"kind": kind, "source_path": source["path"], "text": text,
            "sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
            "selection": [start_line, end_line]}
~~~

不把这段代码当全部安全实现；resolve_source/read_source 必须满足上述边界测试。成功后运行源读取与既有动态加载回归并提交这一个功能单元。

### Task 2: 从既有记录投影作业清单与资产图册

**Files:** Modify 展示脚本及 tests/test_production_board.py。

**Interfaces:**

- normalize_assets(data: object) -> dict：返回 rows、warnings、unparsed。rows 只作内存展示。
- summarize_assets(rows: Sequence[dict]) -> dict：返回 reference_count、referenced_file_count、reused_file_count、planned_new_file_count、unknown_file_action_count、incomplete。referenced_file_count 是记录中的去重文件路径数，包含计划路径，不等于实际已有文件数；reused_file_count 只计明确 file_action=reuse、readiness=file_ready 且本次路径核验 file_exists=True 的文件。缺失状态时不凑数，新制数在不完整时标 incomplete，不显示成总完成数。
- 规范化 row：id、name、type、file、panel、decision、readiness、usage_status、version、purpose、clips、dependencies、next_action、file_action、raw。缺失值为 None 或空列表，不捏造默认“已采用”。build_board 路径核验后添加内部 file_exists=True/False/None，分别代表存在、确认缺失、未获准读取或尚未检查，不回写源记录，不改变采用状态。
- 支持显式 rows 列表、assets 列表以及 ID→条目字典。ID 键接受 id/asset_id/char_id/scene_id/prop_id；路径接受 file/path/file_path；名称接受 name/名称/姓名/场景名/道具名，其余仅对应同名字段。多键互相矛盾记冲突，不能静默选一个。
- file_action 仅消费输入已存在的 reuse/generate/rework 值；缺失保持 unknown，不从 decision 或文件是否存在猜出。它是适配可用记录的可选字段，不要求给旧索引补新字段；清单在复用说明中时可直接作为 record 展示。
- 同一 ID 的多文件／状态行均保留；引用人数去重看显式角色身份，文件统计按解析后路径去重，不把 Panel 数算成新图片数。依赖逐项展示原始对象或文本；只有记录明确给出 pending/unresolved/blocked 状态时列为未决，未写状态显示“未记录”，不猜数量为零或自行排序执行。旧未知字段保留在 raw；未知整体结构在 unparsed 原样展示并警告。

- [ ] **Step 1: 写并观察统计和状态 RED。**

~~~python
class AssetProjectionTests(unittest.TestCase):
    def test_panels_share_file_and_reuse_can_need_new_detail(self):
        board = load_script("build_production_board")
        result = board.normalize_assets({"assets": [
            {"id": "SCENE_A", "type": "scene", "file": "table.png",
             "panel": "空场景", "decision": "reuse", "file_action": "reuse"},
            {"id": "PROP_A", "type": "prop", "file": "table.png",
             "panel": "道具", "decision": "reuse", "file_action": "reuse"},
            {"id": "PROP_A", "type": "prop", "file": "detail.png",
             "decision": "reuse", "readiness": "prompt_only",
             "file_action": "generate"}
        ]})
        summary = board.summarize_assets(result["rows"])
        self.assertEqual(2, summary["reference_count"])
        self.assertEqual(2, summary["referenced_file_count"])
        self.assertEqual(1, summary["planned_new_file_count"])
        self.assertEqual("reuse", result["rows"][2]["decision"])
        self.assertEqual("prompt_only", result["rows"][2]["readiness"])

    def test_unknown_format_is_retained_not_empty_success(self):
        board = load_script("build_production_board")
        original = {"旧版说明": ["不要丢失这一项"]}
        result = board.normalize_assets(original)
        self.assertTrue(result["warnings"])
        self.assertEqual(original, result["unparsed"])

    def test_reused_files_need_explicit_readiness_and_path_evidence(self):
        board = load_script("build_production_board")
        rows = [
            {"id": "SCENE_A", "file": "table.png", "panel": "场景",
             "file_action": "reuse", "readiness": "file_ready",
             "file_exists": True},
            {"id": "PROP_A", "file": "table.png", "panel": "道具",
             "file_action": "reuse", "readiness": "file_ready",
             "file_exists": True},
            {"id": "PROP_B", "file": "missing.png",
             "file_action": "reuse", "readiness": "file_ready",
             "file_exists": False},
            {"id": "CHAR_A", "file": "external.png",
             "file_action": "reuse", "readiness": "file_ready",
             "file_exists": None},
        ]
        summary = board.summarize_assets(rows)
        self.assertEqual(3, summary["referenced_file_count"])
        self.assertEqual(1, summary["reused_file_count"])
        self.assertTrue(summary["incomplete"])
~~~

增加表驱动失败测试：列表／assets／ID 字典等价；明确角色数 1、3、7；同路径不同 Panel；同 ID 不同状态和版本；缺文件、缺 ID、重复 ID 冲突、未知采用状态；未声明 file_action 不猜新图数；unknown 字段仍可见；显式 clips/dependencies 保留而不从命名推导。

~~~powershell
python -B -m unittest tests.test_production_board.AssetProjectionTests -v
~~~

- [ ] **Step 2: 实现保守投影。**

~~~python
ID_KEYS = ("id", "asset_id", "char_id", "scene_id", "prop_id")
FILE_KEYS = ("file", "path", "file_path")
NAME_KEYS = ("name", "名称", "姓名", "场景名", "道具名")

def one_value(record, keys):
    values = [record[k] for k in keys if record.get(k) is not None]
    if not values:
        return None
    if any(value != values[0] for value in values[1:]):
        raise ValueError("conflicting aliases")
    return values[0]

def unique_known(values):
    return {value for value in values if value is not None and value != ""}
~~~

逐条投影，坏条目进入 warnings/unparsed，不吞掉整份输入。统计函数只计算已知明确项目；先由 build_board 将可解析文件路径标准化。路径未知、外部目录未准入及互相矛盾的计划动作分别报告；不能把未知当成零、把“有路径”当成已生成或验收通过。依赖仅按记录展示，不在工具里新造调度引擎。

- [ ] **Step 3: GREEN 和回归后提交。**

~~~powershell
python -B -m unittest tests.test_production_board -v
git add drama-studio/scripts/build_production_board.py tests/test_production_board.py
git diff --cached --check
git commit -m "feat: project asset worklists without duplicating source records"
~~~

### Task 3: 本地图片预览、原文复制及 CLI

**Files:** Modify 展示脚本和 tests/test_production_board.py。

**Interfaces:**

- build_board(project_root: Path, *, asset_files: Sequence[Path] = (), record_files: Sequence[Path] = (), prompts: Sequence[dict] = (), image_roots: Sequence[Path] = (), generated_at: str | None = None) -> dict。
- 返回 html、sources、warnings、summary。prompts 元素为 path/kind 和可选 start_line/end_line；由 read_source/select_prompt 取得原文，不接受网页脚本直接传内容。
- CLI：--root、--output 必填；可重复 --assets FILE、--record FILE、--image-prompt FILE、--video-prompt FILE、--prompt-range KIND FILE START END、--image-root DIR；可选 --overwrite。至少一个文本输入。无 --output 不产生文件；输出必须是 root 内 .html，不覆盖任何源文件。
- --image-root 只准入其中已被索引引用的图片，不遍历该目录。不能把“允许目录”变成扫描、导入或上传授权。
- 返回码：成功导出 0，具体警告写 stderr；非法显式输入、全部文本不可读、输出冲突为 2。单张图片缺失只给占位，不阻断其余来源。

- [ ] **Step 1: 增加原文、安全与 CLI RED。**

~~~python
import base64
from html.parser import HTMLParser

class CopyPayloads(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if "data-prompt-utf8" in attrs:
            self.values.append(base64.b64decode(
                attrs["data-prompt-utf8"]).decode("utf-8"))

class RenderTests(unittest.TestCase):
    def test_copy_has_only_selected_original(self):
        board = load_script("build_production_board")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "台词.txt"
            text = 'Hold. 🎬\r\n</script><img src=x onerror=alert(1)>\r\n'
            source.write_bytes(text.encode("utf-8"))
            result = board.build_board(
                root, prompts=[{"path": source, "kind": "video"}],
                generated_at="2026-09-19T00:00:00Z")
            parser = CopyPayloads()
            parser.feed(result["html"])
            self.assertEqual([text], parser.values)
            self.assertNotIn("<img src=x", result["html"])
            self.assertEqual(text.encode("utf-8"), source.read_bytes())
~~~

增加测试：两种 Prompt 各有独立载荷；record 中出现 BLOCK 1、围栏或评审文字不会自动变成复制正文；行范围保持 CRLF；本地 PNG 真实引用；SVG/HTML 伪装图片拒绝预览；未允许外部图片只标未加载；旧版本／候选不自动标当前；图片同文件多 Panel 一次预览；图片加载失败反馈；不出现远程 src、脚本 URL、媒体 Base64 或源文件写入；源码 hash 随内容变化，旧 HTML 标快照。使用原创文本和合成的极小栅格夹具，不读用户作品。

CLI 以 subprocess 真实运行，覆盖：中文路径、其他 cwd、唯一新产物、默认拒绝覆盖、--overwrite 仍拒绝覆盖输入、输出越界、输出目录不存在、零输入、非法 kind、单文件缺失和部分图片缺失。写完测试运行并记录正确 RED。

- [ ] **Step 2: 最小实现安全渲染与复制。**

~~~python
import base64
import html

def prompt_region(prompt):
    payload = base64.b64encode(prompt["text"].encode("utf-8")).decode("ascii")
    label = "图片提示词" if prompt["kind"] == "image" else "视频提示词"
    return (
        '<section data-prompt-utf8="' + payload + '">'
        '<h3>' + label + '</h3><button type="button" data-copy>复制原文</button>'
        '<pre tabindex="0">' + html.escape(prompt["text"], quote=True) + '</pre>'
        '<p role="status" aria-live="polite"></p></section>'
    )
~~~

固定 JS 用 TextDecoder 解码 data-prompt-utf8，不以 innerText 重建正文：

~~~javascript
document.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-copy]");
  if (!button) return;
  const region = button.closest("[data-prompt-utf8]");
  const bytes = Uint8Array.from(atob(region.dataset.promptUtf8),
                               char => char.charCodeAt(0));
  const text = new TextDecoder("utf-8", {fatal: true}).decode(bytes);
  const status = region.querySelector('[role="status"]');
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = "已复制提示词原文；不包含状态说明。";
  } catch {
    let field = region.querySelector("textarea");
    if (!field) {
      field = document.createElement("textarea");
      field.readOnly = true;
      field.setAttribute("aria-label", "提示词原文手动复制");
      region.appendChild(field);
    }
    field.value = text;
    field.focus();
    field.select();
    status.textContent = "自动复制不可用，请手动复制已选原文。";
  }
});
~~~

图片只由已核 Path.as_uri 生成本地 href/src。检查栅格魔数与允许扩展名，不仅靠后缀；首版支持 PNG/JPEG/WebP/GIF，其他格式显示原路径和未预览原因。不对图片做转换、缩略图落盘或语义验收。图片 error 事件显示未加载状态，候选／未核状态不因 img.onload 改为通过。

HTML 采用严格转义、固定脚本和样式。CSP 禁 connect/object/frame/form；脚本与样式用实际内容 hash；图像只开放所需本地 file 来源，不放开 http/https/data。标题、描述、文件名和未知字段均作文本，不执行第三方 HTML、SVG 或链接。系统字体、响应式卡片、长文折行、可见键盘焦点、文字状态标识。页面只读，无生成按钮、支付操作或源数据编辑。

CLI 读取完成后只写显式 output；输出存在时先检查 --overwrite，输出与任意文本／图片输入重合一律拒绝。以临时同目录文件原子替换时须在异常路径清理该次临时文件；不得出现留在项目中的隐式缓存。实现时优先直接独占创建新文件，覆盖分支才用经过测试的替换。

- [ ] **Step 3: GREEN、实际 CLI 和回归后提交。**

~~~powershell
python -B -m unittest tests.test_production_board -v
python -B -m unittest discover -s tests -v
git add drama-studio/scripts/build_production_board.py tests/test_production_board.py
git diff --cached --check
git commit -m "feat: render local asset previews and isolated prompt copies"
~~~

### Task 4: 原位接入资产职责与正式入口

**Files:** 修改文件图中的原规则位；新增 tests/test_asset_delivery_contracts.py；同步两份共用启动卡和 README。版本在发布阶段统一确定。

**Interfaces:** 使用任务 1–3 的真实参数和状态；制作职责维护既有索引／复用说明，脚本只消费。不给人物库、分镜总表增加第二套必填 Schema。

- [ ] **Step 1: 先跑规则基线与失败合同。**

按 writing-skills 对以下普通请求做无新增规则的独立应用测试，证据留本机，不塞进 Skill：

| 输入 | 核查 |
|---|---|
| 本集四个故事角色，三份已批角色板可复用，新增一人；总表尚未做 | 参考数与新制文件数分开，生成依赖明确，没有固定两人板 |
| 一个总表两个 Panel 分别承担场景和道具 | 一幅预览、两项职责，不新增两张重复图片 |
| 既有武器只需补握持细节 | 沿原 ID 和 reuse，新文件仍待生成 |
| 只改一条英文 Prompt | 原文直交，不强制清单、图册、HTML 或另开团队 |
| 远端生图任务未知、用户未授权增费 | 查原任务，停真实依赖，不由清单自动重试付费 |
| 用户要已有图片与多条 Prompt 的集中交付 | 能找到实际文件、状态和各自纯正文；缺图明确，不用路径冒充图 |

有/无新规则各做 5 次独立样本并人工核读；本来正确的默认不添加重复禁令。把确有遗漏的展示字段放到原交付模板，不只在末尾增加提醒。

合同测试固定工具入口、字段职责和非触发条件，不通过匹配长段旧措辞来锁死文案：

~~~python
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]

class AssetDeliveryContracts(unittest.TestCase):
    def test_tool_is_reachable_from_delivery_owner(self):
        entry = (ROOT / "drama-studio" / "SKILL.md").read_text(encoding="utf-8")
        owner = (ROOT / "drama-studio" / "references" /
                 "file-management.md").read_text(encoding="utf-8")
        self.assertIn("scripts/build_production_board.py", entry)
        self.assertIn("build_production_board.py", owner)
        self.assertIn("只读", owner)
        self.assertIn("原文", owner)

    def test_shared_guide_is_identical(self):
        name = Path("references/startup-guide.md")
        self.assertEqual((ROOT / "drama-crew" / name).read_bytes(),
                         (ROOT / "drama-studio" / name).read_bytes())
~~~

- [ ] **Step 2: 按设计 §4 和 §7 原位修订。**

asset-library 原 §1 明确“身份／状态”和“文件／作业”不同轴，原 §4–§5 补具体视觉缺口到对应图种的选择与复用。丹青交付模板顺序为“本批工作与下一动作→实际资产图册→纯提示词引用”，先列用途、来源、覆盖和依赖，再显示未决项；不把流程说明放入图片 Prompt。

file-management 原 §0–§4 写清索引和源文件权威、图册派生、HTML 快照、刷新与不打包媒体。SKILL 原透明化、资产产出和第 6 步引用这些职责，工具表加一行。启动卡只补可视资产交付与可选看板功能，不新增问卷或审批。README 使用真实已测命令：

~~~powershell
python -B drama-studio/scripts/build_production_board.py --root "C:/项目" --assets "02_资产/asset-index.json" --image-prompt "02_资产/角色提示词.txt" --video-prompt "03_分镜/C01.txt" --output "制作看板.html"
~~~

上例各 --prompt 文件须已确认只含一条纯正文；混合文档使用 --record 或明确 --prompt-range，不复制说明区。外部资产目录使用 --image-root 显式准入，不要求复制回项目。不新增强制背景音乐、额外场景母版、固定板数或固定影片风格。

- [ ] **Step 3: GREEN、独立应用复测和文档一致性检查。**

~~~powershell
python -B -m unittest tests.test_asset_delivery_contracts tests.test_startup_guide_distribution tests.test_production_board -v
python -B -m unittest discover -s tests -v
git diff --check
~~~

检索所有本轮功能入口，确认没有“默认自动生图”“file_ready=已采用”“必须依赖检查器”“禁本地图片”等冲突旧口径。未发生实测媒体生成时不能声称效果通过。检查本地和跨包链接，再精确暂存本任务规则与测试形成提交。

### Task 5: 浏览器验收、独立审查、安装同步与合并发布

**Files:** 本任务变更、必要基线文件、真实合并冲突文件，以及版本／README／CHANGELOG。案例库两份原脏文件和私有配置不加入发布。

**Interfaces:** 使用当前宿主实际可用浏览器与 GitHub 工具。推荐 Native 顺序实施后做一次独立整支审查；若用户选择 Subagent-driven，则按每任务双重审查及最终整支审查执行。

- [ ] **Step 1: 真实浏览器验证。**

用任务内原创文本与合成栅格夹具构建示例看板，样本留本机证据区，不作为创作案例进入 Skill。按 frontend-auto-orchestrator 选择既定简洁展示的实现／验收路径，使用 webapp-testing；需要 DOM、console、network 时再按 browser-testing-with-devtools 获取证据。

1. 本地离线打开，实际图片显示、共享 Panel 不重复生成图片、待生成和缺失各有明确状态。
2. 桌面约 1280px、窄屏约 390px：无阻断阅读的横向溢出；长英文、中文路径和 Prompt 可读，键盘能操作按钮。
3. 点击图片词、视频词复制，实际读取剪贴板并与原文逐字符比较；拒绝剪贴板权限时有手动后备，不只看成功标签。
4. 注入测试文本只呈现文字，无额外脚本／图片节点和远程请求；本地图片被阻止时显示未加载而不是空白成功。
5. 改动源文件后旧板明确仍是快照，重建后哈希／内容变化，不自动沿用审核；渲染前后源文件 bytes 不变。
6. 浏览器无法测试某项时如实记未核，不能把 HTML 字符串测试当真实浏览器验收。临时 localhost 服务若必需，仅绑定 127.0.0.1 且限定证据目录，结束只停止本任务服务。

- [ ] **Step 2: 独立审查和失败闭环。**

按选定执行方式的 Superpowers 审查流程，提供已批准设计、本计划、完整 diff、测试结果和未核项。重点：本机成果是否保全、同源清单与统计、纯正文复制、本地媒体路径安全、默认生图规则未回退。审查者不接手修改共享文件；Critical／Important 修复后重跑对应测试并复核。使用 verification-before-completion，只报告当次真实结果。

~~~powershell
python -B -m unittest discover -s tests -v
git diff --check
git status --short --branch
~~~

- [ ] **Step 3: 合入最新 main 后重跑。**

~~~powershell
git fetch origin main
git log --oneline HEAD..origin/main
git diff --stat HEAD...origin/main
git merge --no-edit origin/main
python -B -m unittest discover -s tests -v
git diff --check
~~~

在隔离工作分支进行，不重置原工作区。冲突按共同来源、本机冻结内容和远端有效改动逐文件处理；不能整包选 ours/theirs。涉及渲染／路径／复制时重新做受影响浏览器验收。merge 前通过的证据不能代替 merge 后证据。

- [ ] **Step 4: 版本、发布范围及安装核验。**

Studio 新增兼容可见能力，按仓库规则升 minor；以施工时本机／工作分支／远端三方已占用版本选择新号，不预写已发布。Crew 若仅同步导航按实际合同变化选择 patch 或保持版本，并说明两包差异。README 文件数用实际可发布文件统计，CHANGELOG 区分“原本机基线保全”与“本轮新增”。

运行实际可用的 skill validator；找不到时报告未运行并进行对应静态检查，不伪造验证器通过。打包前检查文件名与正文，不含凭据、Cookie、私有绑定、用户剧本、媒体、原始第三方提示词、测试截图或内部证据。只带可重跑原创单元测试，案例库沿既有发布规则，不代提交原脏文件。

~~~powershell
git diff --name-only origin/main...HEAD
git diff --numstat origin/main...HEAD
git ls-files -- '*.mp4' '*.mov' '*.wav' '*.mp3' '*.zip' '*.env' '*local-config*' '*.pem' '*.key'
git diff --check origin/main...HEAD
~~~

安装同步前重核正式文件哈希；并发变更按差异合并，不覆盖。非 Git 安装文件先逐项备份，再用 apply_patch 更新已验证对应文件，保留全部私有绑定。源／安装版本和应同步文件哈希一致；从安装路径实际运行展示脚本 --help 与原创只读夹具。两包启动卡仍字节一致，默认生图稳定性测试在安装版复跑。

- [ ] **Step 5: 打包、清理、合并与推送。**

按仓库文档实际打包到明确临时目录并核包内文件清单；测试包完成后仅按精确路径逐个删除。先 neat-freak 聚焦核对本轮文档、版本和 CLI，再 workspace-hygiene Audit；保护备份、证据和其他任务产物，无候选不造清理报告。

原工作区有两份受保护案例改动，不能通过暂存它们或清理现场来达成“干净”。发布使用干净的隔离工作分支；原 main 只在无冲突且安全快进时更新。若分支保护要求 PR，则推送功能分支、创建 PR、按宿主要求附到当前任务，待必要 CI 通过后合并，不绕过保护；若允许直接更新 main，则按用户现有合并授权安全快进并推送。不强推，远端前进则重新合并验证。

执行 finishing-a-development-branch，沿已授权的“合并并推送”目标收尾，不再重复询问是否发布。读取远端 main SHA 核已合入提交；CI 按真实执行、通过、失败、跳过分别报告，排队不等于通过。保护原案例文件哈希，最终只保留其原未提交状态；如与合并路径相撞，停止具体冲突项并报告。

## 计划自审与执行选择

- [x] 设计 §7.1 的同源清单、统计和依赖对应任务 2、4；脚本不代替制作判断。
- [x] 设计 §7.2 的图种与默认对应任务 4，不重复新增身份或固定板数。
- [x] 设计 §7.3–§7.4 的预览、旧格式、纯正文、快照与安全对应任务 1–3、5。
- [x] 设计 §8–§9 的基线、回归、安装、敏感范围及发布对应任务 1、5。
- [x] 五项 Review Focus 各有测试／实际验收步骤；接口与 CLI 名称一致，无检查器硬依赖。
- [ ] 用户审阅本计划并选择执行方式、确认隔离工作区后开始。
- [ ] 所有任务完成、独立审查通过、安装与远端状态实际核验。

推荐 **Native：当前窗口顺序实现＋最后一次独立整支审查**。这些任务共享一个小工具及同一套规则，连续实现可减少交接成本；代码和行为仍按测试先行。另一选项是 **Subagent-driven：每任务独立实现及审查**，审查更密集但上下文与协调成本更高。无论选择哪种，都不付费生图，不省略发布前验证。
