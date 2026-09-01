# 模型能力卡：可灵 Kling（快手）

> 装配时只读**用户指定模型对应的一张卡**；未指定模型走通用保守模式（见 prompt-assembly.md 第 6 节）。

## 基本信息

| 字段 | 值 |
|---|---|
| 模型/版本 | Kling Video 3.0 系列：`kling-video-v3`（旗舰）/ `v3-omni`（多模态全能）/ `v3-turbo`（快速精简）；旧版 `v2.6`、`O1` |
| verified_at | 2026-09-01 |
| evidence_source | 腾讯云官方文档 cloud.tencent.com/document/product/1823/135742；阿里云百炼官方 help.aliyun.com/zh/model-studio/kling-video-generation-api-reference |
| capability_state | **confirmed**（官方 API 文档证实） |
| 模型状态 | 正常服务，V3 为当前主力 |
| 适配器口径 | 本卡「能力参数」区描述**模型能力**；**调用语法因 provider/adapter 而异**（腾讯云：布尔 `settings.multi_shot` + provider 对应分号式 Shot 语法；阿里云百炼自定义多镜头：`multi_shot=true` + `shot_type=customize` + `multi_prompt=[...]`，需元素时另传 `element_list=[...]`）——execution 前在工具预检中记录 provider/adapter/version，按所用接入方实时官方 schema 确定字段层级与可选项；工具能自动识别时由工具选择，不向用户追问 |

> 百炼字段依据（核验于 2026-09-01）：[阿里云百炼 Kling 视频生成 API 参考](https://help.aliyun.com/en/model-studio/kling-video-generation-api-reference/)；execution 仍以本次连接工具实时 schema 为最终真源。

## 能力参数

| 项 | 参数 |
|---|---|
| 支持模式 | 文生 / 图生（首帧）/ 图生（首尾帧）/ 参考生（omni）/ 视频编辑（omni）/ 智能分镜多镜头 |
| 时长 | V3 全系 3–15s；O1 3–10s；V2.6 5/10s 两档 |
| 画幅 | 文生/全能：16:9、9:16、1:1；**图生/首尾帧无画幅参数，输出跟随输入图片比例** |
| 分辨率 | 720p / 1080p / 4K（V3、omni）；turbo 720p/1080p |
| 参考资产上限 | 图生首帧 1 张；首尾帧 2 张；omni 参考生：多视频+多图+`element_list` 元素引用 |
| 首尾帧 | ✅ 支持（V2.6 起全系） |
| 多镜头 | ✅ V3 支持多镜头两种模式：智能分镜（模型自动拆）/ 自定义分镜（每镜 3–15s 独立 prompt）——**调用参数拼写因 provider 而异，见基本信息「适配器口径」** |
| 原生音频/语音 | ✅ V3 / V3-omni / V2.6 支持原生音频（对话+环境+音效，多语言含方言）；**turbo 无音频** |
| 已知冲突 | ①图生/首尾帧模式不接受画幅参数；②自定义多镜头下主 prompt 不生效，须逐镜独立描述（参数名按所用 provider 文档）；③元素引用须按所用 provider 的元素列表参数与 prompt 内标记对应 |
| 失败降级 | >15s 拆两镜；无音频需求换 turbo 提速降本；多镜头不灵退化为单镜连拍 |
| 提示词适配 | prompt ≤2500 字符（超长截断）；多镜头逐镜 prompt 每镜独立描述动作/运镜/时长 |

## 制作侧使用要点

- **首选主力**：短剧竖屏 9:16 + 3–15s + 原生音频一次到位，接近「一镜一条提示词」直接出片。
- 口型/对白镜用 V3 或 V2.6（原生音频+口型同步）；纯画面快速迭代用 turbo。
- 人物跨镜一致性用 omni 的参考生 + 元素引用（`element_list`），配合资产库角色图链式传递。
- 首尾帧成组镜头：两镜首尾帧用同一输入图衔接（尾帧=下一镜首帧）。
