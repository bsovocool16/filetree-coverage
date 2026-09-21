#!/usr/bin/env python3
"""
build_coverage.py — turn a room's ledger into coverage.json for the viewer.

    build_coverage.py <room id or store folder> -o coverage.json [--expect-file expected.json] [--session <id>] [--since <ISO time>]

Each user prompt starts a question segment; the tool events until the next
prompt belong to it; the Stop event's text is its answer. Per file per
segment the tier is the furthest of:

    untouched   nothing in the segment reached it
    listed      it appeared in a directory listing or a glob, or a search ran over its folder without matching it
    hit         a search matched it (Grep, grep, rg)
    read        it was opened (Read, cat, head, sed -n, pdftotext, ...); the fraction of lines or pages is recorded
    cited       its name appears in the answer

`cumulative` holds the same per file across all segments: max tier, how many
segments listed / hit / read / cited it, and the largest fraction read.
"""
import argparse
import fnmatch
import json
import re
import sys
from collections import defaultdict
from pathlib import Path

HOME_DEFAULT = Path.home() / ".claude" / "plugins" / "config" / "filetree-coverage"
RANK = {"untouched": 0, "listed": 1, "hit": 2, "read": 3, "cited": 4}
TIERS = [
    {"id": "untouched", "label": "Not touched"},
    {"id": "listed", "label": "Listed or searched, no hit"},
    {"id": "hit", "label": "Matched a search"},
    {"id": "read", "label": "Opened"},
    {"id": "cited", "label": "Named in the answer"},
]


def find_store(arg: str) -> Path:
    p = Path(arg).expanduser()
    if p.is_dir() and (p / "room.json").exists():
        return p
    import os
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
    """Group events into question segments on prompt boundaries."""
    segs = []
    cur = None
    for e in events:
        if e.get("type") == "prompt":
            cur = {"prompt": e, "events": [], "answer": None}
            segs.append(cur)
            continue
        if cur is None:
            cur = {"prompt": None, "events": [], "answer": None}
            segs.append(cur)
        if e.get("type") == "answer":
            cur["answer"] = e
        elif e.get("type") == "subanswer":
            cur["events"].append(e)
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


NAME_STOP = {"agreement", "the", "and", "of", "inc", "llc", "corp", "co", "ltd", "letter", "schedule", "policy", "report", "plan"}


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


def files_in_scope(all_files, scope: str):
    if scope in ("", "."):
        return list(all_files)
    pre = scope.rstrip("/") + "/"
    return [f for f in all_files if f.startswith(pre) or f == scope]


