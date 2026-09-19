# 本机基线、提示词检查与方法补强 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 保全本机 Crew 6.26.12／Studio 1.21.8，在原位补齐确定性提示词检查及经行为对照证明的制作方法缺口。

**Architecture:** 先在隔离工作区保存可发布的本机基线，再增加一个标准库检查器；Dreamina 文件入口消费同一原文和检查结果，普通字符串入口保持兼容。方法仍归已有 Crew／Studio 主责段落，不另建路由平台或规则层；只读看板在后续独立计划中消费本计划的解析接口。

**Tech Stack:** Python 3 标准库、unittest、Markdown、PowerShell、Git；不新增运行时依赖。

**Spec:** [已批准设计](../specs/2026-09-19-local-baseline-production-enhancement-design.md)。状态：计划待用户审阅；以下测试和实现均未执行。

## Global Constraints

- 以本机最新版为基线，保留现有改动，再补；补完之后再同步合并最新的 main。
- 本机 Drama Crew：6.26.12；本机 Drama Studio：1.21.8。
- 本次不付费生成媒体，不安装外部 Skill，不修改用户剧本，不把创作样本放进 Skill，不清理其他任务文件。
- 继续采用原规则位覆盖、合并或替换，不在 Skill 尾部追加补丁，不重建团队、正典、评分体系或案例索引。
- 不设每镜固定时长、镜数或招数，不一概拦硬切、静止、首尾帧、30 秒、相同镜长或无对白。
- 格式语言与对白语言分别继承目标配置。不能因中文标题改写英文台词。
- 没有结构化对照时只运行有依据的检查，其他项明确记未核。
- 不要求用户再维护一份独立真源；可选检查对照从已有记录提取，不成为每项目必交文件。
- `drama-studio/references/case-library/README.md`、`metadata.json` 两个既有脏文件保持原样，不自动暂存、回退或顺手提交。
- main 独有的脚本修复、测试和文档不得因本机文件覆盖而丢失。
- 本轮不生成媒体，所以不能据此宣布打击感、口型、表情或整条无人值守生产线已验收。
- 文件编辑使用 apply_patch；不整包覆盖、不强推、不重置、不批量删除。

## Review Focus

1. 中文路径、BOM、CRLF、首尾空白及带标点英文对白：检查不能改变有效正文，预览字符串与读取的正文相同。归任务 2、4。
2. 一镜到底内部动作节点、同镜长、静止镜、无对白、合唱与抢话：不被误判为镜头重叠或容量错误。归任务 2、3。
3. 未知标题、重复八段、缺锁词对照或缺参考清单：不能跳过解析后给完整通过，也不能猜 Clip 边界。归任务 2、3。
4. 同一人物的道具状态、单人复杂空间、无亲缘关系、背影与英文对白：不能套题材模板、额外造图、加能力或改原句。归任务 5。
5. 安装版与 main 分叉、动态脚本导入、单包安装：保留既有有效修复和依赖；新导入不能只在脚本启动目录可用。归任务 1、4，后续计划任务 9 做合并后复核。

---

## 文件职责与执行顺序

本计划相对路径均以隔离工作区根为准；现有源码根为 `D:/视频/ai-short-drama-skills`，本机包根为 `C:/Users/Administrator/.codex/skills`。执行前读取适用 AGENTS 与 Superpowers 执行技能；使用 using-git-worktrees 创建隔离工作区，不修改已有其他工作树。

| 文件 | 职责 |
|---|---|
| `drama-studio/scripts/validate_prompt.py`（新） | 单 Clip 解析、确定性检查、清楚的批量正文边界与只读 CLI |
| `drama-studio/scripts/dreamina_route.py` | 文件输入／检查接线；仍只生成官方命令预览 |
| `tests/prompt_fixtures.py`（新） | 小型原创测试输入；不进入 Skill 安装包 |
| `tests/test_validate_prompt.py`（新） | 解析、时间线、声音、引用、缺证据与 CLI 退出码 |
| `tests/test_dreamina_production_tools.py` | 同一原文接入及原有工具回归 |
| 任务 5 所列 references | 各自原位的方法补强；不再创建一份重复方法手册 |

任务 1 → 2 → 3 → 4 → 5 顺序执行。每任务完成其测试后形成清楚提交；计划勾选只代表实际已完成，不提前勾选。功能之间不并行写共享文件。

### Task 1: 隔离保全本机基线，识别 main 独有修复

