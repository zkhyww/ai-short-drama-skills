# Script Revision Quality Gates Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Prevent the failure modes proven by the three 60-episode tests, enforce separate production/submission outputs, and then revise all three projects against the corrected `drama-crew` contract.

**Architecture:** Add a deterministic Markdown screenplay preflight tool for facts a program can judge, while keeping aesthetic review in the existing Wen Yin/Qing Wu/Ji Heng roles. Update the duration, dialogue, continuity, submission, and scoring contracts so numeric budgets are diagnostic rather than padding targets. Only after the new skill passes regression and packaging checks, dispatch precise revision packets to the three original project threads.

**Tech Stack:** Python 3 standard library, `unittest`, Markdown contracts, PowerShell/Git, Codex task coordination.

**Spec:** `docs/superpowers/specs/2026-09-03-script-revision-quality-gates-design.md`

## Global Constraints

- Production output and standard submission output are separate content views derived from one locked production master.
- `《剧名》_标准投稿阅读稿.md` is mandatory for a full-project submission deliverable; DOCX is optional and generated only when explicitly requested.
- `350–500` is a diagnostic band for a 90–120 second live-action episode, never a lower-bound padding target.
- Automated checks may block deterministic errors but must not auto-rewrite dialogue or assign aesthetic scores.
- Existing story direction, major relationships, first-season closure, and next-season suspense in the three projects remain unchanged.
- No production approval until targeted revision, representative read timing, and independent reacceptance are complete.

---

### Task 1: Add the deterministic screenplay preflight tool

**Files:**
- Create: `drama-crew/scripts/audit_screenplay.py`
- Create: `tests/test_drama_crew_screenplay_audit.py`

**Interfaces:**
- Produces: `audit_master(text: str, expected_episodes: int | None) -> AuditResult`
- Produces: `audit_submission(text: str, expected_episodes: int | None) -> AuditResult`
- Produces: `audit_pair(master_text: str, submission_text: str, expected_episodes: int | None) -> AuditResult`
- Produces CLI: `python drama-crew/scripts/audit_screenplay.py --master <path> --submission <path> --expected-episodes 60 [--json]`
- `AuditResult.blocking` controls exit code: `0` when no blocking findings, `1` otherwise.

- [ ] **Step 1: Write failing unit tests for deterministic failures**

Create synthetic fixtures, not copies of private project scripts. Tests must establish:

```python
def test_submission_rejects_empty_episode_outline_and_internal_fields():
    result = audit_submission(INVALID_SUBMISSION, expected_episodes=2)
    codes = {item.code for item in result.findings if item.severity == "error"}
    assert "EMPTY_EPISODE_OUTLINE" in codes
    assert "INTERNAL_FIELD_IN_SUBMISSION" in codes

def test_submission_rejects_beat_markup_duplicate_people_and_visible_action_hint():
    result = audit_submission(INVALID_FORMAT, expected_episodes=1)
    codes = {item.code for item in result.findings if item.severity == "error"}
    assert {"PRODUCTION_BEAT_IN_SUBMISSION", "DUPLICATE_PERSON", "VISIBLE_ACTION_IN_DIALOGUE_HINT"} <= codes

def test_master_rejects_invalid_romance_axis():
    result = audit_master("romance_axis=weak\n# 第 1 集", expected_episodes=1)
    assert any(item.code == "INVALID_ROMANCE_AXIS" for item in result.findings)

def test_non_spoken_writing_action_is_not_counted_as_dialogue():
    result = audit_submission(WRITING_ACTION_SAMPLE, expected_episodes=1)
    assert result.metrics["spoken_chars"] == len("我不同意")

def test_valid_pair_passes_and_reports_only_spoken_time_range():
    result = audit_pair(VALID_MASTER, VALID_SUBMISSION, expected_episodes=1)
    assert not result.blocking
    assert result.metrics["spoken_seconds_at_3_5_cps"] >= result.metrics["spoken_seconds_at_4_5_cps"]
    assert "estimated_total_runtime" not in result.metrics
```

