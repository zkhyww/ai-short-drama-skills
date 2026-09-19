# 公共案例索引

> 本页由 `metadata.json` 机械生成。它只发布来源元数据与原创中性简述，不发布第三方提示词全文、媒体、本机路径，也不授予再发布许可。模型与效果状态均按来源记录，未复现不等于可复现；案例不得新增或改写项目正典事实。

使用时先按当前创作、对白或制作问题缩小候选；用途标签只供发现，不证明适配。存在有效私有绑定时，所选 ID 必须先匹配 canonical metadata，而不是本页发布快照；再核输入缺项、原文完整性、模型声称与依据、来源/取得/观看/复现状态，获准且单条 TXT 可达时才读取，不整库注入。

没有绑定时，本页及包内 metadata 只可帮助发现公开候选，不能据此声称已读本地原文；使用现有规则做原创设计并如实写明证据状态。逐条缺输入、归属提醒与原始状态说明保存在同 ID metadata 记录中；公开可读不等于取得原文或再发布许可。

## 本地绑定与维护

私有绑定写入同目录且已被 Git 忽略的 `local-config.json`，只含 `canonical_metadata`、`local_root`、`local_view`。安装副本中的 metadata 是发布快照；存在绑定时，`validate`、`build`、`add` 都使用 canonical metadata，绑定失效会明确失败，不会静默回退快照。该失败只停止案例消费，不阻塞不依赖案例的原创规划。没有绑定时仍可读取和生成包内公共视图。可用 `--config` 显式选择配置；同次调用中的路径参数逐项覆盖该配置。只显式传 `--metadata` 而不传 `--config` 时视为独立上下文，不自动混用私有绑定。

```powershell
python drama-studio/scripts/case_library.py validate
python drama-studio/scripts/case_library.py build
python drama-studio/scripts/case_library.py add --record '<新增或补缺记录.json>' --author-record '<可选的新作者记录.json>'
python drama-studio/scripts/case_library.py build --metadata '<显式metadata.json>' --public-view '<显式公共README.md>' --local-root '<显式本地案例根>' --local-view '<显式本地入口.md>'
```

正常新增或同 ID 补缺必须走 `add`，不得改历史 `snapshot.original_case_count`。`add` 可在同一事务加入一个新作者与一个案例：先核作者、真实 TXT/locator、标准化 SHA-256、完整 schema、重复 ID/指纹及别名，再一起刷新 metadata、公共视图和本地 `开始这里.md`；任一步失败都不改这三份文件。新 ID 才追加；同 ID 只填 `null`、空字符串/数组/对象，完全相同的值幂等，非空冲突拒绝。只有经批准的非空事实更正才直接编辑 canonical metadata，保留可审查 diff，再运行 `validate` 与 `build`。每条取得的第三方原文独立保存为纯原文 TXT，只保留真实原文；来源、授权与取得状态写对应 metadata，现有字段不足时写同 ID 本地来源旁档；我方归纳另存并标明，成果以稳定 ID 与 locator 回指唯一原文，不造第二份混合真源。同一帖子含多段不同原文时按不同指纹保留。新增材料先提取问题、条件、机制、落位、输出核验、排除项与来源，再按项目事实/媒介/模型适配，并用不同主体和相反条件对照；获得持久化/升格授权后只把原创方法合并进原主责规则位。已读、已收集或用户喜欢不证明真实媒体效果，文本测试只能支持设计改进声明。

