"""Static owner/consumer contracts, not generated-media or fresh-context tests."""
from pathlib import Path
import json
import os
import re
import unittest

ROOT = Path(os.environ.get("PRODUCTION_SKILL_ROOT", Path(__file__).resolve().parents[1]))


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


class ProductionLearningContracts(unittest.TestCase):
    def contains(self, path, *tokens):
        body = read(path)
        missing = [token for token in tokens if token not in body]
        self.assertFalse(missing, f"{path}: missing anchors {missing}")
        return body

    def test_defaults_have_one_owner_reachable_from_consumers(self):
        owner = "drama-studio/references/prompt-assembly.md"
        self.contains(owner, "4–15", ">15–30", "seedance2.0fast_vip",
                      "seedance2.5", "720p", "单次", "单集")
        for consumer in (
            "drama-studio/SKILL.md",
            "drama-studio/references/models/seedance.md",
            "drama-studio/references/models/dreamina.md",
            "drama-studio/references/external-platforms.md",
            "drama-crew/references/startup-guide.md",
            "drama-studio/references/startup-guide.md",
        ):
            with self.subTest(consumer=consumer):
                self.contains(consumer, "prompt-assembly.md", "§1")
        self.assertEqual(
            (ROOT / "drama-crew/references/startup-guide.md").read_bytes(),
            (ROOT / "drama-studio/references/startup-guide.md").read_bytes(),
        )

    def test_brand_purpose_is_reachable_without_mandatory_monetization(self):
        self.contains("drama-crew/references/startup-guide.md", "品牌用途", "commercial-craft")
        self.contains("drama-crew/SKILL.md", "commercial-craft.md", "§8")
        owner = self.contains("drama-crew/references/commercial-craft.md",
                              "品牌角色", "结尾回报", "排除", "未经实测")
        self.assertNotIn("第一步永远先问", owner)

    def test_direct_assembly_owner_and_entry_are_present(self):
        self.contains("drama-studio/SKILL.md", "纯拼接", "陆离角色卡", "技术导出")
        self.contains("drama-studio/references/role-cards.md",
                      "纯拼接范围", "标准完整制作", "原生音轨", "未做语义复审")

    def test_reference_diagnosis_and_reuse_owner_is_reachable(self):
        self.contains("drama-studio/SKILL.md", "asset-library.md")
        self.contains("drama-studio/references/asset-library.md",
                      "低分辨率", "运动模糊", "残影", "代表性", "批量放大",
                      "重建", "事实恢复", "同 ID", "拓扑", "背景活动")

    def test_appearance_revision_reaches_actual_selection_contract(self):
        for consumer in ("drama-studio/SKILL.md",
                         "drama-studio/references/role-cards.md"):
            self.contains(consumer, "shot-contract", "实际选片")
        self.contains("drama-studio/references/shot-contract.md",
                      "前后相邻", "妆容", "衣装", "台词", "出口方向", "未受影响")

    def test_dialogue_and_audio_evidence_have_owners(self):
        self.contains("drama-crew/SKILL.md", "dialogue-craft", "§9")
        self.contains("drama-crew/references/dialogue-craft.md",
                      "请求/意愿", "已获许可", "已经完成", "WPM", "互斥")
        self.contains("drama-studio/references/prompt-assembly.md",
                      "提示词时码", "生成音频", "实际选片", "ASR", "静帧")

    def test_request_and_cost_evidence_reach_provider_owner(self):
        self.contains("drama-studio/SKILL.md", "models/dreamina.md", "file-management.md")
        self.contains("drama-studio/references/models/dreamina.md",
                      "冻结请求", "实际命令", "按序", "credit_count", "余额", "价格偏差")
        self.contains("drama-studio/references/file-management.md", "实际命令", "按序")

    def test_timeline_contract_documents_executable_schema(self):
        body = self.contains("drama-studio/references/role-cards.md",
                             "--timeline", "--clip", "timeline=Path", "720×1280",
                             "相对路径", "互斥", "原始媒体")
        examples = re.findall(r'`(\{"clips":\[.*?\]\})`', body)
        self.assertTrue(examples, "No timeline JSON example in editing owner")
        clip = json.loads(examples[0])["clips"][0]
        self.assertEqual(set(clip), {"path", "in", "out"})
        self.assertLess(clip["in"], clip["out"])
        self.contains("drama-studio/references/file-management.md",
                      "既有时间线", "源文件", "入点", "出点", "顺序")

    def test_clip_capacity_has_spatial_and_display_basis(self):
        self.contains("drama-studio/references/prompt-assembly.md",
                      "Shot（", "Clip（", "动作依赖", "接触", "目标屏幕", "光源")

    def test_explicit_capability_examples_survive_default_change(self):
        # Supported choices are not all defaults; retain real 1080p capability.
        self.contains("drama-studio/references/models/dreamina.md",
                      "Seedance 2.5", "480p/720p/1080p")
        self.contains("drama-studio/references/models/seedance.md", "1080p")


if __name__ == "__main__":
    unittest.main()
