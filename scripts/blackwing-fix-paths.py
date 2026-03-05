#!/usr/bin/env python3
"""
Black Wing Dispatch - Fix CSS Paths
TacRaven Solutions LLC

Embeds CSS directly into all existing blog posts.
"""

import os
import re
import argparse
from pathlib import Path


def fix_post_css(html_path, css_content):
    """Embed CSS directly into a blog post."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if CSS is already embedded
    if '<style>' in content and 'color-bg-primary' in content:
        return False
    
    # Find the </head> tag and insert embedded CSS before it
    if '</head>' in content:
        # Remove existing stylesheet link
        content = re.sub(
            r'<link[^>]*rel="stylesheet"[^>]*href="[^"]*blackwing[^"]*\.css"[^>]*>\s*',
            '',
            content
        )
        
        # Add embedded CSS
        css_block = f'''<style>
{css_content}
</style>
</head>'''
        content = content.replace('</head>', css_block)
        
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    
    return False


def fix_all_posts(website_dir):
    """Embed CSS in all blog posts."""
    website_root = Path(website_dir)
    blackwing_dir = website_root / 'intel' / 'blackwing'
    css_path = website_root / 'assets' / 'css' / 'blackwing-dispatch.css'
    
    # Load CSS
    if not css_path.exists():
        print(f"Error: CSS not found at {css_path}")
        return
    
    with open(css_path, 'r', encoding='utf-8') as f:
        css_content = f.read()
    
    print(f"Loaded CSS ({len(css_content)} chars)")
    
    fixed_count = 0
    
    for html_file in blackwing_dir.rglob('*.html'):
        if html_file.name == 'index.html':
            continue
        
        if fix_post_css(html_file, css_content):
            print(f"Fixed: {html_file.name}")
            fixed_count += 1
        else:
            print(f"OK: {html_file.name}")
    
    print(f"\nFixed {fixed_count} files")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Embed CSS in Black Wing posts')
    parser.add_argument('--website-dir', required=True, help='Path to website repository root')
    args = parser.parse_args()
    fix_all_posts(args.website_dir)
