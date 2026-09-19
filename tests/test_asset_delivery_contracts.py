from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def read(path):
    return (ROOT / path).read_text(encoding='utf-8')


class AssetDeliveryContracts(unittest.TestCase):
    def test_tool_reachable_from_entry_and_delivery_owner(self):
        self.assertIn('scripts/build_production_board.py', read('drama-studio/SKILL.md'))
        owner = read('drama-studio/references/file-management.md')
        for field in ('build_production_board.py','--prompt-range','--image-root','只读','快照','原文'):
            self.assertIn(field,owner)

    def test_asset_work_is_distinct_from_identity_and_raw_prompts(self):
        owner = read('drama-studio/references/asset-library.md')
        for field in ('file_action','reuse','generate','rework','复用文件数','新制文件数'):
            self.assertIn(field,owner)
        self.assertIn('不从身份判词推断',owner)
        self.assertIn('同一文件的多个 Panel',owner)
        self.assertIn('大幅清晰正脸头肩肖像',owner)

    def test_owner_delivers_work_preview_then_separate_prompts(self):
        owner = read('drama-studio/references/role-cards.md')
        for field in ('本批工作与下一动作','实际资产图册','纯提示词引用','不强制看板'):
            self.assertIn(field,owner)

    def test_source_labels_are_not_rewritten_by_preview(self):
        owner = read('drama-studio/references/file-management.md')
        for field in ('来源采用状态','不改写','加载成功','内容审核','不打包媒体'):
            self.assertIn(field,owner)

    def test_shared_guide_is_identical_and_exposes_optional_delivery(self):
        path = 'references/startup-guide.md'
        self.assertEqual((ROOT/'drama-crew'/path).read_bytes(),(ROOT/'drama-studio'/path).read_bytes())
        self.assertIn('可视图册',read('drama-crew/'+path))
        self.assertIn('可选离线看板',read('drama-crew/'+path))


if __name__ == '__main__':
    unittest.main()