def build_segment(seg, room_files, meta):
    all_paths = [f["path"] for f in room_files]
    per = {}

    def rec(path):
        return per.setdefault(path, {"tier": "listed", "listed": 0, "hits": 0, "reads": 0, "ranges": [], "pages": set(),
                                     "full_reads": 0, "tools": set(), "agents": set(), "named": False})

    def bump(path, tier):
        d = rec(path)
        if RANK[tier] > RANK[d["tier"]]:
            d["tier"] = tier

    known = set(all_paths)
    for e in seg["events"]:
        t = e.get("type")
        if e.get("files"):
            e = {**e, "files": [f for f in e["files"] if f in known]}
        if e.get("file") and e["file"] not in known:
            continue
        tool = e.get("tool") or e.get("via") or ""
        agent = e.get("agent")
        if t == "listed":
            for f in e.get("files") or []:
                rec(f)["listed"] += 1; rec(f)["tools"].add(tool); bump(f, "listed")
            if "scope" in e and not e.get("files"):
                for f in files_in_scope(all_paths, e["scope"]):
                    rec(f)["listed"] += 1; bump(f, "listed")
        elif t == "scanned":
            for f in files_in_scope(all_paths, e.get("scope", "")):
                if meta[f]["ext"] in (".pdf", ".docx", ".xlsx", ".pptx", ".zip", ".png", ".jpg", ".tif", ".tiff"):
                    continue  # a text search does not look inside binaries
                rec(f)["listed"] += 1; bump(f, "listed")
        elif t == "hit":
            for f in e.get("files") or []:
                rec(f)["hits"] += 1; rec(f)["tools"].add(tool); bump(f, "hit")
        elif t == "read":
            f = e.get("file")
            if not f:
                continue
            d = rec(f); d["reads"] += 1; d["tools"].add(tool); bump(f, "read")
            if agent:
                d["agents"].add(agent)
            m = meta.get(f, {})
            if e.get("pages") and m.get("pages"):
                d["pages"] |= parse_pages(e["pages"])
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
        m = meta.get(f, {})
        frac = None
        if d["full_reads"]:
            frac = 1.0
        elif d["pages"] and m.get("pages"):
            frac = min(1.0, len(d["pages"]) / m["pages"])
        elif d["ranges"]:
            total = m.get("lines")
            covered = sum(b - a + 1 for a, b in merge_ranges(d["ranges"]))
            frac = min(1.0, covered / total) if total else None
        files_out[f] = {
            "tier": d["tier"], "listed": d["listed"], "hits": d["hits"], "reads": d["reads"],
            "read_fraction": None if frac is None else round(frac, 3),
            "read_lines": [list(r) for r in merge_ranges(d["ranges"])] if d["ranges"] else None,
            "read_pages": sorted(d["pages"]) if d["pages"] else None,
            "tools": sorted(x for x in d["tools"] if x), "agents": sorted(d["agents"]),
            "named": d["named"], "named_unopened": d["named"] and RANK[d["tier"]] < RANK["read"],
        }
    return files_out, answer


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

    segs = segment(events)
    # drop prompts that touched nothing in the room, so numbering matches what the map shows
    kept, skipped = [], 0
    for seg in segs:
        files_out, _ = build_segment(seg, room["files"], meta)
        if not files_out and not a.keep_empty:
            skipped += 1
            continue
        kept.append(seg)
    # --merge 2-3 / --merge 5,6 : fold follow-up turns into one question (numbers as the unmerged map shows them)
    if a.merge:
        groups = []
        for spec in a.merge:
            nums = set()
            for part in spec.split(","):
                part = part.strip()
                if "-" in part:
                    lo, hi = part.split("-", 1)
                    nums.update(range(int(lo), int(hi) + 1))
                elif part:
                    nums.add(int(part))
            groups.append(sorted(n for n in nums if 1 <= n <= len(kept)))
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
        kept = merged
    questions = []
    for seg in kept:
        files_out, answer = build_segment(seg, room["files"], meta)
        qi = len(questions) + 1
        qid = f"q{qi}"
        globs = list(expect_map.get("*", [])) + list(expect_map.get(qid, []))
        expected = sorted({p for p in all_paths for g in globs if fnmatch.fnmatch(p, g) or fnmatch.fnmatch(p, g.rstrip("/") + "/*")})
        prompt = (seg["prompt"] or {}).get("text", "(events before the first prompt)")
        sessions = {e.get("session") for e in seg["events"] if e.get("session")}
        questions.append({
            "id": qid, "question": prompt.strip()[:2000], "answer": answer, "merged_from": seg.get("merged_from"),
            "asked_at": (seg["prompt"] or {}).get("t"), "session": next(iter(sessions), None),
            "files": files_out, "expected": expected, "excerpts": [],
            "summary": {
                "files_total": len(all_paths),
                "files_listed": sum(1 for d in files_out.values() if RANK[d["tier"]] >= 1),
                "files_hit": sum(1 for d in files_out.values() if RANK[d["tier"]] >= 2),
                "files_read": sum(1 for d in files_out.values() if RANK[d["tier"]] >= 3),
                "files_cited": sum(1 for d in files_out.values() if d["tier"] == "cited"),
                "files_named_unopened": sum(1 for d in files_out.values() if d["named_unopened"]),
                "events": len(seg["events"]),
            },
        })

    # cumulative
    cum = {}
    for p in all_paths:
        c = {"tier": "untouched", "q_listed": 0, "q_hit": 0, "q_read": 0, "q_cited": 0, "q_named_unopened": 0, "reads": 0, "max_read_fraction": None}
        for q in questions:
            d = q["files"].get(p)
            if not d:
                continue
            r = RANK[d["tier"]]
            if r > RANK[c["tier"]]:
                c["tier"] = d["tier"]
            if r >= 1: c["q_listed"] += 1
            if r >= 2: c["q_hit"] += 1
            if r >= 3: c["q_read"] += 1
            if r >= 4: c["q_cited"] += 1
            if d.get("named_unopened"): c["q_named_unopened"] += 1
            c["reads"] += d["reads"]
            if d["read_fraction"] is not None:
                c["max_read_fraction"] = max(c["max_read_fraction"] or 0, d["read_fraction"])
        cum[p] = c

    out = {
        "generated_at": __import__("time").strftime("%Y-%m-%dT%H:%M:%S"),
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
            "summary": {
                "questions": len(questions),
                "files_total": len(all_paths),
                "ever_listed": sum(1 for c in cum.values() if RANK[c["tier"]] >= 1),
                "ever_hit": sum(1 for c in cum.values() if RANK[c["tier"]] >= 2),
                "ever_read": sum(1 for c in cum.values() if RANK[c["tier"]] >= 3),
                "ever_cited": sum(1 for c in cum.values() if RANK[c["tier"]] >= 4),
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
    print(f"cumulative: {s['files_total']} files · ever listed {s['ever_listed']} · ever hit {s['ever_hit']} · "
          f"ever opened {s['ever_read']} · ever cited {s['ever_cited']} · never touched {s['never_touched']}")


if __name__ == "__main__":
    main()
