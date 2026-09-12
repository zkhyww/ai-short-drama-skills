# 公共案例索引

> 本页由 `metadata.json` 机械生成。它只发布来源元数据与原创中性简述，不发布第三方提示词全文、媒体、本机路径，也不授予再发布许可。模型与效果状态均按来源记录，未复现不等于可复现；案例不得新增或改写项目正典事实。

使用时按当前创作、对白或制作问题匹配用途标签，只读命中单条。需要原提示词时，必须在获准且已绑定的本地案例根中读取；本页没有本地原文时，使用现有规则做原创设计，不伪称读过案例。

逐条缺输入、归属提醒与原始状态说明保存在生成本页所用的 [metadata.json](metadata.json) 同 ID 记录中；私有绑定可把维护命令指向唯一 canonical metadata，包内文件只作发布快照。公开可读不等于取得原文再发布许可。

## 本地绑定与维护

私有绑定写入同目录且已被 Git 忽略的 `local-config.json`，只含 `canonical_metadata`、`local_root`、`local_view`。安装副本中的 metadata 是发布快照；存在绑定时，`validate`、`build`、`add` 都使用 canonical metadata，绑定失效会明确失败，不会静默回退快照。没有绑定时仍可读取和生成包内公共视图。可用 `--config` 显式选择配置；同次调用中的路径参数逐项覆盖该配置。只显式传 `--metadata` 而不传 `--config` 时视为独立上下文，不自动混用私有绑定。

```powershell
python drama-studio/scripts/case_library.py validate
python drama-studio/scripts/case_library.py build
python drama-studio/scripts/case_library.py add --record '<新增或补缺记录.json>' --author-record '<可选的新作者记录.json>'
python drama-studio/scripts/case_library.py build --metadata '<显式metadata.json>' --public-view '<显式公共README.md>' --local-root '<显式本地案例根>' --local-view '<显式本地入口.md>'
```

正常新增或同 ID 补缺必须走 `add`，不得改历史 `snapshot.original_case_count`。`add` 可在同一事务加入一个新作者与一个案例：先核作者、真实 TXT/locator、标准化 SHA-256、完整 schema、重复 ID/指纹及别名，再一起刷新 metadata、公共视图和本地 `开始这里.md`；任一步失败都不改这三份文件。新 ID 才追加；同 ID 只填 `null`、空字符串/数组/对象，完全相同的值幂等，非空冲突拒绝。只有经批准的非空事实更正才直接编辑 canonical metadata，保留可审查 diff，再运行 `validate` 与 `build`。每条取得的第三方原文独立保存为纯原文 TXT，只保留真实原文；来源、授权与取得状态写对应 metadata，现有字段不足时写同 ID 本地来源旁档；我方归纳另存并标明，成果以稳定 ID 与 locator 回指唯一原文，不造第二份混合真源。同一帖子含多段不同原文时按不同指纹保留。新增外部材料先是入库候选；经过项目适配、相称核验并获得持久化/升格授权后，才可能进入正式规则。

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
