import importlib.util
import json
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

SPEC = importlib.util.spec_from_file_location("profile_builder", Path(__file__).resolve().parents[1] / "scripts/update_profile.py")
profile = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(profile)


def repo(name, stars=0, **kwargs):
    return {"name": name, "owner": {"login": "Nousphera"}, "private": False,
            "stargazers_count": stars, "description": "Research project", **kwargs}


class ProfileTests(unittest.TestCase):
    def test_tracks_all_public_projects_including_new_archived_and_forked(self):
        data = [repo(".github", 50), repo("nousphera.github.io", 50), repo("Private", 50, private=True),
                repo("New", 4), repo("Archived", 3, archived=True), repo("Fork", 2, fork=True)]
        projects = profile.select_projects(data)
        self.assertEqual([p["name"] for p in projects], ["New", "Archived", "Fork"])
        self.assertEqual(sum(p["stars"] for p in projects), 9)

    def test_pagination_loads_a_second_page(self):
        urls = []
        def request(url):
            urls.append(url)
            return [repo(f"p{i}") for i in range(100)] if url.endswith("page=1") else [repo("last", 7)]
        records = profile.fetch_repositories(request)
        self.assertEqual(len(records), 101)
        self.assertTrue(urls[-1].endswith("page=2"))

    def test_pagination_failure_never_returns_partial_totals(self):
        def request(url):
            if url.endswith("page=1"):
                return [repo(f"p{i}") for i in range(100)]
            raise RuntimeError("API unavailable")
        with self.assertRaises(RuntimeError):
            profile.fetch_repositories(request)

    def test_invalid_or_empty_responses_are_rejected(self):
        for records in [[], [repo("a"), repo("A")], [repo("../bad")], [repo("a", -1)],
                        [repo("a", True)], [repo("a", owner={"login": "Other"})]]:
            with self.subTest(records=records), self.assertRaises(ValueError):
                profile.select_projects(records)

    def test_daily_snapshot_replaces_same_day_and_preserves_prior_days(self):
        history = profile.update_history([], profile.select_projects([repo("A", 7)]), "2026-10-15")
        history = profile.update_history(history, profile.select_projects([repo("A", 9)]), "2026-10-15")
        history = profile.update_history(history, profile.select_projects([repo("A", 8), repo("B", 1)]), "2026-10-16")
        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["repositories"], {"A": 9})
        self.assertEqual(history[1]["repositories"], {"A": 8, "B": 1})
        self.assertEqual(history[1]["stars"], 9)

    def test_dated_snapshots_never_backfill_the_past(self):
        history = profile.update_history([], profile.select_projects([repo("A", 7)]), "2026-10-15")
        with self.assertRaises(ValueError):
            profile.update_history(history, profile.select_projects([repo("A", 8)]), "2026-10-14")

    def test_new_projects_are_discoverable_and_metadata_is_escaped(self):
        projects = profile.select_projects([repo("New", description='[link](https://bad.example) | <img>\n**bold**')])
        text = profile.render_catalog([], projects)
        self.assertIn("More projects", text)
        self.assertIn("https://github.com/Nousphera/New", text)
        self.assertNotIn("[link]", text)
        self.assertNotIn("<img>", text)
        self.assertIn("&#124;", text)

    def test_trend_handles_zero_stars_and_a_single_observation(self):
        history = profile.update_history([], profile.select_projects([repo("A")]), "2026-10-15")
        for dark in (True, False):
            svg = profile.render_trend(history, dark)
            ET.fromstring(svg)
            self.assertNotIn("polyline", svg)
            self.assertIn("First daily snapshot", svg)

    def test_history_can_show_declining_totals(self):
        history = [{"date": "2026-10-15", "stars": 10, "repositories": {"A": 10}},
                   {"date": "2026-10-16", "stars": 3, "repositories": {"A": 3}}]
        svg = profile.render_trend(history)
        ET.fromstring(svg)
        self.assertIn('70.0,79.0 790.0,138.5', svg)

    def test_both_readmes_share_the_same_complete_generated_content(self):
        catalog = json.loads((profile.ROOT / "profile/catalog.json").read_text())
        records = [repo(p["repo"], 1) for g in catalog for p in g["projects"]]
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "profile").mkdir()
            for name in ["catalog.json", "README.template.md"]:
                (root / "profile" / name).write_text((profile.ROOT / "profile" / name).read_text())
            outputs = profile.build(root, records, "2026-10-15")
            self.assertEqual(outputs["README.md"], outputs["profile/README.md"])
            self.assertNotIn("{{", outputs["README.md"])
            self.assertEqual(outputs["README.md"].count("<details>"), 5)
            self.assertIn("14 stars across 14 public projects", outputs["README.md"])
            self.assertEqual(list(root.glob("data/*")), [])


if __name__ == "__main__":
    unittest.main()
