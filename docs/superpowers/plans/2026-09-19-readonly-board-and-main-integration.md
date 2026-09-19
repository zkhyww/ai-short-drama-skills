# 只读制作看板与 main 整合 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 提供不污染 Prompt 的按需本地快照看板，在通过验证后保留双侧成果、同步安装版并合并最新 main。

**Architecture:** 看板复用已完成的提示词解析接口，只读取本次明确指定的文件并生成一个静态 HTML，不成为生产必经关卡。源码、基线副本、私有项目数据严格分开；原有审核和发布流程继续负责放行，不新建数据库或活动真源。

**Tech Stack:** Python 标准库、静态 HTML/CSS/JavaScript、unittest、宿主浏览器验证工具、Git；产品无需 npm、服务端或数据库。

**Spec:** [已批准设计](../specs/2026-09-19-local-baseline-production-enhancement-design.md)。依赖 [提示词检查与方法计划](2026-09-19-production-checks-and-methods.md) 任务 1–5。状态：计划待审，未实现、未测试、未安装、未发布。

## Global Constraints

- 以本机最新版为基线，保留现有改动，再补；补完之后再同步合并最新的 main。
- 本次不付费生成媒体，不安装外部 Skill，不修改用户剧本，不把创作样本放进 Skill，不清理其他任务文件。
- 看板仅在用户请求或当前交付确需集中浏览时生成；不打开它、不提供完整资产数据或只要一条提示词，都不影响原有制作功能。
- 不建服务、数据库或自动扫描整盘，不新增可编辑的活动真源。
- 复制按钮只复制选定 Clip 的最终提示词原文，不带来源、分析、状态徽标或检查报告。
- 无法明确正文边界时不提供“最终 Prompt”复制。
- 不读取凭据，不自动下载或内嵌媒体、不上传云端；本地路径可用于本地看板，但看板及项目内容不随 Skill 发布。
- 不对 main 强推，不用重置或清理命令处理冲突。
- 安装同步前重新核本机文件哈希，只更新本任务已验证的对应文件。
- 版本号按合并时已占用版本顺延，禁止回退或重用已发布号。
- 必须区分：静态合同通过、程序测试通过、行为任务通过、真实媒体通过。

## Review Focus

1. Clip 原文中含 CRLF、emoji、引号、反斜杠、HTML 或 `</script>`：显示安全且复制保持原文，不混徽标。归任务 6、7。
2. 只有旧格式、含报告的文件、多个 Clip 边界不明、源文件已改变：提供来源和明确状态，不生成误导复制按钮或宣称实时。归任务 6、7。
3. 中文路径、丢失记录、目录越界、相似前缀目录、符号链接／junction、脚本式 URL：不读取／链接越界内容、不自动加载媒体。归任务 6。
4. 浏览器拒绝剪贴板、file URL 权限限制、长文／窄视口：按钮有明确反馈及手动后备，不能仅靠 HTML 字符串断言。归任务 7。
5. main 或安装包在施工期间有新变化，原工作区有脏案例文件：保留所有现场，重新合并及回归，冲突不能靠覆盖、强推或暂存私有文件解决。归任务 9。

---

## 文件与接口总图

| 文件 | 职责 |
|---|---|
| `drama-studio/scripts/build_production_board.py`（新） | 有界只读输入、来源快照、HTML 渲染和复制后备 |
| `drama-studio/scripts/validate_prompt.py` | 由前项计划提供，复用正文切片／解析／检查，不复制第二套解析器 |
| `tests/test_production_board.py`（新） | 原文、边界、安全、只读、输出及 CLI 测试 |
| `drama-studio/references/file-management.md`、`SKILL.md` | 看板的派生用途与按需入口 |
| 两包 `references/startup-guide.md` | 同一共用导航，仅补已实现的可选功能 |
| `README.md`、`CHANGELOG.md` | 面向使用者说明及真实版本增量 |

任务编号承接前一计划，从 6 起。任务 6 → 7 → 8 → 9，不并行改动共享规则。

### Task 6: 有界输入与安全快照渲染

**Files:**
- Create: `drama-studio/scripts/build_production_board.py`。
- Create: `tests/test_production_board.py`。
- Consume unchanged: `tests/prompt_fixtures.py`、检查器脚本。

