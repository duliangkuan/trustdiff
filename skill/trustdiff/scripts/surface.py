#!/usr/bin/env python3
"""trustdiff surface mapper.

Maps the blast radius of a change: which files changed, which functions/classes
changed, and who calls them. Regex-based instrument -- fast and dependency-free,
not an oracle. The reviewing agent must still read the code.

Usage:
  python surface.py --base <before-dir> --head <after-dir> [--json out.json]
  python surface.py --git <range>            # e.g. main...HEAD, run inside the repo

Output (stdout, JSON):
{
  "changed_files": [{"path": "...", "status": "added|removed|modified"}],
  "changed_symbols": [{"name": "...", "kind": "function|class", "file": "...",
                        "status": "added|removed|modified",
                        "old_signature": "...", "new_signature": "..."}],
  "callers": {"symbol": [{"file": "...", "line": 3, "text": "..."}]},
  "constraint_docs": ["CLAUDE.md", ...]
}
"""
import argparse
import json
import os
import re
import subprocess
import sys

CODE_EXT = {".py", ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs"}
SKIP_DIRS = {".git", "node_modules", "__pycache__", ".venv", "venv", "dist", "build",
             ".pytest_cache", ".mypy_cache"}
CONSTRAINT_DOCS = ["CLAUDE.md", "AGENTS.md", "CONTRIBUTING.md", "ARCHITECTURE.md"]

PY_DEF = re.compile(r"^([ \t]*)(?:async\s+)?def\s+([A-Za-z_]\w*)\s*(\([^)]*\))", re.M)
PY_CLASS = re.compile(r"^([ \t]*)class\s+([A-Za-z_]\w*)", re.M)
JS_FUNC = re.compile(
    r"^([ \t]*)(?:export\s+)?(?:async\s+)?function\s+([A-Za-z_$][\w$]*)\s*(\([^)]*\))", re.M)
JS_ARROW = re.compile(
    r"^([ \t]*)(?:export\s+)?(?:const|let|var)\s+([A-Za-z_$][\w$]*)\s*=\s*(?:async\s*)?\(", re.M)
JS_CLASS = re.compile(r"^([ \t]*)(?:export\s+)?class\s+([A-Za-z_$][\w$]*)", re.M)


def list_files(root):
    out = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS]
        for fn in filenames:
            ext = os.path.splitext(fn)[1]
            if ext in CODE_EXT:
                full = os.path.join(dirpath, fn)
                rel = os.path.relpath(full, root).replace("\\", "/")
                out[rel] = full
    return out


def read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def extract_symbols(text, path):
    """Return {name: {kind, signature, body_hash}} for one file."""
    syms = {}
    if path.endswith(".py"):
        patterns = [(PY_DEF, "function", True), (PY_CLASS, "class", False)]
    else:
        patterns = [(JS_FUNC, "function", True), (JS_ARROW, "function", False),
                    (JS_CLASS, "class", False)]
    lines = text.splitlines()
    for pat, kind, has_sig in patterns:
        for m in pat.finditer(text):
            indent, name = m.group(1), m.group(2)
            sig = m.group(3) if has_sig and m.lastindex >= 3 else ""
            # capture the symbol body: from def line until dedent (cheap heuristic)
            start_line = text.count("\n", 0, m.start())
            body = []
            for ln in lines[start_line:start_line + 200]:
                if body and ln.strip() and not ln.startswith(indent + " ") \
                        and not ln.startswith(indent + "\t") and ln[:len(indent) + 1].strip():
                    if not ln.strip().startswith(("}", ")", "]")):
                        break
                body.append(ln)
            syms[name] = {"kind": kind, "signature": name + sig,
                          "body": "\n".join(body).rstrip()}
    return syms


def find_callers(name, files_map, def_files):
    """grep call sites of `name` across head files, skipping its own definition lines."""
    word = re.compile(r"\b" + re.escape(name) + r"\b")
    defline = re.compile(r"\b(?:def|class|function)\s+" + re.escape(name) + r"\b"
                         r"|(?:const|let|var)\s+" + re.escape(name) + r"\b")
    hits = []
    for rel, full in files_map.items():
        text = read(full)
        if name not in text:
            continue
        for i, ln in enumerate(text.splitlines(), 1):
            if word.search(ln) and not defline.search(ln) and not ln.strip().startswith("#"):
                hits.append({"file": rel, "line": i, "text": ln.strip()[:160]})
    return hits


