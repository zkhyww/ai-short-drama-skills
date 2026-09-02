from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


class DramaCrewDialogueSubmissionContracts(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = read("drama-crew/SKILL.md")
        cls.dialogue = read("drama-crew/references/dialogue-craft.md")
        cls.writing = read("drama-crew/references/writing-craft.md")
        cls.commercial = read("drama-crew/references/commercial-craft.md")
        cls.roles = read("drama-crew/references/role-cards.md")
        cls.scorecard = read("drama-crew/references/review-scorecard.md")
        cls.ledger = read("drama-crew/references/canon-ledger.md")
        cls.bible = read("drama-crew/references/character-bible.md")
        cls.studio_skill = read("drama-studio/SKILL.md")
        cls.studio_roles = read("drama-studio/references/role-cards.md")
        cls.studio_assets = read("drama-studio/references/asset-library.md")
        cls.studio_ext = read("drama-studio/references/external-platforms.md")
        cls.submission = read("drama-crew/references/submission-format.md")
        cls.fight = read("drama-crew/references/genre-and-fight-rules.md")
        cls.learnings = read("drama-crew/references/learnings.md")
        cls.studio_learnings = read("drama-studio/references/learnings.md")
        cls.studio_prompt = read("drama-studio/references/prompt-assembly.md")
        cls.studio_assets = read("drama-studio/references/asset-library.md")

    def test_version_reference_and_stage_order_are_wired(self) -> None:
        self.assertIn("version: 6.17.8", self.skill)
        self.assertIn("version: 1.13.0", self.studio_skill)
        self.assertIn("references/submission-format.md", self.skill)
        dialogue_gate = self.skill.index("### 第 3.7 步：台词桌读与表演化精修关")
        compliance_gate = self.skill.index("### 第 3.8 步：合规初核关")
        final_review = self.skill.index("### 第 3.9 步：总编终审关")
        self.assertLess(dialogue_gate, compliance_gate)
        self.assertLess(compliance_gate, final_review)

    def test_sentence_level_mechanical_rules_are_not_active_contracts(self) -> None:
        active_contracts = "\n".join(
            (self.dialogue, self.writing, self.commercial, self.roles, self.scorecard)
        )
        for obsolete in (
            "每句台词在说话的同时必须至少干一件活",
            "每句台词之后，至少发生一项变化",
            "至少 1 次位置位移",
            "沉默时必须有小动作",
            "单句 ≤ 15 字",
            "单句≤15字",
            "单句 12–18 字",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, active_contracts)

    def test_dialogue_owner_uses_breath_beat_and_performance_logic(self) -> None:
        self.assertIn("文茵写正文时对照 §1/§2/§4/§5/§7", self.dialogue)
        for required in (
            "一个对话回合或表演节拍",
            "一口气只表达一个意图",
            "停顿、改口、抢话、答非所问、自我纠正、未说完",
            "不机械添加语气词",
            "专业信息",
            "承重词",
            "句尾落点",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.dialogue)

    def test_dialogue_diagnostics_do_not_become_new_fixed_templates(self) -> None:
        self.assertNotIn("三组黄金对比（直接套用）", self.writing)
        self.assertIn("不是固定四拍", self.commercial)
        self.assertIn("关键对话场", self.commercial)
        self.assertIn("问句→完整回答→点评结论", self.dialogue)

    def test_existing_roles_own_refinement_recheck_and_gate(self) -> None:
        for required in (
            "文茵 3.7 台词桌读与表演化精修下发模板",
            "剧情事实、证据、知情边界、人物关系、结果、目标时长与季终悬念",
            "完整修订稿",
            "台词精修变更表",
            "青梧 3.7 改动场局部复核下发模板",
            "只复核发生改动的场次",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.roles)
        self.assertIn("对白硬度门", self.scorecard)
        self.assertIn("不得用其他维度平均放行", self.scorecard)
        self.assertIn("对白硬度门", self.roles)

    def test_submission_view_is_derived_from_single_production_master(self) -> None:
        for required in (
            "完整制作母稿.md",
            "《剧名》_投稿阅读稿.docx",
            "唯一内容真源",
            "派生阅读视图",
            "每集另起一页",
            "script_rev",
            "SHA-256",
            "不得生成、推断或预填",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.submission)
        self.assertIn("### 第 4A 步：内部制作母稿", self.skill)
        self.assertIn("### 第 4B 步：投稿阅读稿排版", self.skill)
        self.assertIn("只能把完整制作母稿交给 `drama-studio`", self.skill)
        self.assertIn("逐页渲染", self.submission)
        self.assertIn("只改投稿阅读稿的字体/分页/缩进/标题层级", self.skill)
        self.assertIn("在投稿阅读稿里改台词/动作/剧情", self.skill)
        self.assertIn("投稿阅读稿不得作为第二内容真源", self.roles)

    def test_submission_uses_standard_screenplay_format(self) -> None:
        # v6.17.1：内部母稿保持 Markdown；对外阅读且工具可用时默认 DOCX。
        self.assertIn("§4a 标准剧本排版", self.submission)
        self.assertIn("**场{集}-{场} {日/夜} {内/外} {地点}**", self.submission)
        self.assertIn("**人物：", self.submission)
        self.assertIn("空格分隔", self.submission)
        self.assertIn("∆", self.submission)
        self.assertIn("无指定模板时的团队通用投稿阅读格式", self.submission)
        # v6.17.4：按火山引擎剧创口径区分 OS/VO，字幕按需，括号只留可执行提示。
        self.assertIn("【字幕】", self.submission)
        self.assertIn("（OS）", self.submission)
        self.assertIn("（VO）", self.submission)
        self.assertNotIn("≤5 字", self.submission)
        self.assertIn("自然短语", self.submission)
        self.assertIn("【字幕】身份行按需", self.skill)
        for contract in (self.skill, self.roles, self.submission):
            with self.subTest(contract=contract[:30]):
                self.assertIn("DOCX 工具可用时默认交付 DOCX", contract)
                self.assertIn("Markdown", contract)
                self.assertIn("降级", contract)
        self.assertIn("PDF 只在用户或接收方明确要求时生成", self.submission)

    def test_submission_default_structure_is_reader_facing_and_ordered(self) -> None:
        section = self.submission[
            self.submission.index("## 4. 通用投稿阅读稿结构") :
            self.submission.index("### §4a 标准剧本排版")
        ]
        expected = (
            "1. 封面",
            "2. 一句话卖点",
            "3. 故事梗概",
            "4. 主要人物",
            "5. 粗纲",
            "6. 逐集集纲",
            "7. 正文",
        )
        positions = [section.index(item) for item in expected]
        self.assertEqual(positions, sorted(positions))
        self.assertIn("选题分析结论只作可选策划附件", section)
        self.assertIn("不默认并入投稿剧本正文", section)

    def test_authentic_voice_principles_and_literary_ai_words_are_wired(self) -> None:
        # v6.16.0：吸收 novel-creator 裁定项——正向人声七招 + 文学向 AI 高频词
        self.assertIn("正向人声七招", self.writing)
        for principle in ("不完整", "重复", "延迟", "出错误", "身体在场", "活在当下"):
            with self.subTest(principle=principle):
                self.assertIn(principle, self.writing)
        self.assertIn("文学向 AI 高频词", self.writing)
        self.assertIn("与此同时", self.writing)
        self.assertIn("涌上心头", self.writing)
        self.assertIn("沉默即回合", self.dialogue)
        self.assertIn("不按次数设硬上限", self.dialogue)
        self.assertIn("重复沉默没有新增压力、关系或含义", self.dialogue)
        self.assertIn("天降解决", self.scorecard)
        self.assertIn("16 条", self.scorecard)
        self.assertIn("突变合法路径四步", self.bible)

    def test_master_doc_carries_outline_bible_and_visual_anchors(self) -> None:
        # v6.17.1：母稿含粗纲/集纲/人物档案/基础视觉事实；投稿版按阅读顺序输出。
        for required in ("粗纲与集纲", "人物视觉锚定", "人物小传档"):
            with self.subTest(required=required):
                self.assertIn(required, self.submission)
        for required in ("粗纲/集纲/人物档案（小传节）", "人物视觉锚定行"):
            with self.subTest(required=required):
                self.assertIn(required, self.skill)
        for required in ("一句话卖点", "故事梗概", "主要人物", "粗纲", "逐集集纲"):
            with self.subTest(required=required):
                self.assertIn(required, self.submission)
        self.assertIn("视觉锚定", self.roles)
        self.assertIn("视觉锚定", self.bible)
        self.assertIn("人物视觉锚定行", self.studio_assets)

    def test_visual_anchor_contract_separates_story_facts_from_production_design(self) -> None:
        crew_contracts = "\n".join((self.skill, self.roles, self.bible, self.submission))
        self.assertIn("基础视觉事实", crew_contracts)
        self.assertNotIn("唯一文字依据", crew_contracts)
        for required in (
            "逐字继承 crew 基础视觉事实",
            "制作设计/推断",
            "不得覆盖 crew 基础视觉事实",
            "≥3 条稳定结构轴",
            "≥2 条必须在脸部",
            "8-12 个视觉词",
            "forbidden 3-5 项",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_assets)
        self.assertIn("覆盖 crew 基础视觉事实即失败", self.studio_roles)

    def test_master_content_changes_sync_all_reader_facing_sections_in_one_revision(self) -> None:
        for required in (
            "同一 `script_rev` 内同步",
            "故事梗概",
            "人物档案",
            "粗纲",
            "逐集集纲",
            "关键事件",
            "人物状态",
            "集数",
            "结尾卡点",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.submission)
        self.assertIn("同一 `script_rev` 内同步", self.skill)

    def test_red_light_14_and_15_use_distinct_evidence(self) -> None:
        self.assertIn("#14 时长结构模板化只核秒数结构变奏", self.roles)
        self.assertIn("#15 天降解决只核未铺垫外力", self.roles)
        self.assertIn("主角行动、代价与因果铺垫", self.roles)

    def test_character_and_dialogue_diagnostics_do_not_use_mechanical_failure_counts(self) -> None:
        self.assertNotIn("一场最多一次", self.dialogue)
        self.assertNotIn("四步缺任一 = OOC = 返修", self.bible)
        self.assertIn("四项是因果证据维度", self.bible)
        self.assertIn("可跨场分布或隐含", self.bible)
        self.assertIn("以能否由压力、经历和前文推导裁决", self.bible)
        self.assertIn("七招是可选策略", self.writing)
        self.assertIn("不为显得自然机械添加口误、错名或身体反应", self.writing)
        self.assertNotIn("一次口误比十句精准台词更像人", self.writing)

    def test_os_vo_follow_volcengine_profile_without_fake_numeric_standard(self) -> None:
        # v6.17.4：国内微短剧默认采用火山引擎剧创口径；OS 质量按功能判断，不设伪行业配额。
        for required in (
            "火山引擎「剧创」口径",
            "OS = 角色内心独白",
            "VO = 画外音",
            "不设统一条数、单条字数或连续条数配额",
            "其他角色听不见",
            "OS 计入净台词字数",
            "不越权替别人内心播报",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.writing)
        for obsolete in ("第一人称画外音", "单场 1-3 条", "单条 ≤30 字", "连续 OS 不超过 2 条"):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, self.writing)
        self.assertIn("接收方模板优先", self.submission)
        self.assertIn("身份不能从当下画面或对白快速读明", self.submission)
        self.assertIn("可见动作另写 `∆` 行", self.submission)
        self.assertIn("OS 内心独白、VO 画外音与必要旁白", self.commercial)

    def test_gap_awareness_loop_is_wired_end_to_end(self) -> None:
        # v6.17.5：缺口感知三件套——词库/红灯#16/六行自检+沉淀回路，端到端接线
        # 1. 战斗动作词库
        for required in ("战斗动作词库", "环境反馈链", "反词穷纪律"):
            with self.subTest(required=required):
                self.assertIn(required, self.fight)
        # 2. 红灯 #16：15→16 全量换口径，旧口径禁残留
        self.assertIn("16 条", self.scorecard)
        self.assertIn("动作词穷", self.scorecard)
        self.assertIn("暴涨", self.scorecard)
        self.assertIn("16 条", self.roles)
        self.assertIn("动作词穷", self.roles)
        self.assertNotIn("机械过 15 条", self.roles)
        # 3. 文茵六行自检（六行齐全 + 先补后写）
        for line in ("写批前六行自检", "题材", "战戏", "情绪", "场景", "专业", "词穷", "先补后写"):
            with self.subTest(line=line):
                self.assertIn(line, self.roles)
        # 4. 沉淀回路：learnings 升格表有词库去向 + 触发表有补缺行
        self.assertIn("战斗动作/情绪语汇/场景质感词库", self.learnings)
        self.assertIn("运行时补缺是经验库的主动来源", self.learnings)

    def test_self_evolution_engineering_and_language_assets_are_wired(self) -> None:
        # v6.17.6：自进化工程化（CI/复盘仪式）+ 语言资产库 + 对标解剖工序
        # 1. 复盘仪式：单人/团队分流 + 判定法 + CI 引用
        for required in ("项目复盘仪式", "git log --format", "PR", "contract-tests.yml", "squash"):
            with self.subTest(required=required):
                self.assertIn(required, self.learnings)
        # 2. 升格表有语料去向
        self.assertIn("方言俚语/年代语/行话语料", self.learnings)
        # 3. 语言资产库：四类语料+纪律，接声音指纹
        for required in ("语言资产库", "地域方言", "俚俗语", "年代语", "行业行话", "一人一语域", "上下文可自明", "报菜名"):
            with self.subTest(required=required):
                self.assertIn(required, self.dialogue)
        # 4. 六行自检第 5 行扩词
        self.assertIn("专业与地域", self.roles)
        # 5. 对标解剖五步 + M/F 七问七拍 + 防抄口径
        for required in ("对标剧本解剖工序", "通读", "量化", "可抄", "防抄", "产出入库", "M1 消费入口", "M7 表达奇点", "F1 失衡压制", "F7 后果/新任务", "机制可迁移，表达不可照搬"):
            with self.subTest(required=required):
                self.assertIn(required, read("drama-crew/references/topic-research.md"))
        # 6. 望舒卡交付物含解剖报告
        self.assertIn("解剖报告", self.roles)

    def test_team_default_and_physical_wording_discipline_are_wired(self) -> None:
        # v6.17.7 / studio v1.12.0：团队默认反转 + 物理措辞纪律 + 外部素材索引
        # 1. crew：团队 PR 默认、单人降为例外快道、直推禁区
        for required in ("团队为默认", "单人快道（例外）", "直推 main 禁区", "squash"):
            with self.subTest(required=required):
                self.assertIn(required, self.learnings)
        # 2. studio：复盘仪式同构 + 团队默认同口径
        for required in ("项目复盘仪式", "团队为默认", "contract-tests.yml"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_learnings)
        # 3. 物理措辞纪律：两禁 + 五维 + 自检核对项
        for required in ("物理措辞纪律", "禁文学化修辞", "心如刀割", "禁 AI 执行不了的精确物理值", "相对化", "光线", "动作", "表情", "声音", "空间"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_prompt)
        self.assertIn("无文学化修辞残留", self.studio_prompt)
        self.assertIn("无 AI 执行不了的精确物理值", self.studio_prompt)
        # 4. 外部素材索引：gptimage2 登记 + 不进 git 铁律
        for required in ("外部素材索引", "gptimage2", "不进 git"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_assets)

    def test_external_platform_routing_is_wired(self) -> None:
        # v6.17.8 / studio v1.13.0：flova 实测驱动的外部平台工序端到端
        # 1. 能力面实测数据 + 三类关系判定
        for required in ("flova", "171", "替代", "增强", "无关", "导演美学风格包"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_ext)
        # 2. 三步匹配规则 + 用户确认（不静默耗积分）
        for required in ("需求归类", "skill_list", "skill_feed", "NFKC", "用户确认", "积分"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_ext)
        # 3. 交接格式三基准 + 纪律
        for required in ("剧本类", "分镜类", "素材类", "交接纪律"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_ext)
        # 4. SKILL 预检句接线 + 加载表注册
        self.assertIn("external-platforms.md 路由", self.studio_skill)
        self.assertIn("references/external-platforms.md", self.studio_skill)
        # 5. crew 升格表有外部平台去向
        self.assertIn("外部平台能力面/匹配报告", self.learnings)

    def test_murphy_boundaries_keep_fast_path_and_authority_limits(self) -> None:
        self.assertIn("快写/单集预览在原文茵任务内", self.skill)
        self.assertIn("未经润色的原始草稿", self.skill)
        self.assertIn("不新增用户弹窗", self.submission)
        self.assertIn("不得生成、推断或预填", self.submission)
        self.assertIn("不新增角色", self.skill)

    def test_public_docs_and_markdown_count_match_release(self) -> None:
        crew_markdown_count = len(list((ROOT / "drama-crew").rglob("*.md")))
        self.assertEqual(18, crew_markdown_count)
        readme = read("README.md")
        changelog = read("CHANGELOG.md")
        self.assertIn("| `drama-crew` | 6.17.8 | 18 |", readme)
        self.assertIn("| `drama-studio` | 1.13.0 | 28 |", readme)
        self.assertIn("`drama-crew` v6.17.8", changelog)
        self.assertIn("`drama-studio` v1.11.2", changelog)
        self.assertIn("投稿阅读稿", readme)
        self.assertIn("台词桌读", readme)

    def test_directory_uniqueness_audit_is_wired_before_final_review(self) -> None:
        self.assertIn("终审前目录唯一性核验", self.skill)
        self.assertIn("最终/final/副本/汇总", self.skill)
        self.assertIn("目录核验", self.roles)
        self.assertIn("文件治理失守", self.scorecard)

    def test_duplicate_check_evidence_has_single_default_location(self) -> None:
        self.assertIn("v6.14.0 统一留痕口径", self.skill)
        self.assertIn("候选结构查重", self.skill)
        self.assertIn("查重结论", self.skill)
        self.assertIn("02A", self.skill)

    def test_ledger_increments_are_standalone_files_with_adaptive_batch_size(self) -> None:
        self.assertIn("增量落位口径（唯一", self.ledger)
        self.assertIn("{项目名}_增量_E{起}-E{止}.md", self.ledger)
        self.assertIn("批次粒度（唯一口径）", self.ledger)
        self.assertIn("10-20 集/批", self.ledger)
        self.assertIn("不建议低于 5 集/批", self.ledger)
        self.assertIn("{项目名}_增量_E{起}-E{止}.md", self.roles)
        self.assertNotIn("5 集/批，用户另指定批大小时从用户", self.ledger)
        self.assertIn("逐集续写完整正文", self.skill)

    def test_second_structure_variation_and_duration_template_checks(self) -> None:
        self.assertIn("秒数结构变奏", self.commercial)
        self.assertIn("±10%", self.commercial)
        self.assertIn("每 10 集至少 1 次结构变奏", self.commercial)
        self.assertIn("时长结构模板化", self.scorecard)
        self.assertIn("时长结构模板化", self.roles)
        self.assertIn("16 条", self.scorecard)

    def test_artifact_necessity_matrix_is_documented(self) -> None:
        self.assertIn("产物必要性判定表", self.submission)
        self.assertIn("必产条件", self.submission)
        self.assertIn("全量档", self.submission)
        self.assertIn("标准档", self.submission)
        self.assertIn("轻量档", self.submission)
        self.assertIn("产物档位", self.skill)
        self.assertIn("产物必要性判定表", self.skill)

    def test_cognitive_depth_and_expression_strategy_are_independent(self) -> None:
        for required in (
            "认知深度",
            "察觉现象 / 猜测原因 / 理解机制",
            "表达策略",
            "直说 / 试探 / 回避 / 半句 / 行动",
            "经历、训练与前文证据",
            "已经理解也可能选择回避",
            "仅凭直觉也可能直接说出判断",
            "知情范围",
            "退回上游",
            "9.1",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.dialogue)
        for stereotyped_rule in (
            "身份/职业/年龄/教育决定",
            "底层角色信口行业黑话",
            "感觉到」的可以直接说",
            "隐约意识到」的要用行为或半句泄露",
        ):
            with self.subTest(stereotyped_rule=stereotyped_rule):
                self.assertNotIn(stereotyped_rule, self.dialogue)

    def test_ai_trace_uses_cause_first_minimal_fix_and_no_forced_edit(self) -> None:
        self.assertIn("处置三原则", self.writing)
        self.assertIn("成因定位先于改写", self.writing)
        self.assertIn("最小修复", self.writing)
        self.assertIn("自然文本不硬改", self.writing)
        self.assertIn("下方条目只作排查信号", self.writing)
        self.assertIn("具体位置与证据", self.writing)
        self.assertNotIn("下方命中任一即返修具体句子", self.writing)
        self.assertIn("本段不改", self.scorecard)
        self.assertIn("不为评分强改", self.scorecard)

    def test_subjective_attention_does_not_delete_production_anchors(self) -> None:
        for required in (
            "主观注意力",
            "空间建立",
            "视觉连续性",
            "世界信息",
            "关键道具",
            "§18 场景设定段",
            "客观镜头",
            "群像调度",
            "§12 动作节拍段",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.writing)
        self.assertIn("装饰性环境", self.scorecard)
        self.assertIn("认知与视角越界", self.scorecard)
        self.assertIn("场景设定段、客观镜头、群像调度与动作节拍段", self.roles)
        self.assertNotIn("环境细节只有能改变人物行动、情绪或信息时才写", self.writing)
        self.assertNotIn("人物关系或选择会变吗？不会就删", self.writing)
        self.assertNotIn("2-3 个关键帧", self.writing)
        self.assertNotIn("2-3个关键帧", self.writing)

    def test_conflict_resolution_follows_authority_before_first_deviation(self) -> None:
        for required in (
            "先确定权威事实",
            "首次偏离权威事实",
            "账本记录错误就修账本",
            "用户已确认正文不得自动修改",
            "无明确权威时才上报用户裁决",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.ledger)
        self.assertIn("顺链核对", self.ledger)
        self.assertIn("首次偏离权威事实的可编辑位置", self.roles)
        self.assertNotIn("修源点后", self.ledger)

    def test_ai_trace_scan_count_and_role_ownership_are_consistent(self) -> None:
        self.assertIn("AI 痕迹扫描（5 类", self.scorecard)
        self.assertIn("A–E 共 28 项", self.roles)
        self.assertIn("认知与视角越界", self.roles)
        for obsolete in ("AI 痕迹四维扫描", "AI痕迹四维扫描"):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, self.scorecard)
                self.assertNotIn(obsolete, self.roles)
                self.assertNotIn(obsolete, self.writing)

    def test_v6151_does_not_claim_clean_room_or_reuse_source_examples(self) -> None:
        changelog = read("CHANGELOG.md")
        self.assertNotIn("豆包 human-signal 机制级融合（清洁室改写", changelog)
        self.assertNotIn("v6.15.0 sol 豆包 human-signal 机制级融合（清洁室改写", self.skill)
        for source_like_phrase in (
            "雷声响起来的时候，他刚好把那句",
            "禁止为证明工作量而重写",
            "只看手、只听声音、只盯",
        ):
            with self.subTest(source_like_phrase=source_like_phrase):
                self.assertNotIn(source_like_phrase, self.writing)


if __name__ == "__main__":
    unittest.main()
