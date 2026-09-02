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
        cls.submission = read("drama-crew/references/submission-format.md")

    def test_version_reference_and_stage_order_are_wired(self) -> None:
        self.assertIn("version: 6.15.0", self.skill)
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
        self.assertIn("| `drama-crew` | 6.15.0 | 18 |", readme)
        self.assertIn("`drama-crew` v6.15.0", changelog)
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
        self.assertIn("14 条", self.scorecard)

    def test_artifact_necessity_matrix_is_documented(self) -> None:
        self.assertIn("产物必要性判定表", self.submission)
        self.assertIn("必产条件", self.submission)
        self.assertIn("全量档", self.submission)
        self.assertIn("标准档", self.submission)
        self.assertIn("轻量档", self.submission)
        self.assertIn("产物档位", self.skill)
        self.assertIn("产物必要性判定表", self.skill)

    def test_cognitive_permission_split_from_knowledge_ledger(self) -> None:
        self.assertIn("认知与表达权限", self.dialogue)
        self.assertIn("认知错位", self.dialogue)
        self.assertIn("表达权限", self.dialogue)
        self.assertIn("知情范围", self.dialogue)
        for required in ("认知与表达权限", "越权", "退回上游", "9.1"):
            with self.subTest(required=required):
                self.assertIn(required, self.dialogue)

    def test_ai_trace_uses_cause_first_minimal_fix_and_no_forced_edit(self) -> None:
        self.assertIn("处置三原则", self.writing)
        self.assertIn("成因定位先于改写", self.writing)
        self.assertIn("最小修复", self.writing)
        self.assertIn("自然文本不硬改", self.writing)
        self.assertIn("本段不改", self.scorecard)
        self.assertIn("不为评分强改", self.scorecard)

    def test_observer_blind_spot_excludes_action_beat_section(self) -> None:
        self.assertIn("观察者盲区", self.writing)
        self.assertIn("无功能环境", self.scorecard)
        self.assertIn("观察者盲区", self.scorecard)
        self.assertIn("认知与视角越界", self.scorecard)
        self.assertIn("§12 豁免声明", self.writing)
        self.assertIn("禁止用「观察者盲区/关键帧」思维砍动作节拍段", self.writing)
        self.assertIn("不适用于动作节拍段", self.roles)
        self.assertNotIn("2-3 个关键帧", self.writing)
        self.assertNotIn("2-3个关键帧", self.writing)

    def test_conflict_resolution_starts_from_earliest_source(self) -> None:
        self.assertIn("最早出现问题的源点", self.ledger)
        self.assertIn("顺链核对", self.ledger)
        self.assertIn("最早出现问题的源点集/场", self.roles)


if __name__ == "__main__":
    unittest.main()