- [ ] **Step 2: Run the new test file and verify RED**

Run: `python -m unittest tests.test_drama_crew_screenplay_audit -v`

Expected: import failure because `drama-crew/scripts/audit_screenplay.py` does not exist.

- [ ] **Step 3: Implement the smallest read-only auditor**

Use Python standard library only. Define immutable findings and aggregate metrics:

```python
@dataclass(frozen=True)
class Finding:
    severity: Literal["error", "warning"]
    code: str
    line: int
    message: str

@dataclass
class AuditResult:
    findings: list[Finding]
    metrics: dict[str, int | float | dict[str, int]]

    @property
    def blocking(self) -> bool:
        return any(item.severity == "error" for item in self.findings)
```

The submission auditor must inspect the `## 正文` body separately from reader-facing front matter. It must block empty/missing required sections, wrong episode count, internal fields, production beat markup, duplicate names, nonstandard speaker-side annotations, and visible-action hints. It must emit warnings for ten-or-more dialogue lines without a new action, repeated action/time lines, and high-frequency institutional terms. The master auditor must block any `romance_axis` value other than `on|off`.

Spoken-character counting must accept only dialogue-shaped lines, remove voice/performance parentheses after the colon, count `OS/VO`, and exclude speaker-side non-speaking annotations such as `（写字）`, `（打字）`, `（举牌）`, `（字幕）`, and `（手语）`. It may report pure spoken duration at 3.5 and 4.5 characters/second; it must not invent total runtime.

- [ ] **Step 4: Run unit tests and verify GREEN**

Run: `python -m unittest tests.test_drama_crew_screenplay_audit -v`

Expected: all new tests pass.

- [ ] **Step 5: Commit the auditor task**

```powershell
git add drama-crew/scripts/audit_screenplay.py tests/test_drama_crew_screenplay_audit.py
git commit -m "feat: add screenplay submission preflight"
```

---

### Task 2: Correct the duration, dialogue, continuity, and review contracts

**Files:**
- Modify: `drama-crew/references/commercial-craft.md`
- Modify: `drama-crew/references/dialogue-craft.md`
- Modify: `drama-crew/references/writing-craft.md`
- Modify: `drama-crew/references/canon-ledger.md`
- Modify: `drama-crew/references/review-scorecard.md`
- Modify: `drama-crew/references/role-cards.md`
- Modify: `tests/test_drama_crew_dialogue_submission_contracts.py`

**Interfaces:**
- Consumes: `audit_screenplay.py` CLI from Task 1.
- Produces: one duration evidence vocabulary shared by writer, canon checker, and final reviewer.
- Produces: two-tier dialogue review covering load-bearing scenes and ordinary/mid-series scenes.

- [ ] **Step 1: Add failing contract assertions**

Add assertions that require the following exact concepts and reject the obsolete behavior:

```python
self.assertIn("诊断区间，不是逐集最低配额", self.commercial)
self.assertIn("禁止为补足字数增加同义解释或程序话术", self.commercial)
self.assertIn("逐项动作/停顿估时", self.commercial)
self.assertIn("只能标为估算", self.commercial)
self.assertNotIn("净台词按 350–500 字收", self.commercial)
self.assertIn("普通中段、低冲突或报告类场景", self.scorecard)
self.assertIn("语义功能重复", self.dialogue)
self.assertIn("显式时间锚", self.ledger)
self.assertIn("预检失败不得进入评分放行", self.scorecard)
```

- [ ] **Step 2: Run the affected contract tests and verify RED**

Run: `python -m unittest tests.test_drama_crew_dialogue_submission_contracts -v`

Expected: the newly added contract test fails on missing new wording or obsolete hard-band wording.

- [ ] **Step 3: Replace the owner paragraphs rather than append patches**