**Interfaces:**
- Consumes: `extract_prompt_clips(text: str) -> dict`、`parse_prompt(text: str) -> dict`、`read_prompt_file(path: Path) -> str`；检查调用为 `validate_prompt(text: str, *, duration: float | None = None, locked_speech: list[dict] | None = None, references: list[dict] | None = None, reference_root: Path | None = None) -> dict`，数据结构见前项计划任务 2–3。
- `resolve_source(root: Path, value: str | Path, *, must_exist: bool = True) -> Path`：解析真实路径并限制在 root 内；不接受网络／脚本式 URL、设备路径、凭据文件或目录作为输入。
- `build_board(project_root: Path, *, prompt_files: Sequence[Path] = (), record_files: Sequence[Path] = (), generated_at: datetime | None = None) -> dict`：返回 `html:str, sources:list[dict], warnings:list[dict]`，不写任何源文件。
- Source：`path:str, sha256:str|None, mtime_ns:int|None, version:dict, status:str`；hash 来自实际读取 bytes，版本仅取显式 `script_rev/storyboard_rev` 字段，不能从文件名推已审。
- Warning：`code:str, source:str|None, message:str`。
- `main(argv: list[str] | None = None) -> int`：`--root ROOT --prompt FILE` 可重复，`--record FILE` 可重复，`--output FILE` 必填；不覆盖输入，已存在输出默认拒绝，只有明确 `--overwrite` 才替换这个单文件。
- CLI 必须至少指定一个 prompt 或 record。不从项目根递归发现文件。

- [ ] **Step 1: 写原文保真和路径边界失败测试。**

```python
import base64
from html.parser import HTMLParser
from pathlib import Path
import tempfile
import unittest
from tests.prompt_fixtures import prompt_text
from tests.test_dreamina_production_tools import load_script

class CopyPayloads(HTMLParser):
    def __init__(self):
        super().__init__()
        self.values = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if "data-prompt-utf8" in values:
            self.values.append(base64.b64decode(
                values["data-prompt-utf8"]).decode("utf-8"))

class ProductionBoardTests(unittest.TestCase):
    def test_copy_payload_is_original_prompt_not_html_or_status(self):
        board = load_script("build_production_board")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            source = root / "机场片段.txt"
            text = prompt_text().replace(
                "只有房间环境声", "原样文字 <b>不执行</b> 🎬；只有房间环境声")
            text = text.replace("\n", "\r\n")
            source.write_bytes(text.encode("utf-8"))
            original = source.read_bytes()
            result = board.build_board(root, prompt_files=[source])
            parser = CopyPayloads()
            parser.feed(result["html"])
            self.assertEqual([text], parser.values)
            self.assertEqual(original, source.read_bytes())

    def test_similar_prefix_directory_is_out_of_scope(self):
        board = load_script("build_production_board")
        with tempfile.TemporaryDirectory() as folder:
            parent = Path(folder)
            root = parent / "project"
            sibling = parent / "project-private"
            root.mkdir()
            sibling.mkdir()
            secret = sibling / "private.txt"
            secret.write_text("outside", encoding="utf-8")
            with self.assertRaises(ValueError):
                board.resolve_source(root, secret)
```

继续逐组增加 RED：

| 输入 | 预期 |
|---|---|
| 两个明确 Clip 标题及不同原文 | 两个复制区，各自只含对应正文，不串片段 |
| 未明确分隔的两套八段，夹有评审章节 | 来源可读，零“最终 Prompt”复制区，CLIP_BOUNDARY |
| 旧四区块或普通分镜记录 | 显示原记录／链接，不伪造已解析提示词 |
| 明确但不存在的源文件 | 条目记缺失，不臆造内容；其他独立来源仍可展示 |
| `../` 越界、同名前缀目录、UNC、`javascript:`、`data:` | 拒绝；不读文件、不生成可点击恶意链接 |
| 项目内符号链接／junction 实际指向外部 | resolve 后拒绝；宿主不支持创建链接时测试明确 skip，Windows 发布前补实际核验 |
| `.env`、Cookie／密钥等明确凭据路径 | 拒绝，且 HTML 无其内容 |
| `</script><img src=x onerror=alert(1)>`、带引号文件名 | HTML 转义，不新增可执行节点或外联请求 |
| source 生成后被改写 | 老 HTML 明确为快照；再次构建得到不同哈希，不沿用旧 QC |
| 只有 record、无 prompt；一条 prompt、无资产库 | 都可生成，不要求补空文件 |

