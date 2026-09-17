from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]


def read(relative_path: str) -> str:
    return (ROOT / relative_path).read_text(encoding="utf-8")


def section_between(text: str, start: str, end: str) -> str:
    return text[text.index(start) : text.index(end, text.index(start) + len(start))]


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
        cls.world = read("drama-crew/references/world-bible.md")
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
        cls.studio_shots = read("drama-studio/references/shot-contract.md")
        cls.studio_storyboard = read("drama-studio/references/storyboard-craft.md")
        cls.studio_performance = read(
            "drama-studio/references/dimensions/dim-performance.md"
        )

    def test_reference_and_stage_order_are_wired(self) -> None:
        self.assertIn("references/submission-format.md", self.skill)
        dialogue_gate = self.skill.index("### 第 3.7 步：台词桌读与表演化精修关")
        compliance_gate = self.skill.index("### 第 3.8 步：合规初核关")
        final_review = self.skill.index("### 第 3.9 步：总编终审关")
        self.assertLess(dialogue_gate, compliance_gate)
        self.assertLess(compliance_gate, final_review)

    def test_external_case_learning_is_evidence_scoped_and_not_auto_injected(self) -> None:
        for learning in (self.learnings, self.studio_learnings):
            for required in (
                "外部成功/失败案例",
                "普通问答不触发",
                "来源 URL",
                "授权状态",
                "已见事实 / 作者声称 / 我方推断",
                "输入与后期条件",
                "适用 / 不适用范围",
                "实际验证",
                "无复现不宣称可复现",
                "低置信或待讨论条目不得自动",
            ):
                with self.subTest(required=required):
                    self.assertIn(required, learning)
            self.assertIn("点赞量或重发次数", learning)
            self.assertIn("资料截断属于采集缺项", learning)

    def test_external_method_reference_and_generation_execution_are_separate_routes(self) -> None:
        method_route = section_between(self.studio_ext, "## 2. ", "## 2.5 ")
        for required in (
            "方法参考",
            "planning_only",
            "实际生成",
            "原有 `execution` 流程",
            "作品任务 → 观看重点 / 已有约束 → 已有规则与本地方法 → 具体设计 → 相称核验",
            "不要求用户点名",
            "不强迫每次联网",
            "已有检索授权",
            "已有入库授权",
            "没有检索授权时记录缺项",
            "继续有依据的原创规划",
            "不为每条材料重复确认",
            "本次任务明确不联网或不落盘",
            "观看重点 + 已锁事实资产 + 目标模型条件",
            "现有资产 / 镜头 / `prompt-assembly.md` §2 路由后正文",
            "固定计数",
            "不能为使用方法补人物、建筑、道具、破坏状态或改结果",
            "读取方法不等于安装、运行脚本、上传或生成",
            "仅引用解决当前观看任务的必要范围",
            "输出是带启用条件的可选建议",
            "除非既有硬边界或当前任务证据已要求",
            "不得把外部方法改写成新的必做项、齐套检查、硬门槛或每镜合同",
            "条件不足只能保留候选，不能靠换措辞启用",
            "方法只作用于承担对应观看功能的段落或镜头",
            "先写出可观察的启用条件再给具体创意",
            "不承担该功能的镜头可不启用",
            "缺少具体职责或启用条件时先保留为可选方案",
            "`planning_only` 无需为证明方法有效而付费生成",
        ):
            with self.subTest(required=required):
                self.assertIn(required, method_route)

        external_platform_row = next(
            line
            for line in self.studio_skill.splitlines()
            if line.startswith("| references/external-platforms.md |")
        )
        self.assertIn("作品任务首次判断观看重点与表现机会时读", external_platform_row)
        self.assertIn("后续有界补搜", external_platform_row)
        self.assertNotIn("有明确方法缺口", external_platform_row)

        assembly_checklist = self.studio_prompt[
            self.studio_prompt.index("## 7. 装配自检") :
        ]
        checklist_lines = [
            line for line in assembly_checklist.splitlines() if line.startswith("- [ ]")
        ]
        self.assertIn("观看重点与各镜职责", checklist_lines[0])
        self.assertIn("叙事目的、实际画面/声音或参考职责", checklist_lines[0])
        self.assertIn("不承担该功能的镜头未被要求齐套", checklist_lines[0])
        self.assertNotIn("\n- [ ] 本段观看重点与各镜职责已成立；", assembly_checklist)

        for text in (self.studio_skill, self.studio_roles):
            self.assertIn("核对采用方法", text)
            self.assertNotIn("核采用方法", text)

        workflow_map = section_between(self.studio_ext, "## 2.8 ", "## 3. ")
        self.assertIn("按项目锁定集数", workflow_map)
        self.assertNotIn("61 集粗纲", workflow_map)

        rights_route = section_between(self.studio_ext, "## 2.5 ", "## 2.8 ")
        for required in (
            "公开可读不代表可复制发布",
            "无许可证或来源争议",
            "不复制第三方长文、资产或脚本进公共仓库",
        ):
            with self.subTest(required=required):
                self.assertIn(required, rights_route)
        self.assertNotIn("清洁室消化", rights_route)
        self.assertNotIn("工序编排可复制到我们管线", self.studio_ext)

        platform_registry = self.studio_ext[self.studio_ext.index("## 5. ") :]
        for required in (
            "方法候选",
            "触发 / 输入输出 / 适用模型 / 来源版本 / 许可 / 验证状态",
            "已实测平台能力",
            "候选不得写成已安装可运行",
            "采集、完整观看与生成复现是不同证据",
            "相称的文字、接口或生成验证",
            "未复现不强制付费试制",
            "不阻塞其他已获授权工序",
        ):
            with self.subTest(required=required):
                self.assertIn(required, platform_registry)

    def test_main_entry_and_owner_dispatch_share_context_scoped_learning_route(self) -> None:
        for source in (self.skill, self.studio_skill, self.roles, self.studio_roles):
            for required in (
                "按题材 / 节点 / 模型条件",
                "低置信或待讨论",
                "不自动",
            ):
                with self.subTest(required=required):
                    self.assertIn(required, source)

    def test_external_case_rules_retire_fixed_counts_and_universal_cost_claims(self) -> None:
        learnings = "\n".join((self.learnings, self.studio_learnings))
        for obsolete in (
            "卡点必须带现实代价",
            "高(验证3次+)",
            "中(1-2次)",
            "低(仅1次)",
            "## 6. 体量维护",
            "写入规则（5 条）",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, learnings)
        self.assertIn("见 §6 对照表", self.studio_learnings)

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
            "剧情事实、证据、知情边界、人物关系、结果与季终悬念",
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
            "《剧名》_标准投稿阅读稿.md",
            "唯一内容真源",
            "派生阅读视图",
            "script_rev",
            "SHA-256",
            "不得生成、推断或预填",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.submission)
        self.assertIn("### 第 4A 步：内部制作母稿", self.skill)
        self.assertIn("### 第 4B 步：投稿阅读稿排版", self.skill)
        self.assertIn("只能把完整制作母稿交给 `drama-studio`", self.skill)
        self.assertIn("只改投稿阅读稿的字体/分页/缩进/标题层级", self.skill)
        self.assertIn("在投稿阅读稿里改台词/动作/剧情", self.skill)
        self.assertIn("投稿阅读稿不得作为第二内容真源", self.roles)
        for contract in (self.skill, self.roles, self.submission):
            with self.subTest(contract=contract[:30]):
                self.assertIn("两个不同文件", contract)
                self.assertIn("《剧名》_标准投稿阅读稿.md", contract)

    def test_submission_uses_standard_screenplay_format(self) -> None:
        # 标准投稿 Markdown 是必需阅读视图；DOCX 仅按明确要求派生。
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
        active_skill = self.skill.split("## 版本记录", 1)[0]
        for contract in (active_skill, self.roles, self.submission):
            with self.subTest(contract=contract[:30]):
                self.assertNotIn("DOCX 工具可用时默认交付 DOCX", contract)
        self.assertIn("DOCX 仅在用户或接收方明确要求时生成", self.submission)
        self.assertIn("PDF 只在用户或接收方明确要求时生成", self.submission)

    def test_submission_delivery_requires_complete_outline_and_clean_pair_preflight(self) -> None:
        self.assertIn("逐集集纲非空且覆盖到最后一集", self.submission)
        self.assertIn("预检退出码为 0", self.submission)
        self.assertIn("audit_screenplay.py --master", self.submission)
        self.assertIn("--submission", self.submission)
        self.assertIn("# 第 1 集", self.submission)
        self.assertNotIn("# 第一集", self.submission)
        self.assertIn("--expected-episodes", self.submission)
        for contract in (self.skill, self.roles):
            with self.subTest(contract=contract[:30]):
                self.assertIn("预检退出码为 0", contract)
                self.assertIn("先回完整制作母稿修改", contract)

    def test_carrier_confirmation_uses_evidence_based_runtime_contract(self) -> None:
        self.assertIn("真人=台词驱动", self.skill)
        self.assertIn("350–500 字只作同体量真人短剧的诊断区间", self.skill)
        self.assertNotIn("真人=台词驱动/净台词 350-500 字", self.skill)

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
        # 1. 复盘仪式：保留 CI 与仓库协作流程引用；发布授权不再按账号身份决定
        for required in ("项目复盘仪式", "contract-tests.yml", "squash"):
            with self.subTest(required=required):
                self.assertIn(required, self.learnings)
        # 2. 升格表有语料去向
        self.assertIn("方言俚语/年代语/行话语料", self.learnings)
        # 3. 语言资产库：四类语料+纪律，接声音指纹
        for required in ("语言资产库", "地域方言", "俚俗语", "年代语", "行业行话", "惯性与受压变化", "上下文可自明", "报菜名"):
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

    def test_publication_checks_and_physical_wording_discipline_are_wired(self) -> None:
        # 发布检查与仓库协作流程 + 物理措辞纪律 + 外部素材索引
        # 1. crew：保留 CI 引用与仓库协作方式
        for required in ("contract-tests.yml", "squash"):
            with self.subTest(required=required):
                self.assertIn(required, self.learnings)
        # 2. studio：复盘仪式同构 + CI 与仓库协作方式
        for required in ("项目复盘仪式", "contract-tests.yml", "squash"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_learnings)
        # 3. 画面措辞纪律不能误伤逐字台词、时间码与实际接口参数。
        for required in ("物理措辞纪律", "禁文学化修辞", "心如刀割", "避免不可验证的伪精度", "相对化", "光线", "动作", "表情", "声音", "空间"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_prompt)
        self.assertIn("台词/OS/VO 的原文修辞与数字未被改写", self.studio_prompt)
        self.assertIn("实际参数与时间码保留", self.studio_prompt)
        # 4. 外部素材索引：gptimage2 登记 + 不进 git 铁律
        for required in ("外部素材索引", "gptimage2", "不进 git"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_assets)
        self.assertIn("本地视觉方法索引中的 `gptimage2 图卡库` 条目", self.studio_assets)
        self.assertNotIn("C://Users//Administrator//Downloads//gptimage2//", self.studio_assets)

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

    def test_official_dreamina_default_engine_and_flova_three_usages_are_registered(self) -> None:
        # v1.15.1：官方 dreamina 默认 + 外部 Skill 三种合法用法
        ext = read("drama-studio/references/external-platforms.md")
        for required in ("dreamina", "官方 CLI", "默认引擎", "dreamina user_credit", "dreamina text2image", "dreamina image2image", "dreamina text2video", "dreamina image2video", "dreamina frames2video", "dreamina multimodal2video", "外部 Skill 能力的三种合法用法", "运行时调用", "原创方法归纳", "自建等效工作流", "云端编排", "判定顺序：B > C > A"):
            with self.subTest(required=required):
                self.assertIn(required, ext)
        self.assertIn("默认本机引擎为官方 dreamina CLI", self.studio_skill)
        self.assertNotIn("xmst", ext.lower())

    def test_studio_frontmatter_is_validator_safe_and_scripts_are_discoverable(self) -> None:
        frontmatter = self.studio_skill.split("---", 2)[1]
        description = next(line for line in frontmatter.splitlines() if line.startswith("description:"))
        self.assertNotRegex(description, r"[<>]")
        for required in ("scripts/dreamina_route.py", "scripts/assemble_timeline.py"):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_skill)

    def test_dreamina_model_card_matches_official_cli_modes(self) -> None:
        card = read("drama-studio/references/models/dreamina.md")
        for required in (
            "official CLI",
            "OAuth",
            "text2image",
            "image2image",
            "text2video",
            "image2video",
            "frames2video",
            "multiframe2video",
            "multimodal2video",
            "Seedance 2.5",
            "4–30s",
            "9:16",
            "图生视频画幅跟随输入图",
            "实时 `--help`",
        ):
            with self.subTest(required=required):
                self.assertIn(required, card)

    def test_default_dreamina_seedance_execution_loads_model_and_provider_cards(self) -> None:
        self.assertIn(
            "同时 Read `references/models/seedance.md` 与 `references/models/dreamina.md`",
            self.studio_skill,
        )
        self.assertIn("模型卡与 provider/adapter 能力卡", self.studio_roles)
        seedance = read("drama-studio/references/models/seedance.md")
        self.assertIn("同时读取 `dreamina.md`", seedance)
        self.assertNotIn("对应的一张卡", seedance)

    def test_costume_elaboration_and_selfbuilt_workflow_mapping_are_wired(self) -> None:
        # v1.13.2：服化道极繁纪律 + 自建等效工作流映射
        assets = read("drama-studio/references/asset-library.md")
        for required in ("服化道极繁纪律", "逐层描述清单", "性别×身份服饰适配表", "男-剑修/侠客", "女-剑修", "半透明轻纱", "风格映射", "水墨国风", "3D 次世代写实", "禁大面积暗沉纯黑"):
            with self.subTest(required=required):
                self.assertIn(required, assets)
        ext = read("drama-studio/references/external-platforms.md")
        for required in ("自建等效工作流映射", "一键成片", "dreamina image2image", "时间线合成", "scripts/assemble_timeline.py"):
            with self.subTest(required=required):
                self.assertIn(required, ext)
        self.assertIn("服化道极繁纪律逐层扩写", self.studio_roles)

    def test_setting_sheet_13_modules_realism_anchor(self) -> None:
        # v1.13.5：设定板分流 + 条件化真实感 + 可执行 ffmpeg
        assets = read("drama-studio/references/asset-library.md")
        for required in ("角色综合设定板 13 模块清单", "构图行规范", "画面结构行", "面部细项扩展", "姿态与动作行", "配饰与武器行", "负面提示词基线",
                         "定妆照", "肖像特写", "纯三视图", "细节板", "写实摄影/写实 3D", "2D/水墨/水彩/像素", "不强制毛孔",
                         "真实感锚定", "反模板脸", "深棕色眼睛", "网红脸", "鼻翼阴影", "总吸收项 ≤2", "混血感超标即废图重生成",
                         "金发，蓝眼，欧美脸"):
            with self.subTest(required=required):
                self.assertIn(required, assets)
        ext = read("drama-studio/references/external-platforms.md")
        for required in ("scripts/assemble_timeline.py", "先统一编码、帧率、分辨率与时基", "ffprobe", "外部 WAV/TTS"):
            with self.subTest(required=required):
                self.assertIn(required, ext)
        self.assertIn("§2.6 真实感锚定", self.studio_roles)

    def test_native_audio_replaces_dubbing_step(self) -> None:
        # v1.13.6：Seedance 原生音频为主，且模型 Prompt 与剧本格式分层
        ext = read("drama-studio/references/external-platforms.md")
        for required in ("Seedance 原生音视频联合生成为主", "无需独立配音步骤", "台词内容放在 `{}` 内",
                         "音乐用 `（）`、音效用 `<>`、字幕用 `【】`",
                         "Dreamina 页面示例", "provider/adapter",
                         "每个独立 Clip 在路由后的声音职责位声明角色声线/母音色绑定一次", "外部 WAV/TTS 后备", "音声设计提示词要点"):
            with self.subTest(required=required):
                self.assertIn(required, ext)
        self.assertNotIn("角色名+动作表情描述+冒号+引号台词", ext)
        self.assertNotIn("jimeng audio create", ext)
        audio = read("drama-studio/references/dimensions/dim-audio.md")
        for required in ("原生音频双轨制", "Seedance 提示词格式", "台词内容放在 `{}` 内", "音色锚定", "翻车回退"):
            with self.subTest(required=required):
                self.assertIn(required, audio)
        self.assertNotIn("对白格式（官方规范", audio)
        self.assertIn("外部 TTS", audio)
        self.assertNotIn("jimeng audio create", audio)

    def test_studio_prompt_format_routes_and_model_default_wiring(self) -> None:
        # Wiring guards only; actual prompt consumption is checked with a reader agent.
        prompt = self.studio_prompt
        four_block_schema = prompt.split("### 2A. 通用四区块", 1)[1].split("```", 2)[1]
        four_block_headings = [
            line for line in four_block_schema.splitlines() if line.startswith("【")
        ]
        self.assertEqual(
            ["【基础设定】", "【氛围与画质】", "【声音】", "【画面内容】"],
            four_block_headings,
        )
        eight_block_section = prompt.split("### 2B. 30 秒直出专项八段式", 1)[1]
        heading_map, template_tail = eight_block_section.split("```text", 1)
        eight_block_schema = template_tail.split("```", 1)[0]
        eight_block_headings = [
            line for line in eight_block_schema.splitlines() if line.startswith("=== BLOCK")
        ]
        expected_english_headings = [
            "=== BLOCK 1: MASTER REFERENCE BINDING ===",
            "=== BLOCK 2: VISUAL STYLE & MEDIUM MANDATE ===",
            "=== BLOCK 3: ANTI-GLITCH & PROP TRACKING RULES ===",
            "=== BLOCK 4: SCENE CONTEXT & CONTINUITY LOCK ===",
            "=== BLOCK 5: TIME-CODED DIALOGUE & AUDIO BUDGET ===",
            "=== BLOCK 6: ENVIRONMENTAL TEXT DEVICE ===",
            "=== BLOCK 7: SHOT BREAKDOWN & SPATIAL LOGIC (30 SECONDS) ===",
            "=== BLOCK 8: AUDIO & FOLEY SPECIFICATIONS ===",
        ]
        expected_chinese_headings = [
            "=== 区块 1：主参考绑定 ===",
            "=== 区块 2：视觉风格与媒介指令 ===",
            "=== 区块 3：防错与道具追踪规则 ===",
            "=== 区块 4：场景语境与连续性锁 ===",
            "=== 区块 5：带时码对白与音频预算 ===",
            "=== 区块 6：场内文字载体 ===",
            "=== 区块 7：镜头拆解与空间逻辑（30 秒） ===",
            "=== 区块 8：音频与拟音规格 ===",
        ]
        self.assertEqual(expected_english_headings, eight_block_headings)
        for index, (english, chinese) in enumerate(
            zip(expected_english_headings, expected_chinese_headings), start=1
        ):
            self.assertIn(f"| {index} | `{english}` | `{chinese}` |", heading_map)
        # Startup routing is exercised by the consuming-agent scenarios;
        # keep this check scoped to the output format's exclusivity.
        for fragment in ("不与四区块双交",):
            self.assertIn(fragment, prompt)
        for fragment in ("sum of per-line actual pronunciation counts",
                         "actual pronunciation count"):
            self.assertIn(fragment, eight_block_schema)
        for fragment in ("`seedance2.0fast_vip` / 15 秒一组", "两卡", "5–8 个分镜",
                         "参考生仅 8s", "同一 Clip 内切场景不重置时间", "一个 Shot"):
            self.assertIn(fragment, prompt)
        for fragment in ("用户指定或第 0 步默认", "规划时同时定位", "seedance.md", "dreamina.md"):
            self.assertIn(fragment, self.studio_skill)
        roles = read("drama-studio/references/role-cards.md")
        self.assertIn("连续音频起止秒、覆盖镜号与可见口型区间", roles)
        self.assertIn("逐 Clip 路由后视频提示词", roles)
        self.assertIn("Dialogue/OS/VO", roles)
        with self.subTest(consumer="闻笙非对白声层路由"):
            self.assertTrue(
                "环境、呼吸、脚步、操作声、拟音与音乐落进通用【声音】/30秒专项 Block 8"
                in roles,
                "闻笙必须把普通任务的非对白声层路由到通用【声音】",
            )
        failure_atlas = read("drama-studio/references/failure-atlas.md")
        audio_failure_row = next(
            line for line in failure_atlas.splitlines() if line.startswith("| 6.5 |")
        )
        with self.subTest(consumer="严恪30秒容量失败回退"):
            self.assertTrue(
                "30 秒直出专项不足时先重排，仍不足则回剧情层等待裁决，不延长、拆分/分单或加速"
                in audio_failure_row,
                "30 秒专项不得回退到延长、拆分/分单或加速",
            )
            self.assertTrue(
                "其他时长按 dim-audio 对应任务分支处理" in audio_failure_row,
                "通用回退必须限定为其他时长并服从 dim-audio",
            )
        style = read("drama-studio/references/dimensions/dim-style.md")
        self.assertIn("正文服从项目语言锁", style)
        self.assertNotIn("Vidu=全模块中文", style)
        for stale in ("七段式", "单块最小 2s", "默认 1 Shot/Clip"):
            self.assertNotIn(stale, prompt)

    def test_continuous_dialogue_budget_and_reference_boundaries(self) -> None:
        audio = read("drama-studio/references/dimensions/dim-audio.md")
        for fragment in ("3–3.5 发音字/秒", "不是统一行业标准", "标点不计字但停顿计时",
                         "顺序发声的所有角色共用时间", "L-Cut 不增加声窗容量", "跨独立生成 Clip",
                         "不会自动逐句定位", "不重复加", "原生音频优先", "逐句发音量求和必须等于",
                         "逐句起止声窗时长求和必须大于或等于", "30 秒直出专项容量不足",
                         "不得延长、拆分/分单或加速"):
            self.assertIn(fragment, audio)
        self.assertIn("对白/OS/VO 中的比喻", self.studio_prompt)
        self.assertIn("不造 `@图1`", self.studio_prompt)
        self.assertNotIn("每镜重复写", audio)
        self.assertNotIn("24fps 下 1 字", read("drama-studio/references/lip-sync.md"))

    def test_frozen_mother_voice_is_reused_in_seedance_native_audio(self) -> None:
        ext = read("drama-studio/references/external-platforms.md")
        audio = read("drama-studio/references/dimensions/dim-audio.md")
        assets = read("drama-studio/references/asset-library.md")
        roles = read("drama-studio/references/role-cards.md")
        dreamina = read("drama-studio/references/models/dreamina.md")
        for text in (ext, audio, assets, roles, dreamina):
            with self.subTest(source=text[:40]):
                self.assertIn("已冻结母音色", text)
        self.assertIn("`multimodal2video --audio` 音色参考", ext)
        self.assertIn("仍由 Seedance 原生生成对白与口型", ext)
        self.assertIn("明确绑定音频编号、角色与音色用途", ext)
        self.assertIn("外部 TTS 才是后备", ext)
        self.assertIn("不能只靠重复文字音色描述", audio)
        self.assertIn("后续正式对白镜", assets)
        self.assertIn("母音色参考路由", roles)
        self.assertIn("优先作为 `multimodal2video --audio`", dreamina)
        self.assertNotIn("需要精确母音色时使用外部 WAV/TTS 后备", dreamina)

    def test_murphy_boundaries_keep_fast_path_and_authority_limits(self) -> None:
        self.assertIn("快写/单集预览在原文茵任务内", self.skill)
        self.assertIn("未经润色的原始草稿", self.skill)
        self.assertIn("不新增用户弹窗", self.submission)
        self.assertIn("不得生成、推断或预填", self.submission)
        self.assertIn("不新增角色", self.skill)

    def test_public_docs_and_markdown_count_match_release(self) -> None:
        readme = read("README.md")
        changelog = read("CHANGELOG.md")
        for skill in ("drama-crew", "drama-studio"):
            # Catch a stale release table without pinning all future releases
            # to a particular version or an arbitrary file-count ceiling.
            frontmatter = read(f"{skill}/SKILL.md").split("---", 2)[1]
            version = re.search(r"^\s*version:\s*[\"']?([0-9]+(?:\.[0-9]+)+)[\"']?\s*$", frontmatter, re.M)
            row = re.search(rf"^\| `{skill}` \| ([^|]+) \| (\d+) \|", readme, re.M)
            self.assertIsNotNone(version)
            self.assertIsNotNone(row)
            packaged_files = [
                path for path in (ROOT / skill).rglob("*")
                if path.is_file() and path.suffix in {".md", ".py", ".json"}
                and path.name not in {"local-config.json", "local-index.md"}
            ]
            self.assertEqual(version.group(1).strip(), row.group(1).strip())
            self.assertEqual(len(packaged_files), int(row.group(2)))
            self.assertIn(f"`{skill}` v{version.group(1).strip()}", changelog)
        self.assertIn("`drama-studio` v1.15.2", changelog)
        self.assertIn("`drama-studio` v1.11.2", changelog)
        self.assertIn("投稿阅读稿", readme)
        for public_doc in (readme, read("docs/使用说明.md")):
            with self.subTest(public_doc=public_doc[:30]):
                self.assertIn("《剧名》_标准投稿阅读稿.md", public_doc)
                self.assertIn("audit_screenplay.py", public_doc)
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

    def test_duration_structure_review_requires_actual_fatigue_evidence(self) -> None:
        self.assertIn("实际疲劳或设计重复证据", self.commercial)
        self.assertNotIn("±10%", self.commercial)
        self.assertNotIn("每 10 集至少 1 次结构变奏", self.commercial)
        self.assertIn("时长结构模板化", self.scorecard)
        self.assertIn("时长结构模板化", self.roles)
        self.assertIn("16 条", self.scorecard)

    def test_v620_natural_dialogue_and_flexible_story_contracts_are_wired(self) -> None:
        story = read("drama-crew/references/story-structure.md")
        naming = read("drama-crew/references/naming-rules.md")
        hit = read("drama-crew/references/hit-craft.md")
        topic = read("drama-crew/references/topic-selection.md")
        active_contracts = "\n".join((self.dialogue, self.writing, self.roles, self.scorecard))

        for required in (
            "正常承接词",
            "因果辩解",
            "完整听答",
            "惯性与受压变化",
            "早确认关系",
            "能力兑现",
            "共同完成",
            "相邻微动作",
            "3–3.5 字/秒",
        ):
            with self.subTest(required=required):
                self.assertIn(required, "\n".join((active_contracts, story, self.commercial)))

        for obsolete in (
            "关键场必须有",
            "互通心意不早于收官前 10%",
            "禁纯约会集",
            "稀有姓优先",
            "名意锁",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, "\n".join((active_contracts, story, naming)))

        self.assertIn("类型融合", hit)
        self.assertIn("未知时保持 `carrier=pending`", topic)

    def test_v620_review_round_one_contracts_are_synchronized(self) -> None:
        topic = read("drama-crew/references/topic-selection.md")
        timing_contracts = "\n".join((self.skill, self.dialogue, self.roles))
        commercial_contracts = "\n".join((self.commercial, self.roles))

        for required in (
            "只有用户、平台或已批准预算明确设定的硬性时长才冻结",
            "暂排场景/分镜秒数",
            "模型单次 Clip 上限",
            "不得静默突破",
            "实际付费调用仍需另行授权",
        ):
            with self.subTest(required=required):
                self.assertIn(required, timing_contracts)

        for obsolete in (
            "付费墙比例",
            "三级卡点速查表",
            "四大公式择二",
            "付费后 1-2 集",
        ):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, commercial_contracts)
        self.assertIn("实际 IAP/IAA/混合条件", commercial_contracts)
        self.assertIn("最早有效节点", commercial_contracts)

        self.assertNotIn(
            "句长偏好 / 口头禅或高频词 / 语速节奏 / 拒绝方式", self.roles
        )
        self.assertNotIn("句长偏好/口头禅/语速节奏/拒绝方式", self.roles)
        for required in ("惯性与受压变化", "无目的宣读", "解释失效", "诊断越权"):
            with self.subTest(required=required):
                self.assertIn(required, self.roles)
        review_contracts = "\n".join((self.roles, self.scorecard))
        for obsolete in ("无阻力宣读证据链", "句句完整解释动机", "解释性语言 / 诊断性语言"):
            with self.subTest(obsolete=obsolete):
                self.assertNotIn(obsolete, review_contracts)

        ledger_wiring = "\n".join((self.skill, self.roles))
        self.assertIn("连续性风险命中或批量续写", ledger_wiring)
        self.assertNotIn("集数 ≥10 时首批", ledger_wiring)
        self.assertNotIn("账本初始化（集数≥10）", ledger_wiring)

        self.assertIn("当期模型/制作证据", topic)
        self.assertIn("制作权衡", topic)
        self.assertNotIn("超现实题材给 AI 漫剧，情感现实题材给仿真人或真人", topic)

    def test_dialogue_diagnostics_require_scene_evidence_not_name_swap_templates(self) -> None:
        subtext = section_between(self.dialogue, "## §2 ", "## §3 ")
        emergency_table = section_between(self.dialogue, "## §5 ", "## §6 ")

        self.assertIn("只有人物确有隐瞒、自欺或难言的依据时", subtext)
        self.assertIn("才提示这场戏可能没找到戏眼", subtext)
        self.assertNotIn("三层全平 = 这场戏还没找到戏眼", subtext)

        self.assertIn("完整核心回合", emergency_table)
        self.assertIn("实际同腔证据", emergency_table)
        self.assertNotIn("台词换名试，通用即删", emergency_table)
        self.assertNotIn("换成角色专属句式", emergency_table)
        self.assertNotIn("霸总「你行的。不行也得行。」", emergency_table)

    def test_writing_guidance_uses_function_and_evidence_not_fixed_article_rules(self) -> None:
        pacing = section_between(self.writing, "## 2. ", "## 3. ")
        ai_trace = section_between(self.writing, "## 10. ", "## 11. ")

        for required in ("适用条件", "段落功能", "实际疲劳或设计重复证据"):
            with self.subTest(pacing_required=required):
                self.assertIn(required, pacing)
        for obsolete in (
            "统一骨架",
            "标准节奏",
            "禁止慢铺垫",
            "10 秒内交代",
            "每 15-20 秒",
            "每 15–20 秒",
        ):
            with self.subTest(pacing_obsolete=obsolete):
                self.assertNotIn(obsolete, pacing)

        for required in ("角色", "场合", "保留原意", "最小修复"):
            with self.subTest(ai_trace_required=required):
                self.assertIn(required, ai_trace)
        for obsolete in ("有观点", "长短句交替", "允许混乱", "完美结构=机械"):
            with self.subTest(ai_trace_obsolete=obsolete):
                self.assertNotIn(obsolete, ai_trace)

    def test_role_dispatch_preserves_only_hard_timing_and_keeps_risk_rechecks(self) -> None:
        dialogue_refinement = section_between(
            self.roles,
            "### 文茵 3.7 台词桌读与表演化精修下发模板",
            "## 青梧 · 正典官",
        )
        canon_owner = section_between(
            self.roles,
            "## 青梧 · 正典官",
            "### 青梧 3.7 改动场局部复核下发模板",
        )

        self.assertIn("明确硬限制", dialogue_refinement)
        self.assertIn("暂排时长", dialogue_refinement)
        self.assertIn("活动母稿、集纲与制作计划", dialogue_refinement)
        self.assertNotIn("保持原场次结构、动作节拍和时长目标", dialogue_refinement)

        for required in (
            "实际低风险小体量",
            "已命中连续性风险",
            "用户要求核查",
            "既有 3.7 局部复核",
            "不因集数少于 10 集跳过",
        ):
            with self.subTest(canon_required=required):
                self.assertIn(required, canon_owner)
        self.assertNotIn("<10 集的小体量", canon_owner)

    def test_topic_confirmation_derives_and_passes_romance_axis_without_new_question(self) -> None:
        topic_confirmation = section_between(self.skill, "### 第 2.5 步：", "### 第 3 步：")

        for required in (
            "入选主题是否明确包含恋爱主线或副线",
            "`romance_axis=on|off`",
            "自动确定",
            "下传文茵",
            "不新增用户提问",
        ):
            with self.subTest(required=required):
                self.assertIn(required, topic_confirmation)

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

    def test_runtime_evidence_does_not_pad_dialogue_or_claim_measured_duration(self) -> None:
        for required in (
            "诊断区间，不是逐集最低配额",
            "禁止为补足字数增加同义解释或程序话术",
            "逐项动作/停顿估时",
            "只能标为估算",
            "固定每条动作",
            "固定秒数",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.commercial)
        self.assertNotIn("净台词按 350–500 字收", self.commercial)
        self.assertIn("不适用逐集最低配额", self.writing)
        self.assertNotIn("净台词 350–500 字 = 配音对白量", self.roles)
        self.assertNotIn("净台词 350–500 字 / 语速", self.roles)

    def test_midseries_semantic_repetition_and_time_anchor_gates_are_wired(self) -> None:
        for required in (
            "语义功能重复",
            "删除后不改变选择、关系、证据、压力或后果",
            "普通中段、低冲突或报告类场景",
        ):
            with self.subTest(required=required):
                self.assertIn(required, "\n".join((self.dialogue, self.scorecard)))
        for required in ("显式时间锚", "与账本推进一致"):
            with self.subTest(required=required):
                self.assertIn(required, self.ledger)
        self.assertIn("预检失败不得进入评分放行", self.scorecard)
        self.assertIn("普通中段、低冲突或报告类场景", self.roles)

    def test_dsh_crew_mechanisms_are_absorbed_without_new_workflow(self) -> None:
        for required in (
            "机制真实契约",
            "剧中披露状态",
            "世界真实如何运行",
            "人物当前知道",
            "观众当前知道",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.world)

        for required in (
            "机制耗尽",
            "收束 / 改造 / 移交",
            "信息密度过匀",
            "代价即时结清",
            "承重声源",
            "主动留白",
            "撤出与恢复",
            "声桥",
            "混音参数归制作侧",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.writing)

        for required in (
            "可见/可听载体",
            "直接支持的最强结论",
            "尚未证明的推断",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.ledger)

        combined = "\n".join((self.roles, self.scorecard))
        self.assertIn("机制耗尽", combined)
        self.assertIn("信息密度过匀", combined)
        self.assertIn("尚未证明的推断", combined)

    def test_dsh_studio_mechanisms_are_absorbed_without_mechanical_rules(self) -> None:
        for required in (
            "`prompt_only` / `file_ready` / `external_mount_plan`",
            "`reuse` / `new_variant` / `new_asset` / `unresolved`",
            "未命名群演",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_assets)

        for required in (
            "保留 Shot ID，提升修订号",
            "新 Shot ID",
            "旧 ID 停用",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_shots)

        assembly = "\n".join((self.studio_prompt, self.studio_storyboard))
        for required in (
            "首帧只写开始时已经成立",
            "尾帧只写目标终点",
            "逐字正文只出现一次",
            "`show_now` / `withhold_now`",
            "实际 provider 支持",
        ):
            with self.subTest(required=required):
                self.assertIn(required, assembly)

        for required in (
            "承重台词",
            "不固定顺序",
            "不要求人人错峰反应",
            "诊断",
        ):
            with self.subTest(required=required):
                self.assertIn(required, self.studio_performance)

        for required in (
            "参考资产就绪三态",
            "身份/状态决策四词",
            "未命名群演",
            "保留 Shot ID，提升修订号",
            "首帧只写开始时已经成立",
            "逐字正文只出现一次",
            "`show_now` / `withhold_now`",
            "实际 provider 支持",
            "承重台词",
            "不固定顺序",
        ):
            with self.subTest(role_dispatch=required):
                self.assertIn(required, self.studio_roles)

        for required in (
            "参考资产就绪三态",
            "身份/状态决策四词",
            "保留 Shot ID，提升修订号",
            "`show_now` / `withhold_now`",
            "逐字正文只出现一次",
        ):
            with self.subTest(main_flow=required):
                self.assertIn(required, self.studio_skill)

        active_contracts = "\n".join(
            (self.studio_storyboard, self.studio_performance, self.studio_prompt)
        )
        self.assertNotIn("完整情绪链必须按顺序走完", active_contracts)
        self.assertNotIn("[OS]=同场画外对白", active_contracts)


if __name__ == "__main__":
    unittest.main()
