# Review the frozen output

You are evaluating an engineering changelog, not helping its writer obtain a passing score. Read `judge/expected.json`, any held-out `judge/reference.md`, the frozen submission, and the relevant primary sources. The expected outcomes guide coverage; source evidence decides disagreements. Do not edit the report or the expected outcomes during this review.

If a criterion or accepted report is wrong, name the error and cite the primary source in your decision. Keep the original evaluation record; recommend a correction for future runs separately. This does not excuse other factual or editorial failures in the draft.

Copy `review-template.json` to a separate `review.json` and complete it. Identify yourself and whether this review is independent, self-review, or informed by an earlier result. Do not claim a fresh blind run if the writer has seen feedback or the accepted answer. The runner labels subsequent submissions informed automatically. The writer's access restriction is a protocol, not an operating-system sandbox; report any known contamination or disclosure as a scope failure.

For every criterion, select `pass`, `fail` or `uncertain`, quote the actual relevant wording when it exists, cite the evidence you inspected, and explain the decision. A missing claim can have an empty quote, but its absence needs a concrete explanation. For a failure or uncertainty, supply the repair or missing evidence needed. Generic approval such as “sounds human” is insufficient. Fabricated metrics, false readiness, wrong reporting scope, superseded guarantees and unauthorized disclosure are failures, not points to average away.

`review-units.json` contains paragraphs and sentence-sized units from the exact report. Read each complete paragraph, write the message a senior colleague should take away, and judge whether it communicates that message on one reading. The sentence splitter is only a review aid; abbreviations or Markdown may split awkwardly, so use the full paragraph to interpret it.

For every sentence unit, record its job (`core`, `context`, `qualification`, `mechanism`, `evidence`, `repetition`), a `keep`, `recast` or `delete` decision, and why. Technical vocabulary alone does not justify keeping a sentence. Necessary internal concepts need context; the useful change should lead; qualifications must change the meaning of a claim. Measurement paragraphs need a success definition, cohort and denominator, not the chronology of collecting evidence.

Review links for usefulness and honesty, not merely syntax or status code. Check supporting guides against the implemented API, and distinguish protected content from missing or stale pages. Test evidence describes its actual environment and date, not universal deployment acceptance.

The runner checks review completeness, quotation provenance, version binding, source fingerprints and structural constraints. It cannot decide whether your reasoning is correct. Never fill every field with a generic pass to make the command succeed. A result marked `reviewed_pass` means the named reviewer accepted this exact revision; it is not an automatic score for writing quality.

If changes are needed, return the concrete findings to the writer. Freeze its next output with a new `capture`, then review that revision anew. Keep the failed first result. Do not reuse a review written against different text.
