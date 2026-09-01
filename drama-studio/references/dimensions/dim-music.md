# 维度卡 · 配乐（dim-music）

> 解决的问题：音效与氛围音乐谁管、怎么写进提示词、全剧配乐怎么规划。
> **分工**：镜头级音效+音乐 cue（生成视频时内嵌）→ 景川写进提示词；全剧配乐方案+版权 → 闻笙；后期混音 → 陆离。
> 吸收来源：seedance-20 三层音乐库 + Suno 母题变奏法（微信文章）+ beatra 槽位制 + aladin 规划层。
> Contract 结构：①契约要素 ②选择表 ③修复规则。

## ① 契约要素（每个含声镜头必齐 4 项）

1. **三层世界声**（音乐与对白不得抹掉这三层）：
   - **A1 环境层**：证明地点/时间/天气/空间大小（风声/雨声/房间底噪/街道远近/电流嗡鸣）——一个稳定声学空间一个底床，换场景/时间/天气必须换底床或给动机化声音桥
   - **A2 动作层**：证明身体与物体接触（脚步/衣料/椅子/杯盏/纸/器械），只写画面可见动作，时机与材质必须匹配
   - **A3 点效层**：标记高信息事件（门铃/手机震动/钥匙落地/锁响），稀疏使用，一个 cue 独占那个瞬间
2. **音乐 cue 四要素**：进入点（放在**可见转折点**：门开/消息到/做决定/关键词落/威胁暗示）+ 情绪方向 + 能量 + **退出**（停止/解决/淡出/切静默，必须写）。
3. **安全时长（music_window）**：**不默认全片 BGM**——只在改变情绪方向时加短 cue；音乐窗口 ≤ 镜头实际时长（15 秒 clip 内一 cue；30 秒 clip 可一段完整但紧凑的弧线：进入/发展/峰值/释放/退出写清）。**跨生成不承诺旋律连续**（要全剧主题统一走第②节母题法或槽位法）。
4. **对白优先**：关键台词前音乐降至近静默，人声干爽清晰，尾词后允许一个短 accent 即止；台词段音乐 ducking。

## ② 选择表

### A. 短 cue 情绪节奏矩阵（镜头级，景川用）

| 场景 | 乐器倾向 | 速度起始 | cue 用法 |
|---|---|---|---|
| 恋爱/温暖 | 稀疏钢琴、轻弦乐、软吉他 | 70-90 BPM | 对视/动作后进入，本 clip 内解决 |
| 悬疑/恐怖 | 低脉冲、克制电子氛围 | 60-100 BPM | 保持低能量，一个高细节或切静默 |
| 动作/追逐 | 打击感电子/管弦织体 | 110-160 BPM | 支撑追逐，**决定性接触前切掉**让撞击清晰 |
| 悲伤/离别 | 大提琴、孤独钢琴、长音 | 50-70 BPM | 音符要少，人声呼吸周围留静默 |
| 崛起/反转 | 渐进管弦/后摇式爬升 | 100-130 BPM | 一次爬升一个峰值，然后解决 |
| 日常/轻快 | 轻原声、口哨感/极简电子 | 90-120 BPM | cue 很小，环境与对白为主 |

### B. 剧情阶段 patterns（可直接改写的提示词文案）

- 开场钩：`Music: one low cinematic pulse enters on the reveal, rises for 3 seconds, then stops; wind and the first metallic impact remain louder.`
- 情绪铺垫：`Music: sparse soft piano notes begin after the character looks down, remain quiet under breathing, and resolve within 8 seconds; room tone stays present.`
- 冲突升级：`Music: short tense ostinato enters only as the pursuit begins, accelerates for 7 seconds, then cuts on the door slam; footsteps and breath dominate.`
- 高潮/反转：`Music: one brief orchestral surge begins after the decisive contact, peaks on the reaction, and fully resolves before 12 seconds; the impact transient stays clearest.`

### C. 槽位制全剧配乐包（整季/整剧用，单集走缩量口径，闻笙用，吸收 beatra score-pack）

**规模按范围缩量**：单集试制只配当前集实际命中的可复用床/cue，不强制七类齐全；整季或整剧再按已出现的情绪功能扩成槽位包（紧张/恋爱/喜感/虐心/追逐/揭晓/片尾底乐按需，不设首数配额）。每槽位字段：**用途 | 情绪 | 节奏感 | 乐器 | 能量 | 目标时长**。铁律：`instrumental` 不带歌词；**给对白留位置**写成提示词方向（如 "low strings, room for dialogue, about 45 seconds, no vocals"）；时长只写进提示词不承诺精确秒数；交付带标签曲名（Tension 01…）先试听再进剪辑；真实时长以返回为准。

