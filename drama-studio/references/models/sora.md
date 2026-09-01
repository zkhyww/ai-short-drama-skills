# 模型能力卡：OpenAI Sora 2（⚠️ 已弃用 · 不接生产流程）

> 装配时只读**用户指定模型对应的一张卡**；未指定模型走通用保守模式（见 prompt-assembly.md 第 6 节）。

## 基本信息

| 字段 | 值 |
|---|---|
| 模型/版本 | `sora-2`（标准）/ `sora-2-pro`（高画质） |
| verified_at | 2026-08-31 |
| evidence_source | OpenAI 官方 developers.openai.com/api/docs/guides/video-generation；Sora 2 Prompting Guide（developers.openai.com/cookbook） |
| capability_state | **confirmed**（官方文档证实，历史能力）；但 **model_status = deprecated** |
| 模型状态 | ⚠️ **已弃用（v1.7.2 定版）**：消费者应用（sora.com/App）2026-04-26 已关闭；**Videos API 与 sora-2 系列 2026-09-24 关闭**。本卡仅作历史参考保留，**不选为生产主模型、不进任何装配流程** |

## 能力参数（历史能力，仅供迁移参考）

| 项 | 参数 |
|---|---|
| 支持模式 | 文生 / 图生（图片参考）/ 角色引用（Characters API）/ 视频延长（链式 6 次）/ 视频编辑 / Batch API |
| 时长 | 4–20s（单次，2026-03 起）；延长链式总长可达 120s |
| 画幅 | sora-2：720x1280、1280x720；sora-2-pro 另加 1024x1792、1792x1024、1080x1920、1920x1080 |
| 分辨率 | sora-2 720p；sora-2-pro 最高 1080p（无 4K） |
| 参考资产上限 | 角色引用用 2–4s 参考片段；真人肖像须账号经理审批 |
| 首尾帧 | API 无显式首尾帧参数（用图生参考 + 延长实现） |
| 多镜头 | 单次生成不支持多镜头，靠延长链衔接 |
| 原生音频/语音 | ✅ 原生同步音频（对话+音效+环境） |
| 已知冲突 | 真人（含公众人物）不可生成；**含人脸输入图被拒**；版权角色/音乐被拒；仅限 18 岁以下适宜内容 |
| 失败降级 | 迁移到 Kling V3 / Seedance 2.5 / MiniMax H3 / Veo 3.1 承接原工作流；已导出作品不受影响（API 输出带 C2PA 元数据） |
| 提示词适配 | 官方 Prompting Guide 是**导演式提示词的最佳参考文档**——「像对没见过分镜的摄影师交代」：写清景别、主体、动作、环境、光线、运镜，避免抽象叙事概念；该写作原则可迁移至所有模型 |

## 制作侧使用要点

- **不接入生产流程**。若用户指定 Sora，先提示停用日期并建议迁移。
- 保留价值：官方 Prompting Guide 的导演式提示词方法论，可作为景川七段式提示词的写法参照。
- 迁移对照：物理真实性→Veo 3.1 / Seedance；音画同步+角色一致性→Kling V3 / MiniMax H3；多镜头→Kling V3 / Vidu Q3。
