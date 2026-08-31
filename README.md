# Changelog

An agent skill for turning work across one or more repositories into an engineering update people can actually read.

Give it the repositories and a date range. It researches what changed, brings related commits together, and writes a substantial changelog for engineers and technical leadership. Each update explains what was built, improved, or fixed, why it matters, and any limitation that affects how it can be used.

Repository history records the work as it happened. A useful changelog has to reconstruct what that work achieved. A framework might take dozens of commits to become usable; an important recovery fix might take one. This skill makes that editorial judgment explicit and keeps the evidence behind it available for checking.

## Use it

In Codex, invoke the installed skill with a request such as:

```text
$changelog

Create an engineering changelog for /work/platform and /work/applications,
covering 1–14 June 2026 inclusive, Europe/London.
Write for senior engineers and technical leadership.
Save the draft and evidence under /work/reports/june-update.
```

You can also ask naturally: “Write a change log for these repositories for the last two weeks.” The agent resolves the dates and scope before researching. It asks for genuinely missing inputs, rather than making you fill out a long brief.

## What it produces

- **A complete Markdown changelog**, with updates ordered by significance and grouped around capabilities and outcomes.
- **A separate evidence ledger**, connecting claims to source revisions, previous behavior, tests, readiness, and meaningful exclusions.
- **A short workflow and review note**, recording the actual cutoff, checks performed, and material unresolved limits.
- **Useful exploration links**, usually one to three per update where relevant documentation, APIs, source, or demos exist.

The update's length follows the amount of noteworthy work. Individual entries stay succinct, but the skill does not force a busy fortnight into three themes or turn every commit into a release-note fragment.

A synthetic example of the intended level of detail:

> **Scheduled exports resume after a worker restart**
>
> Export jobs now save their progress between batches. If a worker restarts, its replacement continues from the last completed batch instead of starting the export again. This recovery path is implemented for CSV exports; PDF exports still restart from the beginning.

The entry gives a reader the change, its practical consequence, and the limit that affects use. The commits and recovery-test results belong in its evidence record.

## How it works

The workflow separates research, evidence gathering, grouping, drafting, technical verification, and editorial critique. It starts from the full reporting window, compares changes with the earlier state, and checks implementation and dated records before writing.

Its editorial pass examines every sentence and paragraph. Shared engineering terminology is welcome; unexplained internal names need context. The main result leads, important numbers retain their denominators, and lists of receipts or test procedures move into the evidence ledger. Shortening means choosing what matters, not removing the context that makes a sentence understandable.

Claims stay within the evidence. Implemented does not mean deployed, and deployed does not mean verified in use. A corrected test score is not automatically a product improvement. Familiar comparisons explain a development model without promising compatibility that has not been established.

Links make the report a starting point for exploring the work. The skill checks their relevance and currency, so a stale documentation page becomes an issue to resolve instead of a misleading recommendation.

## Install

Clone this repository, then copy its `changelog` directory into your agent's skill directory. For current Codex local discovery:

```bash
git clone https://github.com/chrischabot/changelog-skill.git
mkdir -p ~/.agents/skills
cp -R changelog-skill/changelog ~/.agents/skills/changelog
```

Check that the destination does not already exist before copying. Codex detects skill changes automatically; restart it if the skill does not appear. Repository-scoped installation can use `.agents/skills/changelog` instead. See the [official Codex skill documentation](https://developers.openai.com/codex/skills) for current locations and invocation options.

The skill uses the `SKILL.md` format and has no required model provider, connector, or private skill dependency. Other compatible agents can load the same directory, but this repository's end-to-end validation is performed in Codex. The optional history collector needs Python 3.10+, Git, and IANA timezone data; it uses only the Python standard library and makes no network calls.

## Scope and safety

Research is read-only. The collector pins revisions, includes older work merged during the window, deduplicates repository aliases, and preserves dirty checkouts. Private evidence stays separate from the public report. External editorial review requires permission to disclose the material involved.

Publishing is a conditional follow-up, not an automatic side effect of requesting a changelog. When authorized, the workflow includes full-text approval where required, the site's documented build, selective commits, and verification of the actual page. It preserves unrelated work and reports deployment separately from live verification.

## Validation and development

Run the deterministic collector tests with:

```bash
python3 -m unittest discover -s tests -v
```

They cover calendar and daylight-saving boundaries, older merged commits, repository aliases, conflicting revisions, shallow history, empty windows, and preservation of source files and previous evidence.

Writing quality needs a different test. The [validation protocol](changelog/references/validation.md) runs the complete skill without revealing the accepted report, then compares coverage, factual fidelity, clarity, and useful links. It does not grade by matching wording or section counts. See [VALIDATION.md](VALIDATION.md) for the results and limits of this release's replay.

The workflow draws on [Servo's engineering-update process](https://github.com/servo/servo.org#how-to-write-a-monthly-update), [Keep a Changelog](https://keepachangelog.com/en/2.0.0/), and [Google's developer documentation guidance](https://developers.google.com/style/highlights). The [source notes](changelog/references/sources.md) explain how the guidance is applied.

## License

MIT. See [LICENSE](LICENSE). A copy travels with the installable skill directory. Linked third-party guidance remains under its own license.
