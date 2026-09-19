# Provider/Adapter 能力卡：Dreamina official CLI（即梦官方命令行）

> 本卡描述本机官方 `dreamina` CLI 的实时适配器能力，不替代 Seedance 模型卡。用户指定即梦/Dreamina 时读本卡；用户指定 Seedance 2.0/2.5 且实际 provider 为 Dreamina 时，同时以本卡和目标子命令实时 `--help` 收紧模型卡，冲突时实时 CLI/后端校验优先。

即梦 Web 的 Blender 白模渲染上传插件是另一入口，安装、相机渲染/本地上传与跳转核对见 [blender-previs §2](../blender-previs.md)。本卡的 CLI 参数、登录与能力声明不自动适用于该插件；插件不会替代角色/场景参考与正式生成核验。

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
| 视频模型 | 未指定模型按 `../prompt-assembly.md` §1 以单次 Clip 时长路由；显式选择优先。全集合 `seedance2.0` / `seedance2.0fast` / `seedance2.0_vip` / `seedance2.0fast_vip` / `seedance2.0mini` / `seedance2.5`；部分图生入口另支持 1.0fast/1.5pro |
| 时长 | Seedance 2.0 系列输出 **4–15s**；Seedance 2.5 输出 **4–30s**；旧模型按具体子命令帮助 |
| 画幅 | 文生/全能参考：1:1、3:4、16:9、4:3、9:16、21:9；单首帧/首尾帧/多帧由输入图推断 |
| 分辨率 | 未指定时默认 **720p**；显式且兼容的设置优先。Seedance 2.5：480p/720p/1080p；`seedance2.0_vip`：720p/1080p/4k；`seedance2.0fast_vip`：720p；其余当前公开 2.0 组合为 720p |
| 2.0 全能参考 | 图≤9、视频≤3、音频≤3、总输入≤12；至少一张图或一段视频；参考视频/音频单段和合计 2–15s |
| 2.5 全能参考 | 图≤30、视频≤10、音频≤10、总输入≤50；允许纯音频；参考视频/音频单段和合计 2–30s；VIP only |
| 原生音频 | Seedance 音视频联合生成按目标模型实时能力执行。角色已有**已冻结母音色**时，优先作为 `multimodal2video --audio` 音色参考，并在 Prompt 中按上传顺序明确绑定音频编号、角色与音色用途；2.0 全能参考还须至少带一张图或一段视频，2.5 允许纯音频参考 |
| 独立 TTS | 官方 CLI 当前没有独立 TTS 子命令；仅用户已授权外部声音处理，且接口不接受参考或实听持续失败时，才由外部 TTS 生成逐句 WAV 并走 lip-sync 后备；不得虚构 `dreamina audio` |

## 已知边界与降级

- `image2video`、`frames2video`、`multiframe2video` 不接受显式画幅；首帧资产必须先生成到目标画幅。
- Seedance 2.5 为 VIP 模式；无权限、余额不足或后端未开放时，按镜头目的降级到 2.0 系列并重新核时长/分辨率，不能静默改参数。
- 30 秒直出专项正式执行前实核目标子命令 `--help`、素材、登录与预算；接口不支持 30 秒时保留单 Clip 30 秒规划并报告执行差异，不能把两次 15 秒提交记录成一次 30 秒调用。
- 某模型首次使用若返回 `AigcComplianceConfirmationRequired`，先在即梦 Web 端完成该模型首次生成，再回 CLI；这不是浏览器签名令牌问题。
- 任务异步提交：发起时保存本次已确认的提示词及其哈希、实际按序输入、模型参数、尝试编号与CLI原始响应；保留 `submit_id`，用 `dreamina query_result --submit_id=...` 查询。区分本地预览、上传、提交接受、排队、生成中、成功/失败和成片验收，不能把HTTP/CLI成功或扣费当成片成功。进程超时/断连而提交结果未知时先查已有任务与本地记录，不盲目重复付费提交；后续自动重试须有实际失败证据及覆盖该次的授权/预算。
- 提交前运行 `scripts/dreamina_route.py` 预览命令，不消耗积分。对照冻结请求核实际命令中的模型、单次时长、分辨率及按序引用；实际执行参数和 provider 回执才是生产事实，预览不等于执行。沿既有调用记录保存 provider/adapter/version、任务 ID、结果路径与差异，不事后凭提示词猜补。预估成本、服务端本任务 `credit_count`（未知记 unknown）及账户余额分别记录；并发消费时余额差不能归因本任务，也不能以一次观察推定通用折扣。发现未解释的重大价格偏差，先暂停依赖批次、核对参数与回执，再按已有授权/预算决定继续；实际执行仍须满足耗积分告知与授权范围。
- **用户指定的附加视频**：不默认添加黑屏、静音或所谓优惠素材。用户明确要求随请求上传但不作创作参考时，先核真实时长、视频流/容器差异、画幅、编码和音轨，不能依据文件名宣称符合上下限；遵守本次模型/provider实际校验，不自动改写用户原件。`--video`仍是模型输入，未证实存在独立非参考附件字段时，只能在第一段明确不继承其画面、音轨、运动、画幅/时长，不作首帧/编辑/续写源、不拼入成片；不能保证技术隔离或优惠。边界文件经明确披露且用户确认可按原件尝试；拒绝时保存原因、停止依赖调用，原请求无授权不另去附件、换素材或加费重提。一次接受不修改通用能力下限。