**Files:**
- Preserve untouched: 源工作区两份脏案例文件；两包全部私有配置。
- Modify by reviewed diff: `drama-crew/SKILL.md`、`drama-studio/SKILL.md`，以及下表明确列出的相对路径；仅有换行差异时不当作行为变化。
- Create from verified installed content: Crew `references/{method-routing,comedy-craft,quiet-drama-craft,theme-design,screenwriting-library}.md`；Studio `references/{emotion-performance-library,blender-previs,h3-comfy-mode-routing}.md`。
- Merge, not replace blindly: Crew `scripts/audit_screenplay.py`；Studio `scripts/{case_library,dreamina_route,assemble_timeline}.py`。
- Modify: `.gitignore`，补防止本机读书库私有绑定和本任务保护副本进入发布的精确排除项。
- Test: `tests/test_drama_crew_screenplay_audit.py`、`tests/test_drama_crew_dialogue_submission_contracts.py`、`tests/test_production_learning_contracts.py`、`tests/test_dreamina_production_tools.py`、`tests/test_startup_guide_distribution.py`、`tests/test_case_library.py`。

**Interfaces:**
- Consumes: 本机两包完整文件清单／哈希、设计前 main `29ee0e76ad151183de6161aef6e789c9887ce6be`、设计提交 `6ed3cc9a0eb35b4b2154510f2b4c4c4271bf28f2`。
- Produces: 可回溯的“保存本机既有成果”基线提交；后续任务在此上修改，不将保存旧成果计为新增功能。

已核对的文档差异候选（前缀＋文件名组成完整路径，不授权迁入表外私有文件）：

| 前缀 | 原有文件 |
|---|---|
| `drama-crew/references/` | `writing-craft.md`、`world-bible.md`、`topic-selection.md`、`topic-research.md`、`title-naming.md`、`submission-format.md`、`story-structure.md`、`startup-guide.md`、`role-cards.md`、`review-scorecard.md`、`naming-rules.md`、`learnings.md`、`hit-craft.md`、`genre-and-fight-rules.md`、`dialogue-craft.md`、`commercial-craft.md`、`character-bible.md`、`canon-ledger.md` |
| `drama-studio/references/` | `storyboard-craft.md`、`startup-guide.md`、`shot-contract.md`、`role-cards.md`、`prompt-assembly.md`、`lip-sync.md`、`learnings.md`、`file-management.md`、`failure-atlas.md`、`external-platforms.md`、`asset-library.md` |
| `drama-studio/references/dimensions/` | `dim-action.md`、`dim-vfx.md`、`dim-style.md`、`dim-shot-size.md`、`dim-performance.md`、`dim-music.md`、`dim-lighting.md`、`dim-camera-move.md`、`dim-blocking.md`、`dim-audio.md` |
| `drama-studio/references/models/` | `seedance.md`、`minimax-hailuo.md`、`dreamina.md` |

- [ ] **Step 1: 读现场并记录双侧回归基线。**

在源工作区核对：

```powershell
git status --short --branch
git rev-parse HEAD
git worktree list
git diff --name-only
Get-FileHash -LiteralPath 'drama-studio/references/case-library/README.md','drama-studio/references/case-library/metadata.json'
python -B -m unittest discover -s tests -v
```

保护的两份文件哈希应分别为 `93A93D44FCD20145638446C0DE583265BEF4A41F6A59B27C044F0B77A153CE89`、`2CCCF5E27C5F4393745E623FE4CF181F4FE716CD4EEC06091EA85EA44F5EC2FA`。发生新变化时重新核差异，不恢复到旧哈希。安装入口哈希与设计 §2 比较。测试失败须列出名称及真实输出；保存迁移不是制造 RED 的理由。

- [ ] **Step 2: 建隔离工作区和只含公开候选的保护副本。**

按 using-git-worktrees 检查根、分支、忽略规则，再创建本任务分支。保护副本放本任务隔离目录内的 `.baseline-snapshot/`，先加忽略；仅对人工核过的具体 Markdown／Python 文件做逐文件备份。私有配置留在原地并核哈希，不读出正文、不复制进公共包。排除：

```gitignore
drama-crew/references/screenwriting-library.local.json
.baseline-snapshot/
.task-evidence/
```

既有 case-library 排除保持有效；不使用 `git add -A` 或整目录复制命令。不迁入 TXT 原始案例、媒体、Cookie、用户剧本、缓存或未核授权资料。

- [ ] **Step 3: 按文件差异保全规则，按行为合并四个脚本。**

读取本机新增文档的直接依赖，确认未把本地资料正文或绝对私有路径带入；保留可移植说明。规则以本机为准，脚本逐文件比较：

```powershell
git log -5 --oneline -- drama-crew/scripts/audit_screenplay.py
git log -5 --oneline -- drama-studio/scripts/dreamina_route.py
git diff --no-index -- drama-studio/scripts/dreamina_route.py C:/Users/Administrator/.codex/skills/drama-studio/scripts/dreamina_route.py
```

`diff --no-index` 的退出码 1 表示有差异，不是工具失败。主线关于空正文、单文件正文、长音轨、输入类型及帧／参考互斥的检查目的保留；如果既有断言绑定已退役措辞，先写新行为用例并观察失败，再替换断言，不能只删旧测试。无需修改的文件不制造差异。两包共用启动卡须为同一内容，但保留卡内 Crew 和 Studio 各自展示分支。

