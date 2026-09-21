#!/usr/bin/env python3
"""
room.py — map a folder so the recorder tracks it, and manage mapped rooms.

    room.py map <folder> [--id <slug>]     index the folder, register it, start a ledger (keeps an existing one)
    room.py list                            mapped rooms, with event counts
    room.py reset <id>                      empty a room's ledger (the index is kept)
    room.py unmap <id>                      stop tracking; the store folder is left in place
    room.py refresh <id>                    re-index the folder (files added or removed since mapping)

The index (room.json) lists every file with its size, and its line count for
text files or page count for PDFs when a PDF library is installed, so the
viewer can say how much of a file was read. Nothing else is extracted; the
documents are not copied.
"""
import argparse
import json
import os
import re
import sys
import time
from pathlib import Path

HOME = Path(os.environ.get("FILETREE_COVERAGE_HOME") or Path.home() / ".claude" / "plugins" / "config" / "filetree-coverage")
REGISTRY = HOME / "rooms.json"
SKIP = {".DS_Store", "Thumbs.db"}
TEXT_EXT = {".txt", ".md", ".markdown", ".csv", ".tsv", ".json", ".rtf", ".log", ".html", ".htm", ".xml"}


def load_registry():
    try:
        return json.loads(REGISTRY.read_text())
    except Exception:
        return {"rooms": []}


def save_registry(d):
    HOME.mkdir(parents=True, exist_ok=True)
    REGISTRY.write_text(json.dumps(d, indent=1))


def slugify(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower()
    return s or "room"


def count_lines(p: Path) -> int | None:
    try:
        n = 0
        with open(p, "rb") as f:
            for chunk in iter(lambda: f.read(1 << 20), b""):
                n += chunk.count(b"\n")
        return n + 1
    except Exception:
        return None


def count_pages(p: Path) -> int | None:
    try:
        from pypdf import PdfReader  # type: ignore
        return len(PdfReader(str(p)).pages)
    except Exception:
        pass
    try:
        import pdfplumber  # type: ignore
        with pdfplumber.open(str(p)) as pdf:
            return len(pdf.pages)
    except Exception:
        return None


def index_folder(root: Path):
    files = []
    for p in sorted(root.rglob("*")):
        if not p.is_file() or p.name in SKIP or any(part.startswith(".") for part in p.relative_to(root).parts):
            continue
        rel = p.relative_to(root).as_posix()
        ext = p.suffix.lower()
        rec = {"path": rel, "size": p.stat().st_size, "ext": ext}
        if ext in TEXT_EXT:
            rec["lines"] = count_lines(p)
        elif ext == ".pdf":
            rec["pages"] = count_pages(p)
        files.append(rec)
    return files


def cmd_map(a):
    root = Path(a.folder).expanduser().resolve()
    if not root.is_dir():
        sys.exit(f"not a directory: {root}")
    reg = load_registry()
    existing = next((r for r in reg["rooms"] if Path(r["root"]) == root), None)
    rid = a.id or (existing["id"] if existing else slugify(root.name))
    if not existing and any(r["id"] == rid for r in reg["rooms"]):
        rid = f"{rid}-{int(time.time()) % 10000}"
    store = HOME / "rooms" / rid
    store.mkdir(parents=True, exist_ok=True)
    files = index_folder(root)
    room = {"id": rid, "root": str(root), "mapped_at": time.strftime("%Y-%m-%dT%H:%M:%S"), "files": files}
    (store / "room.json").write_text(json.dumps(room, indent=1))
    (store / "ledger.jsonl").touch()
    rec = {"id": rid, "root": str(root), "store": str(store), "mapped_at": room["mapped_at"]}
    reg["rooms"] = [r for r in reg["rooms"] if r["id"] != rid] + [rec]
    save_registry(reg)
    n_pdf = sum(1 for f in files if f["ext"] == ".pdf")
    n_nopages = sum(1 for f in files if f["ext"] == ".pdf" and f.get("pages") is None)
    print(f"mapped {rid}: {len(files)} files under {root}")
    print(f"store: {store}")
    if n_pdf and n_nopages == n_pdf:
        print("note: no PDF library installed, so page counts are unknown; reads of PDFs will show as whole-file reads")
    ev = sum(1 for _ in open(store / "ledger.jsonl"))
    if ev:
        print(f"ledger already has {ev} events (use `room.py reset {rid}` to start clean)")


def cmd_list(a):
    reg = load_registry()
    if not reg["rooms"]:
        print("no rooms mapped")
        return
    for r in reg["rooms"]:
        store = Path(r["store"])
        try:
            n = sum(1 for _ in open(store / "ledger.jsonl"))
            files = len(json.loads((store / "room.json").read_text())["files"])
        except Exception:
            n, files = 0, "?"
        print(f"{r['id']}\t{files} files\t{n} events\t{r['root']}")


def _find(reg, rid):
    r = next((r for r in reg["rooms"] if r["id"] == rid), None)
    if not r:
        sys.exit(f"no room {rid}; mapped: {[x['id'] for x in reg['rooms']] or 'none'}")
    return r


def cmd_reset(a):
    r = _find(load_registry(), a.id)
    (Path(r["store"]) / "ledger.jsonl").write_text("")
    print(f"ledger emptied for {a.id}")


def cmd_unmap(a):
    reg = load_registry()
    _find(reg, a.id)
    reg["rooms"] = [r for r in reg["rooms"] if r["id"] != a.id]
    save_registry(reg)
    print(f"unmapped {a.id}; store left at {HOME / 'rooms' / a.id}")


def cmd_refresh(a):
    reg = load_registry()
    r = _find(reg, a.id)
    root = Path(r["root"])
    store = Path(r["store"])
    room = json.loads((store / "room.json").read_text())
    room["files"] = index_folder(root)
    room["refreshed_at"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    (store / "room.json").write_text(json.dumps(room, indent=1))
    print(f"re-indexed {a.id}: {len(room['files'])} files")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    m = sub.add_parser("map"); m.add_argument("folder"); m.add_argument("--id"); m.set_defaults(func=cmd_map)
    sub.add_parser("list").set_defaults(func=cmd_list)
    x = sub.add_parser("reset"); x.add_argument("id"); x.set_defaults(func=cmd_reset)
    u = sub.add_parser("unmap"); u.add_argument("id"); u.set_defaults(func=cmd_unmap)
    f = sub.add_parser("refresh"); f.add_argument("id"); f.set_defaults(func=cmd_refresh)
    a = ap.parse_args()
    a.func(a)


if __name__ == "__main__":
    main()
