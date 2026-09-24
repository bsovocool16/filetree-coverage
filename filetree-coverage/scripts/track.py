#!/usr/bin/env python3
"""
track.py — the passive recorder. Claude Code runs it as a hook after every
file-touching tool call (PostToolUse on Read, Grep, Glob, LS, Bash), on every
user prompt (UserPromptSubmit) and at the end of every turn (Stop). It never
blocks, never changes anything, and exits 0 whatever happens.

It reads the hook's JSON from stdin, keeps only paths that fall inside a mapped
room (see room.py), and appends one line per event to that room's ledger:

    {"t": ..., "type": "prompt", "text": ...}                           a question was asked
    {"t": ..., "type": "listed", "files": [...]}                         files appeared in a listing (Glob, ls, find)
    {"t": ..., "type": "scanned", "scope": "<dir>"}                      a search ran over this folder (its files were searched)
    {"t": ..., "type": "hit", "files": [...], "pattern": ...}            files matched a search (Grep, grep, rg)
    {"t": ..., "type": "read", "file": ..., "offset", "limit", "pages",  a file was opened (Read, cat, head, sed -n, pdftotext ...);
        "start", "lines_returned", "total_lines"}                        for Read, the lines the tool says it returned
    {"t": ..., "type": "answer", "text": ...}                            the turn ended; the assistant's final message

Every event also carries "session", "tool" and, inside a subagent, "agent".
The recorder is deliberately dumb: it does not judge relevance, it does not
know what the question meant, and it does not touch the documents.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import sys
import time
from pathlib import Path

HOME = Path(os.environ.get("FILETREE_COVERAGE_HOME") or Path.home() / ".claude" / "plugins" / "config" / "filetree-coverage")
REGISTRY = HOME / "rooms.json"
MAX_TEXT = 40000  # characters of prompt / answer text kept per event

READ_VERBS = ("cat", "head", "tail", "less", "more", "sed", "awk", "pdftotext", "strings", "python", "python3", "open")
LIST_VERBS = ("ls", "find", "tree", "fd")
GREP_VERBS = ("grep", "rg", "ag", "ack", "egrep", "fgrep")


def load_rooms():
    try:
        d = json.loads(REGISTRY.read_text())
        rooms = []
        for r in d.get("rooms", []):
            store = Path(r["store"])
            # one entry per spelling of the folder's path; a tool call's paths use one of them
            for root in [r["root"], *r.get("aliases", [])]:
                rooms.append((Path(root), store, r["id"]))
        return rooms
    except Exception:
        return []


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%S")


def append(store: Path, event: dict):
    try:
        store.mkdir(parents=True, exist_ok=True)
        with open(store / "ledger.jsonl", "a") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception:
        pass


def is_file(p: Path) -> bool:
    try:
        return p.is_file()
    except OSError:
        return False


def is_dir(p: Path) -> bool:
    try:
        return p.is_dir()
    except OSError:
        return False


def exists(p: Path) -> bool:
    try:
        return p.exists()
    except OSError:
        return False


def resolve(p: str, cwd: str) -> Path | None:
    try:
        p = p.strip().strip("'\"`")
        if not p:
            return None
        q = Path(os.path.expanduser(p))
        if not q.is_absolute():
            q = Path(cwd) / q
        return Path(os.path.normpath(str(q)))
    except Exception:
        return None


def under(path: Path, root: Path) -> str | None:
    try:
        rel = path.relative_to(root)
    except ValueError:
        return None
    s = rel.as_posix()
    return None if s in ("", ".") else s


# Paths that appear in free text (tool output, shell commands). Room paths
# have spaces in them, so we look for tokens that start at a known root.
def paths_in_text(text: str, root: Path, cwd: str) -> list[str]:
    if not text:
        return []
    found = set()
    root_s = str(root)
    # absolute mentions: take the longest run after the root, then shorten it
    # at ":" / whitespace boundaries until it names something that exists
    # (room paths contain spaces and " - ", so a delimiter-based cut is not enough)
    for m in re.finditer(re.escape(root_s) + r"/([^\n\r\"'`|<>]+)", text):
        raw = m.group(1).replace("\\ ", " ")
        cands = [raw.rstrip()]
        for i, ch in enumerate(raw):
            if ch == ":":
                cands.append(raw[:i].rstrip())
        for c in list(cands):
            while " " in c:
                c = c[: c.rfind(" ")].rstrip()
                cands.append(c)
        for c in cands:
            if not c:
                continue
            q = Path(os.path.normpath(str(root / c)))
            rel = under(q, root)
            if rel and exists(root / rel):
                found.add(rel)
                break
    # relative mentions, when the shell was inside the room or a parent of it
    try:
        cwd_p = Path(cwd)
        if under(cwd_p, root) is not None or cwd_p == root:
            base = cwd_p
        elif under(root, cwd_p) is not None:
            base = cwd_p
        else:
            base = None
    except Exception:
        base = None
    if base is not None:
        for line in text.splitlines():
            line = line.strip()
            if not line or len(line) > 255:
                continue
            # grep-style "path:line:text" or "path:text", or a bare path line
            head = re.split(r":\d+[:-]|:(?=\S)", line, maxsplit=1)[0].strip()
            for cand in (head, line):
                q = resolve(cand, str(base))
                if q is None:
                    continue
                rel = under(q, root)
                if rel and exists(root / rel):
                    found.add(rel)
                    break
    return sorted(found)



def paths_in_command(cmd: str, root: Path, cwd: str) -> list[str]:
    """Room paths named as arguments of a shell command (quoted or not)."""
    found = set(paths_in_text(cmd, root, cwd))
    try:
        toks = shlex.split(cmd, posix=True)
    except ValueError:
        toks = re.findall(r'"([^"]+)"|\'([^\']+)\'|(\S+)', cmd)
        toks = [a or b or c for a, b, c in toks]
    for t in toks:
        if not t or t.startswith("-") or t in ("|", "&&", ";", ">", "<"):
            continue
        q = resolve(t, cwd)
        if q is None:
            continue
        rel = under(q, root)
        if rel and exists(root / rel):
            found.add(rel)
        elif q == root:
            found.add("")
    return sorted(found)


def lines_as_files(out: str, root: Path, dirs: list[str], cwd: str) -> list[str]:
    """Output lines of ls/find resolved against the listed folders, then the shell's cwd."""
    found = set()
    bases = [root / d for d in dirs] + ([Path(cwd)] if under(Path(cwd), root) is not None or Path(cwd) == root else [])
    for line in out.splitlines():
        line = line.strip()
        if not line or len(line) > 255:
            continue
        for b in bases:
            q = Path(os.path.normpath(str(b / line)))
            rel = under(q, root)
            if rel and is_file(root / rel):
                found.add(rel)
                break
    return sorted(found)

