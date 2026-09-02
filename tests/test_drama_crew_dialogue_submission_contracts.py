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

    def test_version_reference_and_stage_order_are_wired(self) -> None:
        self.assertIn("version: 6.13.0", self.skill)
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
        submission_path = ROOT / "drama-crew/references/submission-format.md"
        self.assertTrue(submission_path.is_file())
        submission = submission_path.read_text(encoding="utf-8")
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
                self.assertIn(required, submission)
        self.assertIn("### 第 4A 步：内部制作母稿", self.skill)
        self.assertIn("### 第 4B 步：投稿阅读稿排版", self.skill)
        self.assertIn("只能把完整制作母稿交给 `drama-studio`", self.skill)
        self.assertIn("逐页渲染", submission)
        self.assertIn("只改投稿阅读稿的字体/分页/缩进/标题层级", self.skill)
        self.assertIn("在投稿阅读稿里改台词/动作/剧情", self.skill)
        self.assertIn("投稿阅读稿不得作为第二内容真源", self.roles)

    def test_murphy_boundaries_keep_fast_path_and_authority_limits(self) -> None:
        submission = read("drama-crew/references/submission-format.md")
        self.assertIn("快写/单集预览在原文茵任务内", self.skill)
        self.assertIn("未经润色的原始草稿", self.skill)
        self.assertIn("不新增用户弹窗", submission)
        self.assertIn("不得生成、推断或预填", submission)
        self.assertIn("不新增角色", self.skill)

    def test_public_docs_and_markdown_count_match_release(self) -> None:
        crew_markdown_count = len(list((ROOT / "drama-crew").rglob("*.md")))
        self.assertEqual(18, crew_markdown_count)
        readme = read("README.md")
        changelog = read("CHANGELOG.md")
        self.assertIn("| `drama-crew` | 6.13.0 | 18 |", readme)
        self.assertIn("`drama-crew` v6.13.0", changelog)
        self.assertIn("投稿阅读稿", readme)
        self.assertIn("台词桌读", readme)


if __name__ == "__main__":
    unittest.main()
