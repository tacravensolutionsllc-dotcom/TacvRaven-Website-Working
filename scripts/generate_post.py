#!/usr/bin/env python3
"""
TacRaven Blog Post Generator
============================
Generates SEO-optimized blog posts in the TacRaven design style.

Usage:
    python generate_post.py --title "Post Title" --category "Getting Started" --output ./posts/
    python generate_post.py --config post_config.json
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION
# =============================================================================

SCRIPT_DIR = Path(__file__).parent
BLOG_ROOT = SCRIPT_DIR.parent

# Category colors (matches index page)
CATEGORY_COLORS = {
    "getting-started": "var(--green)",
    "certifications": "var(--orange)", 
    "salaries": "var(--blue)",
    "career-paths": "var(--purple)",
    "job-search": "var(--red)",
    "skills": "#1ABC9C",
    "industry-trends": "var(--gold)"
}

CATEGORY_NAMES = {
    "getting-started": "Getting Started",
    "certifications": "Certifications",
    "salaries": "Salaries", 
    "career-paths": "Career Paths",
    "job-search": "Job Search",
    "skills": "Skills",
    "industry-trends": "Industry Trends"
}

# =============================================================================
# LOGO BASE64 - Embedded circular shield logo
# =============================================================================

def get_logo_base64():
    """Load the logo base64 from file or return cached version."""
    b64_file = SCRIPT_DIR / "logo-base64.txt"
    if b64_file.exists():
        return b64_file.read_text().strip()
    return ""

# =============================================================================
# HTML TEMPLATE
# =============================================================================

def get_template():
    return '''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${title} | TacRaven Solutions</title>
    <meta name="description" content="${meta_description}">
    <link rel="canonical" href="https://tacraven.com/blog/posts/${year}/${month}/${slug}.html">
    
    <meta property="og:type" content="article">
    <meta property="og:title" content="${title}">
    <meta property="og:description" content="${meta_description}">
    <meta property="article:published_time" content="${iso_date}">
    
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Oswald:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap');
        
        :root {
            --gold:#D4A32A;--gold-light:#E8C45A;--gold-dim:rgba(212,163,42,0.15);
            --bg-darkest:#0A0A0A;--bg-dark:#0F0F0F;--bg-card:#141414;--bg-elevated:#1A1A1A;
            --text-primary:#FFF;--text-secondary:#B0B0B0;--text-muted:#666;
            --border-dark:#1F1F1F;--border-light:#2A2A2A;
            --red:#E74C3C;--green:#2ECC71;--blue:#3498DB;--orange:#F39C12;--purple:#9B59B6;
            --font-display:'Oswald',sans-serif;
            --font-body:'Inter',-apple-system,sans-serif;
        }
        
        *,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
        html{font-size:17px;scroll-behavior:smooth}
        body{font-family:var(--font-body);background:var(--bg-darkest);color:var(--text-primary);line-height:1.8;min-height:100vh}
        a{color:var(--gold);text-decoration:none;transition:color 0.2s}
        a:hover{color:var(--gold-light)}
        
        /* Header */
        .header{background:var(--bg-dark);border-bottom:1px solid var(--border-dark);height:70px;position:sticky;top:0;z-index:1000}
        .header-inner{max-width:1400px;margin:0 auto;padding:0 2rem;height:100%;display:flex;justify-content:space-between;align-items:center}
        .logo{font-family:var(--font-display);font-size:1.5rem;font-weight:600;letter-spacing:0.05em;color:var(--text-primary)}
        .logo span{color:var(--gold)}
        .nav{display:flex;align-items:center;gap:2rem}
        .nav a{font-size:0.9rem;font-weight:500;color:var(--text-secondary)}
        .nav a:hover,.nav a.active{color:var(--text-primary)}
        .nav-cta{background:var(--gold);color:var(--bg-darkest)!important;padding:0.6rem 1.25rem;border-radius:4px;font-weight:600;text-transform:uppercase;font-size:0.8rem;letter-spacing:0.05em}
        
        /* Hero Banner */
        .hero-banner{position:relative;background:var(--bg-dark);padding:3rem 2rem;overflow:hidden}
        .hero-banner::before{content:'';position:absolute;inset:0;background-image:linear-gradient(rgba(212,163,42,0.03) 1px,transparent 1px),linear-gradient(90deg,rgba(212,163,42,0.03) 1px,transparent 1px);background-size:50px 50px}
        .hero-inner{max-width:1100px;margin:0 auto;position:relative;z-index:1;display:grid;grid-template-columns:1fr auto;gap:3rem;align-items:center}
        .hero-content{max-width:700px}
        .hero-badge-img{width:240px;height:240px;object-fit:contain;filter:drop-shadow(0 0 30px rgba(212,163,42,0.4));animation:float 6s ease-in-out infinite;border-radius:50%;-webkit-mask-image:radial-gradient(circle,black 60%,transparent 100%);mask-image:radial-gradient(circle,black 60%,transparent 100%)}
        @keyframes float{0%,100%{transform:translateY(0)}50%{transform:translateY(-10px)}}
        
        .back-link{display:inline-flex;align-items:center;gap:0.5rem;font-size:0.85rem;font-weight:500;color:var(--text-muted);margin-bottom:1.5rem}
        .back-link:hover{color:var(--gold)}
        .back-link svg{width:16px;height:16px}
        
        .hero-meta{display:flex;align-items:center;gap:1rem;margin-bottom:1rem;flex-wrap:wrap}
        .hero-category{font-family:var(--font-display);font-size:0.7rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:var(--bg-darkest);padding:0.3rem 0.75rem;border-radius:3px}
        .hero-date{font-size:0.85rem;color:var(--text-muted)}
        .hero-read{font-size:0.85rem;color:var(--text-muted)}
        
        .hero-title{font-family:var(--font-display);font-size:3.5rem;font-weight:700;text-transform:uppercase;letter-spacing:0.03em;line-height:1.1;margin-bottom:1.25rem}
        .hero-title span{color:var(--gold)}
        .hero-subtitle{font-size:1.2rem;color:var(--text-secondary);line-height:1.6;max-width:700px}
        
        /* Stats Strip */
        .stats-strip{background:var(--bg-card);border-top:1px solid var(--border-dark);border-bottom:1px solid var(--border-dark);padding:1.5rem 2rem}
        .stats-inner{max-width:900px;margin:0 auto;display:grid;grid-template-columns:repeat(4,1fr);gap:2rem}
        .stat{text-align:center;position:relative}
        .stat:not(:last-child)::after{content:'';position:absolute;right:0;top:50%;transform:translateY(-50%);width:1px;height:60%;background:var(--border-dark)}
        .stat-value{font-family:var(--font-display);font-size:2rem;font-weight:700;color:var(--gold);line-height:1}
        .stat-label{font-size:0.7rem;color:var(--text-muted);text-transform:uppercase;letter-spacing:0.05em;margin-top:0.25rem}
        
        /* Article Content */
        .article-wrap{max-width:900px;margin:0 auto;padding:3rem 2rem}
        .content{font-size:1.05rem;line-height:1.9}
        .content p{margin-bottom:1.5rem;color:var(--text-secondary)}
        .content strong{color:var(--text-primary);font-weight:600}
        .content em{color:var(--text-secondary)}
        
        .content h2{font-family:var(--font-display);font-size:1.75rem;font-weight:600;text-transform:uppercase;letter-spacing:0.05em;color:var(--text-primary);margin-top:3rem;margin-bottom:1.5rem;display:flex;align-items:center;gap:1rem}
        .content h2::before{content:'';width:4px;height:100%;min-height:28px;background:var(--gold);border-radius:2px}
        
        .content h3{font-family:var(--font-display);font-size:1.1rem;font-weight:600;color:var(--gold);margin-top:2rem;margin-bottom:0.75rem;padding-left:1rem;border-left:2px solid var(--gold-dim)}
        
        .content ul,.content ol{margin-bottom:1.5rem;padding-left:0;list-style:none}
        .content li{margin-bottom:0.75rem;padding-left:1.5rem;position:relative;color:var(--text-secondary)}
        .content li::before{content:'';position:absolute;left:0;top:0.6rem;width:6px;height:6px;background:var(--gold);border-radius:50%}
        .content a{text-decoration:underline;text-underline-offset:3px}
        
        /* Callout Boxes */
        .callout{background:var(--bg-card);border:1px solid var(--border-dark);border-radius:8px;padding:1.5rem;margin:2rem 0;position:relative;overflow:hidden}
        .callout::before{content:'';position:absolute;left:0;top:0;bottom:0;width:4px;background:var(--gold)}
        .callout-icon{width:40px;height:40px;background:var(--gold-dim);border-radius:8px;display:flex;align-items:center;justify-content:center;margin-bottom:1rem}
        .callout-icon svg{width:20px;height:20px;stroke:var(--gold);fill:none}
        .callout-title{font-family:var(--font-display);font-size:0.9rem;font-weight:600;text-transform:uppercase;letter-spacing:0.1em;color:var(--gold);margin-bottom:0.5rem}
        .callout p{margin:0;color:var(--text-secondary);font-size:0.95rem}
        
        .callout.success::before{background:var(--green)}
        .callout.success .callout-icon{background:rgba(46,204,113,0.15)}
        .callout.success .callout-icon svg{stroke:var(--green)}
        .callout.success .callout-title{color:var(--green)}
        
        /* Data Cards Grid */
        .card-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:1rem;margin:2rem 0}
        .data-card{background:var(--bg-card);border:1px solid var(--border-dark);border-radius:8px;padding:1.25rem;transition:all 0.3s}
        .data-card:hover{border-color:var(--gold);transform:translateY(-2px)}
        .data-card h4{font-family:var(--font-display);font-size:0.95rem;font-weight:600;color:var(--text-primary);margin-bottom:0.5rem}
        .data-card .highlight{font-family:var(--font-display);font-size:1.25rem;font-weight:700;color:var(--gold);margin-bottom:0.5rem}
        .data-card p{font-size:0.85rem;color:var(--text-muted);margin:0;line-height:1.5}
        
        /* List Cards */
        .list-cards{margin:2rem 0}
        .list-card{display:flex;align-items:flex-start;gap:1rem;background:var(--bg-card);border:1px solid var(--border-dark);border-radius:8px;padding:1rem 1.25rem;margin-bottom:0.75rem;transition:border-color 0.3s}
        .list-card:hover{border-color:var(--gold)}
        .list-card-icon{width:36px;height:36px;background:var(--gold-dim);border-radius:6px;display:flex;align-items:center;justify-content:center;flex-shrink:0}
        .list-card-icon svg{width:18px;height:18px;stroke:var(--gold);fill:none}
        .list-card-info h5{font-family:var(--font-display);font-size:0.9rem;font-weight:600;color:var(--text-primary);margin-bottom:0.2rem}
        .list-card-info p{font-size:0.85rem;color:var(--text-muted);margin:0}
        
        /* Blockquote */
        blockquote{background:var(--bg-card);border:1px solid var(--border-dark);border-radius:8px;padding:1.5rem 1.5rem 1.5rem 2rem;margin:2rem 0;position:relative}
        blockquote::before{content:'"';position:absolute;left:1rem;top:0.5rem;font-family:var(--font-display);font-size:4rem;color:var(--gold-dim);line-height:1}
        blockquote p{margin:0;font-style:italic;color:var(--text-secondary);position:relative;z-index:1;padding-left:1rem}
        
        /* Article Footer */
        .article-footer{margin-top:3rem;padding-top:2rem;border-top:1px solid var(--border-dark)}
        .tags{display:flex;flex-wrap:wrap;gap:0.5rem;margin-bottom:2rem}
        .tag{font-size:0.75rem;font-weight:500;color:var(--text-muted);background:var(--bg-card);border:1px solid var(--border-dark);padding:0.4rem 0.75rem;border-radius:4px;transition:all 0.2s}
        .tag:hover{border-color:var(--gold);color:var(--gold)}
        
        .article-nav{display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem}
        .article-nav a{font-size:0.9rem;font-weight:500;color:var(--text-muted);display:flex;align-items:center;gap:0.5rem}
        .article-nav a:hover{color:var(--gold)}
        .article-nav svg{width:16px;height:16px}
        
        /* Author Box */
        .author-box{background:var(--bg-card);border:1px solid var(--border-dark);border-radius:8px;padding:1.5rem;margin-top:2rem;display:flex;gap:1.25rem;align-items:center}
        .author-avatar{width:60px;height:60px;background:linear-gradient(135deg,var(--gold),var(--gold-light));border-radius:8px;display:flex;align-items:center;justify-content:center;font-family:var(--font-display);font-weight:700;font-size:1.25rem;color:var(--bg-darkest);flex-shrink:0}
        .author-info h4{font-family:var(--font-display);font-size:1rem;font-weight:600;margin-bottom:0.25rem}
        .author-info p{font-size:0.85rem;color:var(--text-muted);margin:0;line-height:1.5}
        
        /* Footer */
        .footer{background:var(--bg-dark);border-top:1px solid var(--border-dark);padding:2rem;margin-top:3rem}
        .footer-inner{max-width:1400px;margin:0 auto;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:1rem}
        .footer-copy{font-size:0.85rem;color:var(--text-muted)}
        .footer-links{display:flex;gap:2rem}
        .footer-links a{font-size:0.85rem;color:var(--text-secondary)}
        
        /* Responsive */
        @media(max-width:900px){.hero-inner{grid-template-columns:1fr;text-align:center}.hero-badge-img{width:180px;height:180px;margin:0 auto}.hero-content{order:2}}
        @media(max-width:768px){.nav{display:none}.hero-title{font-size:2.25rem}.stats-inner{grid-template-columns:repeat(2,1fr);gap:1.5rem}.stat:not(:last-child)::after{display:none}.card-grid{grid-template-columns:1fr}.author-box{flex-direction:column;text-align:center}.footer-inner{flex-direction:column;text-align:center}}
    </style>
</head>
<body>
    <header class="header">
        <div class="header-inner">
            <a href="https://tacraven.com/" class="logo">TAC<span>RAVEN</span></a>
            <nav class="nav">
                <a href="https://tacraven.com/">Home</a>
                <a href="https://tacraven.com/learning-hub/">Learning Hub</a>
                <a href="https://tacraven.com/tools/">Tools</a>
                <a href="https://tacraven.com/threat-map/">Threat Map</a>
                <a href="https://tacraven.com/weekly-reports/">Weekly Reports</a>
                <a href="https://tacraven.com/about/">About</a>
                <a href="https://tacraven.com/pricing/">Pricing</a>
                <a href="/blog/" class="active">Careers</a>
                <a href="https://tacraven.com/contact/" class="nav-cta">Contact</a>
            </nav>
        </div>
    </header>
    
    <section class="hero-banner">
        <div class="hero-inner">
            <div class="hero-content">
                <a href="/blog/" class="back-link">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                    Back to Careers Blog
                </a>
                
                <div class="hero-meta">
                    <span class="hero-category" style="background:${category_color}">${category}</span>
                    <span class="hero-date">${readable_date}</span>
                    <span class="hero-read">• ${read_time} min read</span>
                </div>
                
                <h1 class="hero-title">${title_html}</h1>
                <p class="hero-subtitle">${subtitle}</p>
            </div>
            
            <img src="data:image/jpeg;base64,${logo_base64}" alt="" class="hero-badge-img">
        </div>
    </section>
    
    <div class="stats-strip">
        <div class="stats-inner">
${stats_html}
        </div>
    </div>
    
    <article class="article-wrap">
        <div class="content">
${content}
        </div>
        
        <footer class="article-footer">
            <div class="tags">
${tags_html}
            </div>
            
            <nav class="article-nav">
                <a href="/blog/">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                    Back to Blog
                </a>
            </nav>
        </footer>
        
        <aside class="author-box">
            <div class="author-avatar">TR</div>
            <div class="author-info">
                <h4>TacRaven Solutions</h4>
                <p>We build cybersecurity tools for organizations operating in disconnected, high-security environments. Learn more at <a href="https://tacraven.com">tacraven.com</a>.</p>
            </div>
        </aside>
    </article>
    
    <footer class="footer">
        <div class="footer-inner">
            <p class="footer-copy">© ${year} TacRaven Solutions LLC. All rights reserved.</p>
            <nav class="footer-links">
                <a href="https://tacraven.com/">Main Site</a>
                <a href="https://tacraven.com/privacy/">Privacy</a>
                <a href="https://tacraven.com/contact/">Contact</a>
            </nav>
        </div>
    </footer>
</body>
</html>'''

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def slugify(text):
    """Convert text to URL-friendly slug."""
    text = text.lower()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)
    return text.strip('-')

def estimate_read_time(content):
    """Estimate reading time in minutes."""
    word_count = len(re.sub(r'<[^>]+>', '', content).split())
    return max(1, round(word_count / 200))

def format_title_with_highlight(title, highlight_word=None):
    """Format title with optional highlighted word in gold."""
    if highlight_word and highlight_word.lower() in title.lower():
        pattern = re.compile(re.escape(highlight_word), re.IGNORECASE)
        return pattern.sub(f'<span>{highlight_word}</span>', title, count=1)
    # Default: highlight last significant word
    words = title.split()
    if len(words) > 2:
        words[-1] = f'<span>{words[-1]}</span>'
    return ' '.join(words)

def generate_stats_html(stats):
    """Generate stats strip HTML from list of (value, label) tuples."""
    html = ""
    for value, label in stats:
        html += f'''            <div class="stat">
                <div class="stat-value">{value}</div>
                <div class="stat-label">{label}</div>
            </div>
'''
    return html

def generate_tags_html(tags):
    """Generate tags HTML from list of tag strings."""
    return '\n'.join([f'                <span class="tag">{tag}</span>' for tag in tags])

# =============================================================================
# CONTENT COMPONENTS
# =============================================================================

def callout(title, content, style="default"):
    """Generate a callout box."""
    icon = '<svg viewBox="0 0 24 24" stroke-width="2"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5M2 12l10 5 10-5"/></svg>'
    if style == "success":
        icon = '<svg viewBox="0 0 24 24" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>'
    
    cls = "callout success" if style == "success" else "callout"
    return f'''
            <div class="{cls}">
                <div class="callout-icon">{icon}</div>
                <p class="callout-title">{title}</p>
                <p>{content}</p>
            </div>
'''

def data_cards(cards):
    """Generate a grid of data cards. cards = [(title, highlight, description), ...]"""
    html = '            <div class="card-grid">\n'
    for title, highlight, desc in cards:
        html += f'''                <div class="data-card">
                    <h4>{title}</h4>
                    <div class="highlight">{highlight}</div>
                    <p>{desc}</p>
                </div>
'''
    html += '            </div>\n'
    return html

def list_cards(items):
    """Generate list cards with icons. items = [(title, description), ...]"""
    icon = '<svg viewBox="0 0 24 24" stroke-width="2"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/><path d="M22 4L12 14.01l-3-3"/></svg>'
    html = '            <div class="list-cards">\n'
    for title, desc in items:
        html += f'''                <div class="list-card">
                    <div class="list-card-icon">{icon}</div>
                    <div class="list-card-info">
                        <h5>{title}</h5>
                        <p>{desc}</p>
                    </div>
                </div>
'''
    html += '            </div>\n'
    return html

def blockquote(text):
    """Generate a styled blockquote."""
    return f'''
            <blockquote>
                <p>{text}</p>
            </blockquote>
'''

# =============================================================================
# MAIN GENERATOR CLASS
# =============================================================================

class BlogPostGenerator:
    def __init__(self):
        self.logo_base64 = get_logo_base64()
        self.template = get_template()
    
    def generate(self, 
                 title,
                 subtitle,
                 category_slug,
                 content,
                 stats=None,
                 tags=None,
                 highlight_word=None,
                 date=None):
        """
        Generate a complete blog post.
        
        Args:
            title: Post title (will be uppercased)
            subtitle: Post subtitle/description
            category_slug: Category key (e.g., 'getting-started')
            content: HTML content for the article body
            stats: List of (value, label) tuples for stats strip
            tags: List of tag strings
            highlight_word: Word to highlight in gold in the title
            date: Publication date (datetime or 'YYYY-MM-DD' string)
        
        Returns:
            dict with 'html', 'slug', 'filepath' keys
        """
        # Parse date
        if date is None:
            date = datetime.now()
        elif isinstance(date, str):
            date = datetime.strptime(date, "%Y-%m-%d")
        
        year = date.strftime("%Y")
        month = date.strftime("%m")
        iso_date = date.strftime("%Y-%m-%d")
        readable_date = date.strftime("%B %d, %Y")
        
        # Category
        category = CATEGORY_NAMES.get(category_slug, "Getting Started")
        category_color = CATEGORY_COLORS.get(category_slug, "var(--green)")
        
        # Title formatting
        title_html = format_title_with_highlight(title, highlight_word)
        
        # Slug
        slug = slugify(title)
        
        # Read time
        read_time = estimate_read_time(content)
        
        # Meta description
        meta_description = subtitle[:155] + "..." if len(subtitle) > 155 else subtitle
        
        # Stats
        if stats is None:
            stats = [
                ("3.5M", "Unfilled Jobs"),
                ("33%", "Job Growth"),
                ("$124K", "Median Salary"),
                ("~0%", "Unemployment")
            ]
        stats_html = generate_stats_html(stats)
        
        # Tags
        if tags is None:
            tags = [category, "Cybersecurity", "Career"]
        tags_html = generate_tags_html(tags)
        
        # Build HTML
        html = self.template
        replacements = {
            '${title}': title,
            '${title_html}': title_html,
            '${subtitle}': subtitle,
            '${meta_description}': meta_description,
            '${category}': category,
            '${category_color}': category_color,
            '${year}': year,
            '${month}': month,
            '${slug}': slug,
            '${iso_date}': iso_date,
            '${readable_date}': readable_date,
            '${read_time}': str(read_time),
            '${stats_html}': stats_html,
            '${content}': content,
            '${tags_html}': tags_html,
            '${logo_base64}': self.logo_base64
        }
        
        for key, value in replacements.items():
            html = html.replace(key, value)
        
        return {
            'html': html,
            'slug': slug,
            'year': year,
            'month': month,
            'filepath': f"posts/{year}/{month}/{slug}.html"
        }
    
    def save(self, post_data, base_dir=None):
        """Save generated post to filesystem."""
        base_dir = Path(base_dir or BLOG_ROOT)
        
        # Create directory
        post_dir = base_dir / "posts" / post_data["year"] / post_data["month"]
        post_dir.mkdir(parents=True, exist_ok=True)
        
        # Write file
        filepath = base_dir / post_data["filepath"]
        filepath.write_text(post_data["html"], encoding="utf-8")
        
        return str(filepath)

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    # Example: Generate a sample post
    generator = BlogPostGenerator()
    
    # Build content using helper functions
    content = '''
            <p>This is an example blog post generated by the TacRaven blog generator. It demonstrates all the available styling components.</p>
            
            <h2>Section Heading</h2>
            
            <p>Regular paragraph text goes here. You can use <strong>bold text</strong> and <em>italic text</em> for emphasis. Links look like <a href="#">this example link</a>.</p>
            
            <h3>Subsection Heading</h3>
            
            <p>Subsections use a gold color with a left border accent.</p>
            
            <ul>
                <li>First bullet point item</li>
                <li>Second bullet point item</li>
                <li>Third bullet point item</li>
            </ul>
'''
    
    content += callout("Pro Tip", "This is a callout box for highlighting important information.")
    
    content += data_cards([
        ("SOC Analyst", "$55K - $75K", "Entry-level security operations role"),
        ("Security Engineer", "$90K - $130K", "Mid-level technical security role"),
    ])
    
    content += list_cards([
        ("CompTIA Security+", "Industry standard entry-level certification"),
        ("CySA+", "Advanced analyst certification for blue team roles"),
    ])
    
    content += blockquote("This is an important quote that stands out from the rest of the content.")
    
    content += callout("Ready to Start?", "Check out TalonPrep for free Security+ practice questions.", style="success")
    
    # Generate the post
    post = generator.generate(
        title="Example Blog Post Title",
        subtitle="This is an example subtitle that describes what the post is about.",
        category_slug="getting-started",
        content=content,
        tags=["Example", "Tutorial", "Getting Started"],
        highlight_word="Title"
    )
    
    print(f"Generated post: {post['filepath']}")
    print(f"Slug: {post['slug']}")
    
    # Uncomment to save:
    # filepath = generator.save(post)
    # print(f"Saved to: {filepath}")
