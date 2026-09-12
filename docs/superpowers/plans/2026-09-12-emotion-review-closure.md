# 跨题材情感与审核闭环 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将已批准的跨题材情感方法、审核闭环和遗留冲突净化落到正式 Crew/Studio，验证后同步安装。

**Architecture:** 复用现有主责章节、派单字段与分层审核。顺序完成 Crew 和 Studio 两个可独立审查单元；测试样本仅留私有 QA，版本和同步在验证后收尾。

**Tech Stack:** Markdown Skill、Python unittest、Git；fresh-context 消费代理做语义测试。

**Spec:** `docs/superpowers/specs/2026-09-12-emotion-review-closure-design.md`

## Global Constraints

- 原规则位覆盖、合并或替换；移除被取代的冲突旧口径，不追加补丁章。
- 正式 Skill 只放通用方法与接口；创作样本、原始测试回答和对比证据保留在独立私有 QA。
- 全季人物无固定人数；既定核心人物同等叙事深度，按当前任务读取而非删除档案。
- 60–90 秒短集每集有成立的爽点或实质反转，默认约半分钟有效反馈；不精确卡秒、不要求每集独立感情场。
- `romance_axis=on|off` 只表示恋爱线；未定项用自然语言说明，不造枚举、不默认 off。
- 审核缺材料应说明实际已核范围与未核范围，不能默认无问题；青梧与季衡仍分层，不重复全量审计。
- 3.7 精修不新增证据、能力、关系、结果或其他承重事实；结构问题回剧情层。同批自动返修最多三次，未解决继续阻塞。
- 世界观、正典与制作资产按承重风险启用，继承既有事实，不以集数、预览档位或主配角名称免核。
- 保留模型与媒体验证、发布与预算授权边界；不因账号是仓库 owner 自动推送。
- 本轮不恢复双剧、不生成媒体、不关机、不合并或推送；同步已验证的正式安装副本时保留本机路由与私有绑定。

## 验证与证据位置

- 工作树：现有 `fix/crew-payoff-cast`；开工 `557066222b90ff84d293013a4efe27be73fde122`，clean。
- 工程基线已执行：`python -B -m unittest discover -s tests -v`，116/116，0 skipped。
- 旧消费失败：私有 `D:/视频/drama-skill-qa_20260912-payoff-cast/验收记录.md` 及五份最终版；不得改写历史结论。
- 本轮私有 QA：`D:/视频/drama-skill-qa_20260912-emotion-review/`；任务文件 `消费任务.md`、对照 `基线_01.md`–`基线_05.md`、新版 `新版_01.md`–`新版_05.md`，审核链与验收记录同目录。
- 不新增只 grep 规则语句的测试；语义靠真实消费，现有语法/运行合同靠既有测试。

### Task 1: Crew 情感、审核与遗留创作规则原位净化

**Files:**
- Modify: `drama-crew/SKILL.md`
- Modify: `drama-crew/references/story-structure.md`, `topic-selection.md`, `character-bible.md`, `genre-and-fight-rules.md`
- Modify: `drama-crew/references/role-cards.md`, `review-scorecard.md`, `title-naming.md`, `world-bible.md`, `submission-format.md`, `dialogue-craft.md`, `learnings.md`
- Related references only where a directly replaced rule is duplicated: `writing-craft.md`, `commercial-craft.md`, `canon-ledger.md`
- Evidence: existing `docs/validation/2026-09-12-crew-payoff-cast.md` (append accurate closure status within existing items, preserving historical evidence); new validation summary only after results exist.
- Test: existing `tests/test_drama_crew_dialogue_submission_contracts.py`; shared suite `tests/`; private behavior files above.

**Interfaces:**
- Consumes: approved spec; prior evidence; before-edit control output, supplied by controller.
- Produces: existing Wen/Qingwu/Jiheng templates with source-complete input and evidence-scoped review; general emotion uses story §2/§4, romance on additionally uses §3. Existing enums/columns and 3.7 boundary remain.

