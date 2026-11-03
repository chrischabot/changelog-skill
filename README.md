# Changelog skill

Changelog is an agent skill that turns the work in one or more Git repositories into an engineering update people can actually read. Give a coding agent the repositories and a date range, and it researches what changed, brings related commits together and writes a complete changelog that explains what was built, improved or fixed, why it matters and any limitation that affects how it can be used. It is for whoever owes the team a fortnightly or monthly update, and for the senior engineers and technical leaders who have to read one.

It exists because repository history records work in the order it happened, while a reader wants to know what that work achieved. A framework might take dozens of commits to become usable, an important repair can sit inside a commit called "Maintenance work", and a branch written last month may only land this week. A summary of the log recovers none of that, so the writer has to read the diffs, decide which changes add up to one capability, and keep what was merged apart from what was deployed or verified in use. This skill makes that editorial judgment explicit and keeps the evidence behind it available for checking.

## How it works

The skill is a written procedure for the agent, supported by two small Python tools where a rule can be enforced in code.

Research starts from a complete inventory. The collector turns inclusive calendar dates in an explicit timezone into a baseline and a cutoff revision for each repository, then lists every commit reachable from the cutoff but not the baseline, which picks up older work merged during the window that `git log --since` can omit. It rejects shallow clones, which cannot show the full history, and leaves a dirty checkout as it found it.

The agent then reads the diffs and the code as it stood at the cutoff, and writes an evidence ledger before any prose: for each candidate change, its sources, the earlier behavior, what changed, the consequence the evidence supports, how ready it is and any numbers with their denominators. Commits are combined only when they produce one outcome for the reader, so the fixes that made a feature usable travel with it, while two integrations that merely share a directory stay separate. Each entry is drafted from a single message, "the change is ___; the reader gains or needs to know ___", and the whole document then goes through separate factual and editorial reviews. The editorial pass asks what job each sentence is doing and moves research narration into the ledger. Reader links are opened and checked for relevance, because a 200 response can still be a login page.

A run delivers a complete Markdown changelog ordered by significance, the evidence ledger, and a short note recording the cutoff, the checks performed and any limits left unresolved. The length follows the amount of noteworthy work rather than a fixed number of themes, and a single entry looks like this synthetic example:

> **Scheduled exports resume after a worker restart**
>
> Export jobs now save their progress between batches. If a worker restarts, its replacement continues from the last completed batch instead of starting the export again. This recovery path is implemented for CSV exports; PDF exports still restart from the beginning.

## Install

Clone this repository and copy its `changelog` directory into your agent's skill directory. For Codex:

```bash
git clone https://github.com/chrischabot/changelog-skill.git
mkdir -p ~/.agents/skills
cp -R changelog-skill/changelog ~/.agents/skills/changelog
```

Check that the destination does not already exist before copying. Codex detects skill changes automatically, so restart it only if the skill does not appear. To install for one repository, use `.agents/skills/changelog` instead; the [Codex skill documentation](https://learn.chatgpt.com/docs/build-skills) covers the other locations.

The skill uses the `SKILL.md` format and needs no particular model provider, connector or companion skill. Other compatible agents can load the same directory, although end-to-end validation has only been done in Codex. The collector and evaluation runner need Python 3.10+, Git and IANA timezone data; they use only the standard library and make no network calls.

## Usage

Invoke the skill in Codex with the repositories, dates and, if you have a preference, an audience and output location:

```text
$changelog

Create an engineering changelog for /work/platform and /work/applications,
covering 1–14 June 2026 inclusive, Europe/London.
Write for senior engineers and technical leadership.
Save the draft and evidence under /work/reports/june-update.
```

You can also ask in ordinary words, as in "Write a change log for these repositories for the last two weeks", although automatic selection of the skill has not been established, so use `$changelog` if the agent does not pick it up. The agent resolves the dates and scope before researching and asks only for inputs it genuinely cannot work out. Repositories are treated as read-only during research. Publishing is a separate step that happens only when you ask for it and authorize it, and private evidence stays out of the report.

The agent runs the history collector when it is useful, and the [evidence guide](changelog/references/evidence.md) explains how to run it yourself across several repositories or at pinned revisions. Its output and the evidence ledger can contain secrets and private names, so keep them out of public repositories.

## Validation

Unit tests can't tell you whether a changelog is any good, and most of this skill is instructions rather than code, so the [evaluation suite](changelog/evals/README.md) makes the review itself repeatable. You supply a writer, a different reviewer and the isolation between them, and its runner holds back the expected outcomes, freezes each submission by hash and will not pass a writing submission until a named reviewer has judged that exact text.

[VALIDATION.md](VALIDATION.md) records the results, failures included. Two blind replays against a private, previously accepted report fell short of it, missing substantive changes and, in the second run, losing material security qualifications, and those failures became the coverage and message-planning rules now in the skill. A final informed pass of review and correction reached that report's substantive coverage, but the final skill has not had a third blind replay. It is a regression case rather than a benchmark, so plan to check what the agent writes against its ledger and not to publish a first draft unread.

## Development

The installable skill lives in `changelog/`: [`SKILL.md`](changelog/SKILL.md) is the workflow the agent follows, [`references/`](changelog/references) holds the evidence, editorial, publishing and validation guidance, and [`scripts/`](changelog/scripts) holds the collector and evaluation runner. The tests for both scripts run from the repository root:

```bash
python3 -m unittest discover -s tests -v
```

## Project background

- [Changelog project overview](https://chabot.dev/projects/#changelog-skill) on Chris Chabot’s site.

## Credits and license

The workflow draws on [Servo's engineering-update process](https://github.com/servo/servo.org#how-to-write-a-monthly-update), [Keep a Changelog](https://keepachangelog.com/en/2.0.0/) and [Google's developer documentation guidance](https://developers.google.com/style/highlights). The [source notes](changelog/references/sources.md) explain how each is applied, along with the Servo and Ladybird updates it uses as examples, Wikipedia's Signs of AI writing checklist and OpenAI's skill guidance.

Released under the [MIT License](LICENSE), copyright 2026 Chris Chabot. A copy travels with the installable skill directory, and linked third-party guidance remains under its own license.
