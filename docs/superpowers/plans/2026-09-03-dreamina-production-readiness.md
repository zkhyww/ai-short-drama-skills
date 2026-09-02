# Dreamina Production Readiness Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the blocked third-party Jimeng production path with official Dreamina routing and add a real, verified ffmpeg assembly path.

**Architecture:** Two small Python standard-library CLIs live under `drama-studio/scripts/`: one builds and validates official Dreamina commands without submitting them, and one normalizes and concatenates media with ffmpeg. Skill references consume these scripts and keep native Seedance audio primary, with external WAV/TTS only as an explicit fallback.

**Tech Stack:** Python 3 standard library, official `dreamina` CLI, ffmpeg/ffprobe, unittest, Markdown Skill resources.

**Spec:** `docs/superpowers/specs/2026-09-03-dreamina-production-readiness-design.md`

## Global Constraints

- Preserve `drama-crew` v6.17.9.
- Start from `drama-studio` v1.13.4 and retain its Seedance native audio behavior.
- Do not submit a paid Dreamina task in tests.
- Do not depend on `jimeng` or `xmst` in the default production path.
- Use official Dreamina CLI flags observed from local `--help`; runtime CLI/backend validation remains authoritative.

---

### Task 1: Official Dreamina command routing

**Files:**
- Create: `drama-studio/scripts/dreamina_route.py`
- Create: `tests/test_dreamina_production_tools.py`

**Interfaces:**
- Consumes: requested model, prompt, duration, resolution, ratio, and optional image/video/audio paths.
- Produces: `build_video_command(...) -> list[str]` and a JSON command preview CLI; it never submits generation itself.

- [x] Write tests for text-only, first-frame, mixed-reference, invalid duration, and forbidden legacy-engine output.
- [x] Run the focused tests and confirm failure because the module does not exist.
- [x] Implement the smallest validated command builder.
- [x] Re-run the focused tests and confirm they pass.

### Task 2: Real ffmpeg timeline assembly

**Files:**
- Create: `drama-studio/scripts/assemble_timeline.py`
- Modify: `tests/test_dreamina_production_tools.py`

**Interfaces:**
- Consumes: ordered clip paths, output path, target width/height/fps, and optional fallback audio path/mode.
- Produces: one normalized H.264/AAC MP4 with a video stream and audio stream.

- [x] Write an integration test that creates two clips with different dimensions/frame rates/audio states and expects one 9:16 playable output.
- [x] Run it and confirm failure because the assembler does not exist.
- [x] Implement normalization, concat, optional audio replace/mix, ffprobe checks, and precise temp cleanup.
- [x] Re-run the integration test and confirm it passes.

### Task 3: Skill contract and release update

**Files:**
- Modify: `drama-studio/SKILL.md`
- Modify: `drama-studio/references/external-platforms.md`
- Modify: `drama-studio/references/asset-library.md`
- Modify: `drama-studio/references/dimensions/dim-audio.md`
- Modify: `drama-studio/references/role-cards.md` if needed for script handoff
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `tests/test_drama_crew_dialogue_submission_contracts.py`

**Interfaces:**
- Consumes: the two executable scripts from Tasks 1-2.
- Produces: `drama-studio` v1.13.5 with official Dreamina as default and discoverable production instructions.

- [x] Replace legacy string-only tests with contracts for validator-safe frontmatter, Dreamina default routing, native-audio fallback boundaries, conditional realism, layout routing, and executable script references.
- [x] Run the contract tests and confirm the old documents fail the new expectations.
- [x] Surgically update the owning paragraphs and version records, removing superseded Jimeng/xmst claims.
- [x] Run focused and full tests until green.
- [x] Validate both skills, package both skills, run the ffmpeg smoke, check Markdown references/fences, and run `git diff --check`.
