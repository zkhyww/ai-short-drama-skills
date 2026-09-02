# Provider/Adapter 能力卡：Dreamina official CLI（即梦官方命令行）

> 本卡描述本机官方 `dreamina` CLI 的实时适配器能力，不替代 Seedance 模型卡。用户指定即梦/Dreamina 时读本卡；用户指定 Seedance 2.0/2.5 且实际 provider 为 Dreamina 时，同时以本卡和目标子命令实时 `--help` 收紧模型卡，冲突时实时 CLI/后端校验优先。

## 基本信息

| 字段 | 值 |
|---|---|
| provider / adapter | 即梦 Dreamina / official CLI |
| 登录 | 官方 OAuth Device Flow：`dreamina login`；`dreamina user_credit` 可验证当前登录与余额 |
| verified_at | 2026-09-03 |
| evidence_source | 本机官方 CLI 的 `dreamina --help` 与各生成子命令 `--help` 实测 |
| capability_state | **confirmed**（本机参数校验层）；模型权限、审核与后端开关仍以提交时返回为准 |

## 命令与模式

| 任务 | 官方命令 | 关键约束 |
|---|---|---|
| 文生图 | `dreamina text2image` | 图像模型 3.0–5.0Pro；1–10 张；必须给 `resolution_type` |
| 参考生图 | `dreamina image2image` | 1–10 张本地参考图；图像模型 4.0–5.0Pro |
| 文生视频 | `dreamina text2video` | Seedance 2.0 系列或 Seedance 2.5；可显式给画幅 |
| 单首帧图生视频 | `dreamina image2video` | 本地首帧 1 张；**图生视频画幅跟随输入图**，命令不接 `ratio` |
| 首尾帧视频 | `dreamina frames2video` | 本地首帧+尾帧；画幅跟随首帧，命令不接 `ratio` |
| 多帧连续故事 | `dreamina multiframe2video` | 2–20 张图；3 张以上逐段给 transition prompt，模型版本固定 |
| 全能混合参考 | `dreamina multimodal2video` | 图像、视频、音频可混合；2.5 允许纯音频参考 |

## 当前参数面

| 项 | 参数 |
|---|---|
| 视频模型 | `seedance2.0` / `seedance2.0fast` / `seedance2.0_vip` / `seedance2.0fast_vip` / `seedance2.0mini` / `seedance2.5`；部分图生入口另支持 1.0fast/1.5pro |
| 时长 | Seedance 2.0 系列输出 **4–15s**；Seedance 2.5 输出 **4–30s**；旧模型按具体子命令帮助 |
| 画幅 | 文生/全能参考：1:1、3:4、16:9、4:3、9:16、21:9；单首帧/首尾帧/多帧由输入图推断 |
| 分辨率 | Seedance 2.5：480p/720p/1080p；`seedance2.0_vip`：720p/1080p/4k；其余当前公开 2.0 组合为 720p |
| 2.0 全能参考 | 图≤9、视频≤3、音频≤3、总输入≤12；至少一张图或一段视频；参考视频/音频单段和合计 2–15s |
| 2.5 全能参考 | 图≤30、视频≤10、音频≤10、总输入≤50；允许纯音频；参考视频/音频单段和合计 2–30s；VIP only |
| 原生音频 | Seedance 音视频联合生成按目标模型实时能力执行；CLI 也可把 WAV/视频作为全能参考输入 |
| 独立 TTS | 官方 CLI 当前没有独立 TTS 子命令；需要精确母音色时使用外部 WAV/TTS 后备，不得虚构 `dreamina audio` |

## 已知边界与降级

- `image2video`、`frames2video`、`multiframe2video` 不接受显式画幅；首帧资产必须先生成到目标画幅。
- Seedance 2.5 为 VIP 模式；无权限、余额不足或后端未开放时，按镜头目的降级到 2.0 系列并重新核时长/分辨率，不能静默改参数。
- 某模型首次使用若返回 `AigcComplianceConfirmationRequired`，先在即梦 Web 端完成该模型首次生成，再回 CLI；这不是浏览器签名令牌问题。
- 任务异步提交：保留 `submit_id`，用 `dreamina query_result --submit_id=...` 查询；状态未知先查任务，不盲目重复付费提交。
- 提交前运行 `scripts/dreamina_route.py` 预览命令；预览不会消耗积分。实际执行前仍须完成耗积分告知，并记录 provider/adapter/version、任务 ID、结果路径和实际成本。
