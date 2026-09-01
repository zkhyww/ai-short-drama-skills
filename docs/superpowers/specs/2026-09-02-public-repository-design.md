# AI 短剧双 Skill 公开仓库设计

## 目标

在 GitHub 账号 `zkhyww` 下建立公开仓库 `ai-short-drama-skills`，发布已经验收的 `drama-crew` 与 `drama-studio`，让团队成员可以清楚地安装、调用、协作维护并验证版本。

## 受众与使用边界

- 主要受众：使用 WorkBuddy/Codex 类本地 Agent 宿主的中文短剧创作与制作团队。
- 主要环境：Windows + WorkBuddy，Skill 安装目录为 `%USERPROFILE%\.workbuddy\skills\`。
- 仓库只包含 Skill 规范和团队使用文档，不包含账号、令牌、Cookie、模型配额、生成素材、项目剧本、内部测试报告或个人工作区路径。
- 视频、图片、音频模型调用仍由使用者自己的环境和授权决定；仓库不附带可用凭据，也不承诺媒体生成能力。

## 冻结版本

- `drama-crew`：v6.12.3，共 17 个 Markdown 文件。
- `drama-studio`：v1.11.1，共 27 个 Markdown 文件。
- 公开副本来自维护者本机 WorkBuddy 的当前生效版本，发布前复制到独立仓库并完成脱敏校验。

## 仓库结构

```text
ai-short-drama-skills/
├── README.md
├── LICENSE
├── CONTRIBUTING.md
├── CHANGELOG.md
├── .gitignore
├── drama-crew/
│   ├── SKILL.md
│   └── references/
├── drama-studio/
│   ├── SKILL.md
│   └── references/
└── docs/
    ├── 使用说明.md
    ├── 特点与架构.md
    ├── 团队协作.md
    └── superpowers/
        ├── specs/
        └── plans/
```

## 文档职责

- `README.md`：项目定位、核心特点、版本、快速安装、最短使用示例和文档导航。
- `docs/使用说明.md`：安装、升级、调用方式、标准交接与直通交接、模型卡和声音工作流。
- `docs/特点与架构.md`：双 Skill 分工、交接合同、按需加载、模型卡、声音连续性和 QC 设计。
- `docs/团队协作.md`：分支、版本、修改边界、验证、评审与发布流程。
- `CONTRIBUTING.md`：提交规则和最小验收门槛。
- `CHANGELOG.md`：当前公开基线和后续版本变化。

## 安装与升级设计

团队成员克隆仓库后，将 `drama-crew` 与 `drama-studio` 两个目录复制到 `%USERPROFILE%\.workbuddy\skills\`。升级时先备份本地自行修改的版本，再按目录覆盖，并重启或刷新宿主。文档不提供会静默覆盖用户目录的安装脚本。

## 公开安全设计

1. 发布前扫描私钥、GitHub/OpenAI Token、通用密钥赋值、环境密钥名和本机用户绝对路径。
2. 将 `dialogue-craft.md` 中指向旧研究工作区的本机路径改为公开可理解的来源说明，不改变创作规则。
3. `.gitignore` 排除 `.skill` 打包物、缓存、临时文件、密钥文件和常见本地配置。
4. Git 推送前复查 `git diff --cached`、远端地址和仓库可见性。

## 许可证

采用 MIT License（Copyright 2026 zkhyww），允许团队与社区使用、修改和再分发，同时保留版权与免责声明。

## 验收标准

- 两个 Skill 目录文件数分别为 17 和 27，版本分别为 6.12.3 和 1.11.1。
- 原生 `quick_validate.py` 对两个 Skill 均返回 `Skill is valid!`。
- 44 个 Markdown 文件围栏成对，无 `.skill`、缓存或临时文件混入源目录。
- 公开树的敏感扫描为 0；仓库文档不存在本机用户绝对路径。
- README、使用说明、特点与架构、团队协作、贡献说明和许可证均存在。
- GitHub 仓库为 public，默认分支为 `main`，本地提交与远端 `main` 一致。

## 非目标

- 不在本次建立自动发布、付费模型调用、媒体生成、团队权限组或 GitHub Actions。
- 不把正在运行的剧本测试项目、测试输出或用户项目资产上传到公开仓库。
