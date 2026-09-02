# Dialogue Performance and Submission Workflow Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a dialogue table-read refinement gate and a single-source production/submission output workflow to `drama-crew`.

**Architecture:** `dialogue-craft.md` remains the dialogue source of truth, while `SKILL.md` and `role-cards.md` route the new pass through existing roles. `submission-format.md` owns output-view transformation, with the Markdown production master remaining authoritative and DOCX remaining derived.

**Tech Stack:** Markdown Skill contracts, Python standard-library semantic regression tests, WorkBuddy `skill-creator` validator and packager.

**Spec:** `docs/superpowers/specs/2026-09-02-dialogue-submission-workflow-design.md`

## Global Constraints

- Modify only this repository; do not touch any external behavior-test script projects.
- Keep eight crew roles and the existing two user confirmation points.
- Do not modify `drama-studio`.
- Do not add a second AI-style score or copy the screenshot's fifteen-dimension rubric.
- Set `drama-crew` to v6.13.0 and keep the production master as the only content source of truth.

---

### Task 1: Contract regression tests

**Files:**
- Create: `tests/test_drama_crew_dialogue_submission_contracts.py`

**Interfaces:**
- Consumes: current Markdown contracts under `drama-crew/`.
- Produces: executable assertions for stage order, removed mechanical rules, dialogue gate, submission derivation and version/file-count synchronization.

- [ ] **Step 1: Write the failing semantic tests**

Use `unittest` and `pathlib` to assert that v6.13.0, stage 3.7, the role templates, `submission-format.md`, README file count, and new dialogue wording exist; assert that the old absolute phrases `每句台词在说话的同时必须至少干一件活`, `每句台词之后，至少发生一项变化`, `至少 1 次位置位移`, and `沉默时必须有小动作` are absent from active contracts.

- [ ] **Step 2: Run tests to verify RED**

Run: `python -B -m unittest tests.test_drama_crew_dialogue_submission_contracts -v`

Expected: failures for missing v6.13.0, missing stage 3.7/output reference, and still-present mechanical dialogue phrases.

### Task 2: Dialogue source of truth and role routing

**Files:**
- Modify: `drama-crew/references/dialogue-craft.md`
- Modify: `drama-crew/references/writing-craft.md`
- Modify: `drama-crew/references/commercial-craft.md`
- Modify: `drama-crew/references/role-cards.md`
- Modify: `drama-crew/references/review-scorecard.md`
- Modify: `drama-crew/SKILL.md`

**Interfaces:**
- Consumes: locked script facts, current text, Qingwu conflict findings and `dialogue-craft.md` table-read contract.
- Produces: a complete revised script, exact change table, changed-scene-only continuity recheck and a blocking dialogue-hardness gate inside the existing dialogue dimension.

- [ ] **Step 1: Replace sentence-level hard rules at the owner sources**

Make one breath/one intention and conversation beat the units of judgment. Convert word counts, quote counts, movement and micro-action requirements into contextual diagnostics, and preserve interruptions, false starts, evasion and silence when they arise from character pressure.

- [ ] **Step 2: Add the table-read refinement contract**

Add a dedicated section to `dialogue-craft.md` defining story locks, performance axes, professional-information distribution, local-only editing, full revised output and an exact before/after change table.

- [ ] **Step 3: Wire existing roles**

Add a second Wen Yin dispatch template for stage 3.7, a changed-scenes-only Qing Wu recheck template, and Ji Heng's blocking hardness gate. Update the main flow so stage 3.7 runs between continuity checking and compliance.

- [ ] **Step 4: Run semantic tests to verify the dialogue group is GREEN**

Run: `python -B -m unittest tests.test_drama_crew_dialogue_submission_contracts -v`

Expected: dialogue and routing assertions pass; output/version assertions may remain failing until Task 3.

### Task 3: Dual output contract and public documentation

**Files:**
- Create: `drama-crew/references/submission-format.md`
- Modify: `drama-crew/SKILL.md`
- Modify: `README.md`
- Modify: `docs/使用说明.md`
- Modify: `docs/特点与架构.md`
- Modify: `CHANGELOG.md`

**Interfaces:**
- Consumes: locked `完整制作母稿.md` and its `script_rev`/SHA-256.
- Produces: a derived `《剧名》_投稿阅读稿.docx` without internal workflow fields or fabricated approval data.

- [ ] **Step 1: Add the output-view source of truth**

Define trigger rules, field keep/remove mapping, generic DOCX layout, per-episode page breaks, approval-field exclusion and source-version provenance in `submission-format.md`.

- [ ] **Step 2: Wire 4A and 4B**

Split final delivery into production master and derived submission view. Keep the production master as the only input to `drama-studio`, and require content edits to return to the master before re-export.

- [ ] **Step 3: Synchronize version and team docs**

Set v6.13.0, change the crew Markdown count to 18, describe the new behavior in README/use/architecture docs, and add a focused CHANGELOG entry.

- [ ] **Step 4: Run semantic tests to verify GREEN**

Run: `python -B -m unittest tests.test_drama_crew_dialogue_submission_contracts -v`

Expected: all tests pass.

### Task 4: Full verification and packaging

**Files:**
- Verify only; no new production files expected.

**Interfaces:**
- Consumes: completed branch tree.
- Produces: validator, reference, fence, package and sensitive-path evidence.

- [ ] **Step 1: Run native validators**

Run both WorkBuddy `quick_validate.py` commands from `docs/团队协作.md`.

- [ ] **Step 2: Run structural checks**

Run the semantic unittest, a Markdown fence parity scan, a local Markdown-link resolution scan, and `git diff --check`.

- [ ] **Step 3: Package to an external temporary directory**

Use the WorkBuddy `package_skill.py` to package both skills, inspect archive member counts and exactly one `SKILL.md` per package, then remove each temporary file by exact path.

- [ ] **Step 4: Audit scope and secrets**

Confirm `git diff --name-only` contains no `drama-studio` or `drama-night-tests` paths, and scan changed files for credentials, private absolute paths and generated artifacts.

- [ ] **Step 5: Commit the verified implementation**

Run `git add` on the exact changed files and commit with `feat: add dialogue refinement and submission workflow`.