def tool_response(payload: dict):
    return payload.get("tool_response") or payload.get("tool_result") or ""


def result_text(payload: dict) -> str:
    """The tool's output as plain text. Claude Code returns structured results:
    Read as {"file": {"content", ...}}, Grep as {"filenames": [...], "content"},
    Bash as {"stdout", "stderr"}; older payloads and other tools return strings."""
    r = tool_response(payload)
    if isinstance(r, dict):
        parts = []
        f = r.get("file")
        if isinstance(f, dict) and isinstance(f.get("content"), str):
            parts.append(f["content"])
        if isinstance(r.get("filenames"), list):
            parts.append("\n".join(str(x) for x in r["filenames"]))
        for k in ("text", "content", "stdout", "output"):
            v = r.get(k)
            if isinstance(v, str):
                parts.append(v)
            elif isinstance(v, list):
                parts.append("\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in v))
        if parts:
            return "\n".join(parts)
        return json.dumps(r)[:200000]
    if isinstance(r, list):
        return "\n".join(x.get("text", "") if isinstance(x, dict) else str(x) for x in r)
    return str(r)


def count_lines(text: str) -> int:
    return text.count("\n") + (1 if text and not text.endswith("\n") else 0)


def handle_tool(payload: dict, rooms):
    tool = payload.get("tool_name", "")
    inp = payload.get("tool_input") or {}
    cwd = payload.get("cwd") or os.getcwd()
    out = result_text(payload)
    base = {"t": now(), "session": payload.get("session_id"), "tool": tool}
    if payload.get("agent_id"):
        base["agent"] = payload.get("agent_type") or payload.get("agent_id")

    for root, store, rid in rooms:
        ev = []
        if tool == "Read":
            p = resolve(inp.get("file_path") or inp.get("path") or "", cwd)
            rel = under(p, root) if p else None
            if rel:
                e = {**base, "type": "read", "file": rel}
                for k in ("offset", "limit", "pages"):
                    if inp.get(k) not in (None, ""):
                        e[k] = inp[k]
                tr = tool_response(payload)
                meta = tr.get("file") if isinstance(tr, dict) else None
                if isinstance(meta, dict) and isinstance(meta.get("numLines"), int):
                    # the tool says which lines it returned; it truncates long files, so a Read with
                    # no offset or limit is not necessarily a full read
                    e["start"] = meta.get("startLine") or 1
                    e["lines_returned"] = meta["numLines"]
                    if isinstance(meta.get("totalLines"), int):
                        e["total_lines"] = meta["totalLines"]
                else:
                    e["lines_returned"] = count_lines(out)
                if isinstance(tr, dict) and tr.get("type") == "error":
                    e["error"] = True
                ev.append(e)
        elif tool == "Grep":
            scope = resolve(inp.get("path") or ".", cwd)
            rel_scope = under(scope, root) if scope else None
            in_room = rel_scope is not None or (scope == root)
            hits = paths_in_text(out, root, cwd)
            if in_room:
                ev.append({**base, "type": "scanned", "scope": rel_scope or "", "pattern": inp.get("pattern"), "glob": inp.get("glob")})
            if hits:
                ev.append({**base, "type": "hit", "files": hits, "pattern": inp.get("pattern")})
        elif tool in ("Glob", "LS"):
            listed = paths_in_text(out, root, cwd)
            scope = resolve(inp.get("path") or ".", cwd)
            rel_scope = under(scope, root) if scope else None
            if listed:
                ev.append({**base, "type": "listed", "files": listed, "pattern": inp.get("pattern")})
            elif rel_scope is not None or scope == root:
                ev.append({**base, "type": "listed", "files": [], "scope": rel_scope or ""})
        elif tool == "Bash":
            cmd = inp.get("command") or ""
            # a `cd <room path>` inside the command moves the shell; resolve the rest against it
            for m_cd in re.finditer(r"(?:^|&&|;|\|)\s*cd\s+(\"[^\"]+\"|'[^']+'|\S+)", cmd):
                eff = resolve(m_cd.group(1).strip("\"'"), cwd)
                if eff is not None and (eff == root or under(eff, root) is not None):
                    cwd = str(eff)
            mentioned = paths_in_command(cmd, root, cwd)       # room paths named in the command ("" = the room itself)
            dirs = [m for m in mentioned if m == "" or is_dir(root / m)]
            files = [m for m in mentioned if m and is_file(root / m)]
            in_out = paths_in_text(out, root, cwd)             # room paths that appeared in the output
            out_files = sorted(set([f for f in in_out if is_file(root / f)] + lines_as_files(out, root, [d for d in dirs if d], cwd)))
            shell_in_room = under(Path(cwd), root) is not None or Path(cwd) == root
            verbs = {os.path.basename(seg.strip().split()[0]) for seg in re.split(r"\||&&|;", cmd) if seg.strip()}
            if verbs & set(GREP_VERBS):
                # the search looked at every text file in its scope, and surfaced the ones in the output
                for sc in dirs or ([""] if shell_in_room else []):
                    ev.append({**base, "type": "scanned", "scope": sc, "pattern": None, "via": "bash"})
                if out_files:
                    ev.append({**base, "type": "hit", "files": out_files, "via": "bash"})
            if verbs & set(LIST_VERBS):
                if out_files or dirs or shell_in_room:
                    ev.append({**base, "type": "listed", "files": out_files, "via": "bash", **({"scope": dirs[0]} if dirs and not out_files else {})})
            if verbs & set(READ_VERBS):
                for f in files:
                    e = {**base, "type": "read", "file": f, "via": "bash", "lines_returned": count_lines(out)}
                    if re.search(r"\b(head|tail|sed)\b", cmd):
                        e["partial"] = True
                    ev.append(e)
            if not ev and (files or out_files):
                ev.append({**base, "type": "listed", "files": sorted(set(files + out_files)), "via": "bash"})
        for e in ev:
            if e.get("type") in ("hit", "listed") and not e.get("files") and "scope" not in e:
                continue
            append(store, e)


def main():
    try:
        raw = sys.stdin.read()
        payload = json.loads(raw) if raw.strip() else {}
    except Exception:
        return
    rooms = load_rooms()
    if not rooms:
        return
    stores = list(dict.fromkeys(store for _, store, _ in rooms))  # a room with an alias appears twice in rooms
    try:
        ev = payload.get("hook_event_name", "")
        base = {"t": now(), "session": payload.get("session_id")}
        if payload.get("agent_id"):
            base["agent"] = payload.get("agent_type") or payload.get("agent_id")
        if ev == "UserPromptSubmit":
            text = payload.get("user_input") or payload.get("prompt") or ""
            for store in stores:
                append(store, {**base, "type": "prompt", "text": text[:MAX_TEXT]})
        elif ev in ("Stop", "SubagentStop"):
            text = payload.get("last_assistant_message") or ""
            if not text and payload.get("transcript_path"):
                text = last_assistant_from_transcript(payload["transcript_path"])
            for store in stores:
                append(store, {**base, "type": "answer" if ev == "Stop" else "subanswer", "text": text[:MAX_TEXT]})
        elif ev == "PostToolUse":
            handle_tool(payload, rooms)
    except Exception:
        pass


def last_assistant_from_transcript(path: str) -> str:
    try:
        last = ""
        with open(path) as f:
            for line in f:
                try:
                    o = json.loads(line)
                except Exception:
                    continue
                msg = o.get("message") if isinstance(o.get("message"), dict) else o
                if (msg.get("role") or o.get("type")) != "assistant":
                    continue
                content = msg.get("content")
                if isinstance(content, str):
                    last = content
                elif isinstance(content, list):
                    txt = "\n".join(b.get("text", "") for b in content if isinstance(b, dict) and b.get("type") == "text")
                    if txt.strip():
                        last = txt
        return last
    except Exception:
        return ""


if __name__ == "__main__":
    main()
    sys.exit(0)
