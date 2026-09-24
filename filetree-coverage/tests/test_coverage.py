"""
End-to-end tests: hook payloads shaped like the ones Claude Code sends go
through track.py into a ledger, and build_coverage.py turns the ledger into
coverage.json. Standard library only; run from the plugin folder with

    python3 -m unittest discover tests
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"

ROOM_FILES = {
    "01 Corporate/1.01 Charter.txt": 10,
    "03 Contracts/3.1 Customers/3.1.01 Supply Agreement - Halvorsen.txt": 40,
    "03 Contracts/3.1 Customers/3.1.02 Amendment (scanned).pdf": None,
    "03 Contracts/3.4 Financing/3.4.01 Credit Agreement.txt": 20,
    "03 Contracts/3.4 Financing/3.4.02 Intercreditor Agreement.txt": 5000,
    "06 Litigation/6.01 Litigation Schedule.txt": 8,
}


class Room:
    """A mapped folder in a throwaway config home, and a way to feed it hook payloads."""

    def __init__(self, tmp: Path):
        self.root = tmp / "room"
        self.home = tmp / "home"
        for rel, n in ROOM_FILES.items():
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            if n is None:
                p.write_bytes(b"%PDF-1.4 not really")
            else:
                p.write_text("".join(f"line {i}\n" for i in range(1, n + 1)))
        self.env = {**os.environ, "FILETREE_COVERAGE_HOME": str(self.home)}
        self.run("room.py", "map", str(self.root), "--id", "t")

    def run(self, script, *args, stdin=None):
        return subprocess.run([sys.executable, str(SCRIPTS / script), *args], input=stdin, env=self.env,
                              capture_output=True, text=True, check=True)

    def hook(self, event, session="s1", **payload):
        payload = {"hook_event_name": event, "session_id": session, "cwd": str(self.root), **payload}
        self.run("track.py", stdin=json.dumps(payload))

    def prompt(self, text, session="s1"):
        self.hook("UserPromptSubmit", session, prompt=text)

    def stop(self, text, session="s1"):
        self.hook("Stop", session, last_assistant_message=text)

    def read(self, rel, session="s1", start=1, n=None, total=None, **inp):
        total = total or ROOM_FILES[rel]
        n = n or total
        p = str(self.root / rel)
        self.hook("PostToolUse", session, tool_name="Read", tool_input={"file_path": p, **inp},
                  tool_response={"type": "text", "file": {"filePath": p, "content": "x\n" * n, "numLines": n,
                                                          "startLine": start, "totalLines": total}})

    def grep(self, scope, pattern, hits, session="s1"):
        self.hook("PostToolUse", session, tool_name="Grep", tool_input={"pattern": pattern, "path": str(self.root / scope)},
                  tool_response={"mode": "files_with_matches", "numFiles": len(hits),
                                 "filenames": [str(self.root / h) for h in hits]})

    def coverage(self):
        out = self.home / "coverage.json"
        self.run("build_coverage.py", "t", "-o", str(out))
        return json.loads(out.read_text())


class CoverageTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.room = Room(Path(self._tmp.name))

    def tearDown(self):
        self._tmp.cleanup()

    def test_interleaved_sessions_stay_apart(self):
        r = self.room
        r.prompt("credit agreement change of control?", "s1")
        r.read("03 Contracts/3.4 Financing/3.4.01 Credit Agreement.txt", "s1")
        r.prompt("unrelated question in another window", "s2")
        r.read("06 Litigation/6.01 Litigation Schedule.txt", "s2")
        r.read("01 Corporate/1.01 Charter.txt", "s1")
        r.stop("See 3.4.01 Credit Agreement, section 7.", "s1")
        r.stop("Nothing pending.", "s2")
        q1, q2 = r.coverage()["questions"]
        self.assertEqual(q1["session"], "s1")
        self.assertEqual(set(q1["files"]), {"03 Contracts/3.4 Financing/3.4.01 Credit Agreement.txt", "01 Corporate/1.01 Charter.txt"})
        self.assertEqual(q1["files"]["03 Contracts/3.4 Financing/3.4.01 Credit Agreement.txt"]["tier"], "cited")
        self.assertIn("Credit Agreement", q1["answer"])
        self.assertEqual(set(q2["files"]), {"06 Litigation/6.01 Litigation Schedule.txt"})
        self.assertEqual(q2["answer"], "Nothing pending.")

    def test_read_share_comes_from_the_lines_the_tool_returned(self):
        r = self.room
        r.prompt("q")
        r.read("03 Contracts/3.1 Customers/3.1.01 Supply Agreement - Halvorsen.txt", start=11, n=10, offset=11)
        f = r.coverage()["questions"][0]["files"]["03 Contracts/3.1 Customers/3.1.01 Supply Agreement - Halvorsen.txt"]
        self.assertEqual(f["read_lines"], [[11, 20]])
        self.assertEqual(f["read_fraction"], 0.25)

    def test_truncated_read_without_limit_is_partial(self):
        r = self.room
        r.prompt("q")
        r.read("03 Contracts/3.4 Financing/3.4.02 Intercreditor Agreement.txt", n=2000)
        f = r.coverage()["questions"][0]["files"]["03 Contracts/3.4 Financing/3.4.02 Intercreditor Agreement.txt"]
        self.assertEqual(f["read_fraction"], 0.4)
        self.assertEqual(f["total_lines"], 5000)

    def test_searches_are_recorded_per_folder_not_per_file(self):
        r = self.room
        r.prompt("q")
        r.grep("", "change of control", ["03 Contracts/3.4 Financing/3.4.01 Credit Agreement.txt"])
        r.grep("03 Contracts", "consent", [])
        r.grep("03 Contracts/3.4 Financing", "Required Lenders", ["03 Contracts/3.4 Financing/3.4.02 Intercreditor Agreement.txt"])
        q = r.coverage()["questions"][0]
        # only files a search matched get a per-file record
        self.assertEqual(set(q["files"]), {"03 Contracts/3.4 Financing/3.4.01 Credit Agreement.txt",
                                           "03 Contracts/3.4 Financing/3.4.02 Intercreditor Agreement.txt"})
        self.assertTrue(all(f["tier"] == "hit" for f in q["files"].values()))
        self.assertEqual({p: d["searched"] for p, d in q["folders"].items()},
                         {"": 1, "03 Contracts": 1, "03 Contracts/3.4 Financing": 1})
        self.assertEqual(q["folders"]["03 Contracts/3.4 Financing"]["patterns"], ["Required Lenders"])
        self.assertEqual(q["summary"]["files_in_searched_folders"], 6)
        self.assertEqual(q["summary"]["files_in_searched_folders_text"], 5)  # the PDF is not text-searchable

    def test_listing_marks_the_folder(self):
        r = self.room
        r.prompt("q")
        r.hook("PostToolUse", tool_name="Bash", tool_input={"command": 'ls "06 Litigation"'},
               tool_response={"stdout": "6.01 Litigation Schedule.txt\n", "stderr": ""})
        q = r.coverage()["questions"][0]
        self.assertEqual(q["files"], {})
        self.assertEqual(q["folders"]["06 Litigation"]["listed"], 1)
        self.assertEqual(q["summary"]["folders_listed"], 1)

    def test_named_but_never_opened(self):
        r = self.room
        r.prompt("q")
        r.stop("The 6.01 Litigation Schedule lists nothing material.")
        f = r.coverage()["questions"][0]["files"]["06 Litigation/6.01 Litigation Schedule.txt"]
        self.assertTrue(f["named_unopened"])
        self.assertEqual(f["tier"], "untouched")

    def test_folder_mapped_through_a_symlink(self):
        """Tool calls may name the folder by the link or by its target; both record, once."""
        r = self.room
        link = Path(self._tmp.name) / "link"
        link.symlink_to(r.root)
        r.run("room.py", "map", str(link), "--id", "t")
        r.prompt("q")
        r.hook("PostToolUse", tool_name="Read", tool_input={"file_path": str(link / "01 Corporate/1.01 Charter.txt")},
               tool_response={"type": "text", "file": {"content": "", "numLines": 10, "startLine": 1, "totalLines": 10}})
        r.read("06 Litigation/6.01 Litigation Schedule.txt")
        ledger = (r.home / "rooms" / "t" / "ledger.jsonl").read_text().splitlines()
        self.assertEqual(sum('"type": "prompt"' in line for line in ledger), 1)
        self.assertEqual(set(r.coverage()["questions"][0]["files"]),
                         {"01 Corporate/1.01 Charter.txt", "06 Litigation/6.01 Litigation Schedule.txt"})

    def test_older_read_events_still_count(self):
        """Ledgers written before Read recorded start/lines_returned from the tool result."""
        r = self.room
        store = r.home / "rooms" / "t" / "ledger.jsonl"
        store.write_text("\n".join(json.dumps(e) for e in [
            {"session": "s1", "type": "prompt", "text": "q"},
            {"session": "s1", "tool": "Read", "type": "read", "file": "01 Corporate/1.01 Charter.txt", "lines_returned": 1},
        ]) + "\n")
        f = r.coverage()["questions"][0]["files"]["01 Corporate/1.01 Charter.txt"]
        self.assertEqual(f["read_fraction"], 1.0)


if __name__ == "__main__":
    unittest.main()