- [ ] **Step 4: 验证迁移不丢行为。**

```powershell
python -B -m unittest tests.test_drama_crew_screenplay_audit tests.test_dreamina_production_tools tests.test_startup_guide_distribution tests.test_case_library -v
python -B -m unittest discover -s tests -v
git diff --check
git diff --stat
```

分开记录已执行通过、失败、跳过。静态合同不能替代执行测试；尚未关闭的实际错误阻塞对应放行。迁移前后的已通过行为不得退化；不通过降低测试标准取得绿色。

- [ ] **Step 5: 明确路径暂存并提交基线。**

只暂存经 Step 3 核对的文件及必要回归测试；逐个检查 `git diff --cached`，确认无案例脏文件／私有资料。

```powershell
git diff --cached --name-only
git diff --cached --check
git commit -m "chore: preserve verified local Crew and Studio baseline"
```

### Task 2: 原文保真的八段、镜头解析和确定性检查

**Files:**
- Create: `drama-studio/scripts/validate_prompt.py`。
- Create: `tests/prompt_fixtures.py`、`tests/test_validate_prompt.py`。
- Modify: `drama-studio/references/prompt-assembly.md` §2、§3、§7（仅接口落点，先测后改）。

**Interfaces:**
- `parse_prompt(text: str) -> dict`：单 Clip，返回 `source_text`、`blocks`、`shots`、`speech`、`references`、`declared_duration_ms`、`declared_shot_count`、`issues`。
- Block：`number:int, title:str, start:int, end:int, line:int, text:str`；偏移是原字符串的字符偏移，行号从 1 起。
- Shot：`id:str, start_ms:int, end_ms:int, line:int`。只收顶层“分镜N／镜头N／SHOT N”行，不收内部动作节点。
- Speech：`id:str, speaker:str, kind:str, start_ms:int, end_ms:int, text:str, line:int`；`text` 保留原文，仅去掉明确的外围引用符号／字段分隔，不翻译、纠错或规范化标点。
- Reference：`handle:str, line:int`；已支持的编号媒体引用归一为 `image_1/video_1/audio_1` 等逻辑键，资产 ID 不自动视为媒体。
- `validate_prompt(text: str, *, duration: float | None = None, locked_speech: list[dict] | None = None, references: list[dict] | None = None, reference_root: Path | None = None) -> dict`：任务 2 先实现结构／时间线，任务 3 补对照检查。
- Report：`exit_code:int, coverage:list[dict], issues:list[dict], parsed:dict`。Coverage 项为 `check:str, state:checked|not_checked|not_applicable, reason:str`；Issue 项为 `code:str, severity:error|warning|unverified, line:int|None, message:str`。没有笼统 `verified=true`。
- `extract_prompt_clips(text: str) -> dict`：返回 `clips:list[dict], issues:list[dict]`。每个 Clip 为 `id:str|None, prompt:str, start:int, end:int, line:int`，严格取原文切片。仅支持单条纯正文或独立 `## Clip C01`／`## 片段 C01` 标题明确分隔的多条；边界含糊返回空 clips 和 `CLIP_BOUNDARY`，不猜截。

- [ ] **Step 1: 写原创小夹具和失败测试。**

`tests/prompt_fixtures.py`：

```python
HEADINGS = (
    "【一、主参考绑定】", "【二、视觉风格与媒介】",
    "【三、道具与人物状态】", "【四、场景与连续性】",
    "【五、对白与发声时间】", "【六、场内文字】",
    "【七、镜头与动作】", "【八、声音与拟音】",
)

def prompt_text(*, speech="无", shots=None):
    if shots is None:
        shots = "分镜1丨停留丨00:00-00:30丨连续拍摄丨固定机位，窗边空椅。"
    bodies = (
        "文字生成，无参考媒体。片段概述：空椅静候，1镜，目标30秒。",
        "已锁真人媒介，自然晨光。", "无道具交接。",
        "窗在北墙，室内晨间，机位不越门。", speech, "NONE",
        shots, "只有房间环境声，无额外配乐。",
    )
    return "\n".join(h + "\n" + b for h, b in zip(HEADINGS, bodies)) + "\n"
```

在新测试文件用现有 `tests.test_dreamina_production_tools.load_script` 动态加载检查器；缺脚本时由该 helper 给出明确 AssertionError，不以导入异常冒充功能 RED。