- [ ] **Step 2: 运行确认 RED。**

```powershell
python -B -m unittest tests.test_production_board -v
```

测试缺脚本使用现有 load_script 的断言；创建测试环境失败与生产行为失败分开报告。

- [ ] **Step 3: 实现读取、边界和快照语义。**

输入只允许 root 内显式指定的文本文件（.md/.txt/.json/.csv）；扩展名由输入读取处判断，输出端独立要求 .html，不让源文件扩展名白名单误拒合法输出。resolve_source 只负责路径／凭据边界：先拒绝 URL／UNC／设备路径和明确的凭据名，再 resolve 根及输入，用路径结构判断，而不是字符串前缀：

```python
root = root.resolve(strict=True)
candidate = value if isinstance(value, Path) else Path(value)
candidate = candidate if candidate.is_absolute() else root / candidate
candidate = candidate.resolve(strict=must_exist)
try:
    candidate.relative_to(root)
except ValueError as exc:
    raise ValueError("source escapes project root") from exc
```

输入文件读一次 bytes，SHA256 和解析都基于这批 bytes；读取前后 stat 不一致则告知来源在读取时改变，重试该文件一次，仍变化就跳过并记警告。不存在的文件按 missing；越界／凭据等属于不合法输入，不把它包装成普通缺失而继续读取。只提取明确键，未知旧记录原样转义展示，不自行连表；记录里的任意 URL 或路径仅作文字，只有已明确指定且通过边界核验的源文件生成链接。

页面固定显示“本地制作快照”、生成时刻、来源文件、哈希／版本和“源文件更新后需重新生成”。已记录的 QC 仅作为原记录值展示，并带版本／未复核说明；看板自己的结构检查不能升级为已审、已上传或媒体通过。

正文使用 `extract_prompt_clips` 的原切片；无法确定边界仅来源链接。确定性错误的 Prompt 可以原样展示与复制，但按钮旁必须显示错误／未核范围，不能当成已批准可提交；不修改原文自动修复。

- [ ] **Step 4: 实现转义与复制原文载荷。**

```python
import base64
import html

encoded = base64.b64encode(prompt.encode("utf-8")).decode("ascii")
safe_visible_text = html.escape(prompt, quote=True)
copy_region = (
    '<section data-prompt-utf8="' + encoded + '">'
    '<button type="button" data-copy>复制 Prompt 原文</button>'
    '<pre tabindex="0">' + safe_visible_text + '</pre>'
    '<p role="status" aria-live="polite"></p></section>'
)
```

Base64 仅为安全携带字符，不作为加密或授权机制。标题、来源、版本、警告均单独 html.escape；不把不可信文字插入 script、CSS 或原始 href。脚本为固定本地字符串，没有字符串代码执行、外联资源或媒体标签。本地文件链接由已核 Path.as_uri() 产生；页面不访问这些文件，用户点击才打开。

render 采用固定样式：系统字体、清楚分区、长文换行、可见焦点与高对比状态；不引入前端框架或品牌重设计。CSP 禁外联（connect-src none、img-src none），静态脚本／样式采用实际内容 hash，不能用放开所有脚本作为解决方案。

- [ ] **Step 5: 跑测试并提交。**

```powershell
python -B -m unittest tests.test_production_board tests.test_validate_prompt -v
python -B -m unittest discover -s tests -v
git add drama-studio/scripts/build_production_board.py tests/test_production_board.py
git diff --cached --check
git commit -m "feat: build bounded read-only production snapshots"
```

### Task 7: 复制反馈、CLI 输出与真实浏览器验收

**Files:** Modify `drama-studio/scripts/build_production_board.py`、`tests/test_production_board.py`。仅本地测试证据放 `.task-evidence/production-board/`。

**Interfaces:**
- Consumes: 任务 6 的 HTML 中 `data-prompt-utf8`、按钮和 status 区。
- Produces: 复制成功／失败明确反馈；失败时显示只读文本框并选中，供手动复制；不更改 source。
- CLI：成功生成且有警告仍返回 0、stderr 列警告；非法输入／全体源不可读取／输出冲突返回 2，不伪造正常看板。

- [ ] **Step 1: 用真实 CLI 添加失败测试。**

使用 TemporaryDirectory 与原创夹具，实际运行脚本。检查：输出是唯一新文件；源 bytes 不变；默认不覆盖已有 HTML；output 与任一输入相同即使加 --overwrite 也拒绝；输出越界拒绝；从其他 cwd 执行仍可动态导入解析器。

