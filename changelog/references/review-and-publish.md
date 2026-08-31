# Review and conditional publication

## Factual and coverage review

Check the whole draft against the evidence ledger, not just its riskiest paragraph. For every update verify novelty, dates, supported behavior, counts, causation, and readiness. Reconcile different claims about the same component across updates. Check material candidates omitted from the draft and distinguish intentional grouping from accidental omission.

Pay particular attention to familiar comparisons, “all” and “now,” success rates, deployment claims, authentication, payment handling, data durability, protocol compatibility, and performance. Those can turn a small imprecision into a materially different claim.

Historical test records support only the version, environment, path, and date they actually tested. Reading them does not mean you ran them. An artifact being built, accepted, deployed, and successfully used are distinct states.

## Editorial review

Perform the sentence and paragraph audit in editorial.md. A useful review entry contains:

- The exact sentence or paragraph under review.
- The information a reader needs, or the distracting detail they do not need.
- A proposed correction that preserves supported meaning.
- A one-sentence paraphrase of the update's change and consequence.

Keep these notes separate from the reader-facing draft. A reviewer who has the ledger may catch factual omissions; a reader without it is better placed to expose missing context. When separate agents are unavailable or unauthorized, do these as distinct passes and state that the review was not independent.

Do not defer to a generic positive verdict when the text still fails the reader test. Resolve each actionable finding, then read the complete revision. Record the exact draft version or hash reviewed; a later edit needs a fresh check of the changed passage and any affected claims elsewhere.

## Link review

Choose links for exploration, not proof of effort. Prefer a guide for adopting a framework, the API surface for an SDK, the relevant source directory for an implementation, or a demo showing the new behavior. A public protocol reference is useful when the reader may not know the protocol.

Check the actual destination and title/content. Record redirects, access requirements, stale information, and missing pages. Do not publish a link as “Documentation” if it lands on an unrelated introduction or describes an older API. Do not weaken access controls or bypass a denied login to make a link check pass.

Keep portable reader links separate from local evidence links. A protected canonical documentation or source URL may be appropriate for colleagues even when anonymous HTTP requests return 401 or 404. Verify the intended content through an authorized source, label the access limitation in the ledger, and do not claim to have opened a protected page you could not access. Local evidence snapshots remain useful in the ledger and delivery note, but are not replacements for the report's exploration links.

If the user asks for stale documentation to be repaired, treat that as a distinct authorized follow-up. Check the docs against source, preserve any requested publication order, and validate the newly built docs separately from the changelog.

## Publishing, only when requested

1. Confirm that the full-text approval requirement, if any, is satisfied. Approval may already exist in the conversation; do not ask for it again. Prepare all reversible work before requesting a genuinely missing final approval.
2. Read the site's build and deployment instructions and its existing brand guidance. Recheck git status and changes by ownership. Keep unrelated edits intact, including mixed files and generated output from other work.
3. Apply only the approved copy and useful links. Respect the requested destination and navigation behavior. Do not redesign the page or introduce decorative conventions the user did not ask for.
4. Regenerate generated files through the documented build. Do not hand-edit them or use an older build as validation of new copy. If a dirty checkout would publish unrelated work, use a permitted isolated export of the intended source, without moving or resetting other people's files.
5. Run appropriate existing content, build, and link checks. Inspect the rendered page at useful desktop and mobile sizes, including heading, spacing, overflow, links, and navigation. Avoid adding brittle tests that simply duplicate the prose.
6. Review the exact diff and stage only authorized files or hunks. Check the staged names and content before committing. Never sweep in unrelated work, reset another owner's index, or infer that “publish” grants permission to modify upstream repositories.
7. Deploy through the documented authorized path. Check the resulting artifact/version, deployment status, and actual destination. Then verify the reader-facing route and links where access permits. A successful build or deployment command alone is not live page acceptance.
8. Report commit/push, deployment, and live verification separately. If signed-in browser verification is blocked, say so; do not claim it succeeded or weaken authentication. Leave private evidence and credentials out of the public page and repository.

This workflow does not grant permission for remote writes, messages, paid services, or access to private material. Follow the user's scope and the host's controls.