### D. 母题变奏法（要全剧主题身份统一时用，吸收 Suno 文章）

1. 先定 **4-8 音母题**（轮廓/节奏指纹/收束方式三个识别点）
2. 生成弦乐为主、旋律克制的**母版**（谨慎钢琴吉他——起音太清易抢戏；弦乐长音做氛围底层）
3. 用**六轴变奏**出场景分支：旋律完整度（完整→三音片段→两音影子→只留节奏）/ 音区 / 织体密度 / 脉冲 / 和声稳定度 / 空间与动态
4. 提示词四问：戏剧功能？旋律出现程度？哪组乐器前景哪组铺底？给对白留多少空间？
5. Exclude 清单持续排除：piano/acoustic guitar/vocals/choir/drum kit/trailer hits/heroic melody/pop structure
6. 变奏示例：紧张=母题压进低音弦乐切分脉冲（108BPM）；正能量=再和声到大调（96BPM）；温柔=中提琴大提琴接力（64BPM）；缓慢=母题拉成长音取消脉冲（42BPM）

### E. 曲库检索路径（闻笙出检索词，用户/剪辑下载）

按授权类型分组，不把「royalty-free」误写成「免费」：YouTube 音频库 / Mixkit / Pixabay / FMA 可检索免费或开放授权条目；爱给 / 淘声 / 耳聆网须逐曲核许可证；Epidemic 属订阅制/单曲许可的授权曲库。检索词按「情绪+曲风+强度」组合（如「紧张 弦乐 ostinato 中强」），按情绪连续段合并分段，标淡入淡出；最终是否可商用只看该曲下载时适用的许可证据。

## ③ 修复规则（音频块拒绝检查，命中即重写）

| 失败 | 处理 |
|---|---|
| 习惯性全片 BGM | 改为只在情绪转折点加短 cue，其余静默/环境声承载 |
| 音乐窗口超 clip 时长 | 砍到 ≤ 实际时长；30s 以上弧线拆清进入/峰值/退出 |
| 音乐盖对白 | 台词前降近静默 + ducking；对白 0dB 不动 |
| 多声部等音量堆叠 | 层级重排：A1 低持续 / A2 清晰同步 / A3 一 cue 短暂前置 |
| cue 在 clip 尾未解决 | 补退出（停止/解决/淡出/切静默） |
| 声称跨生成旋律连续 | 改母题法（同主题基因）或接受 clip-local；不写「无缝循环」 |
| 换场景不换环境底床 | 新空间给新 ambience 契约或动机化声音桥 |
| 用情绪词代替戏剧任务（「悲伤」没说谁失去什么） | 回 dim-performance 补戏剧任务再配乐 |
| 版权不清 | 见下「版权自查」 |

## 版权自查（闻笙执行，进交付核对）

1. **供应商级权利矩阵（每首/每次生成必填）**：`provider / plan / generated_at（或 downloaded_at）/ terms_version（或 license_url）/ commercial_use / attribution / post_subscription_use / evidence_saved`。未知写 `not_verified`，不得凭「AI 生成」或「royalty-free」自动判可商用。
2. AI 生成音乐按具体供应商与生成时适用条款核验：例如使用 Suno 时才套用其免费/付费计划及生成时点规则；AIVA、Adobe 等按各自许可，不把某一家规则泛化给所有平台。保存提示词、生成时间、计划/订阅状态、条款版本与后期修改记录。
3. 授权曲库逐曲核对免费、订阅制、单曲许可、CC0、CC-BY 或其他许可；CC-BY 按原许可署名，Epidemic 等订阅制曲库另核项目/频道覆盖和订阅结束后的使用边界，留存授权页或下载凭证。
4. beatra 类包的所有权或商用声明以下载当日条款为准，留存授权页；翻唱、采样、使用现有歌曲片段仍需词曲与录音**双授权**，缺一不用。

> 供应商差异示例（核验于 2026-09-01）：[Suno 商用权说明](https://help.suno.com/en/articles/9601665) / [AIVA Licensing](https://www.aiva.ai/licensing) / [Epidemic Sound Commercial Plan](https://www.epidemicsound.com/commercial-subscription/)。链接只作核验入口，项目证据须保存生成/下载当日适用条款版本。
