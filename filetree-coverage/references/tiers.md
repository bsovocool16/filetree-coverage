# What the map records, and what it doesn't

Every file in the mapped folder gets one tier per question, the furthest stage a tool call reached:

| tier | recorded when | what a reviewer can conclude |
|---|---|---|
| not matched or opened | no search returned it and nothing opened it | the session did not engage with it (it may still sit in a searched or listed folder; see below) |
| matched a search | a search returned it | the session saw it as a candidate and chose not to open it (or opened it, in which case the tier is higher) |
| opened | `Read`, `cat`, `head`, `tail`, `sed -n`, `pdftotext` ... touched it; line ranges (from `Read` offsets/limits or `head`-style commands) or PDF page ranges are recorded, so a share of the file is known when the index has its length | part or all of it was in front of the model |
| named in the answer | its name (or VDR index number) appears in the turn's final message **and** it was opened | the answer rests on it, at least nominally |

Listings and search scopes are recorded per folder, not per file. A search over a folder, or a listing of it, shows the session looked there; it does not show the session considered any one file, and marking every file in a searched folder made nearly every file in a room "touched". The map shades each searched folder as a sector from the folder out past its files. A search over a folder covers its subfolders, so a search of the room, then of `03 Material Contracts`, then of `3.4 Financing` gives three nested sectors, and the shade deepens where they overlap. A folder whose contents a listing showed gets a grey arc inside its files.

Rooms over 400 files are drawn around what the session did. A folder with a matched, opened or named file opens to one leaf per file, so the unopened files beside them stay visible; folders a search or listing covered open while they fit; every other folder collapses to a small box with its file count. Nothing is dropped: a folder no question entered is still on the map. Clicking any folder opens or closes it, one level at a time; marking files as expected is a separate mode (the Mark expected button), so a click always does one kind of thing. In the cumulative view the opened area grows question by question.

Two flags sit beside the tiers. **Named, never opened**: the answer names a file that nothing opened. That is the same signal whether the answer is confessing a gap ("the credit agreement was not reviewed") or asserting something about a document it never read, and both deserve a look. **Not indexable** only exists in the pipeline format, where text extraction failed; the passive recorder does not extract text, so a scanned PDF simply shows whether it was opened.

The cumulative view keeps, per file, the highest tier across all questions, how many questions matched / opened / named it, the total number of opens, and the largest share read; per folder, how many questions searched or listed it.

## Limits that matter

The recorder sees tool calls, not attention. "Opened" means the content was returned to the model; whether the model used it is not observable. Share-of-file is computed from line ranges and page ranges the tools report; a `cat` counts as a full read. For `Read`, the share comes from the lines the tool reports returning, so a long file it truncated counts as partial even when no offset or limit was asked for.

Bash parsing is heuristic. Room paths are recognized in the command (quoted, unquoted, or backslash-escaped) and in the output (absolute paths; relative lines when the shell was inside the room; `ls` output resolved against the listed folder). A command that reaches a room file through a variable, a glob the shell expands, or a script the recorder cannot see will be missed or under-classified. When the map surprises you, the ledger is plain JSONL and the tool call it came from is one line.

Text searches skip binaries: a `grep` over a folder does not read its PDFs or Word files. The map's search counts say how many files under searched folders a text search could read, and a PDF's detail panel says when its folder was searched but it was not.

"Named in the answer" is a name match: the file's basename without extension, its VDR index number (`3.4.01`), or the basename minus the index. Answers that refer to a document by a shorter alias ("the Halvorsen MSA") will not match. The pipeline format's `[[n]]` citations are exact; the passive format trades that precision for not having to dictate how the answer is written.

Expected sets are the reviewer's. A gap list built from a folder glob ("everything under Material Contracts") checks coverage against a document class; one built by clicking is a spot check. Neither finds a relevant file the reviewer did not think of.

## Ledger and coverage.json

Ledger (`~/.claude/plugins/config/filetree-coverage/rooms/<id>/ledger.jsonl`), one JSON object per line:

```
{"t","session","type":"prompt","text"}
{"t","session","tool","type":"listed","files":[...]}            or {"type":"listed","files":[],"scope":"<dir>"}
{"t","session","tool","type":"scanned","scope":"<dir>","pattern"}
{"t","session","tool","type":"hit","files":[...],"pattern"}
{"t","session","tool","type":"read","file","offset","limit","pages","start","lines_returned","total_lines","partial"}
{"t","session","type":"answer","text"}                           (SubagentStop writes "subanswer")
```
Events made inside a subagent carry `"agent": "<agent type>"`.

coverage.json (from `build_coverage.py`):

```
mode: "passive", tiers: [...]
files[]          path, size, lines | pages
questions[]      id, question, answer, asked_at, session, expected[],
                 files{path → tier, hits, reads, read_fraction, read_lines[[a,b]...], total_lines, read_pages[], tools[], agents[], named, named_unopened},
                 folders{path → searched, listed, patterns[]}          ("" is the room)
                 summary
cumulative       files{path → tier, q_hit, q_read, q_cited, q_named_unopened, reads, max_read_fraction},
                 folders{path → q_searched, q_listed}, summary
```

The viewer reads this shape from any source. `scripts/collectors/bm25_pipeline.py` writes the older pipeline variant (tiers retrieved / in_context / cited with `[[n]]` excerpt citations) for a retrieval system outside Claude Code; the viewer renders both.