## 动作与打斗

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| ACT-001 | 御剑群战：用于研究打斗、御剑、群战、FPV。 | 打斗 / 御剑 / 群战 / FPV | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@df_reno](https://x.com/df_reno) / [原帖](https://x.com/df_reno/status/2097677503422976328) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ACT-002 | 古寺双武僧：用于研究武僧拳脚、连续攻防、环境受力。 | 武僧拳脚 / 连续攻防 / 环境受力 | Seedance 2.5／Pollo · 视频（author_or_source_claim_unverified） | [@lansenai](https://x.com/lansenai) / [原帖](https://x.com/lansenai/status/2098232543611121832) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ACT-003 | 雪境双刀追战：用于研究雪境追战、双色刀气、连续空间位移。 | 雪境追战 / 双色刀气 / 连续空间位移 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@Chengzilhy](https://x.com/Chengzilhy) / [原帖](https://x.com/Chengzilhy/status/2098326362801221835) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ACT-006 | 雨夜缠斗与伤势累积：用于研究抱缠摔投、压制反制、伤势持续、重力失衡、雨水。 | 抱缠摔投 / 压制反制 / 伤势持续 / 重力失衡 / 雨水 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@lansenai](https://x.com/lansenai) / [原帖](https://x.com/lansenai/status/2095035960170102871) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| ACT-007 | 车厢三人围堵与错位脱困：用于研究多人空间、走位脱困、借墙转体、时间拉伸、手扶立杆。 | 多人空间 / 走位脱困 / 借墙转体 / 时间拉伸 / 手扶立杆 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@CharaspowerAI](https://x.com/CharaspowerAI) / [原帖](https://x.com/CharaspowerAI/status/2095225284807074072) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| ACT-004 | 玄幻双人重击：用于研究打斗、玄幻、双人重击。 | 打斗 / 玄幻 / 双人重击 | 模型未核明 · 视频（author_or_source_claim_unverified） | [@lansenai](https://x.com/lansenai) / [原帖](https://x.com/lansenai/status/2097629748805484837) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ACT-005 | 纯剑术高速近战：用于研究双人剑术、高速近战、伪一镜到底。 | 双人剑术 / 高速近战 / 伪一镜到底 | Seedance 2.0 · 视频（author_or_source_claim_unverified） | [@Arvin010717](https://x.com/Arvin010717) / [原帖](https://x.com/Arvin010717/status/2098282939796905997) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ACT-008 | GTA恋人争执与托盘反弹：用于研究连续攻防、只闪避不反击、亲吻打断、托盘接触、子弹时间、实体环绕。 | 连续攻防 / 只闪避不反击 / 亲吻打断 / 托盘接触 / 子弹时间 / 实体环绕 | 模型未注明（不能确认为2.5） · 视频（author_or_source_claim_unverified） | [@yura_elkin](https://x.com/yura_elkin) / [原帖](https://x.com/yura_elkin/status/2098370471414677906) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| ACT-009 | 石院近身肉搏与累积破坏：研究双人近身攻防中接触、受力、位移与环境破坏的连续关系，以及摄影如何显现打击点；强化物理风格候选，不作为所有打斗的强度模板。 | 打斗 / 近身武侠 / 连续攻防 / 接触与受力 / 累积破坏 / 身份连续 / 攻击轴线 / 命中点 / 强化物理特效 | 模型未核明 · 视频（not_stated_in_retrieved_post） | [@lansenai](https://x.com/lansenai) / [原帖](https://x.com/lansenai/status/2098529517736476962) | metadata_only；complete_as_recorded；媒体 downloaded_technical_metadata_checked_not_viewed_not_reproduced；许可 unknown |
| ACT-010 | 巴黎连通空间枪战与近身交锋：15秒风格化枪战片段：以巷道、庭院和室内的相连地理组织枪械动作与近身交锋，结合声效、行动中切景和末拍收束；补充黑帮动作片的空间连续参考。 | 枪战 / 黑帮片参考 / 犯罪动作片参考 / 连通空间 / 巷道到室内 / 枪械与近身交锋 / 行动驱动切镜 / 枪声与碰撞 / 风格化动画 | Seedance 2.5 · 视频（author_claim_not_reproduced） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2099139902373765297) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| ACT-011 | 末日街区人犬协同枪战：15秒末日街区枪战片段：持枪主角与犬伙伴保持共同目标和可辨身份，结合空中、低位与近景，以及战后远景形成关系与规模对照；不是写实黑帮题材实测。 | 枪战 / 黑帮片参考 / 末日动作 / 人犬协同 / 伙伴关系 / 群体威胁 / 角色辨识 / 战后收束 / 远景规模 / 风格化动画 | Seedance 2.5 / TapNow · 视频（author_claim_not_reproduced） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2099095658804154778) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |

