# Studio 30 秒直出八段式 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development. Steps use checkbox syntax for tracking.

**Goal:** 将用户已明确选定的完整八段式落进正式 Studio，英文为本次用途，中文同架构适配。

**Architecture:** 保留现有单点终编、事实源与角色分工。只在原格式主责位增加可观察触发的30秒专项；其余文件消费同一契约。

**Tech Stack:** Markdown Skills、Python unittest、PowerShell备份/本机同步。

**Spec:** `docs/superpowers/specs/2026-09-12-studio-30s-eight-block-design.md`

## Global Constraints

- 本专项单次固定 `00:00–00:30`；一 Clip 一条八段正文，不与旧四区块双交、不增加团队。其他时长/未启用本专项的任务沿用原通用格式。
- 英文剧默认英文 Prompt、英文对白与匹配口音/声线；中文项目同架构适配中文，不把英文词数当汉字数。
- 用户最后的完整八段为唯一依据；不放单剧样本，不上传原片，不修改Crew/私有案例绑定，不push或关机。
- 只在原规则位覆盖、合并或替换，移除被替代的冲突句；不在末尾追加补丁章。
- 保留参考真实绑定、剧情事实、平台能力、声音单正文、角色权限与预算边界。

### Task 1: 原位接入八段式及全部直接消费者

**Files:** 主修改 `drama-studio/references/prompt-assembly.md`；同步 `drama-studio/SKILL.md`、`references/role-cards.md`、`asset-library.md`、`storyboard-craft.md`、`failure-atlas.md`、`external-platforms.md`、`dimensions/dim-audio.md`、`models/seedance.md`、`models/dreamina.md`；仅实际冲突时同步 `dimensions/dim-style.md`；README/CHANGELOG；既有格式合同测试中只调整被路由变化取代的旧断言。版本为Studio1.16.0，Crew不动。

**Interfaces:** 消费现有分镜唯一事实源、实际参考绑定、母音色状态、语言与模型项目锁；产出仍一Clip一Prompt Unit，专项输出八段，其余通用四区块。

- [ ] 读取指定主责原位，列出定位与冲突；以私有QA `消费测试任务.md`运行旧版五次fresh-context小样，主控逐项读原文。旧版未显现的问题不得冒充本轮新增能力。
- [ ] 在§2原位保留通用四区块，落完整八段模板及中英文标题映射，按Spec更新所有直接消费者。模板内不能含案例中的专有人名/品牌/桥段，最终Prompt只含实际生产内容。
- [ ] 同一任务新版五次fresh-context消费；额外定向中文完整Prompt、3D媒介、无图待执行条件。主控核词数、时码、持物链、两种语言、未触发分支和不支持30s边界。测试回答不进入Skill。
- [ ] 执行 `python -m unittest discover -s tests -q` 与 `git diff --check`，自审diff，按明确路径提交。不能新增只检查词句存在的断言代替行为验证。
- [ ] 独立任务评审（符合需求+改动质量），必要时按原作者单波修复；最终分支审查仅从本分支起点75b1269起，既有已审情感改动不重做。

### Task 2: 已验证Studio的本机同步与可见交付

**Files:** 只同步Task1实际变化的Studio运行文件到已安装 `C:/Users/Administrator/.codex/skills/drama-studio/`。私有QA根 `D:/视频/drama-skill-qa_20260912-30s-eight-block/` 保存备份、补丁与回执。公开验证摘要在 `docs/validation/2026-09-12-studio-30s-eight-block.md`。

**Interfaces:** 源正文为Task1通过复核的冻结提交；安装入口保留当前Drama/JUTIAN分流并更新version/source_commit，案例local-config不变。

- [ ] 核源提交、安装原基线metadata7b8c122及目标文件哈希；备份每个精确文件并复核哈希，形成只含本次变化的apply_patch补丁。不得重跑上一轮一次性安装助手。
- [ ] 申请正常提权执行明确补丁，逐文件比对源正文与安装正文（metadata可差异），写回执。失败时只按本次精确备份恢复，不覆盖他人变更。
- [ ] 主控复核安装哈希、metadata与私有绑定；补准确验证摘要，不把抽帧、规则测试称为新生成媒体已通过。
- [ ] 聚焦文档一致性及本任务根收尾审计；保留证据与原片，不批删，最终给正式文件链接。
