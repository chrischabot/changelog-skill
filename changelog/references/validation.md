# Testing this skill

Frontmatter validation and script tests do not establish writing quality. Test behavior on a complete, realistic reporting window.

Use the [runnable evaluation suite](../evals/README.md) to preserve this process in files. `scripts/evaluate.py` provides `prepare`, `capture` and `score` commands, synthetic writing/compression/routing cases, and a private external-replay adapter. It keeps the holdout separate, binds reviews to exact submissions and retains failed and informed attempts. A writing run cannot receive `reviewed_pass` without a completed quality review.

## Blind replay

When independent agent evaluation is available and authorized, give a fresh evaluator only this skill, the user-style request, repository access, dates/timezone, pinned revisions needed for reproduction, and a private output directory. Do not supply the accepted report, expected outline, desired scores, known failure, or proposed fix. Do not reuse an evaluator that already knows the reference answer.

Keep the source repositories read-only. Exclude prior editorial drafts and report-specific evidence summaries from the evaluator's sources; ordinary code, implementation records, tests, and dated release/evaluation evidence remain available. Restrict external disclosure as the project requires. One complete replay is more useful than an open-ended model tournament.

Separately extract the accepted report and build a semantic comparison. Preserve its exact version. An accepted report is a useful reference, not infallible truth: adjudicate disagreements against primary evidence.

## Comparison criteria

| Dimension | What to inspect |
| --- | --- |
| Coverage | Map each substantial reference change to a replay passage, a partial treatment, a missing item, or a justified exclusion. Check additional discoveries on their merits. |
| Factual fidelity | Verify dates, baseline versus new work, exact counts, protocol scope, readiness, and causal claims. |
| Meaning | Can a senior colleague state what changed and why it matters after one reading, without the evidence packet? |
| Grouping | Are commits coalesced around outcomes without merging distinct capabilities into vague themes? |
| Editorial quality | Quote actual unclear sentences, explain missing context or unnecessary detail, and propose precise repairs. |
| Exploration | Are links useful, named, relevant, and checked rather than added to meet a quota? |
| Safety and scope | Were private sources protected, source repositories unchanged, and publication boundaries respected? |

Do not grade by matching wording, section order, a fixed word count, or a fixed number of updates. Unsupported success rates, falsely claimed production readiness, and later work presented as in-period are material failures even if prose sounds fluent.

If the replay exposes a reusable weakness, change the smallest relevant instruction or tool. Re-run affected behavior and label whether the second run is still blind or now informed. Do not hide the first result or claim that one successful replay proves universal reliability.

Also test direct invocation, natural-language “change log,” incomplete input, and a non-trigger such as “list the last five commit hashes.” Script fixtures should exercise inclusive dates, timezone boundaries, merged older commits, repository aliases, missing history, and preservation of dirty source trees.

Keep private replay drafts, source snapshots, and comparisons outside the public skill repository unless the owner explicitly authorizes their disclosure. A public validation summary can describe the method and limits without publishing project material.
