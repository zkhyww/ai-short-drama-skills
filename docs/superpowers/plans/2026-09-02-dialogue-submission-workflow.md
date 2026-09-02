# Submission and Visual Contract Correction Plan

> **Execution:** Follow `superpowers:executing-plans`, `superpowers:test-driven-development`, `superpowers:verification-before-completion`, and `superpowers:finishing-a-development-branch`. This task is executed inline because no user-authorized subagent delegation is in scope.

**Goal:** Correct the v6.17.0 submission-layout and cross-package visual-anchor contracts without modifying the three existing scripts.

**Architecture:** `submission-format.md` remains the source of truth for the production/submission views. `character-bible.md` owns crew-side visual facts; `drama-studio/references/asset-library.md` owns production-level character anchors. Runtime templates must reproduce those owner contracts without inventing a parallel rule.

**Target versions:** `drama-crew` v6.17.1 and `drama-studio` v1.11.2.

**Spec:** `docs/superpowers/specs/2026-09-02-dialogue-submission-workflow-design.md`

## Constraints

- Keep the eight crew roles, six studio roles, and existing two user confirmation points.
- Do not add files, roles, workflow gates, scoring dimensions, or user prompts.
- Do not edit the three completed behavior-test scripts.
- Keep the Markdown production master as the only content source of truth.
- Limit studio changes to the visual-anchor intake contract and its version/documentation wiring.

## Task 1: Add contract counterexample tests

**File:** `tests/test_drama_crew_dialogue_submission_contracts.py`

- [x] Assert that outward-reading intent with an available DOCX tool selects DOCX and Markdown is only a fallback.
- [x] Assert the reader-facing section order and that selection analysis is optional.
- [x] Assert crew visual facts and studio production-anchor responsibilities are compatible.
- [x] Assert red-light checks #14 and #15 use different evidence.
- [x] Assert silence, OOC, and human-voice guidance do not become fixed-count failure rules.
- [x] Assert master-content changes synchronize affected front matter inside one `script_rev`.
- [x] Run the focused test and observe RED before production edits.

## Task 2: Correct owner contracts and runtime templates

**Files:**

- `drama-crew/references/submission-format.md`
- `drama-crew/references/character-bible.md`
- `drama-crew/references/dialogue-craft.md`
- `drama-crew/references/writing-craft.md`
- `drama-crew/references/role-cards.md`
- `drama-crew/SKILL.md`
- `drama-studio/references/asset-library.md`
- `drama-studio/references/role-cards.md`
- `drama-studio/SKILL.md`

- [x] Make Markdown authoritative for the internal master only; select DOCX by default for outward reading when tools are available.
- [x] Order submission sections as cover, logline, synopsis, characters, broad outline, episode outline, script.
- [x] Move selection analysis out of the default script body and into an optional planning attachment.
- [x] Require all affected master sections to stay synchronized inside one revision.
- [x] Treat the crew visual line as immutable story facts, then let studio add labeled production design and pass the existing differentiation gate.
- [x] Separate #14 duration-pattern evidence from #15 deus-ex-machina evidence.
- [x] Replace fixed-count silence/OOC/humanization rules with causal diagnostics.

## Task 3: Synchronize release and public documentation

**Files:**

- `README.md`
- `CHANGELOG.md`
- `docs/使用说明.md`
- `docs/特点与架构.md`
- this plan and its linked design spec

- [x] Publish v6.17.1 / v1.11.2 consistently.
- [x] Document carrier routing, section order, single-source synchronization, and visual ownership.
- [x] Remove active overclaims that the team layout is a universal industry standard or that one crew line is a complete drawing specification.

## Task 4: Verify

- [x] Run the focused semantic contract suite and the full test suite.
- [x] Check Markdown fence parity and local Markdown references.
- [x] Run `git diff --check`, inspect the complete diff, and scan changed files for credentials and private paths.
- [x] Try the native validator/package flow and record the exact limitation: the available validator uses Windows-default decoding and rejects WorkBuddy's top-level `version`; no `package_skill.py` exists in the installed skill roots.
- [x] Audit the scoped worktree with `workspace-hygiene`; do not delete protected or unrelated files.

## Task 5: Finish the branch

- [ ] Commit the exact verified files on `fix/v6.17.1-submission-visual-contracts`.
- [ ] Offer the user the three `finishing-a-development-branch` choices: local merge, push/PR, or keep the branch.
