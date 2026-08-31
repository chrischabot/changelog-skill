"""Small, original synthetic sources. Nothing here is project evidence."""
import json
import os
from pathlib import Path
import subprocess


def git(repo, *args, when=None):
    env = dict(os.environ, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM="1")
    if when:
        env.update(GIT_AUTHOR_DATE=when, GIT_COMMITTER_DATE=when)
    return subprocess.check_output(["git", "-C", str(repo), *args], env=env,
                                   stderr=subprocess.PIPE).decode().strip()


def commit(repo, day, message, files):
    for name, content in files.items():
        path = repo / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    git(repo, "add", ".")
    git(repo, "commit", "-m", message, when=f"2026-06-{day:02d}T12:00:00Z")


def fortnight(root):
    core, labs = root / "core", root / "labs"
    for repo in [core, labs]:
        repo.mkdir(parents=True)
        git(repo, "init", "-b", "main")
        git(repo, "config", "user.name", "Synthetic Fixture")
        git(repo, "config", "user.email", "fixture@example.invalid")
        git(repo, "config", "commit.gpgsign", "false")
        git(repo, "config", "core.hooksPath", str(root / "no-hooks"))
    commit(core, 1, "Existing runtime", {
        "runtime/render.py": "def render(title):\n    return '<h1>' + title + '</h1>'\n",
        "runtime/routes.py": "def stream_target(url):\n    return url.split('?')[0]\n",
        "runtime/tokens.py": "def authorize(token, method):\n    return token['role'] == 'account'\n"})
    commit(labs, 1, "Existing applications and packages", {
        "README.md": "# Synthetic Labs\nNo hosted guides, source remote or demos exist for this fictional project.\n",
        "packages/registry.json": json.dumps(["http", "login"]),
        "packages/http/client.py": "def request(path):\n    return {'path': path}\n",
        "packages/login/gate.py": "def admit(session):\n    return bool(session)\n",
        "apps/archive/storage.py": "def publish(store, new_head, old_chunks):\n    store['head'] = new_head\n",
        "apps/bookings/store.py": "def reserve(db, seat, booking):\n    db.set(seat, booking)\n"})
    commit(labs, 3, "Add atomic reservation", {
        "apps/bookings/store.py": "def reserve(db, seat, booking):\n    db.atomic_put({seat: booking, 'booking:' + booking: True})\n"})
    commit(labs, 4, "Introduce shared export package", {
        "packages/exportkit/exporter.py": "def csv_batches(rows, checkpoint, send, save):\n    # send must acknowledge a batch before its checkpoint is saved.\n    # Replayed sends require an idempotency key at the destination.\n    for index in range(checkpoint, len(rows)):\n        send(index, rows[index])\n        save(index + 1)\n\ndef pdf_export(render):\n    # PDF has no saved progress.\n    return render()\n",
        "apps/invoices/main.py": "from exportkit.exporter import csv_batches\nexport = csv_batches\n",
        "apps/analytics/main.py": "from exportkit.exporter import csv_batches\nexport = csv_batches\n",
        "packages/registry.json": json.dumps(["http", "login", "exportkit"]),
        "tests/exportkit_copy.py": "# Fixture copy, not an application consumer.\n",
        "evidence/export-check.json": json.dumps({"environment": "local", "result": "resume from last saved batch", "hosted_deployment": False})})
    commit(core, 5, "Scope automation credentials", {
        "runtime/tokens.py": "DEFAULT_TTL_HOURS = 12\nMAX_TTL_HOURS = 168\nREADS = {'account.info', 'account.balance'}\n\ndef authorize(token, method):\n    if token['role'] == 'account':\n        return True\n    return method in READS or method.startswith('app:' + token['app'] + ':')\n"})
    commit(labs, 6, "Share notification integration", {
        "packages/notify/delivery.py": "def deliver(send, save_outcome, payload):\n    receipt = send(payload)\n    for attempt in range(3):\n        if save_outcome(receipt):\n            return receipt\n    raise RuntimeError('outcome could not be saved; do not resend blindly')\n",
        "packages/registry.json": json.dumps(["http", "login", "exportkit", "notify"]),
        "evidence/notification-check.json": json.dumps({"unit_check": "send called once while save retries", "live_provider_send": False})})
    commit(labs, 7, "Maintenance work across storage and fixtures", {
        "apps/archive/storage.py": "def publish(store, new_head, old_chunks):\n    store['head'] = new_head\n    # Cleanup follows successful publication and is bounded.\n    for key in old_chunks[:32]:\n        store.pop(key, None)\n    return old_chunks[32:]\n",
        "tests/exportkit_copy.py": "# Generated fixture copy; not another deployed consumer.\n"})
    commit(core, 7, "Maintenance work across request handling", {
        "runtime/routes.py": "def stream_target(url):\n    # Preserve caller query parameters for streaming requests.\n    return url\n"})
    commit(labs, 9, "Move booking handler to simpler application loop", {
        "apps/bookings/store.py": "def reserve(db, seat, booking):\n    db.compare_and_swap(seat, None, booking)\n    # A crash here can leave a reserved seat without the separate booking row.\n    db.set('booking:' + booking, True)\n"})
    commit(labs, 10, "Connect shared login", {
        "packages/login/gate.py": "def consume_nonce(store, nonce):\n    if store.get(nonce):\n        return False\n    store[nonce] = True\n    return True\n\ndef refuse(publish):\n    try:\n        publish('denied')\n        return True\n    except OSError:\n        return False\n",
        "apps/portal/main.py": "from login.gate import refuse\n\ndef handle(authenticated, publish):\n    if not authenticated and refuse(publish):\n        return 'stopped'\n    return 'private content'\n"})
    attempts = [{"client": "A", "id": n, "within_budget": True, "browser_pass": True} for n in range(1, 6)]
    attempts += [{"client": "B", "id": n, "within_budget": n != 3,
                  "browser_pass": True if n <= 3 else None} for n in range(1, 6)]
    commit(labs, 14, "Record client evaluation", {
        "evidence/attempts.json": json.dumps(attempts, indent=2),
        "evidence/recheck.json": json.dumps({"initial_browser_passes": 2, "corrected_browser_passes": 8,
            "attempts": 10, "same_artifacts": True, "redeployed": False,
            "reason": "corrected browser assertions", "task": "build and deploy a small public web app"}),
        "evidence/status.md": "The implementation has local checks only. Hosted package and login acceptance remain unverified.\n"})
    commit(labs, 16, "Add PDF resume after the reporting window", {
        "packages/exportkit/pdf.py": "def resume_pdf(checkpoint):\n    return checkpoint\n"})
    (labs / "evidence/status.md").write_text("UNCOMMITTED: claim every deployment is ready. This is not reporting-window evidence.\n")
    alias = root / "core-alias"
    alias.symlink_to(core, target_is_directory=True)
    return {"repos": [{"path": str(p)} for p in [core, labs, alias]],
            "start": "2026-06-02", "end": "2026-06-15", "timezone": "UTC"}


