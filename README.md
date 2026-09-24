# filetree-coverage

A Claude plugin that maps a folder of documents and then records, passively, what a session does with its files. Map
the folder once; work as usual (ask questions, let Claude search, read, spawn subagents, however it likes); then draw the
map. The map is a radial file tree, one branch per top-level folder and one leaf per file, colored by how far the
session got with each file for a given question: matched a search, opened (and how much of it), named in the answer;
the folders it searched or listed are shaded beneath the files. A cumulative view shows the same across every question asked, and lists the files nothing has ever
opened. The reviewer marks the files an answer should have rested on, and the page lists the ones it never reached.

It is a filetree retrieval audit. The first use is data-room diligence, where "did it look at the credit agreement?"
has no answer inside most AI review tools. It dictates nothing about the search; it records tool calls. Every answer is a
draft for attorney review, and the map is an audit of what was touched, not a certificate of completeness.

An independent project by Benjamin Sovocool, not affiliated with or endorsed by Anthropic. It follows the conventions of
the [claude-for-legal](https://github.com/anthropics/claude-for-legal) plugins so that it fits the same workflow.

## How it works

| step | what happens | who does it |
|---|---|---|
| map | the folder is indexed (paths, sizes, line or page counts; no content) and registered; a ledger starts | `/filetree-coverage:map <folder>` → `scripts/room.py` |
| record | after every file-touching tool call, on every prompt and at the end of every turn, a hook appends one line to the ledger: listings, search scopes and hits, opens with line or page ranges, the prompt, the answer | `hooks/hooks.json` → `scripts/track.py`, automatically |
| show | the ledger is cut into questions at prompt boundaries, tiers are computed per file per question and cumulatively, and the page is rendered with a printed summary | `/filetree-coverage:show` → `scripts/build_coverage.py`, `scripts/render_viewer.py` |

Nothing in between is prescribed. The recorder sees `Read` (with offsets, limits and PDF page ranges), `Grep`, `Glob`,
`LS`, and `Bash` (it parses commands and output for room paths: `cat`/`head`/`sed -n`/`pdftotext` are opens,
`ls`/`find` listings, `grep`/`rg` searches). Subagents' calls are recorded and tagged with the agent's name.

## Install

This repository is a one-plugin marketplace, laid out like `anthropics/claude-for-legal`. In a Claude Code session:

```
/plugin marketplace add bsovocool16/filetree-coverage
/plugin install filetree-coverage@filetree-coverage
```

From a clone or the zip, give the folder path in place of `bsovocool16/filetree-coverage`. The hooks are registered by the
install; a new session picks them up. Python 3.10+ is the only requirement. `pip3 install pypdf` (or `pdfplumber`) adds
PDF page counts so partial reads of PDFs show as a share; `pip3 install pillow` is needed only for the demo's two
scanned-PDF examples.

### What you bring

A local folder of documents, with its folder structure (a room on Intralinks, Datasite or a DMS has to be exported
first), and your questions. Optionally, for each question, the folders or files you expect the answer to rest on, as
globs, so the page can list the misses; or mark them by clicking on the map.

Nothing leaves the machine. The scripts are standard library, make no network calls, never read or copy document
content, and write only under `~/.claude/plugins/config/filetree-coverage/`.

### Try it first

`/filetree-coverage:demo` builds and renders the bundled recorded session on the fictional data room (Project Lantern:
Meridian Coatings, Inc., 63 files in ten VDR folders, three diligence questions). `--live` generates a fresh copy of the
room, maps it, and lets you ask questions of it so the recorder captures a real session.

## Chronology of governing documents

`/filetree-coverage:chronology <folder>` is the second skill, for the failure that shows up when a room holds several rounds
of financing documents: every version of the investors' rights agreement gets pulled into context and the 2023 answer
comes back to a 2025 question. The scan (`scripts/chronology_scan.py`) classifies each file (charter, bylaws, IRA, ROFR
and co-sale, voting, stock plan, SPA, SAFE or note, side letter, consent), reads whether it is an original, an amendment
or a restatement and its ordinal, takes the date from the instrument's own text, checks the signature block for
executed / unsigned / draft, pulls the prior agreements the recitals name and whether the text says it supersedes them,
and computes per family the chain of restatements, the amendments hanging off each, the operative instrument and the
superseded ones. It flags what it cannot settle; the skill has Claude open those documents, verify each restatement's
recitals against the chain, settle SAFE conversions from the SPA, and write the chronology: an operative-today table, a
dated table with the effect of every instrument cited to its clause, pending drafts, side letters, gaps and flags.

The rules it applies are stated in the skill: an amendment layers and is read together with its base; a restatement
replaces the base and every earlier amendment to it; a draft supersedes nothing; a superseded document is still the
record of what governed at its time; side letters bind only their parties; each round's SPA stays relevant and SAFEs
terminate on conversion. `examples/halcyon/` is a generated 26-document set (seed, Series A, Series B) with the traps
built in, and `chronology.md` there is the output a test session produced from it.

## What the map shows

| mark | meaning |
|---|---|
| hollow | not matched or opened |
| green | matched a search |
| dark green (wedge = share read) | opened; a partial read shows the share of lines or pages |
| darkest green, white core | named in the answer, and opened |
| amber dashed ring | named in the answer but never opened: check it |
| red ring | marked as expected by the reviewer, not opened |
| blue sector | a search ran over the folder; it covers the subfolders, and the shade deepens where a subfolder was searched again |
| grey arc inside a folder's files | a listing showed the folder's contents |
| small box with a count | a collapsed folder in a room over 400 files: nothing happened in it; click to open |
| number beside a leaf (cumulative view) | opened in that many questions |

`references/tiers.md` has the definitions, the limits (Bash parsing is heuristic; "named" is a name match; text searches
skip binaries), and the ledger and JSON shapes.

## Related work

No open-source tool or published skill was found that renders what a session touched against a corpus's own folder
tree. The nearest:

- [Mike](https://github.com/willchen96/mike) (MikeOSS, the open-source Harvey/Legora alternative, AGPL-3.0) answers
  project questions agentically through `list_documents`, `fetch_documents`, `read_document` and `find_in_document`
  tools and persists those tool events with each message, so the raw data for this map already exists in its database;
  its UI shows "Reading document…" while streaming and has no per-project view of what was and was not read. A coverage
  panel there would be a natural contribution; this plugin does the same thing for Claude Code sessions, where the tool
  calls arrive through hooks.
- In `anthropics/claude-for-legal`, `corporate-legal`'s `diligence-issue-extraction` keeps a hand-maintained folder-level
  VDR inventory with a status column, and `tabular-review` gives every document a row. This plugin sits beside them as
  the file-level record of what any of them actually touched.
- Chronology skills in `claude-for-legal` (`litigation-legal/chronology`) and in the registry (Andrew Bird's
  `chronology-builder`, Scott Margetts's `timeline-generator`) build event chronologies from a matter file or disclosure
  bundle: what happened when. This plugin's `chronology` is instrument lineage: what amends, restates or supersedes what,
  and which version governs. Different question, same word.
- RAG inspection tools ([rag-inspector](https://github.com/jmmg-696/rag-inspector),
  [RAGxplorer](https://github.com/Glareone/RAG-Explorer), [Renumics RAG](https://github.com/Renumics/renumics-rag),
  [RAGViz](https://arxiv.org/abs/2411.01751)) show retrieved chunks in embedding space or attention over retrieved
  passages; none maps the untouched remainder of a corpus.

## Layout

```
.claude-plugin/marketplace.json     marketplace manifest (one plugin)
filetree-coverage/                  the plugin
  .claude-plugin/plugin.json        manifest
  hooks/hooks.json                  the recorder's hooks (UserPromptSubmit, PostToolUse, Stop, SubagentStop)
  CLAUDE.md                         optional practice-profile template
  skills/map/SKILL.md               map a folder; list, reset, refresh, unmap rooms
  skills/show/SKILL.md              build and render the map, read it aloud
  skills/chronology/SKILL.md        operative stack and dated chronology of governing documents
  skills/demo/SKILL.md              replay the bundled session, run live on a generated room, or run the chronology set
  scripts/track.py                  the hook: reads a tool call, keeps room paths, appends to the ledger
  scripts/room.py                   index and register folders
  scripts/build_coverage.py         ledger → coverage.json (per question + cumulative)
  scripts/render_viewer.py          coverage.json → coverage.html, plus the printed summary
  scripts/make_demo_vdr.py          generates the fictional M&A room
  scripts/chronology_scan.py        first pass for the chronology: classification, dates, status, lineage, flags
  scripts/make_demo_vc.py           generates the fictional financing set (Halcyon Robotics)
  scripts/collectors/bm25_pipeline.py   a retrieval pipeline that writes the same coverage.json, for use outside Claude Code
  assets/viewer_template.html       the map (self-contained; no build step; no network)
  references/tiers.md               tier definitions, limits, ledger and JSON shapes
  examples/lantern/                 questions, expected sets, and the recorded session (store/)
  examples/halcyon/                 the chronology scan output and a worked chronology for the financing set
  tests/                            recorder-to-coverage tests on Claude Code-shaped hook payloads
                                    (`python3 -m unittest discover tests`, from the plugin folder)
```

## License

Copyright 2026 Benjamin Sovocool. Licensed under the [PolyForm Noncommercial License 1.0.0](LICENSE.md): free to use, copy
and modify for noncommercial purposes. Any commercial use, including use in a law firm's practice, needs a license from the
author.

Required Notice: Copyright 2026 Benjamin Sovocool