```python
import unittest
from tests.prompt_fixtures import HEADINGS, prompt_text
from tests.test_dreamina_production_tools import load_script

class PromptStructureTests(unittest.TestCase):
    def test_continuous_nodes_are_not_extra_shots(self):
        validator = load_script("validate_prompt")
        text = prompt_text(shots=(
            "分镜1丨停留丨00:00-00:30丨连续拍摄丨固定机位。\n"
            "  00:02-00:08：窗帘被风吹动。\n"
            "  00:08-00:20：椅背的影子缓慢移动。"
        ))
        result = validator.validate_prompt(text, duration=30)
        self.assertEqual(0, result["exit_code"])
        self.assertEqual(1, len(result["parsed"]["shots"]))
        self.assertEqual(text, result["parsed"]["source_text"])

    def test_missing_block_is_an_error_not_silent_partial_pass(self):
        validator = load_script("validate_prompt")
        result = validator.validate_prompt(
            prompt_text().replace(HEADINGS[5], ""), duration=30)
        self.assertEqual(1, result["exit_code"])
        self.assertIn("BLOCK_MISSING", [x["code"] for x in result["issues"]])
```

把以下手工预期写成独立 `subTest`，每新增一组先 RED 再 GREEN：

| 变体 | 预期 |
|---|---|
| 中文八段、英文八段；中文标题＋英文对白 | 合法结构，不改台词 |
| 同一标题重复、八段乱序、空段 | 退出 1，对应 BLOCK_DUPLICATE／BLOCK_ORDER／BLOCK_EMPTY |
| 全文“拍好一点”、不能识别的核心时间线 | 退出 2，具体未解析位置 |
| 两个 15 秒镜头，静止／硬切 | 合法，不强制不同镜长 |
| 0–8、9–30；0–8、7–30；3–30；0–31 | TIMELINE_GAP／OVERLAP／START／END |
| 倒序、负数、NaN、无穷、未闭合区间 | 不接受为合法时码，退出 1 或结构无法解析时 2 |
| 概述 3 镜实际 2 镜，概述 25 秒实际 30 秒 | SUMMARY_SHOTS／SUMMARY_DURATION |
| CRLF、尾换行、合法段前空白 | source_text 原样保留 |
| 单条纯正文；明确两条 Clip；无标题的重复八段或混有报告章节 | 分别返回 1／2／0 条可复制正文；最后一种 CLIP_BOUNDARY |

- [ ] **Step 2: 运行确认 RED。**

```powershell
python -B -m unittest tests.test_validate_prompt -v
```

先看测试失败来自缺少生产检查器／确定性行为，不是测试语法或错误路径。

- [ ] **Step 3: 逐组实现最小解析与报告。**

标题映射固定在检查器一处；中文严格对应上方八题，英文接受已记录的八项：

```python
ENGLISH_HEADINGS = (
    "MASTER REFERENCE BINDING",
    "VISUAL STYLE & MEDIUM MANDATE",
    "ANTI-GLITCH & PROP TRACKING RULES",
    "SCENE CONTEXT & CONTINUITY LOCK",
    "TIME-CODED DIALOGUE & AUDIO BUDGET",
    "ENVIRONMENTAL TEXT DEVICE",
    "SHOT BREAKDOWN & SPATIAL LOGIC",
    "AUDIO & FOLEY SPECIFICATIONS",
)
```

英文允许 `=== BLOCK 7: ... (30 SECONDS) ===` 包装；格式归一仅作用于标题识别，不能写回正文。若标题序号与职责不符，报告错误；未知结构不自动猜八段。

用 `splitlines(keepends=True)` 累计原文偏移，保证字节解码后的字符切片准确。识别顶层 Shot／中文分镜标题中的起止时码，秒数转整数毫秒，不用浮点累加或等分补时。

```python
from decimal import Decimal, InvalidOperation

def time_ms(value: str) -> int:
    value = value.strip().removesuffix("秒").removesuffix("s")
    parts = value.split(":")
    if len(parts) > 3 or not value:
        raise ValueError("invalid timecode")
    try:
        values = [Decimal(p) for p in parts]
    except InvalidOperation as exc:
        raise ValueError("invalid timecode") from exc
    if any(not v.is_finite() or v < 0 for v in values):
        raise ValueError("invalid timecode")
    if len(values) > 1 and any(v >= 60 for v in values[1:]):
        raise ValueError("invalid timecode")
    if any(v != v.to_integral_value() for v in values[:-1]):
        raise ValueError("fractional hours or minutes are invalid")
    seconds = Decimal(0)
    for part in values:
        seconds = seconds * 60 + part
    milliseconds = seconds * 1000
    if milliseconds != milliseconds.to_integral_value():
        raise ValueError("timecode precision exceeds milliseconds")
    return int(milliseconds)
```

`time_ms(value: str) -> int` 是本文件私有实现工具，不新增公共格式。连续区间检查逐段比较实际整数起止，首先要求 start=0、end>start，随后相邻 end=start，最后与有证据的总时长对齐。没有总时长对照时只核连续性并把总长核验标未核。

退出码优先级：输入／必要结构不可解析为 2；否则确定性错误为 1；否则 0。遗漏一个可识别段属于确定性结构错误 1；完全不是可识别的单条八段正文为 2。静止、硬切、无对白和 NONE 不作为错误。