```python
def test_cli_refuses_to_replace_its_prompt_input(self):
    import subprocess
    import sys
    from tests.test_dreamina_production_tools import SCRIPTS
    with tempfile.TemporaryDirectory() as folder:
        root = Path(folder)
        source = root / "clip.txt"
        source.write_text(prompt_text(), encoding="utf-8")
        original = source.read_bytes()
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "build_production_board.py"),
             "--root", str(root), "--prompt", str(source),
             "--output", str(source), "--overwrite"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(2, result.returncode)
        self.assertEqual(original, source.read_bytes())
```

- [ ] **Step 2: 运行并记录正确的失败。**

```powershell
python -B -m unittest tests.test_production_board -v
```

- [ ] **Step 3: 实现 CLI 与固定复制脚本。**

解析后校验输入／输出不重合，输出必须是 root 内显式 .html；不自动创建多层输出目录。读取源只读，成功后只写指定 HTML。静态 JS 以 UTF-8 还原原文，成功后更新可访问状态区：

```javascript
document.addEventListener("click", async (event) => {
  const button = event.target.closest("button[data-copy]");
  if (!button) return;
  const region = button.closest("[data-prompt-utf8]");
  const status = region.querySelector('[role="status"]');
  const bytes = Uint8Array.from(
    atob(region.dataset.promptUtf8), (char) => char.charCodeAt(0));
  const text = new TextDecoder("utf-8", {fatal: true}).decode(bytes);
  try {
    await navigator.clipboard.writeText(text);
    status.textContent = "已复制 Prompt 原文；检查与审核状态未包含在内。";
  } catch {
    let manual = region.querySelector("textarea");
    if (!manual) {
      manual = document.createElement("textarea");
      manual.readOnly = true;
      manual.setAttribute("aria-label", "Prompt 原文手动复制");
      region.appendChild(manual);
    }
    manual.value = text;
    manual.focus();
    manual.select();
    status.textContent = "浏览器不允许自动复制，请手动复制已选文本。";
  }
});
```

自动复制按字符串逐字符保持；手动后备可能受浏览器／系统换行转换影响，页面明确不宣称二进制文件拷贝。不以 HTML 的 innerText 重建 Prompt；来源、状态绝不进入载荷。

- [ ] **Step 4: 单元 GREEN 后，用实际浏览器验证。**

按 webapp-testing 与浏览器证据流程，优先宿主浏览器；不使用截图作为剪贴板内容证明。

1. 在本任务证据目录用 apply_patch 创建两个原创八段夹具（中英对白各一，含长文与特殊字符），运行已实现 CLI 生成看板。
2. 打开本地看板，核 1280px 桌面与约 390px 窄视口：来源／状态清楚、Prompt 可读、键盘可聚焦按钮，无横向挤出导致内容缺失。
3. 授予测试页剪贴板权限时，点击按钮后实际读取剪贴板字符串，与解码后原文逐字符比较；不只看“已复制”标签。
4. 拒绝权限后点击，确认真实失败反馈、只读后备文本框和选区；不伪造成功。
5. 点击已指定源文件链接；如果宿主限制 file URL，页面仍显示完整本地路径供打开，不绕过权限或上传云端。
6. 用浏览器 DOM 和网络观察确认恶意文本只显示为文字，没有新增 img/script 节点或外联请求。
7. 修改夹具的原文后，老看板仍是明确旧快照；再次生成后哈希／内容改变，旧 QC 未自动沿用。

浏览器自动化不可用时明确记“未做浏览器验收”，不把任务 7 标完成。上述网页没有产品后端；如测试工具必须 HTTP，仅临时启动绑定 127.0.0.1 的文件服务且限定本证据目录，测试完停止本任务服务，不停止他人进程。

- [ ] **Step 5: 完整回归与提交。**

```powershell
python -B -m unittest discover -s tests -v
git add drama-studio/scripts/build_production_board.py tests/test_production_board.py
git diff --cached --check
git commit -m "fix: preserve prompt copying and handle local browser limitations"
```

### Task 8: 正式入口、启动卡与文档同步

**Files:** Modify `drama-studio/SKILL.md` 工具表、第 6 步交付；`drama-studio/references/file-management.md` 原目录职责及派生文件段；两包 `references/startup-guide.md` 现有功能导航；`README.md` 对应使用说明。暂不预写发布版本或“全部验收”。

