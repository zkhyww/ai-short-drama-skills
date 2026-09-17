# Production defaults and production-learning implementation plan

> For agentic workers: use superpowers:subagent-driven-development task by task. Implementation is authorized by the user's accepted twelve-point assessment and explicit default-setting instruction. Do not ask for the same approval again.

**Goal:** Apply the approved production lessons to the existing Crew/Studio entry points and tools, including default 720p video and Seedance 2.5 for a single requested clip longer than 15 seconds.

**Architecture:** Keep Crew responsible for story and Studio for production. Amend existing owner paragraphs; do not add roles, approval gates, mandatory reports, duplicate indexes, or project-specific story material. Source and installed skills are intentionally different versions: make narrow parallel changes, never overwrite the installed packages with the older source packages.

**Tech stack:** Markdown skill references; Python stdlib routing/ffmpeg helpers and unittest; local ffmpeg.

**Spec:** The approved requirements below are the binding specification for this bounded change.

## Approved requirements and global constraints

- Model/resolution priority: explicit current user instruction, then approved project setting, then compatible defaults. Default video resolution is 720p. In Dreamina, an unspecified model uses seedance2.0fast_vip for an individual 4–15 second clip and seedance2.5 for an individual >15–30 second clip. Total episode duration is not individual clip duration. Unsupported duration or an explicit incompatible model is reported, never silently changed or split. No new paid calls.
- Add a brand-story application to the existing brief: audience, business purpose, visible/emotional ending payoff, brand role, excluded commercial content. Do not auto-apply IAA/IAP to brand promotion or assert distribution results without data.
- Strengthen the current revision entry point: inspect the affected upstream/downstream selected footage after a change of identity state, makeup, clothes, emotion, dialogue, blocking, props or exit direction; keep unaffected accepted material.
- Make the existing actual command/parameters the production facts; compare model, duration, resolution, ordered references with the frozen request. Distinguish estimate, provider charge and account balance; stop dependent batch on unexplained material price drift. Preserve the already-scoped optional user-requested attachment rules, without guaranteed discounts.
- Add direct-assembly scope: approved material + explicit request for only trimming/concatenation retains audio and performs required normalization/export, without unsolicited captions, music, external semantic review or paid work. Do not claim skipped review passed. Standard and explicitly commissioned full review remain available.
- Diagnose low resolution vs motion smear/ghosting before batch upscaling; test representative required views, redraw only actual gaps and preserve known structure/large text. Distinguish reconstruction from factual recovery.
- Reinforce existing assets: one independent identity board per needed character, same-ID state variants only for actual gaps, reusable approved scenes, missing-only combined boards with no obligatory keyframes, topology before added viewpoints, empty architectural reference distinct from live background activity.
- Keep natural dialogue fact/permission/modality boundaries. Estimate speech using the actual language's units and compatible actions; generated audio and selected clip time become editing evidence, not prompt timing. ASR/frame inspection has limited evidentiary scope.
- Maintain Shot/Clip/episode separation; choose generation spans by spatial/action dependency and actual capability. No universal hard cut count or contact-avoidance rule. Make promised changes visible at the intended screen size with consistent identity and motivated light.
- Persist minimal actual selected-source/in/out/order information in the existing timeline rather than parallel ledgers. Support that input directly in the assembly helper; preserve original media and legacy callers.
- No editing the unrelated case-library working changes. No remote push/publication, no client-specific content in distributed skills. Back up changed installed files and prove unchanged files remain untouched.

## Task 1: Executable routing and edit selection

**Files:** `drama-studio/scripts/dreamina_route.py`, `drama-studio/scripts/assemble_timeline.py`, `tests/test_dreamina_production_tools.py`.

**Interfaces:** Keep existing explicit Python calls and `--clip` CLI working. `build_video_command` accepts an omitted model and omitted resolution and resolves defaults from `duration`. CLI omitted `--model` must reach this resolver, not pre-fill the short-clip model. The command preview continues to submit nothing.

Add mutually exclusive `--timeline PATH` alongside repeatable `--clip`. The JSON input is `{"clips":[{"path":"relative-or-absolute.mp4","in":0.75,"out":8.25}, ...]}` with seconds and relative paths resolved against the JSON parent. `in` defaults to 0 and omitted `out` uses the source end. Reject invalid/non-finite/inverted/out-of-range cuts and source/output collisions before rendering. Preserve audio, normalize frame rate/pixel format/dimensions and reset PTS before assembling. Default assembly size becomes 720x1280; explicit size wins. The JSON is the existing minimal edit record; no mandatory additional report or audit.

- [ ] Add tests before implementation: 15 vs 16/30 second default routing; explicit 2.5/1080p unchanged; explicitly incompatible 2.0/16 seconds rejected; >30 seconds rejected; CLI default behavior.
- [ ] Add real ffmpeg integration coverage for ordered source in/out cuts (visibly distinct synthetic colors, different frame rates), retained audio, output duration tolerance and original-input protection; negative manifest/ambiguous input checks. Keep existing tests.
- [ ] Run the focused tests and record expected pre-change failures.
- [ ] Implement only the specified behavior and fix the focused tests.
- [ ] Run the full existing suite once, inspect the diff, commit this task's files, and record RED/GREEN evidence.

## Task 2: Reachable rule amendments and scoped installation staging

**Files:** existing owner paragraphs in Crew/Studio `SKILL.md`, shared `references/startup-guide.md` (identical in both packages of each version line), Crew commercial/writing/dialogue references as needed; Studio asset/shot/prompt/model/file-management/role entry points as needed; repository README/CHANGELOG; neutral behavior regression cases. Do not mechanically modify every named file if the owner and consumers already suffice.

**Interfaces:** Consume Task 1 routing and timeline CLI exactly. Root controller prepares an ignored staged copy of the installed packages, and worker applies the same semantics there while retaining their additional features. Source patch versions advance from Crew 6.23.2 / Studio 1.17.2; installed versions from Crew 6.26.10 / Studio 1.21.5. Do not conflate version lines or erase installed-only unified eight-block conventions.

- [ ] Read owner sections and current consumer wording; use recorded neutral baseline scenarios to identify missing guidance vs enforcement gaps.
- [ ] Amend original paragraphs, add only needed conditional subparagraphs and remove directly superseded statements. Retain legitimate exceptions; no project story, media or personal paths.
- [ ] Apply equivalent narrow edits to the staged installed copies. Leave real installed files unchanged until review completes.
- [ ] Update neutral behavior cases for >15-second unspecified model, explicit model override, brand-service brief, direct assembly, connected appearance revision, ghosted source, empty-space reference with active extras, and actual vs planned audio timing.
- [ ] Run contract tests and new neutral scenario checks; verify startup copies agree within each version line and detect obsolete default wording. Update version/readme/changelog truthfully with review scope.
- [ ] Commit repository changes and report staged file paths and evidence; do not install or push.

## Controller finish

- [ ] Independent task and whole-branch reviews, then focused fixes if needed.
- [ ] Preserve original source working changes; keep committed feature branch available without forcing a merge or publication.
- [ ] Back up exact changed installed files, copy only reviewed staged changes and changed scripts, verify matching hashes, preserve all other installed files.
- [ ] Scoped consistency and workspace audit; preserve tests, evidence and backups without recursive deletion. Report active installed defaults, completed improvements and any real limitation.
