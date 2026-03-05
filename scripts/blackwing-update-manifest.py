#!/usr/bin/env python3
"""
Black Wing Dispatch - Sitemap Updater
TacRaven Solutions LLC

Updates sitemap.xml with new posts.
Designed for two-repo architecture.
"""

import argparse
from datetime import datetime
from pathlib import Path


def update_sitemap(website_dir):
    """Update the sitemap with all blog posts."""
    
    website_root = Path(website_dir)
    blackwing_dir = website_root / "intel" / "blackwing"
    sitemap_path = blackwing_dir / "sitemap.xml"
    
    posts = []
    for html_file in blackwing_dir.rglob("*.html"):
        if html_file.name == "index.html":
            continue
        
        rel_path = html_file.relative_to(website_root)
        url = f"https://tacraven.com/{rel_path}"
        mtime = datetime.fromtimestamp(html_file.stat().st_mtime)
        lastmod = mtime.strftime("%Y-%m-%d")
        
        posts.append({"url": url, "lastmod": lastmod})
    
    today = datetime.now().strftime("%Y-%m-%d")
    sitemap_xml = f'''<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
    <url>
        <loc>https://tacraven.com/intel/blackwing/</loc>
        <lastmod>{today}</lastmod>
        <changefreq>daily</changefreq>
        <priority>0.9</priority>
    </url>
'''
    
    for post in sorted(posts, key=lambda x: x["lastmod"], reverse=True):
        sitemap_xml += f'''    <url>
        <loc>{post["url"]}</loc>
        <lastmod>{post["lastmod"]}</lastmod>
        <changefreq>monthly</changefreq>
        <priority>0.7</priority>
    </url>
'''
    
    sitemap_xml += "</urlset>"
    
    with open(sitemap_path, 'w') as f:
        f.write(sitemap_xml)
    
    print(f"Updated: {sitemap_path} ({len(posts)} posts)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--website-dir', required=True)
    args = parser.parse_args()
    update_sitemap(args.website_dir)