正文提取复用相同标题识别：单条纯正文保留全部首尾空白；有明确 Clip 标题时仅剥离标题行，保留正文原始换行；出现不能归属的报告／分析章节、重复未标 Clip 或外层代码围栏则不给复制片段。检查器单次 CLI 不默取多条中的第一条。

- [ ] **Step 4: 跑测试并以真实输入核对旧格式边界。**

```powershell
python -B -m unittest tests.test_validate_prompt -v
python -B -m unittest discover -s tests -v
```

只用原创小夹具；既有案例仅在本地、已获准且可达时可作额外只读检查，不复制其全文进测试或包。旧四区块显示不支持／需人工复核，不强行转写旧稿。

- [ ] **Step 5: 同步原位检查说明并提交。**

§2 保留格式唯一主责；§3 清除“通用中文 vs 30秒专项”的双格式语句，时长差异只归模型能力；§7 将“通用【声音】/专项 Block 5”改为“第五段唯一逐字正文位”。只引用检查器入口、覆盖和未核范围，不把算法或报告混进最终 Prompt。

```powershell
git add drama-studio/scripts/validate_prompt.py tests/prompt_fixtures.py tests/test_validate_prompt.py drama-studio/references/prompt-assembly.md
git diff --cached --check
git commit -m "feat: validate prompt structure and clip timelines without rewriting"
```

### Task 3: 声音、参考、可选锁定对照及只读 CLI

**Files:** Modify `drama-studio/scripts/validate_prompt.py`、`tests/test_validate_prompt.py`、`tests/prompt_fixtures.py`。

**Interfaces:**
- Consumes: 任务 2 的 `parse_prompt`、`validate_prompt`、Report。
- `locked_speech`：按锁定顺序的 `{id, speaker, kind, text}` 字典列表；None=未提供，空列表=已明确没有逐字发声。
- `references`：实际明确输入的 `{handle, kind, path}` 列表，kind 为 image/video/audio/first_frame/last_frame；None=未提供，空列表=明确无参考。path 可选：没有本地文件只核映射并明确文件／上传状态未核。
- `load_context(path: Path) -> dict`：只读 JSON，对允许字段 `duration, locked_speech, references` 做类型检查；错误退出 2。可消费从原记录临时提取的对照，不写新真源；相对素材路径以对照文件父目录为基准。
- `main(argv: list[str] | None = None) -> int`：`python -B .../validate_prompt.py PROMPT --duration 30 --json`，可选 `--context-json FILE`；正文以 UTF-8-sig 解码，保留 CRLF；stdout 文本摘要或 JSON，读取失败 stderr 简述并返回 2。

- [ ] **Step 1: 写锁词保真、声音引用和证据缺失的失败测试。**

```python
class PromptEvidenceTests(unittest.TestCase):
    def test_changed_locked_utterance_is_rejected(self):
        validator = load_script("validate_prompt")
        text = prompt_text(speech=(
            "D01｜Maya｜对白｜00:02-00:05｜轻声｜Don't leave."
        ))
        result = validator.validate_prompt(
            text, duration=30,
            locked_speech=[{
                "id": "D01", "speaker": "Maya", "kind": "对白",
                "text": "Don't go.",
            }],
        )
        self.assertEqual(1, result["exit_code"])
        self.assertIn("LOCKED_SPEECH_TEXT", [i["code"] for i in result["issues"]])

    def test_missing_evidence_is_visible_without_fabricated_success(self):
        validator = load_script("validate_prompt")
        result = validator.validate_prompt(prompt_text(), duration=30)
        states = {c["check"]: c["state"] for c in result["coverage"]}
        self.assertEqual("not_checked", states["locked_speech"])
        self.assertEqual("not_checked", states["reference_inputs"])
        self.assertEqual(0, result["exit_code"])
```

增加实际变体及手工预期：

| 输入 | 预期 |
|---|---|
| D01 双定义；第七段引用不存在的 D09；声窗 28–32 秒 | SPEECH_DUPLICATE／SPEECH_UNDEFINED／SPEECH_WINDOW |
| D01、D02 同一句文本，实际是重复演唱 | 合法；按 ID 不按台词全文去重 |
| 合唱两个声部重叠、明确抢话 | 合法重叠；不以普通 WPM 否决 |
| 同一 ID 在第七段再次完整定义／复写逐字正文 | SPEECH_REDEFINED；只引用 ID 合法 |
| 锁定角色、类型或条目顺序被改 | 分别 LOCKED_SPEECH_SPEAKER／KIND／ORDER |
| 声音记录分行写 ID／说话人／正文 | 支持可明确识别的分行格式；不支持的行定位为未核，不吞掉 |
| `@[Image 1](image_1)`、`@图1` 与实际清单一致 | 映射核过；不冒称已上传／内容正确 |
| `C001`、`P001` 文字资产 ID，无媒体句柄 | 不当作缺图片 |
| 指定参考文件不存在、handle 不存在、类型明确不符 | REF_FILE_MISSING／REF_UNDEFINED／REF_KIND |
| 明确空清单却有 @图1；清单缺失却有 @图1 | 前者错误，后者未核；不能等价处理 |
| NaN 总时长、负时长、坏 JSON、错字段类型、无效 UTF-8 | 退出 2，指出输入问题，不显示 Traceback 代替诊断 |

