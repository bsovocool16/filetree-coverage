#!/usr/bin/env python3
"""
build_coverage.py — turn a room's ledger into coverage.json for the viewer.

    build_coverage.py <room id or store folder> -o coverage.json [--expect-file expected.json] [--session <id>] [--since <ISO time>]

Events are grouped by session, then cut into question segments: each user
prompt starts one, the tool events until that session's next prompt belong to
it, and the Stop event's text is its answer. Several windows recording into
the same room interleave in the ledger; grouping by session keeps them apart.

Per file per segment the tier is the furthest of:

    untouched   no search matched it and nothing opened it
    hit         a search matched it (Grep, grep, rg)
    read        it was opened (Read, cat, head, sed -n, pdftotext, ...); the fraction of lines or pages is recorded
    cited       it was opened and its name appears in the answer

Listings and search scopes are recorded per folder, not per file: a search
over a folder, or a listing of it, says the session looked there, not that it
looked at any one file. Per segment, `folders` maps a folder ("" is the room)
to how many searches ran over it and how many listings showed its contents.
A search over a folder covers its subfolders; the viewer draws that.

`cumulative` holds the same across all segments: per file the max tier, how
many segments hit / read / cited it and the largest fraction read; per folder
how many segments searched or listed it.
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import os
import re
import sys
import time
from pathlib import Path

HOME_DEFAULT = Path.home() / ".claude" / "plugins" / "config" / "filetree-coverage"
RANK = {"untouched": 0, "hit": 1, "read": 2, "cited": 3}
TIERS = [
    {"id": "untouched", "label": "Not matched or opened"},
    {"id": "hit", "label": "Matched a search"},
    {"id": "read", "label": "Opened"},
    {"id": "cited", "label": "Named in the answer"},
]
# a text search (Grep, grep, rg) does not look inside these
BINARY_EXT = {".pdf", ".docx", ".doc", ".xlsx", ".xls", ".pptx", ".zip", ".png", ".jpg", ".jpeg", ".tif", ".tiff", ".msg", ".eml"}


def find_store(arg: str) -> Path:
    p = Path(arg).expanduser()
    if p.is_dir() and (p / "room.json").exists():
        return p
    home = Path(os.environ.get("FILETREE_COVERAGE_HOME") or HOME_DEFAULT)
    try:
        reg = json.loads((home / "rooms.json").read_text())
        for r in reg.get("rooms", []):
            if r["id"] == arg:
                return Path(r["store"])
    except Exception:
        pass
    sys.exit(f"no room store found for {arg}")


def load_ledger(store: Path):
    out = []
    p = store / "ledger.jsonl"
    if not p.exists():
        return out
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except Exception:
            continue
    return out


def segment(events):
    """Group events into question segments: by session, then on prompt boundaries.

    Segments come out in the order their prompts were asked. Events a session
    records before its first prompt get a segment with no prompt."""
    segs = []
    current = {}  # session id -> its open segment
    for e in events:
        sid = e.get("session")
        if e.get("type") == "prompt":
            current[sid] = {"prompt": e, "events": [], "answer": None}
            segs.append(current[sid])
            continue
        cur = current.get(sid)
        if cur is None:
            cur = current[sid] = {"prompt": None, "events": [], "answer": None}
            segs.append(cur)
        if e.get("type") == "answer":
            cur["answer"] = e
        else:
            cur["events"].append(e)
    return segs


def merge_ranges(ranges):
    rs = sorted((a, b) for a, b in ranges if b >= a)
    out = []
    for a, b in rs:
        if out and a <= out[-1][1] + 1:
            out[-1][1] = max(out[-1][1], b)
        else:
            out.append([a, b])
    return out


def parse_pages(spec):
    """'1-5' or '3' or '2,4-6' -> set of page numbers"""
    pages = set()
    for part in str(spec).split(","):
        part = part.strip()
        if "-" in part:
            a, b = part.split("-", 1)
            try:
                pages.update(range(int(a), int(b) + 1))
            except ValueError:
                pass
        elif part.isdigit():
            pages.add(int(part))
    return pages


def name_keys(path: str):
    """Ways an answer might name this file: the full basename without extension, the VDR index number, and the basename minus the index."""
    base = Path(path).name
    stem = re.sub(r"\.[A-Za-z0-9]{1,5}$", "", base)
    keys = {stem.lower()}
    m = re.match(r"^(\d+(?:\.\d+)*)\s+(.*)$", stem)
    if m:
        keys.add(m.group(1))
        rest = m.group(2).strip()
        if len(rest) >= 12:
            keys.add(rest.lower())
    return keys


def cited_in(answer: str, files):
    if not answer:
        return set()
    text = answer.lower()
    cited = set()
    for f in files:
        for k in name_keys(f):
            if len(k) < 4:
                continue
            if re.fullmatch(r"[\d.]+", k):
                if re.search(r"(?<![\d.])" + re.escape(k) + r"(?![\d.])", text):
                    cited.add(f)
                    break
            elif k in text:
                cited.add(f)
                break
    return cited


def folders_of(all_files):
    """Every folder in the room, "" being the room itself."""
    out = {""}
    for f in all_files:
        parts = f.split("/")[:-1]
        for i in range(1, len(parts) + 1):
            out.add("/".join(parts[:i]))
    return out


def parent(path: str) -> str:
    return path.rsplit("/", 1)[0] if "/" in path else ""


def in_scope(path: str, scope: str) -> bool:
    return scope == "" or path.startswith(scope + "/")


def build_segment(seg, meta):
    all_paths = list(meta)
    known = set(all_paths)
    known_folders = folders_of(all_paths)
    per = {}
    folders = {}

    def rec(path):
        return per.setdefault(path, {"tier": "untouched", "hits": 0, "reads": 0, "ranges": [], "pages": set(),
                                     "full_reads": 0, "total_lines": None, "tools": set(), "agents": set(), "named": False})

    def bump(path, tier):
        d = rec(path)
        if RANK[tier] > RANK[d["tier"]]:
            d["tier"] = tier

    def folder(path):
        return folders.setdefault(path, {"searched": 0, "listed": 0, "patterns": set()})

    for e in seg["events"]:
        t = e.get("type")
        tool = e.get("tool") or e.get("via") or ""
        if t == "listed":
            shown = {parent(f) for f in e.get("files") or [] if f in known}
            if "scope" in e and not e.get("files"):
                shown.add((e.get("scope") or "").rstrip("/"))
            for p in shown & known_folders:
                folder(p)["listed"] += 1
        elif t == "scanned":
            scope = (e.get("scope") or "").rstrip("/")
            if scope in known_folders:  # a search scoped to one file is recorded by its hit, if any
                d = folder(scope)
                d["searched"] += 1
                if e.get("pattern"):
                    d["patterns"].add(str(e["pattern"]))
        elif t == "hit":
            for f in e.get("files") or []:
                if f in known:
                    rec(f)["hits"] += 1; rec(f)["tools"].add(tool); bump(f, "hit")
        elif t == "read":
            f = e.get("file")
            if f not in known:
                continue
            d = rec(f); d["reads"] += 1; d["tools"].add(tool); bump(f, "read")
            if e.get("agent"):
                d["agents"].add(e["agent"])
            if e.get("total_lines"):
                d["total_lines"] = e["total_lines"]
            if e.get("pages") and meta[f].get("pages"):
                d["pages"] |= parse_pages(e["pages"])
            elif e.get("start") is not None and e.get("lines_returned") is not None:
                # Read reports the lines it returned; trust that over offset/limit, since it truncates
                start, n = int(e["start"]), int(e["lines_returned"])
                if n > 0:
                    d["ranges"].append((start, start + n - 1))
            elif e.get("offset") not in (None, "") or e.get("limit") not in (None, ""):
                off = int(e.get("offset") or 1)
                lim = e.get("limit")
                n = e.get("lines_returned") or 0
                end = off + (int(lim) if lim not in (None, "") else max(n, 1)) - 1
                d["ranges"].append((off, end))
            elif e.get("partial"):
                n = e.get("lines_returned") or 0
                d["ranges"].append((1, max(n, 1)))
            else:
                d["full_reads"] += 1

    answer = (seg["answer"] or {}).get("text", "")
    for f in cited_in(answer, all_paths):
        d = rec(f)
        d["named"] = True
        if RANK[d["tier"]] >= RANK["read"]:
            bump(f, "cited")

    files_out = {}
    for f, d in per.items():
        m = meta[f]
        frac = None
        if d["full_reads"]:
            frac = 1.0
        elif d["pages"] and m.get("pages"):
            frac = min(1.0, len(d["pages"]) / m["pages"])
        elif d["ranges"]:
            total = d["total_lines"] or m.get("lines")
            covered = sum(b - a + 1 for a, b in merge_ranges(d["ranges"]))
            frac = min(1.0, covered / total) if total else None
        files_out[f] = {
            "tier": d["tier"], "hits": d["hits"], "reads": d["reads"],
            "read_fraction": None if frac is None else round(frac, 3),
            "read_lines": [list(r) for r in merge_ranges(d["ranges"])] if d["ranges"] else None,
            "total_lines": d["total_lines"],
            "read_pages": sorted(d["pages"]) if d["pages"] else None,
            "tools": sorted(x for x in d["tools"] if x), "agents": sorted(d["agents"]),
            "named": d["named"], "named_unopened": d["named"] and RANK[d["tier"]] < RANK["read"],
        }
    folders_out = {p: {"searched": d["searched"], "listed": d["listed"], "patterns": sorted(d["patterns"])}
                   for p, d in sorted(folders.items())}
    return files_out, folders_out, answer


def search_reach(all_paths, folders_out):
    """Files under a searched folder, and how many of them a text search can read."""
    scopes = [p for p, d in folders_out.items() if d["searched"]]
    under = [f for f in all_paths if any(in_scope(f, s) for s in scopes)]
    return len(under), sum(1 for f in under if Path(f).suffix.lower() not in BINARY_EXT)


def parse_merge(specs, n):
    groups = []
    for spec in specs:
        nums = set()
        for part in spec.split(","):
            part = part.strip()
            if "-" in part:
                lo, hi = part.split("-", 1)
                nums.update(range(int(lo), int(hi) + 1))
            elif part:
                nums.add(int(part))
        groups.append(sorted(x for x in nums if 1 <= x <= n))
    return groups


def merge_segments(kept, groups):
    """Fold follow-up turns into one question (numbers as the unmerged map shows them)."""
    merged, used = [], set()
    for i, seg in enumerate(kept, 1):
        if i in used:
            continue
        g = next((g for g in groups if i in g), None)
        if g and g[0] == i:
            parts = [kept[n - 1] for n in g]
            used.update(g)
            merged.append({
                "prompt": {"t": (parts[0]["prompt"] or {}).get("t"),
                           "text": " / ".join((x["prompt"] or {}).get("text", "").strip() for x in parts)},
                "events": [e for x in parts for e in x["events"]],
                "answer": {"text": "\n\n".join((x["answer"] or {}).get("text", "") for x in parts if x["answer"])},
                "merged_from": [f"q{n}" for n in g],
            })
        elif g:
            used.add(i)
        else:
            merged.append(seg)
    return merged


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("room", help="room id or store folder")
    ap.add_argument("-o", "--out", default="coverage.json")
    ap.add_argument("--expect-file", help='JSON {"q1": [globs], "*": [globs]}')
    ap.add_argument("--session", help="keep only events from this session id")
    ap.add_argument("--since", help="keep only events at or after this ISO timestamp")
    ap.add_argument("--keep-empty", action="store_true", help="keep prompts that touched no file in the room")
    ap.add_argument("--merge", action="append", default=[], help="fold turns into one question, e.g. --merge 2-3 or --merge 5,6 (numbers as the unmerged map shows them; repeatable)")
    a = ap.parse_args()

    store = find_store(a.room)
    room = json.loads((store / "room.json").read_text())
    events = load_ledger(store)
    if a.session:
        events = [e for e in events if e.get("session") == a.session]
    if a.since:
        events = [e for e in events if (e.get("t") or "") >= a.since]
    meta = {f["path"]: f for f in room["files"]}
    all_paths = list(meta)

    expect_map = {}
    if a.expect_file:
        expect_map = json.loads(Path(a.expect_file).read_text())

    # drop prompts that touched nothing in the room, so numbering matches what the map shows
    kept, skipped = [], 0
    for seg in segment(events):
        files_out, folders_out, _ = build_segment(seg, meta)
        if not files_out and not folders_out and not a.keep_empty:
            skipped += 1
            continue
        kept.append(seg)
    if a.merge:
        kept = merge_segments(kept, parse_merge(a.merge, len(kept)))

    questions = []
    for seg in kept:
        files_out, folders_out, answer = build_segment(seg, meta)
        qid = f"q{len(questions) + 1}"
        globs = list(expect_map.get("*", [])) + list(expect_map.get(qid, []))
        expected = sorted({p for p in all_paths for g in globs if fnmatch.fnmatch(p, g) or fnmatch.fnmatch(p, g.rstrip("/") + "/*")})
        prompt = (seg["prompt"] or {}).get("text", "(events before the first prompt)")
        sessions = {e.get("session") for e in seg["events"] if e.get("session")}
        reach, reach_text = search_reach(all_paths, folders_out)
        questions.append({
            "id": qid, "question": prompt.strip()[:2000], "answer": answer, "merged_from": seg.get("merged_from"),
            "asked_at": (seg["prompt"] or {}).get("t"), "session": (seg["prompt"] or {}).get("session") or next(iter(sessions), None),
            "files": files_out, "folders": folders_out, "expected": expected, "excerpts": [],
            "summary": {
                "files_total": len(all_paths),
                "files_in_searched_folders": reach,
                "files_in_searched_folders_text": reach_text,
                "folders_searched": sum(1 for d in folders_out.values() if d["searched"]),
                "folders_listed": sum(1 for d in folders_out.values() if d["listed"]),
                "files_hit": sum(1 for d in files_out.values() if RANK[d["tier"]] >= RANK["hit"]),
                "files_read": sum(1 for d in files_out.values() if RANK[d["tier"]] >= RANK["read"]),
                "files_cited": sum(1 for d in files_out.values() if d["tier"] == "cited"),
                "files_named_unopened": sum(1 for d in files_out.values() if d["named_unopened"]),
                "events": len(seg["events"]),
            },
        })

    cum = {}
    for p in all_paths:
        c = {"tier": "untouched", "q_hit": 0, "q_read": 0, "q_cited": 0, "q_named_unopened": 0, "reads": 0, "max_read_fraction": None}
        for q in questions:
            d = q["files"].get(p)
            if not d:
                continue
            r = RANK[d["tier"]]
            if r > RANK[c["tier"]]:
                c["tier"] = d["tier"]
            if r >= RANK["hit"]: c["q_hit"] += 1
            if r >= RANK["read"]: c["q_read"] += 1
            if r >= RANK["cited"]: c["q_cited"] += 1
            if d.get("named_unopened"): c["q_named_unopened"] += 1
            c["reads"] += d["reads"]
            if d["read_fraction"] is not None:
                c["max_read_fraction"] = max(c["max_read_fraction"] or 0, d["read_fraction"])
        cum[p] = c
    cum_folders = {}
    for q in questions:
        for p, d in q["folders"].items():
            c = cum_folders.setdefault(p, {"q_searched": 0, "q_listed": 0})
            c["q_searched"] += 1 if d["searched"] else 0
            c["q_listed"] += 1 if d["listed"] else 0
    ever_searched = [p for p, c in cum_folders.items() if c["q_searched"]]

    out = {
        "generated_at": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "vdr_root": room["id"],
        "folder": room["root"],
        "mode": "passive",
        "tiers": TIERS,
        "pipeline": {"collector": "claude-code hooks (track.py)", "events": len(events), "questions": len(questions), "skipped_empty_prompts": skipped},
        "files": [{"path": f["path"], "size": f["size"], "indexed": True, "chunks": f.get("lines") or f.get("pages") or 0,
                   "lines": f.get("lines"), "pages": f.get("pages")} for f in room["files"]],
        "questions": questions,
        "cumulative": {
            "files": cum,
            "folders": dict(sorted(cum_folders.items())),
            "summary": {
                "questions": len(questions),
                "files_total": len(all_paths),
                "ever_in_searched_folders": sum(1 for f in all_paths if any(in_scope(f, s) for s in ever_searched)),
                "ever_hit": sum(1 for c in cum.values() if RANK[c["tier"]] >= RANK["hit"]),
                "ever_read": sum(1 for c in cum.values() if RANK[c["tier"]] >= RANK["read"]),
                "ever_cited": sum(1 for c in cum.values() if RANK[c["tier"]] >= RANK["cited"]),
                "never_touched": sum(1 for c in cum.values() if c["tier"] == "untouched"),
            },
        },
    }
    outp = Path(a.out)
    outp.parent.mkdir(parents=True, exist_ok=True)
    outp.write_text(json.dumps(out, indent=1))
    s = out["cumulative"]["summary"]
    print(f"wrote {outp}: {len(questions)} question(s) from {len(events)} events"
          + (f" ({skipped} prompt(s) touched nothing in the room and were dropped)" if skipped else ""))
    print(f"cumulative: {s['files_total']} files · in a searched folder {s['ever_in_searched_folders']} · ever matched {s['ever_hit']} · "
          f"ever opened {s['ever_read']} · ever named {s['ever_cited']} · never matched or opened {s['never_touched']}")


if __name__ == "__main__":
    main()
