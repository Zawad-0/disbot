from pathlib import Path
import unittest


class ReadmeTest(unittest.TestCase):
    def test_readme_mentions_project_name(self):
        repo_root = Path(__file__).resolve().parents[1]
        readme = repo_root / "README.md"

        self.assertTrue(readme.exists(), "README.md should exist")
        self.assertIn("disbot", readme.read_text(encoding="utf-8").lower())


if __name__ == "__main__":
    unittest.main()
