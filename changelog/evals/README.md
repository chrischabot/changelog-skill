# Changelog evaluation suite

This suite makes the skill's validation process repeatable. It prepares a writer packet, keeps expected outcomes and any accepted report separate, freezes each submission, and checks an explicit review of coverage, facts and writing quality. It does not call a model service, spend API credits, or publish anything.

The suite travels with the installed skill. Run commands from the skill directory, or use the absolute path to `scripts/evaluate.py`. Python 3.10+, Git and IANA timezone data are sufficient.

## Cases

| Case | What it tests |
|---|---|
| `fortnight` | Two synthetic repositories, an alias, a date cutoff, dirty and later work, package/consumer counts, cross-cutting repairs, a superseded guarantee, evaluation denominators, access-control limits, grouping and link honesty. |
| `compression` | Approximately 33% fewer words while preserving results, context and material limitations. The mechanical tolerance is a 28–38% reduction; a reviewer still decides whether meaning survived. |
| `routing` | Explicit invocation, natural-language dates, missing inputs and a non-trigger. This is instruction conformance, not a test of automatic skill discovery in the host. |
| `external` | A private replay using real repositories, pinned dates/revisions, an accepted report and semantic outcome criteria. Private material stays outside the public skill repository. |

The synthetic sources are original fixtures, not extracts from a private project. They are intentionally small enough for a bounded complete run. They do not establish performance across large or unfamiliar codebases.

## Run a writing evaluation

Prepare a new private directory:

```bash
python3 scripts/evaluate.py prepare --case fortnight --output "$HOME/changelog-evals/run-01"
```

Give an evaluator only the returned `writer/REQUEST.md` and its permitted sources. That request loads a copy of the writing skill without the evaluation answers. Use a fresh agent context where available and authorized. Otherwise declare any prior context or self-review; do not describe it as independent. Keep one lead writer responsible for the complete output.

The runner does not launch agents or enforce an operating-system sandbox. The caller must arrange isolation, permissions and model access. A model that can read the original evaluation files can contaminate its own test; record that as a failure of the blind protocol. Do not send private material to a new service without authorization.

After the writer produces the requested files in `writer/output/`, freeze them:

```bash
python3 scripts/evaluate.py capture --run "$HOME/changelog-evals/run-01"
```

Give a different reviewer the returned `submissions/001/REVIEW.md`, frozen artifacts, `judge/expected.json`, any `judge/reference.md`, and primary source access. The reviewer copies `review-template.json` to a new `review.json` and fills it according to [REVIEWER.md](REVIEWER.md). That records every required outcome, a reader paraphrase for every paragraph, and a decision for every sentence-sized unit.

```bash
python3 scripts/evaluate.py score --run "$HOME/changelog-evals/run-01" --submission 1 --review "$HOME/changelog-evals/run-01/review.json"
```

Without a review, a structurally valid writing submission returns `needs_review`, never a writing-quality pass. A complete review is still a judgment by its named reviewer, not a computed truth. A flattering but unsupported assessment can be wrong; inspect the actual reasons, quotations and source citations.

## Outcomes and revisions

| Result | Exit code | Meaning |
|---|---:|---|
| `reviewed_pass` | 0 | The named reviewer accepts this exact writing revision and all mechanical checks pass. Review independence remains visible. |
| `conformance_pass` | 0 | Routing choices match the case; this says nothing about prose quality or host autodiscovery. |
| `fail` | 1 | A preservation, structural, factual, coverage or editorial requirement remains unmet or uncertain. |
| `input_error` | 2 | Missing files, invalid review fields, changed frozen artifacts or mismatched versions prevent assessment. |
| `needs_review` | 3 | Mechanical checks pass, but no writing review has been supplied. |

Do not average material failures into an overall score. A false readiness claim, wrong denominator, missing capability or unresolved unclear paragraph blocks acceptance. Critiques must name the actual sentence and the missing or distracting information.

After corrections, place the revised files in `writer/output/` and call `capture` again. It creates `002`, keeps `001`, and labels the revision `informed`. Review the new version; the previous review is rejected because its submission hash differs. Each score attempt on a captured submission is retained under its `scores/`, including rejected review bytes and validation errors. Completed judgments include the full review and reviewer identity.

Use `prepare --mode informed` when the writer already has feedback. Use `--mode imported` when assessing an existing output rather than generating a new one. Imported outputs must never be advertised as a new blind replay. The runner's mode records the declared protocol; it cannot prove what a model previously saw.

## Private repository replays

Before the writer runs, the coordinating reviewer extracts independently useful outcomes from the accepted report. Create a private `expected.json`:

```json
{
  "criteria": [
    {
      "id": "export-recovery",
      "requirement": "Explain resumable CSV exports and retain the limitation that PDF exports still restart.",
      "sources": ["service/exporter.py", "tests/recovery_test.py"]
    }
  ]
}
```

Use distinct IDs for substantial outcomes, including important fixes and qualifications. Do not copy the expected outline into the writer's prompt. Different grouping and wording can pass when the same meaning survives. An accepted report can contain errors; adjudicate disagreements against source and explain the resolution.

If an expected outcome is wrong, retain the prepared criterion and record the source-based correction in the review. Fix the case for future runs; do not silently rewrite the held-out answer or penalize a writer for being more accurate than it. Preserve unrelated failures in that same submission.

A private config supplies the collector inputs and holdout paths:

```json
{
  "start": "2026-06-01",
  "end": "2026-06-14",
  "timezone": "Europe/London",
  "repos": [
    {"path": "/work/platform", "ref": "main"},
    {"path": "/work/applications", "ref": "main"}
  ],
  "reference": "/private/accepted-report.md",
  "expected": "/private/expected.json",
  "context": "Additional source-access restrictions, not expected answers."
}
```

Prefer immutable revisions for exact replays; each repository can also specify `baseline`. The collector resolves aliases and dates before preparing the packet. The accepted report and criteria are copied only to `judge/`.

```bash
python3 scripts/evaluate.py prepare --case external --config /private/replay.json --output "$HOME/changelog-evals/real-run"
```

Prepare private artifacts outside the public repository. External source paths remain in place and are only read. Concurrent work may legitimately change their fingerprints; report that drift rather than quietly ignoring it or claiming unchanged working trees. Use an authorized stable source snapshot for a new run if necessary.

## What the checks can establish

The runner pins the skill and input files, hashes expected outcomes and the accepted reference, freezes reviewer instructions, records runner and suite versions, freezes report artifacts, verifies review quotations and complete audit IDs, checks requested word reduction and reader-link path hygiene, and fingerprints tracked/index changes plus untracked non-ignored file contents. It catches changed bytes even when `git status` lists the same dirty filename. Word counts include headings and body text, replace inline links with their labels, and omit standalone link rows.

It does not verify semantic truth, link reachability, absence of external disclosure, all ignored-file writes, or the honesty of a review. Those need source inspection, appropriate tools and a reviewer. Sentence segmentation is a convenience, not a parser of English; the paragraph review supplies context. Passing script tests does not establish writing quality.

When changing the suite, run the repository's `python3 -m unittest discover -s tests -v`. The tests include deliberately incomplete, stale, false-quote and failed reviews; their synthetic passing reviews are validator test doubles, not evidence that generated prose is good. Preserve a complete model-produced case and its actual review separately when reporting behavioral validation.
