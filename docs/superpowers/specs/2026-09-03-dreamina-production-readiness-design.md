# Dreamina Production Readiness Design

## Goal

Make `drama-studio` production-capable with the official `dreamina` CLI as the default local generation engine, without depending on the third-party `jimeng` CLI or its `xmst` signing state.

## Decisions

- Keep the v1.13.4 Seedance native audio workflow: dialogue, environment, effects, and optional music are generated with the video by default.
- Route text-only, first-frame, and mixed-reference video jobs to `dreamina text2video`, `dreamina image2video`, and `dreamina multimodal2video` respectively.
- When Dreamina executes Seedance 2.0/2.5, inject both the Seedance model card and the Dreamina provider/adapter card before applying live CLI validation.
- Treat external TTS/WAV plus lip-sync as a fallback only; the official CLI has no standalone TTS command.
- Add a deterministic ffmpeg/ffprobe timeline assembler that normalizes heterogeneous clips before concatenation and can optionally replace or mix an external fallback audio track.
- Apply pore-level skin requirements only to photorealistic and realistic-3D styles. Stylized 2D media use medium-appropriate surface detail.
- Treat the 13-module layout as the default comprehensive character sheet, while portraits, turnarounds, costume stills, and detail boards retain dedicated layouts.
- Preserve the current flova fallback and authorization/cost gates.

## Non-goals

- Do not repair or retain `xmst` as a production prerequisite.
- Do not submit paid generation tasks during this change.
- Do not add a new agent, user confirmation point, or production artifact category.

## Verification

- Unit tests exercise Dreamina command routing and validation.
- An integration smoke test generates heterogeneous local media with ffmpeg, assembles it, and verifies video/audio streams, 9:16 output, and duration with ffprobe.
- Native validators, package builds, full contract tests, Markdown references/fences, and Git hygiene pass.