- [ ] Step 1: Read spec owner table and precise owner sections. Map each original paragraph to its replacement in task report. Read actual baseline/control outputs before changing runtime rules; do not assume every control fails.
- [ ] Step 2: Repair general emotional method in story §2/§4: for relationship scenes, character concern → meaningful treatment/choice → partner response → relationship or felt experience; for solitary stories, attachment/memory/desire and choices can carry the experience without inventing another person. No seven-emotions checklist or universal beat count. §3 supplies optional romantic development and ties romance-main episodes to their actual promised emotional return. Reuse relationship-concentration and character relationship fields; a calm segment can still carry the primary payoff. Topic/genre rules separate saturated packaging from useful emotional mechanisms; actual risk/overload, not genre labels or track count, decides.
- [ ] Step 3: In existing SKILL loading row/step and role-cards blocks, inject general relationship method for all genres, romance stages only when on. Remove the obsolete 呼吸列 mention. Qingwu consumes current batch text, outline, necessary previous facts and ledger/increment, not either/or text versus increment. Missing input yields scoped unverified items. Jiheng trusts only actually reviewed scope; unresolved review/functional defects remain blocking. Re-review reads revised text and relevant context against original finding, rather than author self-report or deletion of a false label.
- [ ] Step 4: Resolve all Crew rows in spec owner table, including title gates, risk-based world/ledger delivery, generic dialogue condemnation, fixed long-series progression and owner push policy. Keep existing file roles/anchors, and remove directly superseded duplicates. Do not replace concrete quality criteria with blanket “optional”. No new creative sample in runtime files.
- [ ] Step 5: Run focused `python -B -m unittest tests.test_drama_crew_dialogue_submission_contracts -v`, then full `python -B -m unittest discover -s tests -v` once before commit. If a test fails, identify real interface break versus obsolete change-detector; report before changing test design. Self-review `git diff --check` and exact changed files. Commit scoped Crew changes. Controller will run same-input new consumers and independent review; implementer does not spawn agents.

### Task 2: Studio 资产与表演口径原位净化

**Files:**
- Modify: `drama-studio/references/asset-library.md` §3
- Modify: `drama-studio/references/dimensions/dim-performance.md` §1–4
- Related: `drama-studio/references/role-cards.md`, `storyboard-craft.md`, `drama-studio/SKILL.md` only if directly duplicated removed rules conflict.
- Test: existing suite `tests/`; private same-input Studio cases in `消费任务.md`.

**Interfaces:**
- Consumes: locked character and relationship facts from Crew; existing asset IDs, four-block prompt schema and performance contract.
- Produces: risk-based identity anchors and performance design from existing stimulus/intent/partner; no change to JSON fields, IDs, model adapters, assets or production authorization.

- [ ] Step 1: Read approved spec, Studio main skill and exact owner paragraphs; read pre-edit Studio control output. Preserve actual identity/state distinctions and shot continuity.
- [ ] Step 2: Replace role-rank quantity quotas in asset §3 with relevant persistent features and current frame/continuity risk. Choose differentiators needed for this cast, not ≥3 axes/8–12 words/16-versus-8. Do not weaken confirmed main/supporting character identity or redefine all low-frequency cast as disposable.
- [ ] Step 3: Replace forced tics/named gait/mask/softening-target and strong-static/weak-fidget templates in performance original slots. Let existing character/scene evidence govern direct or indirect speech, actual gaze target, speed and response. A temporal/gaze clarification must not rewrite story relation into looking at the camera. Do not fabricate injuries, secrets, relationships or compulsory emotional costs.
- [ ] Step 4: Run focused applicable tests from existing suite, then full `python -B -m unittest discover -s tests -v` once. Check diff and local references. Commit scoped Studio change. Controller runs fresh-context equivalents and independent review.

### Task 3: 版本、验收状态与正式安装交付

**Files:**
- Modify: `drama-crew/SKILL.md`, `drama-studio/SKILL.md` version/history only.
- Modify: `CHANGELOG.md`, version-bearing `README.md` only as currently used.
- Create: `docs/validation/2026-09-12-emotion-review-closure.md` (methods, counts, failures and limitations; no private sample text).
- Outside Git after verification: installed Crew/Studio changed runtime files, original routing and metadata preserved; backups and receipts in private QA.

**Interfaces:**
- Consumes: approved Task 1/2 diffs, actual behavioral/repair-chain evidence and test results.
- Produces: Crew `6.22.0`, Studio `1.15.2`; honest per-layer validation record; frozen runtime commit for installation.

- [ ] Step 1: Controller executes five same-input new-rule consumers and manually reads every result, with the old-rule controls as comparison. Run actual independent audit → scoped revision → independent recheck on relevant failures; keep original outputs. Stop automatic fixing at existing limit, never mark residual load-bearing issues green.
- [ ] Step 2: Publish local validation summary with verified counts and exact version consumed; state what is not tested. Update versions and changelog without rewriting historical claims. Run full suite plus `git diff --check`; commit only intended files.
- [ ] Step 3: Controller requests whole-branch review package, closes findings according to SDD. Then back up changed installed files and apply exact runtime diffs using the approved file-edit mechanism with normal permission escalation. Preserve local description, Drama/JUTIAN router, private case binding, and unrelated metadata. Compare normalized runtime body of every manifest file to frozen source, record hashes and backup path.
- [ ] Step 4: Focused neat-freak consistency pass and workspace-hygiene Audit; retain evidence/worktree and all user assets. Report actual success, limitations, branch/install state. Do not merge, push or shut down.