CLI 使用 `subprocess.run([sys.executable, "-B", script, ...], capture_output=True, text=True, encoding="utf-8")`；TemporaryDirectory 内用小夹具，验证退出 0/1/2 和未写入任何报告／媒体。测试写文件仅作夹具，不当人工文件编辑工具。

- [ ] **Step 2: 跑新测试，确认目前缺少对照检查。**

```powershell
python -B -m unittest tests.test_validate_prompt.PromptEvidenceTests -v
```

- [ ] **Step 3: 实现真实对照，不从 Prompt 自证。**

先解析第五段定义、第七／八段显式声音 ID 引用、第一段实际媒体句柄。声音正文保留标点、大小写、数字和语言，允许重复文字的不同 ID。类型比较允许固定等义枚举（如“对白”与 dialogue），不将仅翻译类型标签误报为改变发声类型；发声者及原句仍与真实对照核对，不改写原文。未知外形的声音记录使相关覆盖标未核；要求锁词核对时不能只比较已解析子集后通过。

```python
def read_prompt_file(path: Path) -> str:
    with path.open("r", encoding="utf-8-sig", newline="") as stream:
        return stream.read()
```

`read_prompt_file(path: Path) -> str` 同时给任务 4 使用。BOM 是编码标记，不进模型正文；其余字符原样保留。对锁定数据按出现顺序逐条比较 id、speaker、kind、text。无对照是 not_checked，不用空列表伪装。环境文字不算说话，合唱重叠不算镜头重叠。

参考只读检查使用 `Path.resolve()`、`is_file()`，不下载、不上传、不自动读取媒体内容。只把有明确语法或清单支持的标识纳入媒体对照；未识别的 provider 专属句柄指明未核位置，不把“未识别”断言为“文件缺失”。

CLI 拒绝多 Clip 文件；需要逐条检查时先通过 `extract_prompt_clips` 确定边界。stdout 的报告永不拼接回 Prompt。缺锁词／输入证据的 0 必须列明缺证据项。

- [ ] **Step 4: 跑整个检查器及仓库回归。**

```powershell
python -B -m unittest tests.test_validate_prompt -v
python -B -m unittest discover -s tests -v
```

- [ ] **Step 5: 提交。**

```powershell
git add drama-studio/scripts/validate_prompt.py tests/test_validate_prompt.py tests/prompt_fixtures.py
git diff --cached --check
git commit -m "feat: report speech and reference checks with explicit evidence gaps"
```

### Task 4: Dreamina 文件预览接线，保留普通入口

**Files:** Modify `drama-studio/scripts/dreamina_route.py`、`tests/test_dreamina_production_tools.py`、`drama-studio/references/prompt-assembly.md` §7、`drama-studio/SKILL.md` 工具表和第 2 步自检位置。

**Interfaces:**
- Consumes: `read_prompt_file`、`validate_prompt`、`load_context`。
- CLI: `video --prompt TEXT` 与 `video --prompt-file PATH` 必须二选一；文件入口可选 `--context-json PATH`，普通入口不接受该对照参数。
- Produces: 普通入口保留原 `{"mode":"preview_only","command":[...]}`；文件入口增加 `validation:Report`，退出 1/2 时不产 command。仍绝不执行 `dreamina`。
- `build_video_command`、`build_image_command` 原有签名保持不变。

- [ ] **Step 1: 新增真实 CLI 回归。**

```python
def test_prompt_file_preserves_exact_decoded_text(self):
    from tests.prompt_fixtures import prompt_text
    with tempfile.TemporaryDirectory() as folder:
        path = Path(folder) / "英文片段.txt"
        text = "\r\n" + prompt_text().replace("\n", "\r\n") + "  "
        path.write_bytes(b"\xef\xbb\xbf" + text.encode("utf-8"))
        completed = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "dreamina_route.py"),
             "video", "--prompt-file", str(path), "--duration", "30"],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("preview_only", payload["mode"])
        self.assertIn("--prompt=" + text, payload["command"])
        self.assertEqual(0, payload["validation"]["exit_code"])
```

另测：互斥参数冲突／缺一；坏正文无 command；无参考普通短文本照常预览；image 命令不走八段；合法 first/last 仍走 frames2video；30 秒不降 15 秒；默认 720p 不变；从非 scripts 工作目录启动；现有 `load_script("dreamina_route")` 动态加载仍工作。

- [ ] **Step 2: 运行确认 RED。**

```powershell
python -B -m unittest tests.test_dreamina_production_tools -v
```

- [ ] **Step 3: 最小接线，原文只读一次。**

