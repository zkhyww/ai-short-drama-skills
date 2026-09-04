# DSH Useful Mechanisms Implementation Plan

**Goal:** Add the approved high-value DSH-derived decision mechanisms to the existing Crew and Studio contracts without expanding the workflow.

**Architecture:** Replace or enrich the current owner paragraphs in place, then wire only concise references into existing role dispatch templates and review gates. Contract tests protect both the new behavior and the agreed exclusions.

**Spec:** `docs/superpowers/specs/2026-09-05-dsh-useful-mechanisms-design.md`

## Constraints

- Keep all existing roles, phases, confirmation points, artifact names, schemas, and submission format.
- Do not copy DSH templates, examples, JSONL structures, dashboards, or its OS definition.
- Keep creative diagnostics conditional and evidence-based; do not add fixed per-episode quotas.
- Treat provider observations as project-local unless current provider documentation or runtime schema confirms them.

### Task 1: Add failing contract guards

**Files:**
- Modify: `tests/test_drama_crew_dialogue_submission_contracts.py`

- [x] Assert the Crew mechanism-truth/disclosure split, evidence-bound knowledge inference, mechanism exhaustion paths, uneven information density, delayed/open costs, and sound-dramaturgy concepts.
- [x] Assert the Studio asset states, identity decisions, Shot ID revision rules, frame-boundary semantics, single-copy spoken text, conditional continuation inputs, suspense permissions, and non-mechanical performance rules.
- [x] Assert exclusions: no DSH OS semantics, no fixed seven-beat emotion chain, and no new package Markdown files.
- [x] Run the focused contract suite and confirm it fails against v6.18.0/v1.13.7.

### Task 2: Implement Crew contract changes

**Files:**
- Modify: `drama-crew/references/world-bible.md`
- Modify: `drama-crew/references/writing-craft.md`
- Modify: `drama-crew/references/canon-ledger.md`
- Modify: `drama-crew/references/review-scorecard.md`
- Modify: `drama-crew/references/role-cards.md`
- Modify: `drama-crew/SKILL.md`

- [x] Enrich the current owner sections in place.
- [x] Wire concise, conditional instructions into existing Wen Yin, Qing Wu, and Ji Heng tasks.
- [x] Keep the existing 16 red-light categories and eight scoring dimensions.
- [x] Run the focused contract suite.

### Task 3: Implement Studio contract changes

**Files:**
- Modify: `drama-studio/references/asset-library.md`
- Modify: `drama-studio/references/shot-contract.md`
- Modify: `drama-studio/references/prompt-assembly.md`
- Modify: `drama-studio/references/storyboard-craft.md`
- Modify: `drama-studio/references/dimensions/dim-performance.md`
- Modify: `drama-studio/references/role-cards.md`
- Modify: `drama-studio/SKILL.md`

- [x] Add asset readiness and identity-state decisions in the existing asset contract.
- [x] Replace the over-broad Shot ID invalidation rule.
- [x] Add boundary, spoken-text, continuation, and suspense rules without new schemas.
- [x] Rewrite mechanical performance mandates as load-bearing or failure-evidence diagnostics.
- [x] Run the focused contract suite.

### Task 4: Version, document, verify, and finish

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `docs/使用说明.md` only if user-facing operation changes materially.

- [x] Bump Crew to `6.19.0` and Studio to `1.14.0`; add concise release notes.
- [x] Run all unit tests and both native Skill validators.
- [x] Check Markdown fences, local references, Markdown counts, and `git diff --check`.
- [x] Review the full diff for copied DSH content, secrets, private assets, and workflow expansion.
- [x] Perform documentation consistency and workspace-hygiene audits.
- [ ] Finish the feature branch according to the repository's approved local-main integration policy.
