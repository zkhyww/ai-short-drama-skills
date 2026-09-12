"""Catch missing or divergent startup guidance in independently installed skills."""

from pathlib import Path
import shutil
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


class StartupGuideDistributionTests(unittest.TestCase):
    def test_single_skill_install_keeps_the_complete_shared_guide(self):
        # Break caught: an install copies just one skill, losing a repo-only
        # guide or shipping a stale second copy with different startup behavior.
        guides = []
        for skill in ("drama-crew", "drama-studio"):
            with tempfile.TemporaryDirectory() as tmp:
                installed = Path(tmp) / skill
                shutil.copytree(ROOT / skill, installed,
                                ignore=shutil.ignore_patterns("__pycache__", "local-config.json"))
                guide = installed / "references" / "startup-guide.md"
                self.assertTrue(guide.is_file(), f"{skill} lacks its standalone startup guide")
                guides.append(guide.read_bytes())
        self.assertEqual(guides[0], guides[1], "Packaged startup-guide copies have drifted")


if __name__ == "__main__":
    unittest.main()
