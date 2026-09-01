# AI 短剧双 Skill

这套仓库把短剧工作拆成两个可以独立调用、又能稳定交接的 Skill：`drama-crew` 负责选题、人物、结构、剧本与终审，`drama-studio` 负责资产、分镜、提示词、声音、剪辑与制作 QC。

它不是一个固定题材的提示词模板。主流程只保留编排骨架，创作规范、模型能力和制作维度按任务命中后再加载，适合团队长期维护。

## 当前版本

| Skill | 版本 | 文件数 | 职责 |
|---|---:|---:|---|
| `drama-crew` | 6.12.3 | 17 | 从选题到定稿剧本、账本、合规与终审 |
| `drama-studio` | 1.11.1 | 27 | 从剧本交接到资产、分镜、声音、剪辑与 QC |

## 主要特点

- 剧本侧 8 个角色、制作侧 6 个角色，各自有明确输入、输出和失败判定。
- 标准交接和直通未审稿交接分开处理，不伪造缺失的终审或合规报告。
- `romance_axis` 贯穿创作与评分；没有恋爱线的项目不会被恋爱判据误伤。
- 制作规范按镜头诊断加载，避免把全部维度卡和模型卡塞进每个任务。
- 已内置 Seedance 2.0/2.5、MiniMax/Hailuo H3、Kling、Vidu、即梦，以及 Flow2API 适配的 Gemini Omni 1.1 Flash 模型卡。
- 模型限制按“实时接口 > 指定模型卡 > 未指定模型的保守默认”裁决。
- 文字声音指纹和实际母音色分开管理。每个角色从首次发声起筛选母音色，不要求都从第一集开始。
- 模型内置音色和开源音色不增加许可证、授权或 consent 字段；声音卡只记录连续性真正需要的事实。
- 默认交付文本规划；只有宿主确实接入可用媒体工具并通过预检时，才进入 `execution`。

## 快速安装

```powershell
git clone https://github.com/zkhyww/ai-short-drama-skills.git
cd ai-short-drama-skills

# 首次安装；如果目标目录已经存在，先按 docs/使用说明.md 备份或升级
Copy-Item -Path '.\drama-crew' -Destination "$env:USERPROFILE\.workbuddy\skills\drama-crew" -Recurse
Copy-Item -Path '.\drama-studio' -Destination "$env:USERPROFILE\.workbuddy\skills\drama-studio" -Recurse
```

复制完成后，重启或刷新 WorkBuddy 的 Skill 列表。

## 最短用法

创作剧本：

```text
请用 drama-crew 创作一部 18 集、每集约 90 秒的都市悬疑短剧。
不带货，无恋爱线。先给候选方向，再按流程完成定稿与标准交接。
```

制作规划：

```text
请用 drama-studio 接收这份标准交接，目标模型为 Seedance 2.5。
先做 E01 的资产与分镜规划，不调用媒体生成工具。
```

## 文档

- [使用说明](docs/使用说明.md)：安装、升级、调用与常见问题
- [特点与架构](docs/特点与架构.md)：双 Skill 分工、交接合同、模型卡和声音系统
- [团队协作](docs/团队协作.md)：分支、版本、验证和发布流程
- [贡献指南](CONTRIBUTING.md)：提交修改前需要满足的检查
- [变更记录](CHANGELOG.md)：公开版本基线

## 使用边界

仓库不包含模型账号、API Key、Cookie、媒体生成配额或可直接调用的云服务。模型卡描述的是规划与适配边界，实际执行仍以使用者接入的 provider、adapter 和实时 schema 为准。

许可证号、批准文件编号和节目编号属于发行或报审上游输入。制作侧只在收到正式编号后原样植入，不自行申请、推断或生成。

## License

[MIT License](LICENSE)
