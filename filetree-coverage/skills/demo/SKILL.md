---
name: demo
description: >
  Show the plugin on bundled fictional material: replay a recorded
  three-question session on a 63-file data room and render its map; with
  --live, generate the room, map it and let the user ask questions; with
  --chronology, generate a seed-to-Series-B financing set and run the
  chronology skill on it. Use when the user says "demo", "show me how it
  works", or wants to try it before mapping a real folder.
argument-hint: "[--live] [--chronology] [-o <folder>]"
---

# /demo

Everything is invented: companies, counterparties, numbers, and the recorded session (produced by feeding the recorder the tool calls a session would make). Say so once. `<out>` is `-o`, else a temporary folder.

## Replay (default)

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/build_coverage.py ${CLAUDE_PLUGIN_ROOT}/examples/lantern/store -o <out>/coverage.json --expect-file ${CLAUDE_PLUGIN_ROOT}/examples/lantern/expected.json`
2. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/render_viewer.py <out>/coverage.json -o <out>/coverage.html --standalone --summary`
3. Present the summary as printed, then one line per question: q1, the credit agreement was opened to its first eight lines (42%) and the answer says so; q2, the loss runs and the sales tax audit sat in searched folders and were never matched or opened; q3, the answer names the RCRA registration without opening it and the map flags it; all questions, 40 of 63 files never opened. Deliver the map as `show` does.
4. Close: on a real folder the recorder runs on every tool call; the expected sets in `examples/lantern/expected.json` stand in for the reviewer's.

## Live (`--live`)

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/make_demo_vdr.py <out>/room` (two scanned-PDF examples need Pillow).
2. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/room.py map <out>/room --id lantern-live`
3. Say the room is recording, suggest the questions in `${CLAUDE_PLUGIN_ROOT}/examples/lantern/questions.txt`, and stop. Answer what they ask as you normally would.
4. On request: `/filetree-coverage:show lantern-live --expect-file ${CLAUDE_PLUGIN_ROOT}/examples/lantern/expected.json`.

## Chronology (`--chronology`)

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/make_demo_vc.py <out>/halcyon` — 26 files, seed 2022 to Series B 2025, with the traps built in: an amendment that falls with its base at the next restatement, a certificate of amendment beside two restated charters, an unsigned Series C draft, a Series B agreement filed in the Series A folder, SAFEs converted at Series A, a one-investor side letter, a plan amended twice and never restated.
2. Run `/filetree-coverage:chronology <out>/halcyon` as written.
3. Point out: the 2024 Voting Agreement amendment is superseded by the 2025 restatement (named only in its recital); the draft supersedes nothing; the operative IRA is the 2025 restatement read with its 2026 Amendment No. 1 (§§3.1, 4.1); the plan is operative as amended twice.

## What it does NOT do

- Touches no folder other than `<out>` and the plugin's config folder; sends nothing anywhere.
