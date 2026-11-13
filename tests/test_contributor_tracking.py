import json
import tempfile
import unittest
from pathlib import Path

from contributor_tracking import (
    count_contributor_entries,
    record_contributor,
    update_contributor_table,
)


class RecordContributorTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.served_path = Path(self.temp_dir.name) / "Served.json"

    def test_first_request_creates_account_block_and_count(self):
        times, already_processed = record_contributor(
            self.served_path, "octocat", "The Octocat",
            "2026-11-14", 101,
        )

        self.assertEqual(times, 1)
        self.assertFalse(already_processed)
        data = json.loads(self.served_path.read_text(encoding="utf-8"))
        self.assertEqual(data["Contributors"]["octocat"]["Times"], 1)
        self.assertEqual(data["Contributors"]["octocat"]["Requests"], ["101"])

    def test_repeat_request_updates_existing_account_block(self):
        record_contributor(
            self.served_path, "octocat", "The Octocat",
            "2026-11-14", 101,
        )
        times, already_processed = record_contributor(
            self.served_path, "octocat", "The Octocat",
            "2026-11-15", 102,
        )

        data = json.loads(self.served_path.read_text(encoding="utf-8"))
        self.assertEqual(times, 2)
        self.assertFalse(already_processed)
        self.assertEqual(len(data["Contributors"]), 1)
        self.assertEqual(len(data["Contributors"]["octocat"]["History"]), 2)

    def test_same_issue_is_idempotent(self):
        record_contributor(
            self.served_path, "octocat", "The Octocat",
            "2026-11-14", 101,
        )
        times, already_processed = record_contributor(
            self.served_path, "octocat", "The Octocat",
            "2026-11-14", 101,
        )

        data = json.loads(self.served_path.read_text(encoding="utf-8"))
        self.assertEqual(times, 1)
        self.assertTrue(already_processed)
        self.assertEqual(len(data["Contributors"]["octocat"]["History"]), 1)

    def test_legacy_entry_count_seeds_repeat_usage(self):
        times, already_processed = record_contributor(
            self.served_path, "octocat", "The Octocat", "2026-11-14", 101,
            initial_times=3,
        )
        self.assertEqual(times, 4)
        self.assertFalse(already_processed)


class ContributorTableTests(unittest.TestCase):
    def test_repeat_use_updates_one_cell_and_removes_legacy_duplicates(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Extraordinary.md"
            path.write_text(
                '<table class="contributors"><tr>'
                '<td><a href="https://github.com/octocat"><b>octocat</b></a></td>'
                '<td><a href="https://github.com/octocat/"><b>octocat</b></a></td>'
                '</tr></table>',
                encoding="utf-8",
            )

            update_contributor_table(
                path, "octocat", "https://example.com/avatar.png",
                "https://github.com/octocat", 3,
            )

            from bs4 import BeautifulSoup
            soup = BeautifulSoup(path.read_text(encoding="utf-8"), "html.parser")
            cells = soup.select('table.contributors td a[href="https://github.com/octocat"]')
            self.assertEqual(len(cells), 1)
            self.assertEqual(cells[0].find("small").get_text(strip=True), "Times: 3")

    def test_legacy_markdown_entries_can_be_counted(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Extraordinary.md"
            path.write_text(
                '<table class="contributors"><tr>'
                '<td><a href="https://github.com/octocat">one</a></td>'
                '<td><a href="https://github.com/octocat/">two</a></td>'
                '</tr></table>',
                encoding="utf-8",
            )
            self.assertEqual(
                count_contributor_entries(path, "https://github.com/octocat"),
                2,
            )


if __name__ == "__main__":
    unittest.main()
