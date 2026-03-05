#!/usr/bin/env python3
"""
TacRaven Navigation Updater
Changes "Pricing" to "Programs" in navigation while keeping the link to pricing.html
Run this script from your repository root directory.
"""

import os
import re

# All HTML files in your repo
html_files = [
    '404.html',
    'Blog.html',
    'about.html',
    'cyber-news.html',
    'index.html',
    'learning-hub.html',
    'netforge.html',
    'pricing.html',
    'privacy.html',
    'talonprep.html',
    'terms.html',
    'threat-map.html',
    'tools.html'
]

def update_nav():
    updated_count = 0
    
    for filename in html_files:
        if os.path.exists(filename):
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace "Pricing" text with "Programs" in nav links
            # Keeps href="pricing.html" unchanged, only changes display text
            updated = re.sub(
                r'(<a[^>]*href=["\']pricing\.html["\'][^>]*>)\s*Pricing\s*(</a>)',
                r'\1Programs\2',
                content,
                flags=re.IGNORECASE
            )
            
            if content != updated:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(updated)
                print(f"✓ Updated: {filename}")
                updated_count += 1
            else:
                print(f"– No change needed: {filename}")
        else:
            print(f"✗ File not found: {filename}")
    
    print(f"\n{'='*40}")
    print(f"Complete! Updated {updated_count} file(s).")
    print(f"Nav now shows 'Programs' but still links to pricing.html")
    print(f"\nNext steps:")
    print(f"  1. Review changes: git diff")
    print(f"  2. Stage changes:  git add .")
    print(f"  3. Commit:         git commit -m \"Update nav: Pricing → Programs\"")
    print(f"  4. Push:           git push")

if __name__ == "__main__":
    update_nav()
