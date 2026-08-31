#!/usr/bin/env python3
"""Collect a read-only, revision-pinned inventory; interpretation remains human work."""

import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta
import hashlib
import json
import os
from pathlib import Path
import subprocess
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


def git(root, *args):
    env = dict(os.environ, GIT_OPTIONAL_LOCKS="0")
    result = subprocess.run(
        ["git", "--no-optional-locks", "-C", str(root), *args],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env,
    )
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", "replace").strip())
    return result.stdout


def decoded(data):
    return data.decode("utf-8", "replace").strip()


def revision(root, ref):
    return decoded(git(root, "rev-parse", "--verify", "--end-of-options", f"{ref}^{{commit}}"))


def boundaries(start, end, timezone):
    first, last = date.fromisoformat(start), date.fromisoformat(end)
    if last < first:
        raise ValueError("end must be on or after start")
    zone = ZoneInfo(timezone)
    return (
        datetime.combine(first, time.min, zone),
        datetime.combine(last + timedelta(days=1), time.min, zone),
    )


def first_parent_history(root, tip):
    rows = decoded(git(root, "log", "--first-parent", "--format=%H%x09%cI", tip))
    return [(sha, datetime.fromisoformat(when)) for sha, when in
            (line.split("\t") for line in rows.splitlines())]


