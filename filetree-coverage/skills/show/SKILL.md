---
name: show
description: >
  Draw the coverage map for a mapped folder: a radial file tree colored by how
  far each question got with every file (listed, matched a search, opened and
  how much, named in the answer), a cumulative view across all questions, and
  the files nothing ever opened. Use when the user asks what was read, "did you
  look at X", "which documents did that rest on", "show me the map", "coverage",
  or after any diligence answer over a mapped folder that will be relied on.
argument-hint: "[<room id>] [--expect-file expected.json] [--merge 2-3] [--session <id>] [--since <ISO time>] [-o <folder>]"
---

# /show

The map records tool calls, not judgment: "opened" was opened, "listed" means a listing or search covered it, "not touched" means no call reached it. Whether an untouched file mattered is the reviewer's call; the page lets them mark expected files and lists the ones never opened.

1. Room: `$ARGUMENTS`, else the only mapped room, else `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/room.py list` and ask. None mapped → `/filetree-coverage:map` first.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_coverage.py <room id> -o <out>/coverage.json [--expect-file f] [--merge 2-3] [--session id] [--since t]`
   `<out>`: `-o`, else `~/.claude/plugins/config/filetree-coverage/rooms/<id>/views/<YYYYMMDD-HHMM>/`. Each user prompt is one question; prompts that touched no file are dropped (count printed). `--merge 2-3` (or `5,6`; repeatable; numbers as the unmerged map shows them) folds follow-up turns into one question: offer it when an answer names files a neighbouring turn opened. `--expect-file` is `{"q1": [globs], "*": [globs]}` relative to the room, only from what the reviewer said; never invent one.
3. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_viewer.py <out>/coverage.json -o <out>/coverage.html --standalone --summary`
   Show the printed summary exactly as printed.
4. Deliver: artifact tool available → render a copy without `--standalone` to `<out>/coverage.artifact.html` and publish it; file-sending tool → send `coverage.html`; else give the path. The page is self-contained; marks clicked on it stay in that browser ("Show expected marks as JSON" exports them).
5. Close with two or three sentences, in this order: files the answer names that nothing opened (the answer discusses a document it did not read; check it); expected files listed or matched but not opened; files opened only in part, with the share; then, past one question, how many files no question has opened.

"Named in the answer" counts only files that were also opened; a file named without an open is listed separately because it is the case the reviewer most needs. Tier definitions and limits: `references/tiers.md`.

## What it does NOT do

- Never alters the ledger; only `map reset` does. Reads no document. Certifies nothing: it shows what the session did, the reviewer decides whether that was enough.
