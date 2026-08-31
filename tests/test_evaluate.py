"""Harness tests use review doubles; they do not certify generated writing."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

SCRIPT = Path(__file__).resolve().parents[1] / "changelog/scripts/evaluate.py"
spec = importlib.util.spec_from_file_location("evaluate", SCRIPT)
ev = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ev)


class EvaluationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "run"

    def prepare(self, case="compression", mode="blind"):
        ev.prepare(case, self.root, mode=mode)

    def submit(self, text="# Update\n\nExports resume from saved batches. PDF exports still restart.\n"):
        expected = ev.read_json(self.root / "judge/expected.json")
        for name in expected["artifacts"]:
            (self.root / "writer/output" / name).write_text(text if name == "changelog.md" else "Fixture evidence.\n")
        return ev.capture(self.root)

    def passing_double(self, number=1):
        """Synthetic review of synthetic text, solely to test schema/gates."""
        p = self.root / "submissions" / f"{number:03}"
        review = ev.read_json(p / "review-template.json")
        review["reviewer"] = {"name": "Harness test double", "independence": "self"}
        for row in review["criteria"]:
            row.update(verdict="pass", evidence="Synthetic test input only.", reason="Exercises acceptance-path validation, not factual quality.")
        for row in review["paragraphs"]:
            row.update(verdict="pass", paraphrase="CSV recovery exists and PDF recovery is limited.")
        for row in review["sentences"]:
            row.update(job="core", decision="keep", reason="Synthetic assertion used for validator testing.")
        path = self.root / f"review-{number}.json"
        ev.write_json(path, review)
        return path, review

    def remove_reduction_for_test(self):
        p = self.root / "judge/expected.json"
        expected = ev.read_json(p); expected.pop("reduction")
        ev.write_json(p, expected)
        m = ev.read_json(self.root / "run.json")
        m["expected_sha256"] = ev.sha(p.read_bytes())
        ev.write_json(self.root / "run.json", m)

    def test_writer_packet_does_not_contain_holdout(self):
        self.prepare()
        writer = self.root / "writer"
        self.assertFalse((writer / "skill/evals").exists())
        self.assertFalse((writer / "skill/scripts/evaluate.py").exists())
        self.assertFalse(list(writer.rglob("expected.json")))
        self.assertTrue((self.root / "judge/expected.json").is_file())
        with self.assertRaisesRegex(ValueError, "already exists"):
            self.prepare()

    def test_no_review_is_not_a_quality_pass(self):
        self.prepare(); self.remove_reduction_for_test(); self.submit()
        result = ev.score(self.root, 1)
        self.assertEqual(result["status"], "needs_review")
        self.assertTrue(all(result["checks"].values()))

    def test_heading_only_output_cannot_pass_as_prose(self):
        self.prepare(); self.remove_reduction_for_test(); self.submit("# Empty update\n")
        self.assertIn("has_prose", ev.score(self.root, 1)["failures"])

    def test_complete_review_and_full_audit_required(self):
        self.prepare(); self.remove_reduction_for_test(); self.submit()
        path, review = self.passing_double()
        self.assertEqual(ev.score(self.root, 1, path)["status"], "reviewed_pass")
        review["paragraphs"].clear(); ev.write_json(path, review)
        with self.assertRaisesRegex(ValueError, "every expected ID"):
            ev.score(self.root, 1, path)
        rejected = self.root / "submissions/001/scores/002.json"
        archived = self.root / "submissions/001/scores/002-review.json"
        self.assertEqual(ev.read_json(rejected)["status"], "input_error")
        self.assertEqual(ev.read_json(archived), review)

    def test_pending_or_failed_quality_cannot_average_to_pass(self):
        self.prepare(); self.remove_reduction_for_test(); self.submit()
        path, review = self.passing_double()
        row = review["criteria"][0]
        row.update(verdict="uncertain", repair="Inspect the missing source before accepting coverage.")
        ev.write_json(path, review)
        self.assertEqual(ev.score(self.root, 1, path)["status"], "fail")

    def test_sentence_rewrite_remains_open_until_new_capture(self):
        self.prepare(); self.remove_reduction_for_test(); self.submit()
        path, review = self.passing_double()
        review["sentences"][0]["decision"] = "recast"; ev.write_json(path, review)
        self.assertIn(review["sentences"][0]["id"], ev.score(self.root, 1, path)["failures"])

    def test_stale_review_and_frozen_mutation_are_rejected(self):
        self.prepare(); self.remove_reduction_for_test(); self.submit()
        path, review = self.passing_double()
        second = self.submit("# Changed\n\nExports resume, but PDF files restart.\n")
        self.assertEqual(second["mode"], "informed")
        with self.assertRaisesRegex(ValueError, "exact run and submission"):
            ev.score(self.root, 2, path)
        (self.root / "submissions/001/changelog.md").write_text("edited after review")
        with self.assertRaisesRegex(ValueError, "frozen submission"):
            ev.score(self.root, 1, path)

    def test_absent_quote_duplicate_criteria_and_modified_units_rejected(self):
        self.prepare(); self.remove_reduction_for_test(); self.submit()
        path, review = self.passing_double()
        review["criteria"][0]["quote"] = "This was never written."
        ev.write_json(path, review)
        with self.assertRaisesRegex(ValueError, "quotes text absent"):
            ev.score(self.root, 1, path)
        review["criteria"][0]["quote"] = ""
        review["criteria"].append(review["criteria"][0]); ev.write_json(path, review)
        with self.assertRaisesRegex(ValueError, "exactly once"):
            ev.score(self.root, 1, path)
        ev.write_json(self.root / "submissions/001/review-units.json", {})
        with self.assertRaisesRegex(ValueError, "review units changed"):
            ev.score(self.root, 1, path)

    def test_missing_and_symlinked_deliverables_rejected(self):
        self.prepare()
        with self.assertRaisesRegex(ValueError, "artifact"):
            ev.capture(self.root)
        p = self.root / "writer/output/changelog.md"
        p.symlink_to(self.root / "writer/input.md")
        with self.assertRaisesRegex(ValueError, "symlinked"):
            ev.capture(self.root)
        self.assertFalse((self.root / "submissions").exists())

    def test_local_links_and_bad_reduction_fail_without_semantic_guessing(self):
        self.prepare()
        self.submit("# Update\n\nSee [evidence](/tmp/private/source.py).\n")
        result = ev.score(self.root, 1)
        self.assertIn("portable_reader_links", result["failures"])
        self.assertIn("requested_reduction", result["failures"])
        self.submit("# Update\n\nSee [private evidence](</tmp/private folder/source.py>).\n")
        self.assertIn("portable_reader_links", ev.score(self.root, 2)["failures"])

    def test_routing_is_order_independent_and_explicitly_not_quality(self):
        self.prepare("routing")
        self.assertIn("repositories, dates, timezone", (self.root / "writer/REQUEST.md").read_text())
        request = next(r for r in ev.read_json(self.root / "writer/requests.json") if r["id"] == "missing")
        self.assertIn("Use UTC", request["context"])
        rows = ev.read_json(self.root / "judge/expected.json")["expected_routes"]
        rows.reverse(); rows[0]["reason"] = "Optional explanation is harmless."
        ev.write_json(self.root / "writer/output/routing.json", rows)
        ev.capture(self.root)
        self.assertEqual(ev.score(self.root, 1)["status"], "conformance_pass")
        rows[0]["action"] = "apply"
        ev.write_json(self.root / "writer/output/routing.json", rows)
        ev.capture(self.root)
        self.assertEqual(ev.score(self.root, 2)["status"], "fail")

    def test_synthetic_sources_pin_cutoff_deduplicate_and_detect_dirty_edits(self):
        self.prepare("fortnight")
        snap = ev.read_json(self.root / "writer/source-snapshot.json")
        self.assertEqual(len(snap["repositories"]), 2)
        labs = next(r for r in snap["repositories"] if r["root"].endswith("labs"))
        self.assertTrue(labs["dirty"])
        paths = ev.history.git(labs["root"], "ls-tree", "-r", "--name-only", labs["cutoff"]).decode()
        self.assertNotIn("exportkit/pdf.py", paths)
        rows = json.loads(ev.history.git(labs["root"], "show", labs["cutoff"] + ":evidence/attempts.json"))
        self.assertEqual(sum(r["within_budget"] and r["browser_pass"] is True for r in rows), 7)
        self.submit()
        dirty = Path(labs["root"]) / "evidence/status.md"
        before = ev.fingerprint(labs["root"])
        dirty.write_text("different dirty bytes, same status path")
        self.assertNotEqual(before, ev.fingerprint(labs["root"]))
        self.assertIn("source_unchanged", ev.score(self.root, 1)["failures"])

    def test_expected_and_skill_changes_require_new_run(self):
        self.prepare()
        skill = self.root / "writer/skill/SKILL.md"
        original = skill.read_text(); skill.write_text("changed")
        with self.assertRaisesRegex(ValueError, "skill changed"):
            ev.capture(self.root)
        skill.write_text(original)
        instructions = self.root / "judge/REVIEWER.md"
        original = instructions.read_text(); instructions.write_text("changed")
        with self.assertRaisesRegex(ValueError, "reviewer instructions changed"):
            ev.capture(self.root)
        instructions.write_text(original)
        # Capture must use the prepared instructions, even if the installed
        # suite has moved or changed after preparation.
        with patch.object(ev, "SKILL", self.root / "absent-installation"):
            self.submit()
        (self.root / "submissions/001/REVIEW.md").write_text("changed after capture")
        with self.assertRaisesRegex(ValueError, "frozen review instructions changed"):
            ev.score(self.root, 1)

    def test_imported_mode_is_never_labelled_blind(self):
        self.prepare(mode="imported")
        self.assertEqual(self.submit()["mode"], "imported")
        self.assertEqual(self.submit()["mode"], "imported")

    def test_external_case_uses_private_reference_without_copying_into_writer(self):
        fixture = self.root.parent / "fixtures"
        cfg = ev.load_fixtures().fortnight(fixture)
        ref = self.root.parent / "accepted.md"; ref.write_text("SECRET HOLDOUT TEXT")
        expected = self.root.parent / "expected.json"
        ev.write_json(expected, {"criteria": [{"id": "custom", "requirement": "Custom private outcome."}]})
        cfg.update(reference=str(ref), expected=str(expected))
        config = self.root.parent / "config.json"; ev.write_json(config, cfg)
        ev.prepare("external", self.root, config, mode="imported")
        self.assertEqual((self.root / "judge/reference.md").read_text(), "SECRET HOLDOUT TEXT")
        self.assertNotIn("SECRET HOLDOUT TEXT", (self.root / "writer/REQUEST.md").read_text())
        self.assertEqual(ev.read_json(self.root / "run.json")["mode"], "imported")
        (self.root / "judge/reference.md").write_text("changed reference")
        with self.assertRaisesRegex(ValueError, "accepted reference changed"):
            ev.capture(self.root)


if __name__ == "__main__":
    unittest.main()
