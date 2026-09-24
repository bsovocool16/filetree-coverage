#!/usr/bin/env python3
"""
render_viewer.py — embed a coverage.json into the viewer template and write a
self-contained coverage.html (no network, no build step).

    python3 render_viewer.py coverage.json -o coverage.html
    python3 render_viewer.py coverage.json -o coverage.html --standalone   # adds <html>/<head>/<body> for opening as a local file

Without --standalone the output is the bare page body the Claude Artifact tool
expects (it wraps the skeleton itself). Browsers open the bare form too; the
--standalone form only adds the viewport meta and a document skeleton.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
TEMPLATE = HERE.parent / "assets" / "viewer_template.html"
PLACEHOLDER = "__COVERAGE_JSON__"


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("coverage")
    ap.add_argument("-o", "--out", default="coverage.html")
    ap.add_argument("--template", default=str(TEMPLATE))
    ap.add_argument("--standalone", action="store_true")
    ap.add_argument("--summary", action="store_true", help="also print the per-question summary and gap list")
    a = ap.parse_args()

    data = json.loads(Path(a.coverage).read_text())
    if not isinstance(data.get("files"), list) or not data.get("questions"):
        raise SystemExit("coverage.json needs 'files' and at least one question — run build_coverage.py first")
    for q in data["questions"]:
        for e in q.get("excerpts", []):
            e.pop("text", None)
    payload = json.dumps(data, separators=(",", ":")).replace("</", "<\\/")
    tpl = Path(a.template).read_text()
    if PLACEHOLDER not in tpl:
        raise SystemExit(f"template has no {PLACEHOLDER} marker: {a.template}")
    page = tpl.replace(PLACEHOLDER, payload)
    if a.standalone:
        page = ('<!doctype html><html><head><meta charset="utf-8">'
                '<meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover"></head>'
                '<body style="margin:0">' + page + '</body></html>')
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(page)
    print(f"wrote {out} ({out.stat().st_size // 1024} KB)")

    if a.summary:
        passive = data.get("mode") == "passive"
        read_tiers = {"read", "cited"} if passive else {"in_context", "cited"}
        unindexed = [f["path"] for f in data["files"] if not f.get("indexed", True)]
        for q in data["questions"]:
            s = q["summary"]
            print(f"\n{q['id']}: {q['question'][:160]}")
            if passive:
                print(f"  files {s['files_total']} · in a searched folder {s['files_in_searched_folders']}"
                      f" ({s['files_in_searched_folders_text']} text-searchable) · matched {s['files_hit']} · "
                      f"opened {s['files_read']} · named in answer {s['files_cited']}"
                      + (f" · named but never opened {s['files_named_unopened']}" if s.get("files_named_unopened") else ""))
                partial = [(p, d) for p, d in q["files"].items() if d.get("read_fraction") not in (None, 1, 1.0) and d["tier"] in read_tiers]
                for p, d in sorted(partial, key=lambda x: x[1]["read_fraction"]):
                    print(f"    opened in part: {p}  [{int(d['read_fraction'] * 100)}%]")
                for p, d in q["files"].items():
                    if d.get("named_unopened"):
                        print(f"    named, never opened: {p}")
            else:
                print(f"  files {s['files_total']} ({s.get('files_indexed', s['files_total'])} indexable) · retrieved {s.get('files_retrieved', 0)} · "
                      f"read {s.get('files_in_context', 0)} · cited {s['files_cited']}")
            exp = q.get("expected") or []
            if exp:
                tier = lambda p: (q["files"].get(p) or {}).get("tier", "unindexed" if p in unindexed else "untouched")
                gaps = [p for p in exp if tier(p) not in read_tiers]
                print(f"  expected {len(exp)} · opened {len(exp) - len(gaps)} · missed {len(gaps)}")
                for p in gaps:
                    print(f"    - {p}  [{tier(p)}]")
        if data.get("cumulative"):
            c = data["cumulative"]["summary"]
            print(f"\nall {c['questions']} questions: {c['files_total']} files · ever opened {c['ever_read']} · ever named {c['ever_cited']} · never matched or opened {c['never_touched']}")
            never = [p for p, d in data["cumulative"]["files"].items() if d["tier"] not in read_tiers]
            print(f"  never opened by any question: {len(never)}")
        if unindexed:
            print(f"\nnot indexable ({len(unindexed)}):")
            for p in unindexed:
                print(f"  - {p}")


if __name__ == "__main__":
    main()
