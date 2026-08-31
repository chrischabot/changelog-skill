# Validation

The skill is tested at two levels: deterministic source accounting and the quality of a complete engineering report. Passing the first does not establish the second.

## Source accounting

Twelve isolated Git-fixture tests pass. They exercise inclusive dates, daylight-saving changes, older commits merged during the window, repository aliases, conflicting refs, explicit baselines, non-monotonic timestamps, shallow history, empty windows, invalid inputs, and preservation of dirty files and existing output.

The collector was also run against a real two-repository historical window. Date-only selection reproduced the same baseline revisions, cutoff revisions, commit counts, and merge counts as the independently pinned reference. The skill's metadata validator passes, and the installable directory includes its MIT license.

## Complete report replay

The evaluation uses a private, previously accepted engineering report as a holdout. The evaluator receives the repositories, reporting dates, pinned revisions, and this skill, but cannot read the accepted report, previous editorial drafts, expected outline, or comparison notes. Source repositories remain read-only.

The first blind run did not meet the intended standard. It reconciled the main measurements but grouped different capabilities too broadly, missed substantive repairs, retained too much evaluation procedure, and substituted machine-specific evidence snapshots for portable reader links. Its own editorial review did not catch those problems.

Those failures led to concrete changes in the skill: finer candidate accounting, a second pass over uncited changes, explicit reasons for grouping, a sentence-level editorial audit, selection of a primary evaluation measure, and a distinction between reader links and private evidence links. A second fresh evaluator ran the revised instructions without seeing either report or the first comparison. It recovered more substantial work and produced portable source links, but still omitted useful changes, buried results in procedure, and lost material security qualifications. Complete commit accounting did not prevent these failures.

A final, explicitly informed correction pass received the comparison findings and checked the affected sources again. The skill now requires directory-level coverage, a message plan before prose, explicit review of negative evidence, and confirmation that remote source links contain the cited revision. This is a revision-and-review test, not a third blind result. The comparison also found an incorrect source-repository link in the accepted reference; disagreements are resolved from source rather than by copying that reference.

The final reviewed report recovered the reference's substantive coverage and useful link structure while retaining additional verified changes. Source checks also retracted a repair that had been superseded before the cutoff. The final prose leads with the useful results, keeps necessary denominators and limitations, and leaves investigation details in the evidence record.

The complete final skill has not had a third fresh blind replay. The demonstrated result is a complete workflow with review and correction, not guaranteed first-draft equivalence to an accepted report.

## Limits

This is a regression case, not a broad benchmark of changelog quality. The author knows the source case and refined the instructions in response to its failures; fresh evaluators are blind to the accepted answer, but the case is not an unseen test of generalization. Different repositories, evidence quality, agents, and audiences still require judgment.

Local installation and explicit use in Codex are checked. Automatic skill selection across differently phrased prompts and behavior in other agent hosts are not established by the report replay. Protected documentation can require reader access; a checked source snapshot does not prove that an anonymous browser can open the hosted page.

Private drafts, evidence, and detailed comparisons are kept outside this repository. No private project source or report is bundled with the skill.
