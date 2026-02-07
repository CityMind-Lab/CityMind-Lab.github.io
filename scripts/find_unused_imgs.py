#!/usr/bin/env python3
"""Find and delete unused image/assets under imgs (excluding logo/)."""
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
IMGS = ROOT / "imgs"
# Only consider these as "used" – image + CSS that are linked
EXT_KEEP = (".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".css")

def main():
    # 1. Collect all referenced paths: subdir/filename (no query string)
    refs = set()
    # Match imgs/subdir/name (with optional leading / or ../)
    pattern = re.compile(
        r"imgs/(common|datasets|people|photos|publications)/([^\"'\s\)\?]+)"
    )
    for ext in ("*.html", "*.yaml", "*.yml", "*.css"):
        for f in ROOT.rglob(ext):
            if "node_modules" in str(f) or "wp-content/plugins" in str(f):
                continue
            try:
                text = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            for m in pattern.finditer(text):
                sub, name = m.group(1), m.group(2).split("?")[0].strip()
                if name:
                    refs.add(f"{sub}/{name}")

    # 2. List all files under imgs except logo/
    all_files = []
    for d in ("common", "datasets", "people", "photos", "publications"):
        subdir = IMGS / d
        if not subdir.is_dir():
            continue
        for f in subdir.rglob("*"):
            if f.is_file():
                rel = f.relative_to(IMGS)
                all_files.append(str(rel))

    # 3. Determine unused (only delete image + css, not other assets)
    unused = []
    for rel in all_files:
        if rel in refs:
            continue
        lower = rel.lower()
        if any(lower.endswith(e) for e in EXT_KEEP):
            unused.append(rel)

    # 4. Delete unused
    deleted = []
    for rel in sorted(unused):
        p = IMGS / rel
        if p.is_file():
            try:
                p.unlink()
                deleted.append(rel)
            except Exception as e:
                print(f"Skip delete {rel}: {e}")
    for r in deleted:
        print("Deleted:", r)
    print("Total deleted:", len(deleted))

if __name__ == "__main__":
    main()