COMPRESSION = """# Engineering update

## Clients built working applications within budget

Client A completed all five application tasks within the fixed time and step budgets. Client B completed two of its five attempts, giving seven confirmed successes out of ten attempts overall. Two Client B results remain unverified. A further Client B application worked in the browser after its agent exceeded the budget, so it does not count as an in-budget completion.

The evaluation retained transcripts, build receipts, source trees, screenshots and per-step browser observations for later inspection. Correcting the browser assertions increased browser confirmation from two to eight of the same ten artifacts, without editing or redeploying them. This correction must not be attributed to improvements in the product. Each client had attempted the same small public application tasks under the same limits.

## CSV exports resume after worker restarts

The shared exporter saves its acknowledged progress between batches of CSV rows. A replacement worker resumes from the saved batch after a restart, rather than beginning the entire export again. This lets an interrupted export continue using its recorded progress. PDF exports still start over because they do not yet save a checkpoint.

The implementation was exercised with local restart checks, including a worker stopping after an acknowledged batch and a replacement reading the saved position. These checks establish the local recovery behavior, but no hosted deployment has yet been verified. Both applications now use the same exporter rather than keeping separate implementations of this batch loop.

## Shared login still has access-control gaps

The login package lets applications share provider configuration while retaining separate application sessions. Its consumer can continue serving a protected request if publishing an access refusal fails. Non-atomic nonce consumption also leaves concurrent handoffs without a single-use guarantee. Restricted access therefore cannot yet be relied on.

The source contains both a reusable gate and the application call site that invokes it. Reviewing the package declaration alone would miss the consumer's error handling. Those details remain available in the evidence ledger, alongside the code paths and the remaining repair work.
"""


ROUTING = [
    {"id": "explicit", "request": "$changelog for /work/platform and /work/apps, 1–14 June 2026 inclusive, Europe/London"},
    {"id": "relative", "request": "Write a change log for these repositories for the last two weeks", "context": "Repositories: /work/platform and /work/apps. Current date: 2026-06-15 UTC. Use the fourteen complete days preceding today."},
    {"id": "missing", "request": "$changelog", "context": "Use UTC. No repositories, dates, current project or prior task context are available."},
    {"id": "non-trigger", "request": "List the last five commit hashes", "context": "Current directory is a Git repository."}
]
