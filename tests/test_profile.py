import importlib.util
import json
import tempfile
import unittest
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
        self.assertEqual([p["name"] for p in projects], ["Archived", "Fork", "New"])

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
        for records in [[], [repo("a"), repo("A")], [repo("../bad")], [repo("a", owner={"login": "Other"})]]:
            with self.subTest(records=records), self.assertRaises(ValueError):
                profile.select_projects(records)

    def test_star_total_includes_all_public_projects_but_not_site_or_private_repos(self):
        projects = profile.select_projects([
            repo(".github", 90), repo("nousphera.github.io", 80),
            repo("Private", 70, private=True), repo("Highlighted", 7),
            repo("OtherPublicProject", 2), repo("Archived", 3, archived=True),
            repo("Fork", 4, fork=True),
        ])
        navigation = profile.render_navigation(projects)
        self.assertIn("16 GitHub stars across 4 public project repositories", navigation)
        self.assertIn('href="https://vtsouval.github.io/"', navigation)
        self.assertIn('href="https://nousphera.github.io/"', navigation)
        self.assertNotIn("#publications", navigation)
        self.assertEqual(navigation.count("<a "), 3)
        self.assertEqual(navigation.count("&nbsp; · &nbsp;"), 2)

    def test_invalid_star_counts_abort_instead_of_publishing_a_false_total(self):
        for count in [-1, True, "9", None, 2.5]:
            with self.subTest(count=count), self.assertRaises(ValueError):
                profile.select_projects([repo("Example", count)])

    def test_uncatalogued_projects_do_not_create_an_extra_section(self):
        projects = profile.select_projects([repo("New")])
        self.assertEqual(profile.render_catalog([], projects), "")

    def test_concept_highlighting_escapes_html_and_rejects_missing_terms(self):
        item = {"repo": "Example", "summary": "<unsafe> with vectors", "highlight": "<unsafe>"}
        self.assertEqual(profile.concept_summary(item), "<strong>&lt;unsafe&gt;</strong> with vectors")
        item["highlight"] = "missing"
        with self.assertRaises(ValueError):
            profile.concept_summary(item)

    def test_hidden_highlights_do_not_reappear_as_more_projects(self):
        catalog = [{"title": "Direction", "icon": "layers", "projects": [
            {"repo": "Visible", "summary": "A method."},
            {"repo": "Hidden", "summary": "Another method.", "highlighted": False}]}]
        projects = profile.select_projects([repo("Visible"), repo("Hidden")])
        text = profile.render_catalog(catalog, projects)
        self.assertIn("Visible", text)
        self.assertNotIn("Hidden", text)
        self.assertNotIn("More projects", text)

    def test_overview_uses_one_tag_per_public_highlight_and_keeps_resource_links(self):
        catalog = json.loads((profile.ROOT / "profile/catalog.json").read_text())
        records = [repo(p["repo"]) for g in catalog for p in g["projects"]]
        text = profile.render_catalog(catalog, profile.select_projects(records))
        self.assertEqual(text.count('alt="Open '), 12)
        self.assertEqual(text.count('<kbd>'), 12)
        self.assertNotIn("<table", text)
        self.assertNotIn("nowrap", text)
        self.assertNotIn("<details", text)
        self.assertNotIn("Paper &amp; code links", text)
        self.assertIn("research-overview-phone-dark-static.svg", text)
        self.assertIn("prefers-reduced-motion: reduce", text)
        for group in catalog:
            self.assertIn(group["title"], text)
        for name in ("PLiX", "DA_MLDG", "FiBA"):
            self.assertNotIn(f"project-label-{name}-", text)
        self.assertIn("https://doi.org/10.1145/3626242", text)
        self.assertIn("https://github.com/Nousphera/FedLN", text)
        self.assertIn('alt="FedLN code repository"', text)
        self.assertIn('alt="Read FedLN paper"', text)
        self.assertNotIn("<script", text)

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
            self.assertNotIn("<table", outputs["README.md"])
            self.assertEqual(outputs["README.md"].count("### Highlighted Research Projects"), 1)
            self.assertNotIn("star-tracker", outputs["README.md"])
            self.assertNotIn("Star tracker", outputs["README.md"])
            self.assertEqual(list(root.glob("data/*")), [])


if __name__ == "__main__":
    unittest.main()
