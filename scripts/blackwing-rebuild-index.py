#!/usr/bin/env python3
"""
Black Wing Dispatch - Index Rebuilder
TacRaven Solutions LLC

Scans for all blog posts and rebuilds the index.html with real articles.
"""

import os
import re
import argparse
from pathlib import Path
from datetime import datetime


def extract_post_metadata(html_path):
    """Extract metadata from a blog post HTML file."""
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    metadata = {}
    
    # Extract title
    title_match = re.search(r'<title>([^|]+)\|', content)
    if title_match:
        metadata['title'] = title_match.group(1).strip()
    else:
        metadata['title'] = html_path.stem.replace('-', ' ').title()
    
    # Extract date from meta or path
    date_match = re.search(r'<meta property="article:published_time" content="(\d{4}-\d{2}-\d{2})', content)
    if date_match:
        metadata['date'] = date_match.group(1)
    else:
        # Try to get from path (intel/blackwing/2026/03/file.html)
        parts = html_path.parts
        try:
            year_idx = parts.index('blackwing') + 1
            metadata['date'] = f"{parts[year_idx]}-{parts[year_idx+1]}-01"
        except:
            metadata['date'] = datetime.now().strftime('%Y-%m-%d')
    
    # Extract category
    category_match = re.search(r'<meta property="article:section" content="([^"]+)"', content)
    if category_match:
        metadata['category'] = category_match.group(1)
    else:
        metadata['category'] = 'Defense'
    
    # Extract description/excerpt
    desc_match = re.search(r'<meta name="description" content="([^"]+)"', content)
    if desc_match:
        metadata['excerpt'] = desc_match.group(1)[:200]
    else:
        metadata['excerpt'] = 'Read the full dispatch for detailed analysis.'
    
    # Extract reading time
    time_match = re.search(r'(\d+)\s*min read', content)
    if time_match:
        metadata['reading_time'] = int(time_match.group(1))
    else:
        metadata['reading_time'] = 10
    
    # Build relative URL from intel/blackwing/ directory
    # Posts are at intel/blackwing/2026/03/file.html
    # Index is at intel/blackwing/index.html
    # So URL should be 2026/03/file.html
    try:
        # Find blackwing in path and get everything after it
        parts = html_path.parts
        blackwing_idx = parts.index('blackwing')
        relative_parts = parts[blackwing_idx + 1:]
        metadata['url'] = '/'.join(relative_parts)
    except:
        metadata['url'] = html_path.name
    
    metadata['filename'] = html_path.name
    
    return metadata


def get_category_class(category):
    """Convert category name to CSS class."""
    category_map = {
        'APT Activity': 'apt',
        'Ransomware': 'ransomware',
        'Vulnerability': 'vulnerability',
        'Supply Chain': 'supply-chain',
        'Threat Actor': 'threat-actor',
        'Industrial Control': 'industrial-control',
        'Cloud Security': 'cloud-security',
        'Defense': 'defense',
    }
    return category_map.get(category, 'defense')


def format_date(date_str):
    """Format date as 'Mar 4, 2026'."""
    try:
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        return dt.strftime('%b %d, %Y').replace(' 0', ' ')
    except:
        return date_str


def generate_article_card(post, featured=False):
    """Generate HTML for an article card."""
    cat_class = get_category_class(post['category'])
    featured_class = ' featured' if featured else ''
    featured_badge = '<span class="featured-badge">Featured</span>' if featured else ''
    
    return f'''
                <article class="article-card{featured_class}" data-category="{cat_class}">
                    <div class="article-header">
                        <div class="article-meta">
                            <span class="category-label {cat_class}">
                                <span class="category-dot"></span>
                                {post['category']}
                            </span>
                            <span class="article-date">{format_date(post['date'])}</span>
                            <span class="article-read-time">{post['reading_time']} min read</span>
                        </div>
                        {featured_badge}
                    </div>
                    <h2 class="article-title">
                        <a href="{post['url']}">{post['title']}</a>
                    </h2>
                    <p class="article-excerpt">{post['excerpt']}</p>
                    <div class="article-footer">
                        <div class="article-footer-left">
                            <a href="{post['url']}" class="read-more">Read Dispatch</a>
                        </div>
                    </div>
                </article>
'''


def rebuild_index(website_dir):
    """Rebuild the index.html with real posts."""
    website_root = Path(website_dir)
    blackwing_dir = website_root / 'intel' / 'blackwing'
    index_path = blackwing_dir / 'index.html'
    
    if not index_path.exists():
        print(f"Error: Index not found at {index_path}")
        return
    
    # Find all posts
    posts = []
    for html_file in blackwing_dir.rglob('*.html'):
        if html_file.name == 'index.html':
            continue
        try:
            metadata = extract_post_metadata(html_file)
            posts.append(metadata)
            print(f"Found: {metadata['title']}")
        except Exception as e:
            print(f"Error reading {html_file}: {e}")
    
    if not posts:
        print("No posts found!")
        return
    
    # Sort by date (newest first)
    posts.sort(key=lambda x: x['date'], reverse=True)
    
    # Read current index
    with open(index_path, 'r', encoding='utf-8') as f:
        index_html = f.read()
    
    # Generate article cards
    articles_html = ''
    for i, post in enumerate(posts):
        featured = (i == 0)  # First post is featured
        articles_html += generate_article_card(post, featured)
    
    # Find and replace the posts section
    # Look for the section between <!-- Posts Section --> and the closing </section>
    posts_pattern = r'(<section class="posts-section"[^>]*>\s*<div class="container">)\s*.*?(\s*</div>\s*</section>)'
    
    new_posts_section = f'''\\1
{articles_html}
            \\2'''
    
    new_index = re.sub(posts_pattern, new_posts_section, index_html, flags=re.DOTALL)
    
    # Update article count
    new_index = re.sub(
        r'<strong id="article-count">\d+</strong>',
        f'<strong id="article-count">{len(posts)}</strong>',
        new_index
    )
    
    # Write updated index
    with open(index_path, 'w', encoding='utf-8') as f:
        f.write(new_index)
    
    print(f"\nRebuilt index with {len(posts)} posts")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Rebuild Black Wing Dispatch index')
    parser.add_argument('--website-dir', required=True, help='Path to website repository root')
    args = parser.parse_args()
    rebuild_index(args.website_dir)