**Interfaces:**
- Consumes: 任务 2–7 的真实 CLI 参数与状态。
- Produces: 自动检查接现有装配自检；看板只接按需展示；两份共用启动卡字节一致，保留各包独立可安装。

- [ ] **Step 1: 先做入口行为对照。**

按 writing-skills，给未改入口的执行者两项正常请求：“只交这一条英文视频 Prompt，不做媒体”与“把这几条已有 Prompt 和资产记录整理成方便查看、复制的本地页面”。每次只给相关文件与现有入口，不告诉检查器或看板名字。核是否错误强制整套资产／报告／团队、遗漏现有工具或把看板说明混入复制正文。入口已有正确行为的部分不再加规则。

- [ ] **Step 2: 原位增加最小可执行说明。**

工具表各一行：检查器的已核／未核边界、看板的本地派生快照职责。装配自检写实际调用，交付段只在需集中浏览时引用看板。startup-guide 功能行区分“自动检查”与“可选展示”，不新增审批、强制用户选择功能或每项目新文件。

README 放经测试的真实命令：

```powershell
python -B drama-studio/scripts/validate_prompt.py "C:/项目/03_分镜/clip.txt" --duration 30
python -B drama-studio/scripts/dreamina_route.py video --prompt-file "C:/项目/03_分镜/clip.txt" --duration 30
python -B drama-studio/scripts/build_production_board.py --root "C:/项目" --prompt "03_分镜/clip.txt" --record "02_资产/assets.json" --output "制作快照.html"
```

这些路径是使用说明示意，不在用户机器创建 `C:/项目`。README 明确引用现有记录；无资产记录时省略 --record，无需补一份。逐字英文对白不因中文说明被翻译。

- [ ] **Step 3: 复测入口任务与单包分发。**

同任务、同条件对照修订前后实际产物，检查工具调用和复制边界，不把检索到工具名字算有效调用。两包共用卡修订内容保持一致。

```powershell
python -B -m unittest tests.test_startup_guide_distribution tests.test_validate_prompt tests.test_production_board -v
python -B -m unittest discover -s tests -v
git diff --check
```

仅在已存在静态导航合同确实过时且目的仍需覆盖时更换相应断言；不能另写大量固定措辞快照来充当行为验收。

- [ ] **Step 4: 提交真实入口与使用说明。**

```powershell
git add drama-studio/SKILL.md drama-studio/references/file-management.md drama-studio/references/startup-guide.md drama-crew/references/startup-guide.md README.md
git commit -m "docs: connect optional production tools to existing workflow"
```

### Task 9: 独立审查、最新 main 合并、安装核验与远端同步

**Files:** 仅上述任务已核变更及真实远端冲突文件；版本涉及两包 `SKILL.md`、`CHANGELOG.md`、`README.md` 和确有版本说明的直接消费端。源工作区两份脏案例文件和私有配置保持原样。

**Interfaces:**
- Consumes: 通过的代码／规则／浏览器结果、隔离基线提交、原安装哈希和当前 origin/main。
- Produces: 合并后验证结果、应同步文件哈希匹配、main 提交与真实远端回执；不把本地提交称作已发布。

- [ ] **Step 1: 完成独立整支审查和最新本地验证。**

按执行方式对应的 Superpowers 审查流程，给独立审查者设计、两份计划、完整 diff、测试证据与已知未核项。审查重点为原文保真、未核不假通过、事实锁、路径安全、本机／main 双侧保留。本人复读不冒充独立审查。Critical／Important 先修再复核。

使用 verification-before-completion；记录以下真实结果，明确跳过项及原因：

```powershell
python -B -m unittest discover -s tests -v
git diff --check
git status --short --branch
```

审查和行为证据留本机受保护位置，不进发布包；公开可重跑的小型原创单元测试可进入 tests。

- [ ] **Step 2: 到此才获取并合并最新 main。**

```powershell
git fetch origin main
git log --oneline HEAD..origin/main
git diff --stat HEAD...origin/main
git merge --no-edit origin/main
```

在隔离工作分支执行。冲突文件先读取共同来源、本机冻结副本及远端差异，再按已批准行为合并；不整包选 ours/theirs。冲突触及原工作区脏案例文件时不替用户暂存／覆盖；其原文件保持原地，暂停相关源工作区更新并报告具体范围。

