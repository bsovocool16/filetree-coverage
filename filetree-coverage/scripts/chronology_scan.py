#!/usr/bin/env python3
"""
chronology_scan.py — first pass over a folder of corporate and financing
documents: which instrument each file is, which family it belongs to (charter,
bylaws, IRA, ROFR/co-sale, voting, stock plan, SPA, SAFE/note, side letter,
consent...), whether it is an original, an amendment or a restatement, its
date, whether it is executed or a draft, what prior agreement it names, and
whether its text says it supersedes that prior agreement. Then, per governing
family, the lineage: the chain of restatements, the amendments hanging off
each, what is operative, what is superseded, and what looks missing.

    chronology_scan.py <folder> -o chronology.json [--md chronology.md]

Deterministic and heuristic. It reads titles, recitals, signature blocks and
a few clause patterns; it does not judge. Every uncertain call is written to
`flags` for a reader to resolve, and the skill that uses this script opens the
flagged documents rather than trusting the guess.

Dependencies: standard library; pdfplumber/pypdf/pdftotext for PDFs and
python-docx for .docx when installed.
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
import time
from datetime import date
from pathlib import Path

# ----------------------------------------------------------------------------
# text
# ----------------------------------------------------------------------------

TEXT_EXT = {".txt", ".md", ".markdown", ".rtf", ".html", ".htm"}
SKIP = {".DS_Store", "Thumbs.db"}


def read_text(p: Path) -> str:
    ext = p.suffix.lower()
    try:
        if ext in TEXT_EXT:
            t = p.read_text(errors="replace")
            return re.sub(r"<[^>]+>", " ", t) if ext in (".html", ".htm") else t
        if ext == ".pdf":
            try:
                import pdfplumber  # type: ignore
                with pdfplumber.open(str(p)) as pdf:
                    return "\n\n".join((pg.extract_text() or "") for pg in pdf.pages)
            except Exception:
                pass
            try:
                from pypdf import PdfReader  # type: ignore
                return "\n\n".join((pg.extract_text() or "") for pg in PdfReader(str(p)).pages)
            except Exception:
                pass
            if shutil.which("pdftotext"):
                return subprocess.run(["pdftotext", "-layout", str(p), "-"], capture_output=True, text=True, timeout=120).stdout
            return ""
        if ext == ".docx":
            import docx  # type: ignore
            d = docx.Document(str(p))
            return "\n".join(par.text for par in d.paragraphs)
    except Exception:
        return ""
    return ""


# ----------------------------------------------------------------------------
# classification
# ----------------------------------------------------------------------------

FAMILIES = [  # (id, label, governing?, patterns on title/head)
    ("charter", "Charter", True, r"certificate of incorporation|certificate of amendment|certificate of designation|articles of incorporation|restated certificate|certificate of formation"),
    ("bylaws", "Bylaws", True, r"\bbylaws\b|by-laws"),
    ("ira", "Investors' Rights Agreement", True, r"investors?[’']?\s*rights agreement|\bIRA\b"),
    ("rofr", "ROFR and Co-Sale Agreement", True, r"right of first refusal|co-?sale|\bROFR\b"),
    ("voting", "Voting Agreement", True, r"voting agreement"),
    ("plan", "Equity Plan", True, r"stock plan|equity incentive plan|option plan|incentive plan"),
    ("spa", "Stock Purchase Agreement", False, r"stock purchase agreement|subscription agreement|share purchase agreement"),
    ("safe", "SAFE / Note", False, r"simple agreement for future equity|\bSAFE\b|convertible (promissory )?note|note purchase agreement"),
    ("side", "Side Letter", False, r"side letter"),
    ("mrl", "Management Rights Letter", False, r"management rights"),
    ("consent", "Consent / Resolution", False, r"written consent|resolutions? of|unanimous consent|stockholder consent|board consent|action by"),
    ("waiver", "Waiver", False, r"\bwaiver\b"),
    ("joinder", "Joinder", False, r"\bjoinder\b|adoption agreement"),
    ("termination", "Termination", False, r"termination agreement|agreement to terminate"),
]

ORDINALS = {"amended and restated": 1, "first amended and restated": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10}
ORD_WORDS = {"first": 1, "second": 2, "third": 3, "fourth": 4, "fifth": 5, "sixth": 6, "seventh": 7, "eighth": 8, "ninth": 9, "tenth": 10}
MONTHS = "january|february|march|april|may|june|july|august|september|october|november|december"
DATE_RE = re.compile(rf"\b({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})\b", re.I)
ISO_RE = re.compile(r"\b(20\d{2}|19\d{2})[-._](\d{2})[-._](\d{2})\b")


def title_of(text: str, name: str) -> str:
    for line in text.splitlines()[:12]:
        s = line.strip()
        if len(s) >= 8 and not s.lower().startswith(("draft", "confidential", "execution")):
            return s[:200]
    return re.sub(r"\.[A-Za-z0-9]{1,5}$", "", name)


def classify_family(title: str, head: str, name: str):
    hay = f"{name}\n{title}\n{head[:600]}"
    for fid, label, governing, pat in FAMILIES:
        if re.search(pat, title, re.I) or re.search(pat, name, re.I):
            return fid, label, governing
    for fid, label, governing, pat in FAMILIES:
        if re.search(pat, hay, re.I):
            return fid, label, governing
    return "other", "Other", False


def classify_event(title: str, name: str, family: str):
    t = f"{name} {title}".lower()
    if re.search(r"certificate of amendment", t):
        return "amendment", None
    if re.search(r"certificate of designation", t):
        return "amendment", None
    if re.search(r"joinder|adoption agreement", t):
        return "joinder", None
    if re.search(r"\bwaiver\b", t) and "agreement" not in t.split("waiver")[0][-30:]:
        return "waiver", None
    if re.search(r"termination agreement|agreement to terminate", t):
        return "termination", None
    # "Amendment No. 2 to the Amended and Restated ..." is an amendment; the restatement is what it amends
    m = re.search(r"\bamendment\s+(?:no\.?|number)\s*(\d+)\s+to\b", t)
    if m:
        return "amendment", int(m.group(1))
    m = re.search(r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+amendment\s+to\b", t)
    if m:
        return "amendment", ORD_WORDS[m.group(1)]
    if re.search(r"^\W*(?:\d[\d.]*\s+)?amendment\s+to\b", t) or re.search(r"\bamendment\s+to\s+(?:the\s+)?(?:\w+\s+)?amended and restated", t):
        return "amendment", None
    m = re.search(r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)?\s*amended\s+and\s+restated\b", t)
    if m:
        return "restated", ORD_WORDS.get((m.group(1) or "").strip(), 1)
    if re.search(r"amended and restated bylaws|restated bylaws", t):
        return "restated", 1
    m = re.search(r"amendment\s+(?:no\.?|number)\s*(\d+)", t)
    if m:
        return "amendment", int(m.group(1))
    m = re.search(r"\b(first|second|third|fourth|fifth|sixth|seventh|eighth|ninth|tenth)\s+amendment\b", t)
    if m:
        return "amendment", ORD_WORDS[m.group(1)]
    if re.search(r"\bamendment\b", t) and "amended and restated" not in t:
        return "amendment", None
    if family == "consent":
        return "consent", None
    return "original", None


def _recital_context(head: str, pos: int) -> bool:
    """True when a date sits inside a reference to another instrument ("that certain ... dated as of")."""
    before = head[max(0, pos - 160):pos].lower()
    return bool(re.search(r"that certain|prior agreement|as amended by|thereto", before))


def find_date(text: str, name: str):
    head = text[:4000]
    if re.search(r"as of\s+\[\s*[●•_]*\s*\]", head):
        m = ISO_RE.search(name)
        return (f"{m.group(1)}-{m.group(2)}-{m.group(3)}" if m else None), "filename (the text has a placeholder date)"
    for pat, src in ((rf"\bis\s+(?:made|entered into|dated)(?:\s+and\s+entered\s+into)?\s+as\s+of\s+({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})", "is made as of"),
                     (rf"this\s+[^.]{{0,160}}?\bdated\s+as\s+of\s+({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})", "this ... dated as of"),
                     (rf"(?:dated|made|entered into)\s+(?:and entered into\s+)?as of\s+({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})", "dated as of"),
                     (rf"effective\s+(?:as of\s+|upon filing[^.]{{0,80}}on\s+|on\s+)?({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})", "effective"),
                     (rf"(?:executed|adopted|filed|approved)(?:\s+by[^.]{{0,60}}?)?\s+(?:on\s+)?({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})", "executed/adopted/filed"),
                     (rf"on or about\s+({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})", "on or about"),
                     (rf"as of\s+({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})", "as of")):
        for m in re.finditer(pat, head, re.I):
            if src in ("dated as of", "as of", "first date in text") and _recital_context(head, m.start()):
                continue
            return iso(m.group(1), m.group(2), m.group(3)), src
    # a bare date line near the top (letters: "February 20, 2025.")
    for m in DATE_RE.finditer(head[:600]):
        if not _recital_context(head, m.start()):
            return iso(m.group(1), m.group(2), m.group(3)), "date line at the top"
    m = ISO_RE.search(name)
    if m:
        return f"{m.group(1)}-{m.group(2)}-{m.group(3)}", "filename"
    for m in DATE_RE.finditer(head):
        if not _recital_context(head, m.start()):
            return iso(m.group(1), m.group(2), m.group(3)), "first date in text"
    return None, None


def iso(month, day, year):
    mi = [x for x in MONTHS.split("|")].index(month.lower()) + 1
    return f"{int(year):04d}-{mi:02d}-{int(day):02d}"


def execution_status(text: str, name: str):
    head, tail = text[:800].lower(), text[-3000:]
    if "draft" in name.lower() or re.search(r"\bdraft\b", head) or "for discussion purposes" in head:
        return "draft"
    if re.search(r"\[\s*[●•_]+\s*\]|\[\s*(name|date|title)\s*\]", text[:4000] + tail, re.I):
        return "draft"
    if re.search(r"/s/|/S/|DocuSigned|Signed by:", tail):
        return "executed"
    if re.search(r"By:\s*_{4,}", tail):
        return "unsigned"
    if re.search(r"Filed with the Secretary of State|effective upon filing", text, re.I):
        return "executed"
    return "unknown"


def prior_refs(text: str):
    """Documents the recitals point at: 'that certain X dated as of DATE'."""
    out = []
    for m in re.finditer(rf"that certain\s+([A-Z][^,.;()]{{3,120}}?)\s+(?:dated|made|entered into)\s+as of\s+({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})", text[:8000], re.I):
        out.append({"name": m.group(1).strip(), "date": iso(m.group(2), m.group(3), m.group(4))})
    for m in re.finditer(rf"as amended by\s+([A-Z][^,.;()]{{3,100}}?)\s+(?:thereto\s+)?(?:dated|made)\s+as of\s+({MONTHS})\s+(\d{{1,2}}),?\s+(\d{{4}})", text[:8000], re.I):
        out.append({"name": m.group(1).strip(), "date": iso(m.group(2), m.group(3), m.group(4)), "as_amendment": True})
    return out


def supersession(text: str):
    t = text[:12000].lower()
    sup = bool(re.search(r"(amend(s|ed)?(,)? (and )?restate(s|d)?[^.]{0,120}in (its|their) entirety|supersede[s]?[^.]{0,80}prior|restated in (its|their) entirety|amends, restates and supersedes|restates?,? (and )?integrates?|restated certificate[^.]{0,80}(sections? 242 and 245|section 245))", t))
    cont = bool(re.search(r"except as (expressly |otherwise )?(amended|modified|set forth)[^.]{0,160}(remain|continue)[^.]{0,40}in full force", t))
    return sup, cont


def sections_amended(text: str):
    return sorted(set(re.findall(r"(?:Section|Article)\s+([A-Z]{0,6}\d*(?:\.\d+)*(?:\([a-z]\))?)\s+(?:of the [^.]{0,60}?,?\s*(?:as amended,?\s*)?)?(?:is|are|shall be)\s+(?:hereby\s+|further\s+)?(?:amended|deleted|replaced|restated|supplemented)", text[:20000], re.I)))


def _series_key(label: str):
    if label == "Seed":
        return (0, 0)
    m = re.match(r"Series ([A-Z])(?:-(\d))?", label)
    return (ord(m.group(1)) - 64, int(m.group(2) or 0)) if m else (99, 0)


def round_of(text: str, name: str, title: str = ""):
    def found(hay):
        out = set()
        for m in re.finditer(r"series\s+(seed|[A-Z](?:-\d)?)\b", hay, re.I):
            g = m.group(1)
            out.add("Seed" if g.lower() == "seed" else "Series " + g.upper())
        if re.search(r"\bseed\b", hay, re.I):
            out.add("Seed")
        return out
    in_title = found(f"{name} {title}")
    if in_title:
        return max(in_title, key=_series_key)
    in_text = found(text[:3000])
    return max(in_text, key=_series_key) if in_text else None


# ----------------------------------------------------------------------------
# lineage
# ----------------------------------------------------------------------------

def lineage(docs, family):
    fam = [d for d in docs if d["family"] == family]
    flags = []
    live = [d for d in fam if d["status"] in ("executed", "unknown")]
    drafts = [d for d in fam if d["status"] in ("draft", "unsigned")]
    bases = sorted([d for d in live if d["event"] in ("original", "restated")], key=lambda d: (d["date"] or "9999", d["ordinal"] or 0))
    amends = sorted([d for d in live if d["event"] in ("amendment", "waiver", "joinder")], key=lambda d: d["date"] or "9999")

    # ordinal / date consistency and gaps
    ords = [d["ordinal"] for d in bases if d["event"] == "restated"]
    if ords:
        expected = list(range(1, max(ords) + 1))
        missing = [o for o in expected if o not in ords]
        if missing:
            flags.append(f"restatement ordinal(s) {missing} not in the folder (have {sorted(ords)}); an earlier restatement may be missing or filed elsewhere")
        if not any(d["event"] == "original" for d in bases):
            flags.append("no original instrument found before the restatements")
    for a, b in zip(bases, bases[1:]):
        if a["event"] == "restated" and b["event"] == "restated" and (a["ordinal"] or 0) > (b["ordinal"] or 0):
            flags.append(f"ordinal order conflicts with date order: {a['file']} ({a['date']}) vs {b['file']} ({b['date']})")
    for d in fam:
        if not d["date"]:
            flags.append(f"no date found: {d['file']} (open it)")
        elif d["date_source"] in ("filename", "first date in text"):
            flags.append(f"date taken from the {d['date_source']}: {d['file']} — open it and confirm the instrument's own date")
        if d["status"] == "unknown":
            flags.append(f"no signature block or adoption line found: {d['file']} — confirm it was adopted/executed")

    chain = []
    for i, b in enumerate(bases):
        nxt = bases[i + 1] if i + 1 < len(bases) else None
        mine = [a for a in amends if (a["date"] or "0000") >= (b["date"] or "0000") and (nxt is None or (a["date"] or "9999") < (nxt["date"] or "9999"))]
        chain.append({"base": b["file"], "date": b["date"], "event": b["event"], "ordinal": b["ordinal"], "amendments": [a["file"] for a in mine],
                      "superseded_by": nxt["file"] if nxt else None})
    operative = chain[-1] if chain else None
    superseded = [c["base"] for c in chain[:-1]] + [a for c in chain[:-1] for a in c["amendments"]]

    # prior-agreement references that resolve to nothing in the family
    dates_in_family = {d["date"] for d in fam if d["date"]}
    for d in fam:
        for r in d.get("prior_refs", []):
            if r["date"] not in dates_in_family:
                flags.append(f"{d['file']} refers to a prior instrument dated {r['date']} ({r['name'][:60]}) that is not in the folder")
    for d in bases:
        if d["event"] == "restated" and not d.get("supersedes_language"):
            flags.append(f"restatement without supersession language found in its text: {d['file']} (open it)")
    for a in amends:
        if a["event"] == "amendment" and not a.get("continuity_language") and family != "charter":
            flags.append(f"amendment without 'remains in full force' language found: {a['file']} (open it)")
    for d in drafts:
        flags.append(f"{d['status']}: {d['file']} — excluded from the operative stack")
    return {"chain": chain, "operative": operative, "superseded": superseded, "drafts": [d["file"] for d in drafts], "flags": flags}


# ----------------------------------------------------------------------------
# main
# ----------------------------------------------------------------------------

def scan(root: Path):
    docs = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name in SKIP or any(part.startswith(".") for part in p.relative_to(root).parts):
            continue
        text = read_text(p)
        rel = p.relative_to(root).as_posix()
        title = title_of(text, p.name) if text.strip() else re.sub(r"\.[A-Za-z0-9]{1,5}$", "", p.name)
        fid, flabel, governing = classify_family(title, text[:1500], p.name)
        event, ordinal = classify_event(title, p.name, fid)
        d, dsrc = find_date(text, p.name)
        sup, cont = supersession(text)
        docs.append({
            "file": rel, "title": title, "family": fid, "family_label": flabel, "governing": governing,
            "event": event, "ordinal": ordinal, "date": d, "date_source": dsrc,
            "status": execution_status(text, p.name) if text.strip() else "unreadable",
            "round": round_of(text, p.name, title),
            "prior_refs": prior_refs(text), "supersedes_language": sup if event == "restated" else None, "continuity_language": cont,
            "sections_amended": sections_amended(text) if event == "amendment" else [],
            "text_chars": len(text),
        })
    families = {}
    for fid, label, governing, _ in FAMILIES:
        if governing and any(d["family"] == fid for d in docs):
            families[fid] = {"label": label, **lineage(docs, fid)}
    # folder-vs-round mismatch: a document whose round differs from its folder's round label
    misfiled = []
    for d in docs:
        folder = d["file"].split("/")[0] if "/" in d["file"] else ""
        fy = re.search(r"\((20\d\d)\)|\b(20\d\d)\b", folder)
        if fy and d["date"]:
            folder_year = int(fy.group(1) or fy.group(2))
            if int(d["date"][:4]) > folder_year and d["event"] in ("restated", "original"):
                misfiled.append(f"{d['file']} is dated {d['date']} but sits in a {folder_year} folder")
        fr = re.search(r"series\s+([A-Z])|seed", folder, re.I)
        if fr and d["round"]:
            fr_label = ("Series " + fr.group(1).upper()) if fr.group(1) else "Seed"
            if d["round"] != fr_label and d["family"] != "safe":
                misfiled.append(f"{d['file']} reads as {d['round']} but sits in a {fr_label} folder")
    chron = sorted(docs, key=lambda d: (d["date"] or "9999-99-99", d["file"]))
    return {"folder": str(root), "scanned_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "documents": docs, "families": families,
            "chronology": [{"date": d["date"], "file": d["file"], "family": d["family_label"], "event": d["event"], "status": d["status"], "round": d["round"]} for d in chron],
            "misfiled": misfiled}


def markdown(out):
    L = []
    L.append(f"# Chronology scan — {Path(out['folder']).name}")
    L.append(f"{len(out['documents'])} documents, scanned {out['scanned_at'][:16].replace('T', ' ')}. First pass by chronology_scan.py; flags need a reader.")
    L.append("")
    L.append("## Operative stack (executed instruments only)")
    L.append("| Family | Operative | Dated | Amended by | Supersedes |")
    L.append("|---|---|---|---|---|")
    for fid, f in out["families"].items():
        op = f["operative"]
        if not op:
            L.append(f"| {f['label']} | (none executed) | | | |")
            continue
        L.append(f"| {f['label']} | {Path(op['base']).name} | {op['date'] or '?'} | {', '.join(Path(a).name for a in op['amendments']) or '—'} | {', '.join(Path(s).name for s in f['superseded']) or '—'} |")
    L.append("")
    L.append("## Chronology")
    L.append("| Date | Document | Family | Event | Status | Round |")
    L.append("|---|---|---|---|---|---|")
    for c in out["chronology"]:
        dt = (c['date'] or '?') + (" (draft; date not effective)" if c['status'] in ('draft', 'unsigned') else '')
        L.append(f"| {dt} | {c['file']} | {c['family']} | {c['event']} | {c['status']} | {c['round'] or ''} |")
    flags = [(fid, fl) for fid, f in out["families"].items() for fl in f["flags"]] + [("filing", m) for m in out["misfiled"]]
    L.append("")
    L.append(f"## Flags ({len(flags)})")
    for fid, fl in flags:
        L.append(f"- [{fid}] {fl}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("folder")
    ap.add_argument("-o", "--out", default="chronology.json")
    ap.add_argument("--md", help="also write a markdown table")
    a = ap.parse_args()
    root = Path(a.folder).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")
    out = scan(root)
    Path(a.out).parent.mkdir(parents=True, exist_ok=True)
    Path(a.out).write_text(json.dumps(out, indent=1))
    md = markdown(out)
    if a.md:
        Path(a.md).write_text(md)
    print(md)
    print(f"wrote {a.out}" + (f" and {a.md}" if a.md else ""))


if __name__ == "__main__":
    main()
