#!/usr/bin/env python3
"""
TacRaven Blog Manifest Generator
=================================
Scans the posts/ directory for published blog posts,
extracts metadata from each HTML file, and writes
posts/posts.json for the blog index page to consume.

Usage:
    python update_manifest.py              # Generate manifest
    python update_manifest.py --verbose    # Show details

Called automatically by the GitHub Actions workflow
after each new post is generated.
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
BLOG_ROOT = SCRIPT_DIR.parent
POSTS_DIR = BLOG_ROOT / "posts"
MANIFEST_FILE = POSTS_DIR / "posts.json"

# Category slug → display name mapping
CATEGORY_NAMES = {
    "getting-started": "Getting Started",
    "certifications": "Certifications",
    "salaries": "Salaries",
    "career-paths": "Career Paths",
    "job-search": "Job Search",
    "skills": "Skills",
    "industry-trends": "Industry Trends",
}

# Category slug → CSS class mapping (matches blog.html)
CATEGORY_CSS = {
    "getting-started": "gs",
    "certifications": "cert",
    "salaries": "sal",
    "career-paths": "cp",
    "job-search": "js",
    "skills": "sk",
    "industry-trends": "tr",
}


def extract_metadata(filepath):
    """
    Extract post metadata from an HTML file.
    
    Pulls data from <meta> tags, <title>, and structured HTML elements
    that the generate_post.py template produces.
    """
    try:
        html = filepath.read_text(encoding="utf-8")
    except Exception as e:
        print(f"  Warning: Could not read {filepath}: {e}")
        return None

    meta = {}

    # --- Title ---
    # From <title>Post Title | TacRaven Solutions</title>
    title_match = re.search(r"<title>(.+?)\s*\|\s*TacRaven", html)
    if title_match:
        meta["title"] = title_match.group(1).strip()
    else:
        # Fallback: try <meta property="og:title">
        og_title = re.search(r'property="og:title"\s+content="([^"]+)"', html)
        if og_title:
            meta["title"] = og_title.group(1).strip()
        else:
            meta["title"] = filepath.stem.replace("-", " ").title()

    # --- Excerpt / Description ---
    desc_match = re.search(r'<meta\s+name="description"\s+content="([^"]*)"', html)
    if not desc_match:
        desc_match = re.search(r'property="og:description"\s+content="([^"]*)"', html)
    if desc_match:
        meta["excerpt"] = desc_match.group(1).strip()
    else:
        # Fallback: grab subtitle from .hero-subtitle
        sub_match = re.search(r'class="hero-subtitle"[^>]*>([^<]+)<', html)
        if sub_match:
            meta["excerpt"] = sub_match.group(1).strip()
        else:
            meta["excerpt"] = ""

    # --- Published Date ---
    # From <meta property="article:published_time" content="2026-02-07">
    date_match = re.search(r'article:published_time"\s+content="([^"]+)"', html)
    if date_match:
        meta["date"] = date_match.group(1).strip()
    else:
        # Fallback: extract from directory path (posts/YYYY/MM/slug.html)
        parts = filepath.parts
        try:
            idx = list(parts).index("posts")
            year = parts[idx + 1]
            month = parts[idx + 2]
            meta["date"] = f"{year}-{month}-01"
        except (ValueError, IndexError):
            meta["date"] = "2025-01-01"

    # --- Category ---
    # From hero-category element: <span class="hero-category" style="background:var(--green)">Getting Started</span>
    cat_match = re.search(r'class="hero-category"[^>]*>([^<]+)<', html)
    if cat_match:
        cat_display = cat_match.group(1).strip()
        # Reverse-lookup slug from display name
        meta["category"] = cat_display
        meta["category_slug"] = "getting-started"  # default
        for slug, name in CATEGORY_NAMES.items():
            if name.lower() == cat_display.lower():
                meta["category_slug"] = slug
                break
    else:
        meta["category"] = "Getting Started"
        meta["category_slug"] = "getting-started"

    meta["category_css"] = CATEGORY_CSS.get(meta["category_slug"], "gs")

    # --- Tags ---
    # From tag elements: <span class="tag">Tag Name</span>
    tags = re.findall(r'class="tag"[^>]*>([^<]+)<', html)
    meta["tags"] = tags if tags else [meta["category"], "Cybersecurity"]

    # --- File path (relative to blog root) ---
    meta["filepath"] = str(filepath.relative_to(BLOG_ROOT))

    # --- Slug ---
    meta["slug"] = filepath.stem

    # --- Read time ---
    read_match = re.search(r'(\d+)\s*min\s*read', html, re.IGNORECASE)
    if read_match:
        meta["read_time"] = int(read_match.group(1))
    else:
        # Estimate from content length
        text_only = re.sub(r'<[^>]+>', '', html)
        word_count = len(text_only.split())
        meta["read_time"] = max(1, round(word_count / 200))

    # --- Featured flag ---
    # First post (most recent) will be marked featured by the blog page
    meta["featured"] = False

    return meta


def scan_posts(verbose=False):
    """Scan posts/ directory and collect all post metadata."""
    posts = []

    if not POSTS_DIR.exists():
        print(f"Posts directory not found: {POSTS_DIR}")
        return posts

    # Walk through all HTML files in posts/
    html_files = sorted(POSTS_DIR.rglob("*.html"), reverse=True)

    for filepath in html_files:
        # Skip any index.html files
        if filepath.name == "index.html":
            continue

        if verbose:
            print(f"  Scanning: {filepath.relative_to(BLOG_ROOT)}")

        meta = extract_metadata(filepath)
        if meta:
            posts.append(meta)

    # Sort by date descending (newest first)
    posts.sort(key=lambda p: p.get("date", ""), reverse=True)

    # Mark the newest post as featured
    if posts:
        posts[0]["featured"] = True

    return posts


def generate_manifest(verbose=False):
    """Generate the posts.json manifest file."""
    print("Scanning posts directory...")
    posts = scan_posts(verbose=verbose)

    # Build manifest
    manifest = {
        "generated": datetime.now().isoformat(),
        "count": len(posts),
        "posts": posts
    }

    # Ensure posts directory exists
    POSTS_DIR.mkdir(parents=True, exist_ok=True)

    # Write manifest
    MANIFEST_FILE.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(f"Manifest written: {MANIFEST_FILE}")
    print(f"Total posts indexed: {len(posts)}")

    return manifest


if __name__ == "__main__":
    import sys
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    generate_manifest(verbose=verbose)
