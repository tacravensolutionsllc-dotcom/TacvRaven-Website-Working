#!/usr/bin/env python3
"""
TacRaven Blog Post Patcher
===========================
Run this from your blog root directory (the folder containing Blog.html and posts/).
It will update all existing post HTML files to:
  1. Remove the ~0% Unemployment stat
  2. Change the stats layout from 4-col grid to centered 3-col flex
  3. Fix /blog/ back links to use ../../../Blog.html

Usage:
    python patch_posts.py          # Dry run (preview changes)
    python patch_posts.py --apply  # Apply changes
"""

import os
import re
import sys
from pathlib import Path

def patch_file(filepath, dry_run=True):
    text = filepath.read_text(encoding="utf-8")
    original = text
    changes = []

    # 1. Remove the unemployment stat block
    # Handles variations in whitespace/formatting
    pattern = r'<div class="stat">\s*<div class="stat-value">~0%</div>\s*<div class="stat-label">Unemployment</div>\s*</div>'
    if re.search(pattern, text):
        text = re.sub(pattern, '', text)
        changes.append("Removed ~0% Unemployment stat")

    # 2. Update stats-inner CSS from 4-col grid to centered flex
    old_css = "display:grid;grid-template-columns:repeat(4,1fr)"
    new_css = "display:flex;flex-wrap:wrap;justify-content:center"
    if old_css in text:
        text = text.replace(old_css, new_css)
        changes.append("Updated stats-inner to flex layout")

    # 3. Add flex sizing to .stat if not already present
    old_stat = ".stat{text-align:center;position:relative"
    new_stat = ".stat{text-align:center;position:relative;flex:0 1 200px"
    if old_stat in text and "flex:0 1 200px" not in text:
        text = text.replace(old_stat, new_stat)
        changes.append("Added flex sizing to .stat")

    # 4. Fix /blog/ back links
    if 'href="/blog/"' in text:
        text = text.replace('href="/blog/"', 'href="../../../Blog.html"')
        changes.append("Fixed /blog/ links to ../../../Blog.html")

    # 5. Remove stats-inner grid override from mobile media query
    old_mobile = "stats-inner{grid-template-columns:repeat(2,1fr);gap:1.5rem}."
    if old_mobile in text:
        text = text.replace(old_mobile, "")
        changes.append("Cleaned up mobile media query")

    if text != original:
        if not dry_run:
            filepath.write_text(text, encoding="utf-8")
        return changes
    return []

def main():
    dry_run = "--apply" not in sys.argv
    posts_dir = Path("posts")

    if not posts_dir.exists():
        print("ERROR: 'posts/' directory not found.")
        print("Run this script from your blog root directory (where Blog.html lives).")
        sys.exit(1)

    html_files = list(posts_dir.rglob("*.html"))
    if not html_files:
        print("No HTML files found in posts/")
        sys.exit(0)

    print(f"{'DRY RUN' if dry_run else 'APPLYING CHANGES'}")
    print(f"Found {len(html_files)} post(s) in posts/\n")

    patched = 0
    for f in sorted(html_files):
        changes = patch_file(f, dry_run=dry_run)
        if changes:
            patched += 1
            print(f"  {'[WOULD PATCH]' if dry_run else '[PATCHED]'} {f}")
            for c in changes:
                print(f"    - {c}")

    print(f"\n{'Would patch' if dry_run else 'Patched'} {patched}/{len(html_files)} files.")
    if dry_run and patched > 0:
        print("\nRun with --apply to make changes:")
        print("    python patch_posts.py --apply")

if __name__ == "__main__":
    main()
