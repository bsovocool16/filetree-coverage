---
name: map
description: >
  Start passive coverage tracking on a folder of documents (a data room export,
  a matter folder): from then on every listing, search, open and answer that
  touches its files is recorded, without changing how the session searches. Use
  when the user says "map the data room", "track what you read in this folder",
  "start coverage", or points at a folder before diligence questions; also for
  `list`, `reset`, `refresh`, `unmap` of mapped rooms.
argument-hint: "<folder> [--id <name>] | list | reset <id> | refresh <id> | unmap <id>"
---

# /map

A hook records every file-touching tool call to a ledger, keeping only paths inside mapped folders. Mapping turns the recorder on for a folder; it prescribes nothing about the search.

1. Resolve the folder from `$ARGUMENTS`, else ask. It must be local (export the room first) with its folder structure intact; subfolders become the map's branches.
2. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/room.py map <folder> [--id <name>]` — indexes names, sizes, line/page counts (no content), registers the room under `~/.claude/plugins/config/filetree-coverage/`, starts or keeps its ledger. Report the output as printed.
3. Say in one or two sentences that recording is on for the folder, what it records (listings, search hits, opens with line or page ranges, each prompt and answer), and that `/filetree-coverage:show <id>` draws the map. Offer `reset` if the user wants a clean slate.
4. Carry on with whatever the user asks; do not search differently because the recorder is on.

Management: `room.py list` (rooms, file and event counts); `reset <id>` (empties the ledger; confirm first); `refresh <id>` (re-index after files change); `unmap <id>` (stop recording; store kept).

What the recorder sees and misses: `references/tiers.md`.

## What it does NOT do

- Reads, copies, indexes the content of, or modifies no document; the index is names and sizes.
- Sends nothing anywhere; never blocks or slows a tool call; a failed record is silent.
- Judges no relevance; that is the reviewer's, on the map.
