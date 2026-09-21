#!/bin/bash
# Build a distributable zip of this marketplace: dist/filetree-coverage-<version>.zip, unzipping to one folder that
# `/plugin marketplace add <folder>` accepts. Leaves out .git, caches, dist and any local runs.
set -e
cd "$(dirname "$0")"
V=$(python3 -c "import json; print(json.load(open('filetree-coverage/.claude-plugin/plugin.json'))['version'])")
OUTDIR="${1:-dist}"; mkdir -p "$OUTDIR"; OUT="$OUTDIR/filetree-coverage-$V.zip"; rm -f "$OUT"
T=$(mktemp -d); mkdir -p "$T/filetree-coverage"
tar --exclude=.git --exclude=__pycache__ --exclude=.DS_Store --exclude=dist --exclude=coverage-runs -cf - . | tar -xf - -C "$T/filetree-coverage"
(cd "$T" && zip -qr "$OLDPWD/$OUT" filetree-coverage)
rm -rf "$T"
echo "$OUT ($(du -h "$OUT" | cut -f1), $(unzip -l "$OUT" | tail -1 | awk '{print $2}') files)"