```python
def _require_prompt(prompt: str) -> str:
    if not prompt.strip():
        raise ValueError("prompt must not be empty")
    return prompt

# 在 video 子解析器创建后替换原 required --prompt：
prompt_source = video.add_mutually_exclusive_group(required=True)
prompt_source.add_argument("--prompt")
prompt_source.add_argument("--prompt-file", type=Path)
video.add_argument("--context-json", type=Path)
```

新模块采用脚本旁的绝对路径动态导入，避免测试加载时 sys.path 假设；只在文件分支加载，不影响图片和普通字符串：

```python
def _prompt_tools():
    import importlib.util
    path = Path(__file__).resolve().with_name("validate_prompt.py")
    spec = importlib.util.spec_from_file_location("studio_validate_prompt", path)
    if spec is None or spec.loader is None:
        raise ValueError("prompt checker is unavailable")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
```

文件分支 `read_prompt_file` 一次 → `validate_prompt` → exit_code 为 0 才将同一 text 传 `build_video_command`。报告与 command 分字段输出。CLI 实际指定的时长优先作为对照；额外 context 的相冲突值报告错误，不静默覆盖。素材清单与 CLI 实际输入按类型、顺序核对；没有可证的句柄映射时明记未核，不伪造映射。普通入口原有模式、参考上限与模型参数预检不删。

正式 Studio 第 2 步装配自检自动调用检查器；其他模型可独立调用。自检说明保持短句，正式正文仍只八段。工具缺失报告依赖问题，不能写成已执行。

- [ ] **Step 4: 运行回归并检查没有外部调用。**

```powershell
python -B -m unittest tests.test_dreamina_production_tools tests.test_validate_prompt -v
python -B -m unittest discover -s tests -v
git diff --check
```

- [ ] **Step 5: 提交明确文件。**

```powershell
git add drama-studio/scripts/dreamina_route.py tests/test_dreamina_production_tools.py drama-studio/references/prompt-assembly.md drama-studio/SKILL.md
git commit -m "feat: preview checked prompt files without altering their text"
```

### Task 5: 基于行为失败在原规则位补方法，验证 Crew 到 Studio

**Files:**
- Modify: Studio `references/dimensions/dim-action.md`、`dim-vfx.md`、`dim-blocking.md`、`dim-performance.md` 的原选择／修复表和时间轴段。
- Modify: Studio `references/asset-library.md` §3 身份区分门。
- Modify: Crew `references/genre-and-fight-rules.md` 的动作戏判断及魔法／变身／规则效果。
- Conditional modify only after demonstrated gap: Crew `references/writing-craft.md` §12；Studio `references/emotion-performance-library.md` 中命中的原情绪项；对应 `role-cards.md` 仅在原消费链确实不可达时修正。
- Test artifacts: 隔离工作区 `.task-evidence/production-methods/`，不进入 Skill 或公开提交；输入、原始回答和评审在原测试记录中各自分区。

**Interfaces:**
- Consumes: 已保存的本机原规则、用户原始任务、已锁事实与现有图板。
- Produces: 同一正常作品任务的 Crew 正文 → Studio 具体参考／动作／机位／声音／八段 Prompt；只读选择依据留测试记录，不混入正式正文。
- 方法行的职责：实际问题／可选主路径／所需已定事实／可观察结果。不是新增每镜字段清单。

- [ ] **Step 1: 先运行未补强规则的无技法暗示任务。**

使用 writing-skills，独立新上下文测试。先对下表正常任务各做一次基线筛查，只给必要本机规则和事实，不给审核答案。只对筛查确有失败、准备调整的行为做措辞微测：同场景 no-guidance 控制只移除拟补的方法指导，不移除安全／事实锁；每变体至少 5 次，独立上下文、同模型与推理档位。全部已正确的候选不新增规则。省 token 依靠窄任务与相关原文，不降为只问“该用什么方法”，也不把同一上下文的连续回答当独立样本。

| 测试输入（交给执行者） | 审核期待（不下传） |
|---|---|
| 现代训练，两人无伤对练；甲佯攻后退出，乙守住门口，不分输赢 | 动作可读、距离和回应成立；不加山崩、伤亡或胜负 |
| 超现实对抗；乙被击入石壁后借力返回，既定墙面受损，甲退至台阶 | 接触→受力→位移→回击与破坏延续；不自动降成普通切磋 |
| 四人围堵；甲守门，乙绕柱，丙被推到桌边，丁继续拦出口 | 群体焦点切换后其他人持续存在，不瞬移或凭空退场 |
| 护盾只偏折一次入射，绳印可被既定符号解除；领域对外无效 | 偏折不是抵消，解除有已定条件，内外边界可读 |
| 只知“主角施法解困”，规则和结果均未给，旁边普通对话已锁 | 只退依赖的事实缺口，其余可继续；不编造机制 |
| 单人绕镜面屏风去出口，已有一张正面空景 | 按真实视域缺口判断窄补／预演；不因只有一人免核 |
| 四人静坐闲聊，已有清楚全景及身份参考 | 复用，不因人数多强造俯视图或重画 |
| 已公开的父女，需要可辨共性；另组为师徒；第三组亲缘尚未揭示 | 三种条件分开；不固定相似比例，不让外观剧透 |
| 英文原句“Don't leave.”已锁；人物先喝一口再说，镜头只见背影 | 保留原句；排开喝水与发声，用可见反应，不写可见瞳孔 |
| 正面自然微笑说话；另段哽咽但仍能说完整原句 | 不机械禁止正常表演；留足声窗，不用时间估计认证口型 |