## 玄幻特效与巨物

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| VFX-001 | 真人渐变漫画 单镜头：用于研究长镜头、人物局部风格渐变、环境保真。 | 长镜头 / 人物局部风格渐变 / 环境保真 | Seedance 2.5／Dreamina · 视频（author_or_source_claim_unverified） | [@CharaspowerAI](https://x.com/CharaspowerAI) / [原帖](https://x.com/CharaspowerAI/status/2098109389659889692) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| VFX-005 | 有限兽群与巨兽状态持续：用于研究人兽交互、有限敌群、巨兽比例、受击后碎屑重力、引敌聚集、收剑接触。 | 人兽交互 / 有限敌群 / 巨兽比例 / 受击后碎屑重力 / 引敌聚集 / 收剑接触 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@Arvin010717](https://x.com/Arvin010717) / [原帖](https://x.com/Arvin010717/status/2097930657213395038) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| VFX-006 | 海面法相冰封与碎裂沉降：用于研究法术持续、冻结状态、巨龙法相、海浪交互、粒子沉降。 | 法术持续 / 冻结状态 / 巨龙法相 / 海浪交互 / 粒子沉降 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@df_reno](https://x.com/df_reno) / [原帖](https://x.com/df_reno/status/2097920751693336663) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| VFX-002 | 太极水阵：用于研究单人太极、水流控制、技能展示。 | 单人太极 / 水流控制 / 技能展示 | 模型未核明 · 视频（author_or_source_claim_unverified） | [@lansenai](https://x.com/lansenai) / [原帖](https://x.com/lansenai/status/2097319055829201188) | metadata_only；unknown；媒体 not_independently_verified；许可 unknown |
| VFX-003 | 竹湖百米神龙：用于研究巨物尺度、舞剑召龙、登龙头。 | 巨物尺度 / 舞剑召龙 / 登龙头 | 模型未核明 · 视频（author_or_source_claim_unverified） | [@df_reno](https://x.com/df_reno) / [原帖](https://x.com/df_reno/status/2096562691792163009) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| VFX-004 | 灵魂剥离：用于研究掌击触发、灵魂剥离、城市折叠。 | 掌击触发 / 灵魂剥离 / 城市折叠 | 模型未核明 · 视频（author_or_source_claim_unverified） | [@df_reno](https://x.com/df_reno) / [原帖](https://x.com/df_reno/status/2095854115192701426) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |

## 角色与参考资产

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| REF-011 | 幼鸟成长与同伴接纳：用于研究年龄变化、物种设计、身份连续、孤独转归属。 | 年龄变化 / 物种设计 / 身份连续 / 孤独转归属 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2097182411435938057) | metadata_only；unknown；媒体 not_reviewed_or_reproduced；许可 unknown |
| REF-001 | 女性四视图：用于研究角色、写实、四视图。 | 角色 / 写实 / 四视图 | GPT Image 2.5 · 生图（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2097698694296686623) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-002 | 男性四视图：用于研究角色、写实、四视图。 | 角色 / 写实 / 四视图 | GPT Image 2.5 · 生图（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2097698694296686623) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-003 | 五人角色表：用于研究摄影、多人传递手机、窗侧光、沙龙三视角、房间一致性。 | 摄影 / 多人传递手机 / 窗侧光 / 沙龙三视角 / 房间一致性 | GPT Image 2 · 生图（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2096989398005145678) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-004 | 雾巷双人角色表：用于研究场景、雾夜窄巷、暖煤气灯、湿石板、快速切镜。 | 场景 / 雾夜窄巷 / 暖煤气灯 / 湿石板 / 快速切镜 | GPT Image 2.5 · 生图（author_or_source_claim_unverified） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2098056422223167827) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-005 | 雨夜人物参考表：用于研究摄影、雨夜街道、远景到侧向跟拍、轴线与终点、车灯闪电。 | 摄影 / 雨夜街道 / 远景到侧向跟拍 / 轴线与终点 / 车灯闪电 | 生图模型见来源 · 生图（author_or_source_claim_unverified） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2097359965987934264) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-006 | 哪吒三视图：用于研究角色一致性、三视图、白模动作。 | 角色一致性 / 三视图 / 白模动作 | 生图模型未注明 · 生图（author_or_source_claim_unverified） | [@laowangbabababa](https://x.com/laowangbabababa) / [原帖](https://x.com/laowangbabababa/status/2098246364895547453) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-007 | 送货员参考图模板（参数缺失）：用于研究声音视点、固定对白、惊慌转尴尬、多人互动。 | 声音视点 / 固定对白 / 惊慌转尴尬 / 多人互动 | 生图模板，模型见来源 · 生图（author_or_source_claim_unverified） | [@techhalla](https://x.com/techhalla) / [原帖](https://x.com/techhalla/status/2098334086523683021) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-008 | 咖啡师角色表：用于研究温暖服务表演、职业动作、服装妆发一致、咖啡器具与手部连续、室内美术。 | 温暖服务表演 / 职业动作 / 服装妆发一致 / 咖啡器具与手部连续 / 室内美术 | GPT Image 2 · 生图（author_or_source_claim_unverified） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2096967412067242383) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-009 | 群像替换配套图1：学生群像参考表：用于研究备选、中央人物、人群分别替换、原动作运镜环境保留。 | 备选 / 中央人物 / 人群分别替换 / 原动作运镜环境保留 | 生图模型未注明 · 生图（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2097356202577739977) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-010 | 群像替换配套图2：单人参考表：用于研究备选、中央人物、人群分别替换、原动作运镜环境保留。 | 备选 / 中央人物 / 人群分别替换 / 原动作运镜环境保留 | 生图模型未注明 · 生图（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2097356202577739977) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| REF-012 | 巴黎行动者戏剧化角色海报：单人物戏剧化角色海报提示词：中心英雄形象、服装轮廓和红色图形背景配合，作为枪战片段的视觉配套；不是三视图或完整人物圣经。 | 枪战配套 / 角色参考 / 人物海报 / 服装轮廓 / 视觉风格 / 中心构图 / 既有IP二创 | GPT Image 2.5 · 角色海报（author_claim_not_reproduced） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2099139896438919623) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| REF-013 | 末日人犬搭档双区角色海报：人犬搭档双区角色海报提示词：用人物与动物的体型、配色、服装和位置区分搭档，作为协同动作场面的视觉配套；不是全部上游参考图。 | 枪战配套 / 人犬搭档 / 角色参考 / 双区构图 / 视觉区分 / 伙伴关系 / 既有IP二创 | GPT Image 2.5 · 角色海报（author_claim_not_reproduced） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2099095652638581123) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| BLD-007 | 从已定剧情补齐群体角色参考：利用既有剧情和主角参考，先提出配角、团队与反派群体的候选资产需求；属于分组初稿，不等同于每个故事角色的正式独立参考。 | 角色资产缺口 / 群像候选 / 服装基线 / 背景群演 / 分步迭代 / 角色分组 | GPT Image 2.5 · 生图（被引原帖声称）（quoted_author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2099415835118825732) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| REF-016 | 平民群演差异化补图：基于已有剧情与环境补充平民群演候选，并在后续一张图中调整服装、风格或物种；物种变化仅适用于允许该设定的项目。 | 平民群演 / 资产补缺 / 多样化候选 / 群体服装 / 世界观约束 / 多图迭代 | GPT Image 2.5 / Codex · 生图（author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2098938715200692297) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| REF-015 | 群像角色差异化迭代：接续角色群体初稿，用发型、鞋、服装与配饰细化差异，并修改初稿年龄范围；演示局部改稿，不是独立可裸跑的完整生成提示词。 | 角色差异化 / 局部修改 / 校服继承 / 发型配饰 / 群演候选 / 版本替代 | GPT Image 2.5 · 生图（被引原帖声称）（quoted_author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2099415835118825732) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |

## 场景光影与美术

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| ART-001 | 雾巷暖灯场景：用于研究场景、雾夜窄巷、暖煤气灯、湿石板、快速切镜。 | 场景 / 雾夜窄巷 / 暖煤气灯 / 湿石板 / 快速切镜 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2098056422223167827) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ART-002 | 庭院人物场景：用于研究场景、庭院、人物首帧。 | 场景 / 庭院 / 人物首帧 | GPT Image 2.5 · 生图（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2097698694296686623) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ART-003 | 草地男性人物场景：用于研究摄影、黄金时段、草地、双人甩镜、自然逆光。 | 摄影 / 黄金时段 / 草地 / 双人甩镜 / 自然逆光 | GPT Image 2 · 生图（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2094819241916801165) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ART-004 | 草地女性人物场景：用于研究摄影、黄金时段、草地、双人甩镜、自然逆光。 | 摄影 / 黄金时段 / 草地 / 双人甩镜 / 自然逆光 | GPT Image 2 · 生图（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2094819241916801165) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ART-005 | 沙龙三视角场景：用于研究摄影、多人传递手机、窗侧光、沙龙三视角、房间一致性。 | 摄影 / 多人传递手机 / 窗侧光 / 沙龙三视角 / 房间一致性 | GPT Image 2 · 生图（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2096989398005145678) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ART-006 | 演武场：用于研究角色一致性、三视图、白模动作。 | 角色一致性 / 三视图 / 白模动作 | 生图模型未注明 · 生图（author_or_source_claim_unverified） | [@laowangbabababa](https://x.com/laowangbabababa) / [原帖](https://x.com/laowangbabababa/status/2098246364895547453) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| ART-007 | 照片出鱼与鸟形投影：用于研究诡异氛围、锁定俯拍、软日光、异形投影、物体跨媒介。 | 诡异氛围 / 锁定俯拍 / 软日光 / 异形投影 / 物体跨媒介 | 未注明 · 视频（author_or_source_claim_unverified） | [@umesh_ai](https://x.com/umesh_ai) / [原帖](https://x.com/umesh_ai/status/2096179627853267373) | metadata_only；unknown；媒体 not_reviewed_or_reproduced；许可 unknown |
| ART-008 | 同建筑街道反打补图：从已有场景扩展同建筑风格的街道反打视向；配套作者回复强调区分正面与反打参考，适用于确有相反视向缺口时。 | 场景反打 / 同场景多视向 / 建筑风格继承 / 参考职责 / 空间连续 / 资产补缺 | GPT Image 2.5 / Codex · 生图（author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2098938715200692297) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |

