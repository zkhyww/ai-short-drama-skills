# AI 短剧双 Skill 公开仓库实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 建立并发布 `zkhyww/ai-short-drama-skills`，让团队成员能够安装、理解、协作维护 `drama-crew` 与 `drama-studio`。

**Architecture:** 从本机当前生效 Skill 复制一份独立公开树，公开树只保留运行规范与团队文档，并在推送前完成路径脱敏、敏感扫描、结构校验和原生 Skill 验证。GitHub `main` 是公开分发基线，本机 WorkBuddy 目录仍是当前运行副本，两者通过明确版本号同步。

**Tech Stack:** Markdown、Git、GitHub CLI、PowerShell、Python `quick_validate.py`

**Spec:** `docs/superpowers/specs/2026-09-02-public-repository-design.md`

## Global Constraints

- 远端仓库固定为 `zkhyww/ai-short-drama-skills`，可见性固定为 public，默认分支固定为 `main`。
- 发布版本固定为 `drama-crew` v6.12.3（17 个 Markdown）与 `drama-studio` v1.11.1（27 个 Markdown）。
- 不上传令牌、Cookie、账号、模型配额、项目剧本、媒体素材、内部测试报告或本机用户绝对路径。
- 公开许可证固定为 MIT License，版权人为 `zkhyww`，年份为 2026。
- 不修改 `.workbuddy` 中的当前生效 Skill；所有公开脱敏只发生在独立仓库副本。

---

### Task 1: 建立公开 Skill 树

**Files:**
- Create: `drama-crew/**`
- Create: `drama-studio/**`
- Modify: `drama-crew/references/dialogue-craft.md`

**Interfaces:**
- Consumes: 本机当前生效的 `drama-crew` v6.12.3 与 `drama-studio` v1.11.1。
- Produces: 无密钥、无本机用户路径、文件数固定的公开 Skill 树。

- [ ] **Step 1: 运行公开树缺失门禁并确认失败**

  运行 PowerShell：检查 `drama-crew/SKILL.md`、`drama-studio/SKILL.md` 是否存在，并断言文件数为 17/27。当前预期失败，因为公开树尚未复制。

- [ ] **Step 2: 机械复制两个 Skill 目录**

  从当前生效 WorkBuddy 目录分别复制 `drama-crew` 与 `drama-studio` 到仓库根目录；不复制 `skill-creator`、`.skill` 包或任何运行产物。

- [ ] **Step 3: 脱敏旧研究路径**

  将 `drama-crew/references/dialogue-craft.md` 中旧本机研究目录改成不包含用户名和盘符的来源说明，并保留对 `writing-craft.md` 的规范指向。

- [ ] **Step 4: 运行结构与版本门禁**

  验证文件数为 17/27，版本为 6.12.3/1.11.1，本机用户路径匹配数为 0。

- [ ] **Step 5: 提交公开 Skill 树**

  ```powershell
  git add drama-crew drama-studio
  git diff --cached --check
  git commit -m "feat: publish drama crew and studio skills"
  ```

### Task 2: 编写团队使用与维护文档

**Files:**
- Create: `README.md`
- Create: `docs/使用说明.md`
- Create: `docs/特点与架构.md`
- Create: `docs/团队协作.md`
- Create: `CONTRIBUTING.md`
- Create: `CHANGELOG.md`
- Create: `LICENSE`
- Create: `.gitignore`

**Interfaces:**
- Consumes: Task 1 的公开 Skill 树与版本号。
- Produces: 团队可以独立完成安装、调用、升级、评审和贡献的文档入口。

- [ ] **Step 1: 运行文档缺失门禁并确认失败**

  断言上述 8 个文件全部存在，当前预期失败。

- [ ] **Step 2: 编写 README 与详细文档**

  README 包含定位、双 Skill 分工、主要特点、快速安装、最短调用示例、版本与文档导航；详细文档分别解释使用流程、架构特点和团队协作。

- [ ] **Step 3: 添加许可证、贡献规则、变更记录与忽略规则**

  MIT License 使用 2026 `zkhyww`；`.gitignore` 排除 `.skill`、缓存、密钥和临时文件；贡献规则要求小范围改动、版本同步和验证证据。

- [ ] **Step 4: 验证文档契约**

  检查 README 明确列出 v6.12.3/v1.11.1、标准/直通交接、模型卡按需加载、母音色首次发声筛选、开源/模型内置音色不记录许可证，以及审批编号不由制作侧生成。

- [ ] **Step 5: 提交团队文档**

  ```powershell
  git add README.md LICENSE CONTRIBUTING.md CHANGELOG.md .gitignore docs
  git diff --cached --check
  git commit -m "docs: add team guide and project overview"
  ```

### Task 3: 完整发布验证

**Files:**
- Verify: `drama-crew/**`
- Verify: `drama-studio/**`
- Verify: repository documentation

**Interfaces:**
- Consumes: Task 1 和 Task 2 的全部提交。
- Produces: 可推送的、无敏感项的 Git 提交基线。

- [ ] **Step 1: 运行原生 Skill validator**

  使用本机 `skill-creator/scripts/quick_validate.py` 分别验证仓库内两个 Skill，预期均输出 `Skill is valid!`。

- [ ] **Step 2: 运行 Markdown 与敏感项扫描**

  检查 44 个 Skill Markdown 围栏成对；全仓库扫描私钥、Token、密钥赋值、本机用户路径、`.env` 内容和临时文件，预期 0 命中。

- [ ] **Step 3: 实际打包并核对内容**

  将两个 Skill 打包到系统临时目录，核对包内分别为 17/27 个文件、各有一个 `SKILL.md`，Omni 模型卡恰好一份；随后逐文件删除测试包和空目录。

- [ ] **Step 4: 检查 Git 状态与历史**

  运行 `git status --short --branch`、`git log --oneline --decorate -5` 与 `git diff --check`，预期工作树干净、无空白错误。

### Task 4: 创建公开 GitHub 仓库并推送

**Files:**
- External: `https://github.com/zkhyww/ai-short-drama-skills`

**Interfaces:**
- Consumes: Task 3 验证通过的本地 `main`。
- Produces: 团队可克隆的公开 GitHub 仓库。

- [ ] **Step 1: 复核 GitHub 身份与仓库名**

  运行 `gh auth status`，确认活动账号为 `zkhyww`；确认目标仓库尚不存在。

- [ ] **Step 2: 创建 public 远端并推送 main**

  ```powershell
  gh repo create zkhyww/ai-short-drama-skills --public --source . --remote origin --description "AI short-drama writing and production skills for Chinese agent workflows"
  git push -u origin main
  ```

- [ ] **Step 3: 设置仓库主题**

  设置 `ai-short-drama`、`agent-skills`、`prompt-engineering`、`workbuddy`、`chinese` 五个主题，不启用额外自动化。

- [ ] **Step 4: 远端验收**

  运行 `gh repo view zkhyww/ai-short-drama-skills --json nameWithOwner,visibility,url,defaultBranchRef`，并确认 `git rev-parse HEAD` 与 `git ls-remote origin refs/heads/main` 的提交一致。
