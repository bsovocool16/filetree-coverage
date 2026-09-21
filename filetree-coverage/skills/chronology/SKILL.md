---
name: chronology
description: >
  Dated chronology of a company's governing and financing documents (charter,
  bylaws, IRA, ROFR/co-sale, voting, stock plan, SPAs, SAFEs, side letters,
  consents): which instrument is operative today, which amendments layer onto
  it, what each amended-and-restated version superseded. Use for folders with
  successive rounds (seed, Series A, B…), "which IRA governs", "current
  charter", "put these in order", "what superseded what", "is the 2022
  agreement still in effect", and before answering any question about rights
  under an agreement that has been amended or restated.
argument-hint: "<folder> [-o <out folder>]"
---

# /chronology

Prevents one failure: reading every version of an agreement as if it were live, so a 2023 IRA answers a 2025 question. The chronology settles what is operative, amended, and superseded before anything is quoted.

## Rules

- An amendment layers: it changes the sections it names; base and amendment are read together. Quote the amendment for those sections, the base for the rest.
- A restatement replaces: an "Amended and Restated" agreement supersedes the prior agreement and every earlier amendment to it, listed or not. A later amendment attaches to the restatement.
- Ordinals count: Second A&R supersedes A&R supersedes original. A missing ordinal is a gap to report.
- Charters: a Certificate of Amendment (DGCL §242) amends the current certificate; an A&R Certificate (§245) integrates and supersedes it and its amendments; a Certificate of Designation amends.
- Drafts and unsigned copies are not operative and supersede nothing; report them as pending.
- Superseded is not irrelevant: it fixed the parties' rights at its time, and provisions may survive by their terms. Mark it superseded; keep it in the record.
- Side letters bind only their parties; they are not amendments.
- Transaction documents are not superseded by the next round: each SPA stays relevant for its round. SAFEs and notes terminate on conversion per their terms; confirm from the SPA or a conversion notice.
- Dates come from the instrument's text ("made as of", "effective", filing line); a file-name date is a fallback and is reported as one.

## Steps

1. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/chronology_scan.py <folder> -o <out>/chronology.json --md <out>/chronology.md`
   Classifies each file (family; original / amendment / restatement and ordinal; date and its source; executed / unsigned / draft; prior instruments named in recitals; supersession or continuity language; sections an amendment touches), computes each governing family's chain, operative instrument and superseded set, and prints flags. `<out>`: `-o`, else `chronology-<YYYYMMDD-HHMM>/` beside the folder; never write inside it.
2. Resolve every flag by opening the document (title, recitals, "made as of" line, signature block), never from the file name. Flags cover drafts, unsigned copies, no signature block or adoption line (common for bylaws and plans: confirm the adoption date from the text), dates taken from file names or stray text, restatements without supersession language, amendments without a continuity clause, misfilings (place by the instrument's own date; note the misfiling), and recital references to instruments the folder lacks (a gap; do not infer their terms).
3. Verify each chain: open every restatement's recitals and confirm the prior agreement it names matches the document placed before it, by name and date.
4. Settle transaction documents: for each SAFE or note, find the conversion in the priced round's SPA or a notice and cite it; if only a forward-looking covenant exists, cite it and say issuance is not evidenced; if nothing, say "conversion not evidenced in the room". Record each side letter against the agreement it modifies and the party bound.
5. Write `<out>/chronology.md` in the format below (replace the scan's table; it is a first pass, not a draft) and present it. Every stated effect cites document and clause; where the documents are silent, say so rather than supplying what a standard form would say.
6. `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/room.py list`: if a coverage room covers this folder, say `/filetree-coverage:show` will list which documents this chronology opened.

## Output

```
# Chronology — <company> governing and financing documents
As of <latest executed instrument>. Source: <folder>. <N> documents; <D> drafts/unsigned; <U> adoption unconfirmed; <G> gaps; <F> scan flags resolved.
(G = instruments the documents name or presuppose that the folder lacks: prior agreements, recited approvals, schedules and exhibits.)

## Operative today
| Family | Operative instrument | Dated | Read together with | Supersedes |

## Chronology
| Date | Instrument | Family | Event | Effect | Round | File |
one row per document in date order; Effect cites what it did to what ("supersedes IRA of 2023-05-12 in its entirety (Recitals)"; "amends §1.2(c) (§1)"; "converted at the Series A Initial Closing (SPA §1.1); terminated (SAFE §5)"). Round: the round the document names or whose SPA lists it as a closing deliverable; "Series B (by date)" for a labelled inference; else blank.

## Pending (drafts and unsigned)
## Side letters and party-specific instruments
## Gaps and flags
```

Worked example on the bundled set: `${CLAUDE_PLUGIN_ROOT}/examples/halcyon/chronology.md`.

## What it does NOT do

- Decides no legal effect the documents leave open (survival of rights, validity of an amendment adopted without the required consents, effect of an unfiled charter amendment); it reports what the documents say and flags what they do not.
- Treats no file name, folder or index number as evidence of date or status.
- Modifies nothing. Every chronology is a draft for attorney review.
