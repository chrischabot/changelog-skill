# Editing for meaning

The reader should understand the change on the first pass without opening a commit. Technical precision and readable prose are complementary: keep terminology that names a real engineering concept, but do not mistake an internal object name for an explanation.

## Sentence and paragraph audit

Classify each sentence by its job. A sentence may have more than one job; rewrite it if incidental detail crowds out its main one.

| Job | Editorial action |
| --- | --- |
| Core change or result | Make it the subject and lead of the update. |
| Shared engineering terminology | Keep it when useful. Do not teach basic software concepts to senior engineers. |
| Necessary component context | Briefly say what the component does before describing its new behavior. |
| Material qualification | Keep it next to the claim it changes; express the practical limit directly. |
| Evidence accounting | Move it to the ledger unless the measurement or evaluation is itself the update. |
| Repetition or generic significance | Delete it. Do not replace it with a more elaborate synonym. |

Then inspect the paragraph. Does it state one identifiable change or coherent group? Does each sentence develop that message? Can a colleague state what was added or fixed, and why that matters, after reading it once?

Record the audit compactly by update and sentence: quotation, job, decision, and the reason where a repair is needed. Classifying a paragraph as “technical” or writing a generic positive verdict does not check its sentences. After the first rewrite, repeat the reader test on the actual revised text.

Do not simplify everything into short fragments. Use complete sentences, concrete subjects, and ordinary verbs. Vary sentence length according to the thought. Avoid inflated abstractions such as “a unified operational foundation” when you mean a deployment command or shared login service.

## Synthetic examples

These examples use invented products and numbers; they are not evidence for any real project.

### Lead with the behavior

Weak: “DeploymentIntent now retains operation tokens across reconciliation cycles, including journal recovery, build receipts, and target binding.”

Better: “Interrupted deployments can now resume from another CLI process without starting a second build.”

The second sentence states the useful change. Explain idempotency or account scoping only if those details are needed to understand its guarantee; put the record schema in evidence.

### Introduce the component

Weak: “Maple adds watch mode, leases, barriers, and reconnect handling.”

Better: “Maple keeps development workspaces after their temporary containers are deleted. Editors and compilers still use ordinary local files, and commands can wait until their changes have been saved remotely.”

The new name needs a function. The internal mechanism is not the introduction.

### Preserve the important numbers

Evidence: Two clients each attempted five application tasks. Client A completed five within budget; client B completed two. A third B deployment later worked in a browser, but its agent had exceeded the budget.

Useful: “Client A completed all five application tasks within budget; Client B completed two out of five.”

Misleading: “Eight tests passed.” That mixes two definitions of success and hides the denominator.

If rechecking unchanged applications corrects a score from three to eight, do not write that new platform features raised the score. The correction may belong in the ledger rather than the changelog. If the evaluation machinery itself changed, explain that as its own change.

Do not retain every valid metric just because the update concerns evaluation. Unless the user asks for detailed benchmark analysis, lead with the useful comparison: what task the clients attempted, which result counts as success, and how many attempts succeeded. Keep task-instance names, model-version labels, stage-by-stage counts, instrument failures, and recheck chronology in the ledger. A connection workaround belongs in setup guidance when it affects adoption; describe its function once rather than leaving an unexplained “bridge” in a results paragraph.

### Make qualifications earn their place

Useful: “The adapter supports prerendered pages and limited server functions; request-time React rendering is not supported.” This affects whether someone can adopt it.

Usually unnecessary: “Passing the parser tests does not establish universal production readiness.” If no broad production claim was made, this adds no actionable information.

Useful: “The storefront demonstrates browsing and carts; checkout ends at a local confirmation page.” Calling it an integrated payment system would be false without that limit.

### Shorten by selecting

Weak: “The run retains sources, traces, receipts, browser screenshots, replay logs, and budget evidence to facilitate detailed analysis of the attempts.”

Better, when evaluation tooling is the update: “The evaluation now records enough evidence to reproduce failures and identify where agents get stuck.” Verify that reproduction is actually possible before making that claim.

Otherwise, omit the sentence and report the evaluation's useful result. Do not shorten it into a smaller list of unexplained evidence types.

## Whole-document check

Make headings informative without requiring them to carry every detail. Do not repeat a heading as the first paragraph. Preserve the breadth of the period without listing every feature of each subsystem. Distinct new capabilities deserve separate updates; fixes that make one capability usable usually belong together.

Check that the heading identifies the useful outcome, not merely the research subject. For a distribution change, the news might be that developers can install without private repository access; checksums are supporting behavior. For a dashboard change, the news might be that operations survive reloads; an inventory of controls does not convey that repair. These are examples of the judgment, not required topics or headings.

Read the document continuously after the sentence audit. Remove repeated caveats, repeated introductions, mechanical transitions, and endings that merely announce importance. Use the Wikipedia checklist linked in sources.md as a prompt to notice inflated significance, repetition, and forced structure, not as an AI detector or a rule to ban all words on a list.

When a user edits an example, infer the communication principle, not new facts. A clearer illustrative score cannot overrule the recorded results. Correct the numbers once, preserve the intended clarity, and continue.
