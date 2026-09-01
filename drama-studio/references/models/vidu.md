# 模型能力卡：Vidu（生数科技 ShengShu）

> 装配时只读**用户指定模型对应的一张卡**；未指定模型走通用保守模式（见 prompt-assembly.md 第 6 节）。

## 基本信息

| 字段 | 值 |
|---|---|
| 模型/版本 | **Vidu Q3 系列**（`q3` 参考生 / `q3-pro` 高画质 / `q3-turbo` 快速）；旧版 Q1、Q2 系列 |
| verified_at | 2026-09-01 |
| evidence_source | [腾讯云 TokenHub Vidu 视频生成 API](https://cloud.tencent.com/document/product/1823/135756)（接口参数、时长取值速查与素材通用约束） |
| capability_state | **confirmed**（官方 API 文档证实） |
| 模型状态 | 正常服务；Q3 面向专业影视/短剧/漫剧（2026-01 发布） |
| 适配器口径 | 本卡能力参数按**腾讯云 TokenHub** 当前接口核验；其他 provider/adapter 的可用模式、参数名与上限可能不同。`execution` 前记录 `provider / adapter / version`，按所用接入方实时官方 schema 确定；`planning_only` 未锁接入方时须标明「TokenHub 口径」，不得外推为 Vidu 全渠道统一接口 |

## 能力参数

| 项 | 参数 |
|---|---|
| 支持模式 | 文生 / 图生 / 首尾帧 / 参考生 R2V / **智能切镜** / **音画同出** |
| 时长 | **TokenHub Q3 系列**：文生/图生/首尾帧 1–16s，参考生 3–16s；Q2 文生/图生 1–10s，Q2 pro/turbo 首尾帧 1–8s；参考生 q2-pro 0–10s（0=模型自动判断）、q2 1–10s。时长取值随接口模式变化，不只由模型名决定 |
| 画幅 | 1:1、3:4、4:3、9:16、16:9 |
| 分辨率 | 540p / 720p / 1080p |
| 参考资产上限 | **TokenHub**：直接 `images` 参考 1–7 张，单图 ≤50MB；整个 POST body ≤20MB（Base64 输入同时受请求体限制）。`subjects` 模式每个主体最多 3 张图片，Base64 解码后 <20MB；图片格式 png/jpeg/jpg/webp |
| 首尾帧 | ✅ Q3 pro/turbo、Q2 pro/turbo 支持 |
| 多镜头 | ✅ Q3 智能切镜（多机位一致性出色）；**Q2 Pro 参考生是唯一支持视频输入的档位**（视频参考/编辑） |
| 原生音频/语音 | ✅ Q3 音画同出（口型误差约 ±15ms、20+ 语言、200+ 音色——**capability_state: needs_confirmation**，社区口径未经官方文档逐项证实，按保守值写）；Q2 支持 bgm、movement_amplitude |
| 已知冲突 | ①Q3 参考生与文生/图生/首尾帧时长范围不同（3–16s vs 1–16s）；②`q2-pro` 参考生 0–10s 与图生 1–10s 下限不同；③仅 q2-pro 支持视频主体/直接视频参考；④直接参考与 `subjects` 的 Prompt 上限不同；⑤单图资源上限 50MB 不取消 POST body 20MB 上限 |
| 失败降级 | 超过本次接口时长上限时按动作链自然段与意义变化拆 Clip；需要延长时仅在实时接口明确提供延长能力时使用，否则不臆造延长参数；动作迁移仅在所用 provider/adapter 明确支持时启用 |
| 提示词适配 | **TokenHub**：文生/图生/首尾帧 Prompt ≤5000 字符；参考生 `subjects` 模式 ≤5000 字符；参考生直接 `images/videos` 模式 ≤2000 字符。其他 provider/adapter 以实时 schema 为准；**音画同出须写清每个说话人台词+环境音/音效位置**，音轨跟随画面节拍 |

## 制作侧使用要点

- **参考生强项**：漫剧/短剧多主体一致性，最多 7 主体同时输入并保持一致。
- 对白镜：原生音画同步（±15ms 口型，**needs_confirmation 参考值**），适合台词密集戏。
- 动作戏：Motion Sync 动作迁移——一张目标形象图 + 一段动作源视频即可复刻动作。
- 智能切镜：多机位镜头序列一次生成，适合打斗多机位剪辑。