- [ ] **Step 3: 合并后重跑而非沿用合并前证据。**

```powershell
python -B -m unittest discover -s tests -v
git diff --check
git status --short
```

远端改动触及解析／复制／方法条件时，重跑对应浏览器及行为任务；不能仅靠无冲突自动合并判验收。遇到意外现有失败按名称披露，判断对放行的实际影响。

- [ ] **Step 4: 版本顺延、发布范围扫描与本机同步。**

核本机、工作分支和最新 main 已占用版本，再选择未占用且不降低的 Crew／Studio 新号；不预定为固定补丁号。CHANGELOG 区分“既有本机成果保全”“本轮工具与方法增量”“已验证／未媒体复现”。README、启动卡只写已完成内容。

检查待发布文件名与 diff，不输出秘密值：

```powershell
git diff --name-only origin/main...HEAD
git diff --numstat origin/main...HEAD
git ls-files -- '*.mp4' '*.mov' '*.wav' '*.mp3' '*.zip' '*.env' '*local-config*' '*screenwriting-library.local*' '*.pem' '*.key'
git diff --check origin/main...HEAD
```

再对新变更人工核密钥、Cookie、个人／项目资料、完整第三方提示词和未核授权内容；扫描命中只报告文件与位置。不能把“无常见扩展名”当完整敏感扫描。

同步安装前重核每个目标文件相对任务开始的哈希；有并发变化，先三方合并对应文件。先保存本任务即将修改的每个非 Git 文件可恢复副本，再用 apply_patch 更新已验证内容；保留现有私有绑定和项目资产，绝不整目录替换。应同步的正式源码／安装文件逐项 SHA256 相同，再核两包入口版本及共用启动卡。重新从安装路径调用两工具 --help、只读原创夹具及兼容动态加载，不能只验证仓库副本。

- [ ] **Step 5: 文档聚焦整理、工作区审计与收尾提交。**

先 neat-freak 核本轮主责段落、入口、版本、链接、实际 CLI；再 workspace-hygiene Audit 仅本任务目录。保护 .baseline-snapshot、.task-evidence 和用户现场；缓存仅在有授权、可再生且未被引用时按绝对路径逐项删除。没有候选直接记无可清理项，不额外建清理报告。

精确暂存版本／整合修改：

```powershell
git diff --cached --name-only
git diff --cached --check
git commit -m "chore: finalize verified local-baseline production release"
```

没有实际新增 staged 差异时不做空提交。

- [ ] **Step 6: 按已授权的 main 整合方式收尾并核远端。**

使用 finishing-a-development-branch；用户已要求补完再同步合并最新 main，不重复提出删分支／放弃工作选项。更新源 main 前核两份脏案例文件没有路径冲突，始终不自动 stash、暂存或还原它们。能安全快进才快进；需保护分支或 PR 时沿仓库规则处理，不绕过保护。只有本次发布范围核清、验证完成后才推送，永不强推。

推送成功后读取远端 main SHA 与本地已发布提交比较；CI 如有运行读取实际执行、通过、失败、跳过数量，不把“排队”称通过。若创建 PR，按宿主要求附到当前任务；只作参考的外部 PR 不附。

最终简报仅报告：功能增量、保留的本机能力、测试分层结果、未核媒体范围、本机版本及远端实际状态；源工作区受保护的脏文件仍保留。若安装／合并／推送被具体冲突阻塞，分别说清已完成与未完成，不宣称全部同步。

## 计划自审与验收边界

规划自审：设计 §7 的原文、来源、旧格式、快照、安全与按需边界对应任务 6–8；§8 的整合、并发保护、安装及发布对应任务 9。已逐项核对接口与前项计划一致，五项 Review Focus 均落到具体测试／浏览器步骤；未把规划自审写成产品验收。

- [ ] 用户审阅两份实施计划并选择执行方式后开工。
- [ ] 看板复用检查器，不出现第二套 Clip／八段解析器。
- [ ] 来源、状态与可复制正文隔离；未知格式和缺证据不假通过。
- [ ] 真实浏览器核复制、拒绝权限、链接、长文和窄屏。
- [ ] 最新 main 整合后重新验证，本机同步前重核并发差异。
- [ ] 样本／快照／原媒体／私有绑定不进 Skill 或远端。
- [ ] 最终审查、安装核验、远端与 CI 状态分别有证据；不宣称真实媒体通过。