## 镜头与空间运动

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| CAM-001 | 手机随行跟拍（缺尾）：用于研究摄影、手机随行、一镜到底。 | 摄影 / 手机随行 / 一镜到底 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2097698694296686623) | metadata_only；partial；媒体 not_independently_verified；许可 unknown |
| CAM-002 | 草地黄金时段甩镜：用于研究摄影、黄金时段、草地、双人甩镜、自然逆光。 | 摄影 / 黄金时段 / 草地 / 双人甩镜 / 自然逆光 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2094819241916801165) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| CAM-003 | 五人传递手机：用于研究摄影、多人传递手机、窗侧光、沙龙三视角、房间一致性。 | 摄影 / 多人传递手机 / 窗侧光 / 沙龙三视角 / 房间一致性 | Seedance 2.5／Higgsfield · 视频（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2096989398005145678) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| CAM-004 | 雨夜街道追踪：用于研究摄影、雨夜街道、远景到侧向跟拍、轴线与终点、车灯闪电。 | 摄影 / 雨夜街道 / 远景到侧向跟拍 / 轴线与终点 / 车灯闪电 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2097359965987934264) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| CAM-005 | ATV多视点无缝转场：用于研究多视点转场、同车连续性、地形接续。 | 多视点转场 / 同车连续性 / 地形接续 | Seedance 2.5／Dreamina · 视频（author_or_source_claim_unverified） | [@LudovicCreator](https://x.com/LudovicCreator) / [原帖](https://x.com/LudovicCreator/status/2098109356088656037) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| CAM-006 | 地心飞行一镜到底：用于研究长镜头、地形连续穿越、无剪切 FPV。 | 长镜头 / 地形连续穿越 / 无剪切 FPV | Seedance 2.5／Dreamina · 视频（author_or_source_claim_unverified） | [@LudovicCreator](https://x.com/LudovicCreator) / [原帖](https://x.com/LudovicCreator/status/2097384547369255038) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| CAM-010 | 白馆潜入的视线盲区与反射信息：用于研究悬疑惊悚、视线盲区、反射延迟、白色室内、琥珀光、空间建立。 | 悬疑惊悚 / 视线盲区 / 反射延迟 / 白色室内 / 琥珀光 / 空间建立 | Seedance 2.5 / Dreamina · 视频（author_or_source_claim_unverified） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2096887699357446328) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| CAM-007 | 城市摄影集锦：用于研究摄影、城市航拍、巷道跟拍、升镜、景别组合、音乐卡点。 | 摄影 / 城市航拍 / 巷道跟拍 / 升镜 / 景别组合 / 音乐卡点 | MiniMax H3；作者另称试过2.5 · 视频（author_or_source_claim_unverified） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2096242247490560050) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| CAM-008 | 稳定俯视体育场制作：用于研究稳定机位、前三分之四俯视、手工制作、缩时、体育场空间结构。 | 稳定机位 / 前三分之四俯视 / 手工制作 / 缩时 / 体育场空间结构 | MiniMax H3 · 视频（author_or_source_claim_unverified） | [@aimikoda](https://x.com/aimikoda) / [原帖](https://x.com/aimikoda/status/2095141166962311555) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| CAM-009 | 霓虹摩托连续跟拍：用于研究长镜头、侧后跟拍接续、人物轮廓连续。 | 长镜头 / 侧后跟拍接续 / 人物轮廓连续 | MiniMax H3／Hailuo · 视频（author_or_source_claim_unverified） | [@LudovicCreator](https://x.com/LudovicCreator) / [原帖](https://x.com/LudovicCreator/status/2097746917904052662) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| CAM-011 | 门厅楼梯的空间范围与上下位置锁定：用于研究空间建立、场景边界、上下位置、三角色限制、异版本对照。 | 空间建立 / 场景边界 / 上下位置 / 三角色限制 / 异版本对照 | Seedance 2.0 · 视频（author_or_source_claim_unverified） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2095913793607843990) | metadata_only；unknown；媒体 not_reviewed_or_reproduced；许可 unknown |
| CAM-012 | 高速打斗运镜手册：按冲刺、错位、扫腿、腾空、命中和击退等动作任务选择摄影轨迹、景别与焦点的参考手册；分条选用，不把一镜到底或固定停顿作为通用要求。 | 打斗 / 运镜参考手册 / 动作轨迹 / 攻击方向 / 攻防换位 / 命中点 / 击退距离 / 景别 / 焦点切换 | Seedance（具体版本未提供）（user_label_not_independently_verified） | 用户提供（原作者未核） | metadata_only；complete_as_user_supplied；媒体 no_media_provided_not_reproduced；许可 unknown |
| CAM-013 | 宫殿时尚十姿态连续运镜：以肩部、头发、手掌遮挡和动作匹配连接十个时尚姿态，研究人物动作驱动的摄影转场、服装身份连续及末拍收束。 | 人物展示 / 时尚摄影 / 动作驱动运镜 / 遮挡转场 / 空间连续 / 节拍收束 | Seedance 2.5 / ImagineArt · 视频（author_claim_not_reproduced） | [@ZephyraLeigh](https://x.com/ZephyraLeigh) / [原帖](https://x.com/ZephyraLeigh/status/2098003837990945254) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |

## 人物表演与关系

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| PER-001 | 异星假日多人互动：用于研究人物跨镜一致、朋友互动、微笑与舞蹈、环境声与远处音乐。 | 人物跨镜一致 / 朋友互动 / 微笑与舞蹈 / 环境声与远处音乐 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@techhalla](https://x.com/techhalla) / [原帖](https://x.com/techhalla/status/2097521124154241509) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| PER-002 | 克制失落与黑色幽默：用于研究克制期待转失落、黑色幽默、人犬身份、纸条跨场延续、固定结尾特写。 | 克制期待转失落 / 黑色幽默 / 人犬身份 / 纸条跨场延续 / 固定结尾特写 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@aimikoda](https://x.com/aimikoda) / [原帖](https://x.com/aimikoda/status/2098021955899183300) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| PER-003 | 维修工生活与群体调度：用于研究普通人的克制表演、疲惫与微笑、邻里互助、服装工具包一致、电梯酒馆等群体调度。 | 普通人的克制表演 / 疲惫与微笑 / 邻里互助 / 服装工具包一致 / 电梯酒馆等群体调度 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@aimikoda](https://x.com/aimikoda) / [原帖](https://x.com/aimikoda/status/2094815422063272145) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| PER-004 | 情侣接话与情绪递进：用于研究情侣自然接话、怀疑与短暂安心、克制嫉妒喜剧、服饰首饰一致、环境文字配合表演。 | 情侣自然接话 / 怀疑与短暂安心 / 克制嫉妒喜剧 / 服饰首饰一致 / 环境文字配合表演 | Seedance 2.5／Pollo · 视频（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2095548188765905094) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| PER-005 | 咖啡馆人物与道具：用于研究温暖服务表演、职业动作、服装妆发一致、咖啡器具与手部连续、室内美术。 | 温暖服务表演 / 职业动作 / 服装妆发一致 / 咖啡器具与手部连续 / 室内美术 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@TechieBySA](https://x.com/TechieBySA) / [原帖](https://x.com/TechieBySA/status/2096967412067242383) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| PER-006 | 篝火怀疑转恐惧：用于研究恐惧、群体反应、空间关系、音色冒用。 | 恐惧 / 群体反应 / 空间关系 / 音色冒用 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@aimikoda](https://x.com/aimikoda) / [原帖](https://x.com/aimikoda/status/2094159653861032004) | metadata_only；unknown；媒体 not_reviewed_or_reproduced；许可 unknown |
| PER-007 | 离别前的克制告白：用于研究悲伤、亲密、克制告白、衣物道具一致。 | 悲伤 / 亲密 / 克制告白 / 衣物道具一致 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@aimikoda](https://x.com/aimikoda) / [原帖](https://x.com/aimikoda/status/2093770121848254584) | metadata_only；unknown；媒体 not_reviewed_or_reproduced；许可 unknown |
| PER-008 | 巨人与小鼠的温柔照护：用于研究体型差、照护、尴尬转专注、稳定双人镜头。 | 体型差 / 照护 / 尴尬转专注 / 稳定双人镜头 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2097967512759492846) | metadata_only；unknown；媒体 not_reviewed_or_reproduced；许可 unknown |
| PER-009 | 异种支持小组的分角色反应：用于研究群体关系、哭泣、沉默、异种角色、服装一致。 | 群体关系 / 哭泣 / 沉默 / 异种角色 / 服装一致 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2096982573738033395) | metadata_only；unknown；媒体 not_reviewed_or_reproduced；许可 unknown |
| PER-010 | 虚荣掩饰到当众羞愧：用于研究群体压力、假笑、羞愧、不同年龄、服装锁定。 | 群体压力 / 假笑 / 羞愧 / 不同年龄 / 服装锁定 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2097324379629658318) | metadata_only；unknown；媒体 not_reviewed_or_reproduced；许可 unknown |