def collect(config):
    start, end = boundaries(config["start"], config["end"], config["timezone"])
    if not config.get("repos"):
        raise ValueError("at least one repository is required")
    repositories, commits, seen = [], [], {}
    for spec in config["repos"]:
        root = Path(decoded(git(spec["path"], "rev-parse", "--show-toplevel"))).resolve()
        common = Path(decoded(git(root, "rev-parse", "--path-format=absolute", "--git-common-dir"))).resolve()
        if decoded(git(root, "rev-parse", "--is-shallow-repository")) == "true":
            raise ValueError(f"{root}: shallow history; obtain complete history before claiming coverage")
        tip = revision(root, spec.get("ref", "HEAD"))
        identity = str(common)
        if identity in seen:
            prior = seen[identity]
            if (tip, spec.get("baseline")) != (prior["tip"], prior["requested_baseline"]):
                raise ValueError(f"{root}: same repository supplied with conflicting revisions; choose one")
            prior["aliases"].append(str(Path(spec["path"]).absolute()))
            continue

        history = first_parent_history(root, tip)
        warnings = []
        if any(child[1] < parent[1] for child, parent in zip(history, history[1:])):
            warnings.append("Non-monotonic first-parent committer dates; verify date boundaries manually.")
        cutoff = next((sha for sha, when in history if when < end), None)
        baseline = None
        if cutoff:
            baseline = next((sha for sha, when in first_parent_history(root, cutoff) if when < start), None)
        if spec.get("baseline"):
            baseline = revision(root, spec["baseline"])
            if not cutoff:
                raise ValueError("cannot supply a baseline when no commit precedes the cutoff")
            git(root, "merge-base", "--is-ancestor", baseline, cutoff)
            warnings.append("Explicit baseline supplied; dates alone did not choose the start revision.")

        status = git(root, "status", "--porcelain=v1", "-z", "--untracked-files=normal")
        repo_id = f"repo-{len(repositories) + 1}"
        record = {
            "id": repo_id, "root": str(root), "git_common_dir": str(common),
            "aliases": [str(Path(spec["path"]).absolute())], "requested_ref": spec.get("ref", "HEAD"),
            "tip": tip, "requested_baseline": spec.get("baseline"),
            "baseline": baseline, "cutoff": cutoff,
            "dirty": bool(status), "status_sha256": hashlib.sha256(status).hexdigest(),
            "warnings": warnings,
        }
        seen[identity] = record
        repositories.append(record)
        if not cutoff or cutoff == baseline:
            record["commit_count"] = 0
            record["merge_count"] = 0
            continue
        scope = f"{baseline}..{cutoff}" if baseline else cutoff
        raw = git(root, "log", "--reverse", "--topo-order", "--format=%H%x00%P%x00%cI%x00%aI%x00%s%x00", scope)
        # Git adds a newline between formatted records. NUL separates fields even
        # when subjects contain tabs; Git paths below are NUL separated too.
        parts = raw.split(b"\0")
        rows = []
        for pos in range(0, len(parts) - 1, 5):
            sha, parents, committed, authored, subject = [decoded(x) for x in parts[pos:pos + 5]]
            when = datetime.fromisoformat(committed)
            rows.append({"repository": repo_id, "sha": sha, "parents": parents.split(),
                         "committed_at": committed, "authored_at": authored, "subject": subject,
                         "committer_date_in_window": start <= when < end})

        def with_paths(row):
            if row["parents"]:
                data = git(root, "diff-tree", "--no-commit-id", "--name-only", "-r", "-z",
                           row["parents"][0], row["sha"], "--")
            else:
                data = git(root, "diff-tree", "--root", "--no-commit-id", "--name-only", "-r", "-z", row["sha"], "--")
            row["paths"] = [p.decode("utf-8", "surrogateescape") for p in data.split(b"\0") if p]
            return row

        with ThreadPoolExecutor(max_workers=4) as executor:
            commits.extend(executor.map(with_paths, rows))
        record["commit_count"] = len(rows)
        record["merge_count"] = sum(len(row["parents"]) > 1 for row in rows)
        record["older_or_future_dated_count"] = sum(not row["committer_date_in_window"] for row in rows)
    snapshot = {
        "schema_version": 1,
        "start_inclusive": start.isoformat(), "end_exclusive": end.isoformat(),
        "timezone": config["timezone"],
        "method": "First-parent date boundaries; full reachability difference includes older merged commits. Commit dates approximate branch landing, not release or deployment dates.",
        "repositories": repositories,
    }
    return snapshot, commits


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", action="append", help="Repeat for multiple repositories; defaults to each HEAD")
    parser.add_argument("--start", help="Inclusive YYYY-MM-DD")
    parser.add_argument("--end", help="Inclusive YYYY-MM-DD")
    parser.add_argument("--timezone", help="IANA timezone, for example Europe/London")
    parser.add_argument("--config", type=Path, help="JSON with start, end, timezone, repos[{path, ref?, baseline?}]")
    parser.add_argument("--output", type=Path, required=True, help="New private directory; never overwrites an existing directory")
    args = parser.parse_args()
    try:
        if args.config:
            if any((args.repo, args.start, args.end, args.timezone)):
                raise ValueError("use --config or direct arguments, not both")
            config = json.loads(args.config.read_text())
        else:
            if not all((args.repo, args.start, args.end, args.timezone)):
                raise ValueError("--repo, --start, --end and --timezone are required without --config")
            config = {"repos": [{"path": p} for p in args.repo], "start": args.start,
                      "end": args.end, "timezone": args.timezone}
        if args.output.exists():
            raise ValueError("output already exists; choose a new directory to preserve previous evidence")
        snapshot, commits = collect(config)
        args.output.mkdir(parents=True, mode=0o700, exist_ok=False)
        (args.output / "source-snapshot.json").write_text(json.dumps(snapshot, indent=2) + "\n")
        with (args.output / "commits.jsonl").open("w") as handle:
            for row in commits:
                handle.write(json.dumps(row) + "\n")
        print(json.dumps({"output": str(args.output.resolve()), "repositories": len(snapshot["repositories"]),
                          "commits": len(commits), "warnings": [w for r in snapshot["repositories"] for w in r["warnings"]]}))
    except (ValueError, KeyError, TypeError, OSError, ZoneInfoNotFoundError) as exc:
        parser.exit(2, f"collect_history: {exc}\n")


if __name__ == "__main__":
    main()