每份任务要求交短场景及其制作落点，不拍视频、不新建完整剧。记录真实失败原句和后果，区分缺方法、未读规则、执行错误和原任务事实不足。无失败的候选不加规则。

- [ ] **Step 2: 核读基线，选最小修订形态。**

逐一人工阅读被标记的原始回答，不能只数关键词或“已采用”声明。遗漏现有字段时修消费位置；选择错误时补条件；输出泛化时给具体制作落点；事实缺失时保留原局部退回，不用方法硬填。不改与本轮无关的情绪库条目。

- [ ] **Step 3: 在原表内实施已证实的补强。**

具体落位（写法按基线失败收窄）：

| 主责位 | 最小内容 |
|---|---|
| dim-action ②③ | 闪避／格挡／卸力按既定回应选择；重击写接触、身体受力、位移去向；追击承接距离和路线；群体保持非焦点参与者状态；终局按已定结果收束 |
| dim-vfx ②③ | 拦截、偏折、抵消各有不同落点；束缚及解除条件；领域边界内外；实体法器与派生效果的数量／控制／去向；收束不自动新增代价 |
| genre-and-fight-rules 原段 | 正文自然给出目标、实际应对、必要过程、阶段结果和已批准规则边界；不写制作参数，不以“激战／施法”替代承重事实 |
| dim-blocking ②③ | 用空间依赖和现有素材是否足够替换“≥2 人”风险门；复用→窄补反向视域／俯视→确需且获准的白模 |
| asset-library §3 | 关系已确认且本次需要表现才继承外观共性，同时保留个体区分与披露边界 |
| dim-performance ③④ | 先核可见部位；互斥口部动作与清晰发声错时／换镜而不改词；自然微笑／哽咽不一律排除 |

writing-craft §12 如已完整覆盖则保留，不抄整张制作表。表演共用库如已有对应条目仅引用，不新增 AU 百科。入口与消费端核可达，不新造制作经理／检查表／评分。

- [ ] **Step 4: 复测相同任务及相反条件。**

按 Step 1 相同条件重测，人工逐项核事实、方法和具体产物。5 次中出现不同解释时先修条件表达，不通过堆更多禁令压结果。修一组后复核另外一组，避免“打击反馈”误升级无伤训练或“空间补图”误伤普通多人对话。失败继续局部修复；仍不稳定就如实标未通过，不进入安装发布。

程序完整回归：

```powershell
python -B -m unittest discover -s tests -v
git diff --check
```

静态导航／格式检查只证明引用和文件可达，行为改进必须有原始回答证据。保留未改项及理由，不把样本写进运行时 references。

- [ ] **Step 5: 提交通过的原位规则修改。**

```powershell
git add drama-studio/references/dimensions/dim-action.md drama-studio/references/dimensions/dim-vfx.md drama-studio/references/dimensions/dim-blocking.md drama-studio/references/dimensions/dim-performance.md drama-studio/references/asset-library.md drama-crew/references/genre-and-fight-rules.md
git diff --cached --check
git commit -m "feat: ground action and performance methods in scene facts"
```

条件修改的其他文件只有实际改了且已验证才单独加到暂存；不暂存 .task-evidence。原始行为证据保留本地，最终报告给出实际范围而不虚称媒体通过。

## 计划自审与交接

规划自审：设计 §2／§8 由任务 1 和后续任务 9 承接；§5 由任务 2–4 承接；§4／§6 由任务 5 原位承接；§7 由后续任务 6–8 承接；§9 的五层验证均有对应步骤。已检查占位项、公共接口一致性和五项 Review Focus；这只表示计划自审，不表示产品测试通过。

- [ ] 用户审阅本计划和后续看板／整合计划，确认执行方式。
- [ ] 执行前按 using-git-worktrees 隔离，并重新核现场哈希。
- [ ] 每任务有实际 RED／GREEN／回归记录；任务 1 的既有行为保存如实记为迁移验证。
- [ ] 检查器公共接口与后续看板一致；无隐式网络、付费、修改正文或上传行为。
- [ ] 完成后进入 [只读看板与 main 整合计划](2026-09-19-readonly-board-and-main-integration.md)，不在本计划中提前更新安装包或推送。