## 声音对白与音乐

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| SND-001 | 送货员声音视点：用于研究声音视点、固定对白、惊慌转尴尬、多人互动。 | 声音视点 / 固定对白 / 惊慌转尴尬 / 多人互动 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@techhalla](https://x.com/techhalla) / [原帖](https://x.com/techhalla/status/2098334086523683021) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| SND-002 | 异星旅行者随拍：用于研究人物跨镜一致、自然随拍、呼吸与风声、声音远近。 | 人物跨镜一致 / 自然随拍 / 呼吸与风声 / 声音远近 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@techhalla](https://x.com/techhalla) / [原帖](https://x.com/techhalla/status/2097626129989280077) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| SND-003 | 母女对白与听者口型：用于研究双人多轮对白；说话者口型分配；画外回应；情绪逐渐变化。 | 双人多轮对白；说话者口型分配；画外回应；情绪逐渐变化 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2084576780392771813) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| SND-004 | 葬礼后双人声线连续：用于研究同一人物声线保持；双人轮流发言；画内、画外声音；跨镜连续。 | 同一人物声线保持；双人轮流发言；画内 / 画外声音；跨镜连续 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2084577327451676686) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| SND-005 | Citypop后台至舞台：用于研究演唱动作与场面连续；工作人员提醒；Citypop演唱；观众欢呼。 | 演唱动作与场面连续；工作人员提醒；Citypop演唱；观众欢呼 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [ByteDance Seed](https://seed.bytedance.com/en/) / [原帖](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| SND-006 | 独唱乐队合唱接力：用于研究音乐角色依次加入；钢琴起奏、独唱、弦乐、合唱及掌声；多人音乐表演。 | 音乐角色依次加入；钢琴起奏、独唱、弦乐、合唱及掌声；多人音乐表演 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [ByteDance Seed](https://seed.bytedance.com/en/) / [原帖](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| SND-008 | 笛声停奏慢速返回与单人旁白：用于研究音乐驱动叙事、停奏、速度变化、风声收尾、英文旁白、单人声源。 | 音乐驱动叙事 / 停奏 / 速度变化 / 风声收尾 / 英文旁白 / 单人声源 | Seedance 2.5 · 视频（author_or_source_claim_unverified） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2097270514561511435) | metadata_only；partial；媒体 not_reviewed_or_reproduced；许可 unknown |
| SND-007 | 婚礼致辞停顿与现场弦乐骤停：用于研究停顿、温柔声线反差、现场弦乐、静默、尴尬掌声、原生音。 | 停顿 / 温柔声线反差 / 现场弦乐 / 静默 / 尴尬掌声 / 原生音 | 未明示 · 视频（author_or_source_claim_unverified） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2096928597822890021) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| SND-009 | 海滨双人对唱与合唱收尾：研究女声开场、男声应答、双人合唱与纯器乐尾段的衔接，以及108 BPM编配变化、口型可见性和双人关系表演。 | 唱歌 / 英文演唱 / 双人对唱 / 合唱 / 音乐剧 / 原生人声 / 108 BPM / 分段编配 / 口型 / 关系表演 | Seedance 2.5 / WaveSpeed AI · 视频（author_claim_not_reproduced） | [@ZaraIrahh](https://x.com/ZaraIrahh) / [原帖](https://x.com/ZaraIrahh/status/2086289199280582977) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-010 | 现场演唱与观众接唱：研究歌手与观众接唱、麦克风互动、舞台乐队位置和现场声场；区分原生舞台演唱与录音室式配乐。 | 唱歌 / 英文演唱 / 现场演唱 / 观众接唱 / 麦克风互动 / 手持摄影 / 乐队站位 / 现场混音 | Seedance 2 Mini 与 Seedance 2.0 Full 对照 · 视频（author_claim_not_reproduced） | [@BrentLynch](https://x.com/BrentLynch) / [原帖](https://x.com/BrentLynch/status/2066576320193327424) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-011 | 民谣行进演唱与音标歌词：研究有旋律而非朗读的民谣发声、换气分句、音标歌词及行走跟拍；保留作者对乐谱识别方案失败的说明。 | 唱歌 / 英文演唱 / 民谣 / 音标歌词 / 旋律分句 / 呼吸留白 / 行走跟拍 / 能力限制记录 | Seedance 2.0 · 视频（author_claim_not_reproduced） | [@Dheepanratnam](https://x.com/Dheepanratnam) / [原帖](https://x.com/Dheepanratnam/status/2054832402292244586) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-012 | 三人独立乐队与主唱声场：平台文档中的三人乐队示例：按三张人物图绑定主唱、吉他手和鼓手，结合缓慢推进及主唱高于伴奏的声场。 | 唱歌 / 独立摇滚 / 三人乐队 / 多角色参考 / 主唱与伴奏 / 副歌推进 / 室内现场 | Seedance 2.5 / Runware · 视频（provider_documentation_claim_not_reproduced） | [Runware Docs](https://runware.ai/docs) / [原帖](https://runware.ai/docs/models/bytedance-seedance-2-5/guides/multi-reference-production) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-013 | 整首歌音轨驱动MV规划：以最终歌曲音轨为时间依据，生成歌曲分析、分段、歌手分配和逐段MV提示词；用于已完成翻唱音轨的下游规划，不承担翻唱音频制作。 | 二创歌曲 / 已有音轨 / 翻唱MV下游 / 整首歌规划 / 音频时间基准 / 逐句歌手分配 / 分段口型 / Seedance 2.5 / 完整教程 | Seedance 2.5 / OpenArt · 上游MV规划（author_claim_not_reproduced） | [Ai Lockup](https://www.youtube.com/channel/UC2Jl-LpV_J8l-az2GNG3VUQ) / [原帖](https://www.youtube.com/watch?v=-iDVaCl-ZBk) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-014 | 指定歌声音轨驱动角色演唱：以人物图和包含指定歌曲音轨的参考视频驱动角色演唱；原教程的最简完整口型提示词，适用于已定稿翻唱音轨的视频层。 | 二创歌曲 / 翻唱MV下游 / 已有音轨 / 指定歌曲 / 英文演唱 / 人物参考 / 带音轨视频参考 / 口型 | Seedance 2.0 Fast / Kie.ai · 视频（author_claim_not_reproduced） | [Abdullah Yahya](https://abdullahyahya.com/) / [原帖](https://abdullahyahya.com/2026/05/make-realistic-lip-sync-music-videos-with-seedance-2-0/) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-015 | 指定歌曲绿幕演唱与后期换景：以指定歌曲音轨驱动固定机位绿幕演唱，保留自然面部与身体动作，便于后期抠像换背景；不替代音频翻唱制作。 | 二创歌曲 / 翻唱MV下游 / 已有音轨 / 绿幕演唱 / 固定机位 / 后期换景 / 口型 | Seedance 2.0 Fast / Kie.ai · 视频（author_claim_not_reproduced） | [Abdullah Yahya](https://abdullahyahya.com/) / [原帖](https://abdullahyahya.com/2026/05/make-realistic-lip-sync-music-videos-with-seedance-2-0/) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-016 | 原曲改编为木吉他流行女声：Cover风格候选：将已有曲目重新编为木吉他流行女声，指向原旋律保留与轻编配；没有来源音频对照或本轮复现。 | 二创歌曲 / 音频Cover / 歌曲改编 / 换曲风 / 木吉他流行 / 女声 / 保留旋律 / 未复现候选 | Suno Cover · 音频（版本未注明）（third_party_prompt_candidate_not_reproduced） | [Suno AI Prompt Guide（非官方）](https://sunoaipromptguide.org/) / [原帖](https://sunoaipromptguide.org/suno-prompts-for-covers/) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-017 | 原曲改编为爵士男声：Cover风格候选：为已有曲目指定爵士配器与温暖男声，并要求保留原节奏；不是原曲旋律或特定歌手音色的成功证明。 | 二创歌曲 / 音频Cover / 歌曲改编 / 换曲风 / 爵士男声 / 保留节奏 / 未复现候选 | Suno Cover · 音频（版本未注明）（third_party_prompt_candidate_not_reproduced） | [Suno AI Prompt Guide（非官方）](https://sunoaipromptguide.org/) / [原帖](https://sunoaipromptguide.org/suno-prompts-for-covers/) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-018 | 原曲改编为复古合成器女声：Cover风格候选：为已有曲目指定复古合成器、电子鼓和轻盈女声，并要求保留音乐钩子；没有来源音频对照或本轮复现。 | 二创歌曲 / 音频Cover / 歌曲改编 / 换曲风 / 复古合成器 / 女声 / 保留音乐钩子 / 未复现候选 | Suno Cover · 音频（版本未注明）（third_party_prompt_candidate_not_reproduced） | [Suno AI Prompt Guide（非官方）](https://sunoaipromptguide.org/) / [原帖](https://sunoaipromptguide.org/suno-prompts-for-covers/) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-019 | 双人K-pop多机位MV：双人齐舞、个人展示与多景别接续的提示词候选；原文标30秒但分段只写到29秒，没有音轨或口型复现实证。 | K-pop / 双人齐舞 / 多景别 / MV / 换景接续 | Seedance 2.5 / Dreamina · 视频（author_or_source_claim_unverified） | [@Just_sharon7](https://x.com/Just_sharon7) / [原帖](https://x.com/Just_sharon7/status/2083422886686031982) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| SND-020 | 四人涩谷群舞队形转换：四人全身街头群舞，以菱形、横排、涟漪和V形落位组织连续队形；提示词位于作者评论，末尾疑似截断，不能作完整复现模板。 | K-pop / 四人齐舞 / 队形转换 / 全身舞蹈 / 中央位置 / 连续镜头 | Seedance 2.5 / Dreamina · 视频（author_or_source_claim_unverified） | [@Just_sharon7](https://x.com/Just_sharon7) / [原帖](https://x.com/Just_sharon7/status/2086067758970851614) | metadata_only；partial；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |

## 生物载具与复杂交互

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| INT-001 | F1赛车与维修区：用于研究载具操控、轮胎接地、雨水喷溅、维修区多人协作。 | 载具操控、轮胎接地、雨水喷溅、维修区多人协作 | Seedance 2.5／Dreamina · 视频（author_or_source_claim_unverified） | [@CharaspowerAI](https://x.com/CharaspowerAI) / [原帖](https://x.com/CharaspowerAI/status/2096659796212494521) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| INT-002 | 幼虎与母虎环境探索：用于研究非人角色亲子关系、幼虎踩水、攀木、跟随、毛发与植被交互。 | 非人角色亲子关系、幼虎踩水 / 攀木 / 跟随、毛发与植被交互 | Seedance 2.5／Dreamina · 视频（author_or_source_claim_unverified） | [@CharaspowerAI](https://x.com/CharaspowerAI) / [原帖](https://x.com/CharaspowerAI/status/2096312532432457924) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| INT-003 | 拟人猫接触与群体反应：用于研究拟人动物表演、爪与面部接触、裁判、观众反应时序。 | 拟人动物表演、爪与面部接触、裁判 / 观众反应时序 | Seedance 2.5／Dreamina · 视频（author_or_source_claim_unverified） | [@CharaspowerAI](https://x.com/CharaspowerAI) / [原帖](https://x.com/CharaspowerAI/status/2095587761554071695) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |
| INT-004 | 第一人称绳索障碍与载具：用于研究人物与绳索接触、跨越障碍、载具换场、手部装备持续。 | 人物与绳索接触、跨越障碍、载具换场、手部装备持续 | Seedance 2.5／Dreamina · 视频（author_or_source_claim_unverified） | [@CharaspowerAI](https://x.com/CharaspowerAI) / [原帖](https://x.com/CharaspowerAI/status/2097384592407777294) | metadata_only；complete_as_recorded；媒体 not_reviewed_or_reproduced；许可 unknown |

## 视频接续与局部编辑

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| EDT-001 | 地铁追逐视频延长：用于研究视频延长、地铁到街道、人物与声音续接。 | 视频延长 / 地铁到街道 / 人物与声音续接 | Seedance 2.5 · 视频／编辑（author_or_source_claim_unverified） | [ByteDance Seed](https://seed.bytedance.com/en/) / [原帖](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| EDT-002 | 绿幕足球场景与配角替换：用于研究绿幕替换、场景、障碍、服装、配角、时间段控制。 | 绿幕替换 / 场景 / 障碍 / 服装 / 配角 / 时间段控制 | Seedance 2.5 · 视频／编辑（author_or_source_claim_unverified） | [ByteDance Seed](https://seed.bytedance.com/en/) / [原帖](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| EDT-003 | 早餐片仅修改运镜：用于研究编辑保真、保留人物动作、仅修改运镜。 | 编辑保真 / 保留人物动作 / 仅修改运镜 | Seedance 2.5 · 视频／编辑（author_or_source_claim_unverified） | [ByteDance Seed](https://seed.bytedance.com/en/) / [原帖](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| EDT-004 | 白模到幻想叙事成片：用于研究多步生成、白模到成片、机位与调度继承、多场叙事。 | 多步生成 / 白模到成片 / 机位与调度继承 / 多场叙事 | Seedance 2.5 · 视频／编辑（author_or_source_claim_unverified） | [ByteDance Seed](https://seed.bytedance.com/en/) / [原帖](https://seed.bytedance.com/en/blog/one-take-creation-flexible-referencing-introducing-seedance-2-5) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| EDT-005 | 双角色替换：用于研究后期、身份替换、局部编辑。 | 后期 / 身份替换 / 局部编辑 | Higgsfield Genjutsu · 视频／编辑（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2097698694296686623) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |
| EDT-006 | Genjutsu群像人物替换：用于研究备选、中央人物、人群分别替换、原动作运镜环境保留。 | 备选 / 中央人物 / 人群分别替换 / 原动作运镜环境保留 | Higgsfield Genjutsu · 视频／编辑（author_or_source_claim_unverified） | [@abxxai](https://x.com/abxxai) / [原帖](https://x.com/abxxai/status/2097356202577739977) | metadata_only；complete_as_recorded；媒体 not_independently_verified；许可 unknown |

## Blender与预演参考

| ID | 案例简述 | 用途标签 | 模型声称 | 作者/来源 | 原文与媒体状态 |
|---|---|---|---|---|---|
| BLD-001 | 群体转角与末镜揭示：群体转角与末镜揭示：用于研究多人队形、转角接续、遮挡揭示、角色映射。 | Blender / 多人队形 / 转角接续 / 遮挡揭示 / 角色映射 | Seedance 2.5 · Blender白模参考（author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2099456665859043789) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| BLD-002 | 多高度移动与主观客观视角接续：多高度移动与主观客观视角接续：用于研究高度变化、主观视角、仰拍、局部修订。 | Blender / 高度变化 / 主观视角 / 仰拍 / 局部修订 | Seedance 2.5 · Blender白模参考（author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2098576148955586637) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| BLD-003 | 车辆穿越与慢动作时间映射：车辆穿越与慢动作时间映射：用于研究载具、穿越净空、慢动作、速度视差。 | Blender / 载具 / 穿越净空 / 慢动作 / 速度视差 | Seedance 2.5 · Blender白模参考（author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2098353311808385384) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| BLD-004 | 门口正反打与手部接触：门口正反打与手部接触：用于研究正反打、持物连续、门铰链、听者反应。 | Blender / 正反打 / 持物连续 / 门铰链 / 听者反应 | Seedance 2.5 · Blender白模参考（author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2098041891103412584) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| BLD-005 | 遮挡换焦点与独立对象揭示：遮挡换焦点与独立对象揭示：用于研究遮挡、对象区分、画外路径、接触时序。 | Blender / 遮挡 / 对象区分 / 画外路径 / 接触时序 | Seedance 2.5 · Blender白模参考（author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2097675666590421065) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |
| BLD-006 | 只迁移动作并重新设计镜头：只迁移动作并重新设计镜头：用于研究深度视频、动作迁移、参考职责、单次动作、新运镜。 | 深度视频 / 动作迁移 / 参考职责 / 单次动作 / 新运镜 | Seedance 2.5 · 深度视频参考（author_claim_not_reproduced） | [@TanLuAI](https://x.com/TanLuAI) / [原帖](https://x.com/TanLuAI/status/2099039624257839475) | metadata_only；complete_as_recorded；媒体 not_downloaded_not_viewed_not_reproduced；许可 unknown |

## 历史别名

这批别名只用于定位原有本地 TXT，不计作新增来源；原文件保留。

| 历史别名 | 稳定 ID |
|---|---|
| P03男性四视图 | REF-002 |
| P03女性四视图 | REF-001 |
| P03手机随行跟拍待补全 | CAM-001 |
| P02御剑群战 | ACT-001 |
| P01玄幻双人重击 | ACT-004 |
| P03双角色替换 | EDT-005 |
| P03庭院人物场景 | ART-002 |
