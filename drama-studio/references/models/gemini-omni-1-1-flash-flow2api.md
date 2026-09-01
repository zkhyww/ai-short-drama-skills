# 模型能力卡：Gemini Omni 1.1 Flash（Flow2API 本地适配器）

> 本卡只描述 `zkhyww/flow2api-secure-account-pool` 当前公开并已测试的兼容 API 子集。Google Flow 网页存在但本适配器尚未开放的功能，不得直接写进请求或规划合同。

## 基本信息

| 字段 | 值 |
|---|---|
| 模型/公开 capability | `omni-1.1-flash`（文生视频）/ `omni-1.1-flash-references`（参考图生视频） |
| provider / adapter | Google Flow 上游 / `flow2api-secure-account-pool` 影策兼容层 |
| adapter commit | `ed89a5163e039f0e4e6cd102a11c5d1638e954d7` |
| verified_at | 2026-09-02 |
| capability_state | **confirmed**：下表公开 capability、时长、画幅、参考图数量与兼容端点；**needs_confirmation**：上游实际 Prompt 最大长度、成片是否生成可用对白及声音一致性 |
| evidence_source | [仓库 README](https://github.com/zkhyww/flow2api-secure-account-pool/blob/ed89a5163e039f0e4e6cd102a11c5d1638e954d7/README.md)、[public_model_catalog.py](https://github.com/zkhyww/flow2api-secure-account-pool/blob/ed89a5163e039f0e4e6cd102a11c5d1638e954d7/src/core/public_model_catalog.py)、[yingce_adapter.py](https://github.com/zkhyww/flow2api-secure-account-pool/blob/ed89a5163e039f0e4e6cd102a11c5d1638e954d7/src/api/yingce_adapter.py)、[Omni 1.1 测试](https://github.com/zkhyww/flow2api-secure-account-pool/blob/ed89a5163e039f0e4e6cd102a11c5d1638e954d7/tests/test_omni_1_1_support.py)、[Google Flow 上游能力页](https://support.google.com/flow/answer/16352836) |

## 当前适配器能力

| 能力 | 已验证口径 |
|---|---|
| 文生视频 | `omni-1.1-flash`；0 张图片；8s / 10s，默认 10s |
| 参考图生视频 | `omni-1.1-flash-references`；1–3 张图片；仅 8s |
| 画幅 | 16:9 / 9:16 |
| 分辨率参数 | `native` / `nativeP` / `720P` 等价为上游原生输出；明确拒绝 `1080P / 4K / 2160P / 480P`，不静默降档 |
| Prompt | 不能为空；当前 adapter 未声明固定字符上限。`planning_only` 按本卡规划，`execution` 仍以实时接口错误与 schema 为准 |
| 参考图体积 | 默认单文件 ≤20 MiB；整个 multipart 请求默认约 ≤65 MiB，环境变量可改变，调用前读实时配置 |
| 首帧 / 首尾帧 | 此两项公开 capability **未开放**；参考图模式不等于首帧或首尾帧 |
| 10s 参考生 | **未开放**；不能靠传图给文生 capability 自动猜模式 |
| 多镜头 | 无 `multi_shot` 一类显式字段；只可在 Prompt 内描述时间进程，不承诺 API 级多镜头控制 |
| V2V / Extend | V2V 未作为本 capability 开放；Extend 是成功视频后的独立动作，不是普通生成模式 |
| 原生音频 / 声音控制 | API 返回完整上游视频，但公开 contract 没有独立音频参考、`voice_id`、custom voice 或稳定音色参数。`preset` 只是兼容字段，当前代码仅计入请求指纹，不得把它当作音色锁 |

内部解析 ID（只用于排障，不作为用户模型名）：

```text
8s 横屏  omni_1_1
8s 竖屏  omni_1_1_portrait
10s 横屏 omni_1_1_10s
10s 竖屏 omni_1_1_portrait_10s
```

底层键：8s 文生 `abra_t2v_8s`，8s 参考生 `abra_r2v_8s`，10s 文生 `abra_t2v_10s`。

## `/v1/videos` 调用合同

`POST /v1/videos` 使用 multipart：

```text
model
prompt
seconds
size
resolution_name
preset
input_reference[]
Idempotency-Key
```

- `model` 必须直接选明确 capability；文生与参考生不能自动互猜。
- `input_reference[]` 的数量必须精确落在 capability 范围内。
- 同一 `Idempotency-Key` 加同一请求复用任务；同键改请求返回 409。
- `preset` 不覆盖 capability、时长、画幅或声音能力。
- execution 前记录 `provider=google-flow / adapter=flow2api-secure-account-pool / adapter_commit或version / public_capability`；实时 schema 与本卡冲突时以实时 schema 为准。

## 提示词适配

- 8s / 10s 内只安排一个主导动作链；需要节拍变化时写清起点、转折和可观察结果，不假定接口支持真正多镜头。
- 参考图只用于人物、物件或风格参考；不要把第 1 张图称为首帧，也不要承诺尾帧落点。
- 人物对白可写声音指纹和逐句表演意图（重音、停连、语调、气息），但这只能引导生成，不能证明音色已锁定。
- 若生成结果里出现合适声音，可截取为人物母音色的听觉基准；由于本 adapter 不能回传音频参考，后续需要严格声线连续时改走独立 TTS＋对口型链路。不得仅凭相同 Prompt 声称母音色一致。

## 已知冲突与失败降级

1. Google Flow 上游列出的 4s / 6s、10s References、Frames、V2V 或 custom voice，不等于本 adapter 已开放；只用当前目录可选项。
2. 需要 16s 文生时，不能把本模型 10s 上限误写成 16s；改用已确认支持的模型或在成功视频后按实际 Extend 能力处理。
3. 需要首尾帧、音频参考或稳定 `voice_id` 时，切到实际接口已确认相应能力的模型/独立声音链路，不用 Prompt 假装拥有接口能力。
4. 请求返回 `unsupported_video_parameters` 时，只修改被拒绝的时长、画幅、参考图数量或分辨率；不得静默换 capability、静默降清晰度或丢参考图。