In `commercial-craft.md` §5, keep the 90–120 second and 3.5–4.5 characters/second references as planning inputs. Rewrite the 350–500 rule as a diagnostic band, prohibit padding, and require per-episode columns for spoken characters, speech rate, spoken seconds, action/pause estimates, transition estimates, total estimate, and evidence state. Explicitly forbid fixed-per-action and fixed-per-episode additions as final evidence.

In `dialogue-craft.md`, add semantic-function repetition and padding detection to the existing table-read/refinement owner section. Delete-only testing asks whether a line changes choice, relationship, evidence, pressure, or consequence; unchanged lines are candidates, not automatic deletions.

In `writing-craft.md`, replace shorthand that still presents `350–500` as a per-episode requirement with a direct reference to the evidence-based diagnostic contract in `commercial-craft.md`.

In `canon-ledger.md`, add a cross-episode explicit-time-anchor check so identical clock/date lines must agree with ledger progression; repeated wording alone is not the issue, frozen story time is.

In `review-scorecard.md`, extend the dialogue hardness gate to sample ordinary mid-series/low-conflict/report scenes as well as load-bearing scenes. Formatting preflight, invalid enums, hard continuity conflicts, fake measured runtime, or an unpassed dialogue gate must block `review_state=reviewed` and scoring release.

Synchronize the same responsibilities and exact audit command into the Qing Wu and Ji Heng prompts in `role-cards.md`.

- [ ] **Step 4: Run the affected contract tests and verify GREEN**

Run: `python -m unittest tests.test_drama_crew_dialogue_submission_contracts -v`

Expected: all contract tests pass.

- [ ] **Step 5: Commit the contract correction**

```powershell
git add drama-crew/references/commercial-craft.md drama-crew/references/dialogue-craft.md drama-crew/references/canon-ledger.md drama-crew/references/review-scorecard.md drama-crew/references/role-cards.md tests/test_drama_crew_dialogue_submission_contracts.py
git commit -m "fix: make screenplay quality gates evidence based"
```

---

### Task 3: Enforce separate production and standard-submission deliverables

**Files:**
- Modify: `drama-crew/SKILL.md`
- Modify: `drama-crew/references/submission-format.md`
- Modify: `drama-crew/references/role-cards.md`
- Modify: `tests/test_drama_crew_dialogue_submission_contracts.py`

**Interfaces:**
- Consumes: preflight CLI from Task 1.
- Produces: `{项目名}_完整制作母稿.md` and `《剧名》_标准投稿阅读稿.md` as distinct files.
- Produces: optional DOCX derived from the standard submission Markdown only when explicitly requested.

- [ ] **Step 1: Add failing dual-output contract assertions**

```python
for contract in (self.skill, self.submission, self.roles):
    self.assertIn("《剧名》_标准投稿阅读稿.md", contract)
    self.assertIn("两个不同文件", contract)
self.assertIn("DOCX 仅在用户或接收方明确要求时生成", self.submission)
self.assertIn("预检退出码为 0", self.submission)
self.assertIn("逐集集纲非空且覆盖到最后一集", self.submission)
self.assertNotIn("DOCX 工具可用时默认交付 DOCX", self.submission)
```

- [ ] **Step 2: Run the affected contract tests and verify RED**

Run: `python -m unittest tests.test_drama_crew_dialogue_submission_contracts -v`

Expected: failure because current contracts still make DOCX the default and do not require the new named submission Markdown file.

- [ ] **Step 3: Update the single owner contract and all dispatch points**

In `submission-format.md`, make the two content views mandatory for a full project that includes submission delivery. Keep the production master as the only content source; make standard-submission Markdown the required derived reading view and DOCX an opt-in wrapper. Add an exact preflight command and make exit code zero a delivery condition. The required structure check must explicitly say the episode outline is nonempty and covers the final episode.

In `SKILL.md` steps 4A/4B and `role-cards.md`, mirror the two names and forbid direct independent editing of the submission file. All revisions occur in the master, then the standard submission view is regenerated and audited.

