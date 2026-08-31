import importlib.util
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / "changelog/scripts/collect_history.py"
spec = importlib.util.spec_from_file_location("collector", SCRIPT)
collector = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collector)


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name)
        self.repo = self.base / "repo with spaces"
        self.repo.mkdir()
        self.run_git("init", "-b", "main")
        self.run_git("config", "user.name", "Fixture")
        self.run_git("config", "user.email", "fixture@example.invalid")
        self.run_git("config", "commit.gpgsign", "false")
        self.run_git("config", "core.hooksPath", str(self.base / "no-hooks"))
        self.config = {"start": "2026-08-17", "end": "2026-08-30", "timezone": "Europe/London",
                       "repos": [{"path": str(self.repo)}]}

    def run_git(self, *args, env=None):
        return subprocess.check_output(["git", "-C", str(self.repo), *args],
                                       env=env, stderr=subprocess.PIPE).decode().strip()

    def commit(self, name, when):
        (self.repo / name).write_text(name)
        self.run_git("add", "--", name)
        env = dict(os.environ, GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
        self.run_git("commit", "-m", name, env=env)
        return self.run_git("rev-parse", "HEAD")

    def test_inclusive_dates_pin_history_and_preserve_dirty_tree(self):
        old = self.commit("old", "2026-08-16T22:59:59Z")
        first = self.commit("first", "2026-08-16T23:00:00Z")
        last = self.commit("last with spaces", "2026-08-30T22:59:59Z")
        self.commit("next day", "2026-08-30T23:00:00Z")
        (self.repo / "old").write_text("uncommitted")
        (self.repo / "untracked").write_text("preserve")
        before = self.run_git("status", "--porcelain")
        snapshot, rows = collector.collect(self.config)
        record = snapshot["repositories"][0]
        self.assertEqual((record["baseline"], record["cutoff"]), (old, last))
        self.assertEqual([r["sha"] for r in rows], [first, last])
        self.assertEqual(rows[1]["paths"], ["last with spaces"])
        self.assertTrue(record["dirty"])
        self.assertEqual(self.run_git("status", "--porcelain"), before)
        self.assertEqual((self.repo / "old").read_text(), "uncommitted")

    def test_older_branch_commit_is_included_when_merged_in_window(self):
        baseline = self.commit("baseline", "2026-08-16T12:00:00Z")
        self.run_git("switch", "-c", "old-work")
        old_work = self.commit("older branch work", "2026-08-10T12:00:00Z")
        self.run_git("switch", "main")
        self.commit("main work", "2026-08-18T12:00:00Z")
        env = dict(os.environ, GIT_AUTHOR_DATE="2026-08-19T12:00:00Z", GIT_COMMITTER_DATE="2026-08-19T12:00:00Z")
        self.run_git("merge", "--no-ff", "old-work", "-m", "merge older work", env=env)
        snapshot, rows = collector.collect(self.config)
        self.assertEqual(snapshot["repositories"][0]["baseline"], baseline)
        row = next(r for r in rows if r["sha"] == old_work)
        self.assertFalse(row["committer_date_in_window"])
        self.assertEqual(len(rows), 3)

    def test_alias_and_nested_path_count_once(self):
        self.commit("initial", "2026-08-18T12:00:00Z")
        alias = self.base / "alias"
        alias.symlink_to(self.repo, target_is_directory=True)
        nested = self.repo / "nested"
        nested.mkdir()
        self.config["repos"] += [{"path": str(alias)}, {"path": str(nested)}]
        snapshot, rows = collector.collect(self.config)
        self.assertEqual(len(snapshot["repositories"]), 1)
        self.assertEqual(len(rows), 1)
        self.assertEqual(len(snapshot["repositories"][0]["aliases"]), 3)

    def test_conflicting_refs_are_not_silently_deduplicated(self):
        old = self.commit("old", "2026-08-16T12:00:00Z")
        self.commit("new", "2026-08-18T12:00:00Z")
        self.config["repos"].append({"path": str(self.repo), "ref": old})
        with self.assertRaisesRegex(ValueError, "conflicting revisions"):
            collector.collect(self.config)

    def test_no_changes_and_no_pre_cutoff_commits(self):
        self.commit("old", "2026-08-16T12:00:00Z")
        snapshot, rows = collector.collect(self.config)
        self.assertEqual(rows, [])
        self.assertEqual(snapshot["repositories"][0]["commit_count"], 0)
        self.config.update(start="2026-01-01", end="2026-01-02")
        snapshot, rows = collector.collect(self.config)
        self.assertIsNone(snapshot["repositories"][0]["cutoff"])
        self.assertEqual(rows, [])

    def test_dst_boundary_uses_calendar_days(self):
        start, end = collector.boundaries("2026-03-29", "2026-03-29", "Europe/London")
        self.assertEqual(end.timestamp() - start.timestamp(), 23 * 3600)
        start, end = collector.boundaries("2026-10-25", "2026-10-25", "Europe/London")
        self.assertEqual(end.timestamp() - start.timestamp(), 25 * 3600)

    def test_explicit_baseline_is_recorded_and_must_be_ancestor(self):
        old = self.commit("old", "2026-08-15T12:00:00Z")
        self.commit("usual baseline", "2026-08-16T12:00:00Z")
        tip = self.commit("in window", "2026-08-18T12:00:00Z")
        self.config["repos"][0].update(ref=tip, baseline=old)
        snapshot, rows = collector.collect(self.config)
        self.assertEqual(snapshot["repositories"][0]["baseline"], old)
        self.assertEqual(len(rows), 2)
        self.assertTrue(any("Explicit baseline" in x for x in snapshot["repositories"][0]["warnings"]))
        self.run_git("switch", "--orphan", "unrelated")
        unrelated = self.commit("unrelated", "2026-08-19T12:00:00Z")
        self.config["repos"][0]["baseline"] = unrelated
        with self.assertRaises(ValueError):
            collector.collect(self.config)

    def test_nonmonotonic_dates_warn_instead_of_implying_certain_boundaries(self):
        self.commit("old", "2026-08-16T12:00:00Z")
        self.commit("later dated parent", "2026-08-20T12:00:00Z")
        self.commit("earlier dated child", "2026-08-18T12:00:00Z")
        snapshot, rows = collector.collect(self.config)
        self.assertEqual(len(rows), 2)
        self.assertTrue(any("Non-monotonic" in x for x in snapshot["repositories"][0]["warnings"]))

    def test_invalid_date_order_and_unborn_repository_fail(self):
        with self.assertRaisesRegex(ValueError, "end must"):
            collector.boundaries("2026-08-30", "2026-08-17", "UTC")
        with self.assertRaises(ValueError):
            collector.collect(self.config)

    def test_shallow_clone_rejected(self):
        self.commit("old", "2026-08-16T12:00:00Z")
        self.commit("new", "2026-08-18T12:00:00Z")
        clone = self.base / "shallow"
        subprocess.check_call(["git", "clone", "--depth", "1", self.repo.as_uri(), str(clone)],
                              stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        self.config["repos"] = [{"path": str(clone)}]
        with self.assertRaisesRegex(ValueError, "shallow history"):
            collector.collect(self.config)

    def test_invalid_config_leaves_no_partial_output(self):
        self.commit("old", "2026-08-16T12:00:00Z")
        self.config["repos"].append({"path": str(self.repo), "ref": "nonexistent"})
        config = self.base / "config.json"
        config.write_text(json.dumps(self.config))
        output = self.base / "output"
        result = subprocess.run(["python3", str(SCRIPT), "--config", str(config), "--output", str(output)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertFalse(output.exists())

    def test_existing_output_is_preserved(self):
        output = self.base / "output"
        output.mkdir()
        marker = output / "marker"
        marker.write_text("retain")
        result = subprocess.run(["python3", str(SCRIPT), "--repo", str(self.repo), "--start", "2026-08-17",
                                 "--end", "2026-08-30", "--timezone", "UTC", "--output", str(output)], capture_output=True)
        self.assertEqual(result.returncode, 2)
        self.assertEqual(marker.read_text(), "retain")


if __name__ == "__main__":
    unittest.main()
