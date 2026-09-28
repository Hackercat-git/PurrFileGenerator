import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
import purrfile  # noqa: E402

REPOS = [
    {"name": "a", "language": "Python", "stargazers_count": 10, "forks_count": 2, "fork": False},
    {"name": "b", "language": "Python", "stargazers_count": 5, "forks_count": 1, "fork": False},
    {"name": "c", "language": "Go", "stargazers_count": 1, "forks_count": 0, "fork": False},
    {"name": "d", "language": "Rust", "stargazers_count": 99, "forks_count": 9, "fork": True},
]


class TestPurrFileGenerator(unittest.TestCase):
    def test_forks_excluded_by_default(self):
        s = purrfile.summarize(REPOS)
        self.assertEqual(s["repos"], 3)
        self.assertEqual(s["stars"], 16)
        self.assertEqual(s["languages"][0], ("Python", 2))

    def test_forks_included(self):
        s = purrfile.summarize(REPOS, include_forks=True)
        self.assertEqual(s["repos"], 4)
        self.assertEqual(s["top"][0][0], "d")

    def test_svg_escapes_username(self):
        svg = purrfile.render_svg("<x>", purrfile.summarize(REPOS))
        self.assertIn("&lt;x&gt;", svg)
        self.assertTrue(svg.startswith("<svg"))

    def test_empty_profile(self):
        svg = purrfile.render_svg("nobody", purrfile.summarize([]))
        self.assertIn("nobody", svg)


if __name__ == "__main__":
    unittest.main()