- [ ] **Step 4: Run the affected contract tests and verify GREEN**

Run: `python -m unittest tests.test_drama_crew_dialogue_submission_contracts -v`

Expected: all contract tests pass.

- [ ] **Step 5: Commit the dual-output contract**

```powershell
git add drama-crew/SKILL.md drama-crew/references/submission-format.md drama-crew/references/role-cards.md tests/test_drama_crew_dialogue_submission_contracts.py
git commit -m "fix: enforce separate production and submission views"
```

---

### Task 4: Version, document, validate, and publish the corrected skill

**Files:**
- Modify: `drama-crew/SKILL.md`
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/使用说明.md`

**Interfaces:**
- Produces: `drama-crew` v6.18.0.
- Produces: an installed copy identical to the repository source.

- [ ] **Step 1: Bump and document v6.18.0**

Describe the deterministic preflight, evidence-based runtime, two-tier dialogue review, time-anchor continuity check, and mandatory production/submission split. Document the command:

```powershell
python drama-crew/scripts/audit_screenplay.py --master <制作母稿.md> --submission <标准投稿阅读稿.md> --expected-episodes 60
```

- [ ] **Step 2: Run focused and full regression**

Run:

```powershell
python -m unittest tests.test_drama_crew_screenplay_audit -v
python -m unittest tests.test_drama_crew_dialogue_submission_contracts -v
python -m unittest discover -s tests -v
```

Expected: all tests pass.

- [ ] **Step 3: Run structural validation**

Run Markdown fence parity, local Markdown reference resolution, `git diff --check`, and any repository-provided native skill validator/package command. Confirm no secrets or private project scripts are staged.

- [ ] **Step 4: Sync the installed skill and verify byte equality**

Copy only changed skill files plus the new auditor to the active local installed-skill root when that root exists. Compare hashes or file content for every synced path; do not copy private behavior-test projects into the public repository or installed skill.

- [ ] **Step 5: Commit and push the release**

```powershell
git add drama-crew/SKILL.md README.md CHANGELOG.md docs/使用说明.md
git commit -m "release: drama-crew v6.18.0"
git push origin main
```

Expected: remote `main` contains v6.18.0 and CI succeeds.

---

### Task 5: Dispatch and independently reaccept the three targeted revisions

**Files:**
- Modify only the three private behavior-test project directories assigned by the controller; keep their local paths outside this public repository.

**Interfaces:**
- Consumes: installed `drama-crew` v6.18.0 and its preflight command.
- Produces per project: revised production master, revised standard submission Markdown, synchronized outline/ledger/revision report, and representative read-timing evidence.

- [ ] **Step 1: Send project-specific revision packets to the original tasks**

Use the three existing private project tasks supplied by the controller, not new windows. Keep task IDs, project titles, and local paths in the private execution handoff rather than this public plan.

Each packet must require work only in its own project directory, preservation of unrelated files, master-first editing, regenerated standard submission view, the v6.18.0 preflight, and a final callback containing exact files, audit result, timing evidence, unresolved risks, and score evidence.

- [ ] **Step 2: Wait for all three projects without polling commentary**

Use bounded task waits. Do not treat a controller’s own score or “completed” message as acceptance.

- [ ] **Step 3: Independently run the preflight and targeted semantic review**

For each project, rerun the auditor locally; inspect every previously identified episode plus representative ordinary middle episodes. Compare production master and standard submission view, verify ledger/outline synchronization, and check that no fact, first-season closure, or sequel hook drifted.

- [ ] **Step 4: Return precise fixes when evidence remains**

Send a narrow follow-up to the same project task with locations and expected corrections. Do not restart the whole project or let a task self-approve by raising its numeric score.

- [ ] **Step 5: Record final acceptance state**

Only mark a project production-ready when deterministic preflight is clean, known defects are closed, representative read timing is credible, and independent scoring reaches the contract threshold without red-line caps. Otherwise report the exact remaining blocker.