def compare_dirs(base, head):
    base_files, head_files = list_files(base), list_files(head)
    changed_files, changed_symbols = [], []
    all_paths = sorted(set(base_files) | set(head_files))
    for rel in all_paths:
        b, h = base_files.get(rel), head_files.get(rel)
        if b and not h:
            changed_files.append({"path": rel, "status": "removed"})
            for n, s in extract_symbols(read(b), rel).items():
                changed_symbols.append({"name": n, "kind": s["kind"], "file": rel,
                                        "status": "removed",
                                        "old_signature": s["signature"],
                                        "new_signature": None})
            continue
        if h and not b:
            changed_files.append({"path": rel, "status": "added"})
            for n, s in extract_symbols(read(h), rel).items():
                changed_symbols.append({"name": n, "kind": s["kind"], "file": rel,
                                        "status": "added", "old_signature": None,
                                        "new_signature": s["signature"]})
            continue
        bt, ht = read(b), read(h)
        if bt == ht:
            continue
        changed_files.append({"path": rel, "status": "modified"})
        bs, hs = extract_symbols(bt, rel), extract_symbols(ht, rel)
        for n in sorted(set(bs) | set(hs)):
            old, new = bs.get(n), hs.get(n)
            if old and not new:
                changed_symbols.append({"name": n, "kind": old["kind"], "file": rel,
                                        "status": "removed",
                                        "old_signature": old["signature"],
                                        "new_signature": None})
            elif new and not old:
                changed_symbols.append({"name": n, "kind": new["kind"], "file": rel,
                                        "status": "added", "old_signature": None,
                                        "new_signature": new["signature"]})
            elif old["signature"] != new["signature"] or old["body"] != new["body"]:
                changed_symbols.append({"name": n, "kind": new["kind"], "file": rel,
                                        "status": "modified",
                                        "old_signature": old["signature"],
                                        "new_signature": new["signature"]})
    callers = {}
    for sym in changed_symbols:
        if sym["name"] not in callers:
            callers[sym["name"]] = find_callers(sym["name"], head_files or base_files,
                                                sym["file"])
    docs = [d for d in CONSTRAINT_DOCS
            if os.path.exists(os.path.join(head or base, d))]
    extra = os.path.join(head or base, "docs", "adr")
    if os.path.isdir(extra):
        docs.append("docs/adr/")
    return {"changed_files": changed_files, "changed_symbols": changed_symbols,
            "callers": callers, "constraint_docs": docs}


def compare_git(rng):
    try:
        names = subprocess.run(["git", "diff", "--name-status", rng],
                               capture_output=True, text=True, check=True).stdout
    except (subprocess.CalledProcessError, FileNotFoundError) as e:
        print(json.dumps({"error": "git diff failed: %s" % e}))
        sys.exit(1)
    status_map = {"A": "added", "D": "removed", "M": "modified", "R": "renamed"}
    changed_files = []
    for line in names.splitlines():
        parts = line.split("\t")
        if len(parts) >= 2:
            changed_files.append({"path": parts[-1],
                                  "status": status_map.get(parts[0][0], parts[0])})
    head_files = list_files(".")
    changed_symbols = []
    base_ref = rng.split("...")[0].split("..")[0]
    for cf in changed_files:
        rel = cf["path"]
        if os.path.splitext(rel)[1] not in CODE_EXT:
            continue
        try:
            old_text = subprocess.run(["git", "show", "%s:%s" % (base_ref, rel)],
                                      capture_output=True, text=True).stdout
        except FileNotFoundError:
            old_text = ""
        new_text = read(rel) if os.path.exists(rel) else ""
        bs, hs = extract_symbols(old_text, rel), extract_symbols(new_text, rel)
        for n in sorted(set(bs) | set(hs)):
            old, new = bs.get(n), hs.get(n)
            if old and not new:
                changed_symbols.append({"name": n, "kind": old["kind"], "file": rel,
                                        "status": "removed",
                                        "old_signature": old["signature"],
                                        "new_signature": None})
            elif new and not old:
                changed_symbols.append({"name": n, "kind": new["kind"], "file": rel,
                                        "status": "added", "old_signature": None,
                                        "new_signature": new["signature"]})
            elif old["signature"] != new["signature"] or old["body"] != new["body"]:
                changed_symbols.append({"name": n, "kind": new["kind"], "file": rel,
                                        "status": "modified",
                                        "old_signature": old["signature"],
                                        "new_signature": new["signature"]})
    callers = {}
    for sym in changed_symbols:
        if sym["name"] not in callers:
            callers[sym["name"]] = find_callers(sym["name"], head_files, sym["file"])
    docs = [d for d in CONSTRAINT_DOCS if os.path.exists(d)]
    if os.path.isdir(os.path.join("docs", "adr")):
        docs.append("docs/adr/")
    return {"changed_files": changed_files, "changed_symbols": changed_symbols,
            "callers": callers, "constraint_docs": docs}


def main():
    ap = argparse.ArgumentParser(description="trustdiff surface mapper")
    ap.add_argument("--base", help="directory snapshot before the change")
    ap.add_argument("--head", help="directory snapshot after the change")
    ap.add_argument("--git", help="git range, e.g. main...HEAD (run inside the repo)")
    ap.add_argument("--json", dest="out", help="also write JSON to this path")
    args = ap.parse_args()

    if args.git:
        result = compare_git(args.git)
    elif args.base and args.head:
        result = compare_dirs(args.base, args.head)
    else:
        ap.error("need --git RANGE or --base DIR --head DIR")

    text = json.dumps(result, indent=2)
    print(text)
    if args.out:
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(text)


if __name__ == "__main__":
    main()
