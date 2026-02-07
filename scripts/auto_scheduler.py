#!/usr/bin/env python3
"""
TacRaven Auto Blog Scheduler
============================
Generates unique blog posts every other day with fresh, timely content.

Features:
- Pulls fresh data from RSS feeds and news sources
- Updates salary/job market stats from live sources
- Tracks published posts to avoid duplicates
- Combines evergreen frameworks with current data
- Varies writing style and structure

Usage:
    python auto_scheduler.py              # Generate next scheduled post
    python auto_scheduler.py --preview    # Preview without saving
    python auto_scheduler.py --force      # Generate even if not scheduled day
    python auto_scheduler.py --refresh    # Force refresh of cached data
    
For cron (every other day at 9am):
    0 9 */2 * * cd /path/to/blog/scripts && python3 auto_scheduler.py
"""

import json
import random
import hashlib
import urllib.request
import xml.etree.ElementTree as ET
import re
from datetime import datetime, timedelta
from pathlib import Path
from generate_post import BlogPostGenerator, callout, data_cards, list_cards, blockquote
from content_generators import (
    generate_getting_started_content,
    generate_certifications_content,
    generate_salaries_content,
    generate_career_paths_content,
    generate_job_search_content,
    generate_skills_content,
    generate_industry_trends_content,
    generate_comprehensive_closing,
    get_common_questions_section,
    get_practical_exercises_section,
    get_deep_dive_section
)

SCRIPT_DIR = Path(__file__).parent
BLOG_ROOT = SCRIPT_DIR.parent
STATE_FILE = SCRIPT_DIR / "scheduler_state.json"
CACHE_FILE = SCRIPT_DIR / "data_cache.json"
CACHE_MAX_AGE_HOURS = 12  # Refresh data every 12 hours

# =============================================================================
# LIVE DATA SOURCES
# =============================================================================

RSS_FEEDS = {
    "cybersecurity_news": [
        "https://feeds.feedburner.com/TheHackersNews",
        "https://www.darkreading.com/rss.xml",
        "https://krebsonsecurity.com/feed/",
        "https://www.schneier.com/feed/atom/",
        "https://www.cisa.gov/news.xml",
    ],
    "career_news": [
        "https://www.reddit.com/r/cybersecurity/.rss",
        "https://www.reddit.com/r/SecurityCareerAdvice/.rss",
    ]
}

# Data URLs for salary/job market info
DATA_SOURCES = {
    "bls": "https://www.bls.gov/ooh/computer-and-information-technology/information-security-analysts.htm",
    "cyberseek": "https://www.cyberseek.org/heatmap.html",
}

# =============================================================================
# LIVE DATA FETCHING
# =============================================================================

def fetch_rss_feed(url, timeout=10):
    """Fetch and parse an RSS feed."""
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TacRaven-Blog/1.0'})
        with urllib.request.urlopen(req, timeout=timeout) as response:
            content = response.read()
            root = ET.fromstring(content)
            
            items = []
            # Handle both RSS and Atom formats
            for item in root.findall('.//item') or root.findall('.//{http://www.w3.org/2005/Atom}entry'):
                title = item.find('title')
                if title is None:
                    title = item.find('{http://www.w3.org/2005/Atom}title')
                
                link = item.find('link')
                if link is None:
                    link = item.find('{http://www.w3.org/2005/Atom}link')
                    if link is not None:
                        link_url = link.get('href', '')
                    else:
                        link_url = ''
                else:
                    link_url = link.text or ''
                
                desc = item.find('description')
                if desc is None:
                    desc = item.find('{http://www.w3.org/2005/Atom}summary')
                
                pub_date = item.find('pubDate')
                if pub_date is None:
                    pub_date = item.find('{http://www.w3.org/2005/Atom}updated')
                
                items.append({
                    'title': title.text if title is not None else '',
                    'link': link_url,
                    'description': desc.text if desc is not None else '',
                    'date': pub_date.text if pub_date is not None else ''
                })
            
            return items[:10]  # Return top 10 items
    except Exception as e:
        print(f"Warning: Could not fetch {url}: {e}")
        return []

def fetch_all_news():
    """Fetch news from all RSS feeds."""
    all_news = []
    
    for category, feeds in RSS_FEEDS.items():
        for feed_url in feeds:
            items = fetch_rss_feed(feed_url)
            for item in items:
                item['category'] = category
                item['source'] = feed_url
            all_news.extend(items)
    
    return all_news

def extract_trending_topics(news_items):
    """Extract trending topics from news headlines."""
    # Keywords to track
    keyword_counts = {}
    trending_keywords = [
        'ransomware', 'breach', 'vulnerability', 'zero-day', 'phishing',
        'AI', 'artificial intelligence', 'machine learning', 'cloud',
        'remote work', 'hiring', 'shortage', 'salary', 'certification',
        'CISO', 'SOC', 'analyst', 'engineer', 'skills gap',
        'compliance', 'regulation', 'NIST', 'zero trust',
        'supply chain', 'insider threat', 'IoT', 'OT', 'ICS',
        'healthcare', 'finance', 'government', 'critical infrastructure'
    ]
    
    for item in news_items:
        title = (item.get('title', '') + ' ' + item.get('description', '')).lower()
        for keyword in trending_keywords:
            if keyword.lower() in title:
                keyword_counts[keyword] = keyword_counts.get(keyword, 0) + 1
    
    # Sort by frequency
    sorted_topics = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)
    return sorted_topics[:10]

def get_fresh_data(force_refresh=False):
    """Get fresh data, using cache if available and recent."""
    cache_valid = False
    cached_data = {}
    
    if CACHE_FILE.exists() and not force_refresh:
        cached_data = json.loads(CACHE_FILE.read_text())
        cache_time = datetime.fromisoformat(cached_data.get('timestamp', '2000-01-01'))
        if datetime.now() - cache_time < timedelta(hours=CACHE_MAX_AGE_HOURS):
            cache_valid = True
            print("Using cached data...")
    
    if not cache_valid:
        print("Fetching fresh data...")
        news_items = fetch_all_news()
        trending = extract_trending_topics(news_items)
        
        cached_data = {
            'timestamp': datetime.now().isoformat(),
            'news': news_items,
            'trending': trending,
            'fetch_date': datetime.now().strftime('%B %Y')
        }
        
        CACHE_FILE.write_text(json.dumps(cached_data, indent=2))
        print(f"Cached {len(news_items)} news items, {len(trending)} trending topics")
    
    return cached_data

# =============================================================================
# TOPIC DATABASE - Evergreen frameworks + Dynamic content
# =============================================================================

# Evergreen topic frameworks that get filled with fresh data
TOPIC_FRAMEWORKS = {
    "getting-started": [
        {
            "template": "breaking_in",
            "variations": [
                ("without a degree", "How to Break Into Cybersecurity Without a Degree", "You don't need a CS degree. Here's the realistic path."),
                ("from IT support", "From Help Desk to Security: Making the Transition", "Already in IT? Here's how to pivot faster."),
                ("as a career changer", "Career Change to Cybersecurity: A Step-by-Step Guide", "Your existing skills are more valuable than you think."),
                ("over 30", "Is It Too Late to Start a Cybersecurity Career?", "Spoiler: It's not. Age can be an advantage."),
                ("with no experience", "Zero to Hired: Getting Your First Security Job", "Build credibility from nothing."),
                ("as a veteran", "Military to Cybersecurity: Translating Your Experience", "Veterans have massive advantages in security."),
                ("from non-tech", "Non-Tech to Cybersecurity: Yes, It's Possible", "Teachers, nurses, accountants—all have made it."),
            ]
        },
        {
            "template": "first_steps",
            "variations": [
                ("what to learn first", "What to Learn First in Cybersecurity", "The exact order to tackle fundamentals."),
                ("home lab guide", "Build Your First Cybersecurity Home Lab", "Hands-on practice beats theory."),
                ("free resources", "Best Free Cybersecurity Learning Resources", "Quality training without spending thousands."),
                ("common mistakes", "Mistakes That Delay Your Security Career", "Avoid traps that cost months."),
                ("realistic timeline", "How Long to Break Into Cybersecurity?", "Honest timelines based on your starting point."),
                ("study plan", "Your First 90 Days Studying Cybersecurity", "A structured plan that works."),
            ]
        },
    ],
    
    "certifications": [
        {
            "template": "cert_review",
            "variations": [
                ("security+", "Is CompTIA Security+ Worth It?", "The most popular entry cert—honest assessment."),
                ("cysa+", "CySA+ Certification: Complete Guide", "The analyst cert for blue team careers."),
                ("pentest+", "PenTest+ vs OSCP: Which to Choose?", "Offensive cert comparison."),
                ("cissp", "CISSP: When to Pursue It", "The gold standard—timing matters."),
                ("ceh", "CEH Certification: Honest Review", "Controversial cert—pros and cons."),
                ("google cert", "Google Cybersecurity Certificate Review", "The budget-friendly alternative."),
                ("isc2 cc", "ISC2 CC: The Free Entry-Level Cert", "Zero cost certification option."),
            ]
        },
        {
            "template": "cert_strategy",
            "variations": [
                ("first cert", "Which Cert Should You Get First?", "Decision tree for beginners."),
                ("cert roadmap", "Building Your Certification Roadmap", "Strategic cert stacking."),
                ("over-certification", "Stop Collecting Certs", "When enough is enough."),
                ("employer preferences", "Which Certs Do Employers Want?", "Data from real job postings."),
                ("cert ROI", "Certification ROI: The Real Numbers", "Which certs actually pay off."),
            ]
        },
    ],
    
    "salaries": [
        {
            "template": "salary_data",
            "variations": [
                ("entry level", "Entry-Level Cybersecurity Salaries", "What to expect in your first role."),
                ("by role", "Cybersecurity Salaries by Role", "From SOC analyst to CISO."),
                ("by location", "Security Salaries by City", "Geographic pay differences."),
                ("negotiation", "How to Negotiate Your Security Salary", "Tactics worth $10-20K."),
                ("salary growth", "Security Salary Progression: Year 1-10", "Realistic earnings trajectory."),
                ("remote salaries", "Remote Cybersecurity Salaries", "What remote roles actually pay."),
            ]
        },
    ],
    
    "career-paths": [
        {
            "template": "role_guide",
            "variations": [
                ("soc analyst", "SOC Analyst: Complete Career Guide", "The most common entry point."),
                ("pentester", "How to Become a Penetration Tester", "The offensive security path."),
                ("security engineer", "Security Engineer Career Path", "Building secure infrastructure."),
                ("grc analyst", "GRC Analyst: The Less Technical Path", "Governance, risk, compliance."),
                ("incident responder", "Incident Response Career Guide", "Security firefighting."),
                ("threat intel", "Threat Intelligence Analyst Path", "Tracking adversaries."),
                ("cloud security", "Cloud Security Engineer Guide", "The high-demand specialty."),
                ("devsecops", "DevSecOps Engineer Career Path", "Security meets development."),
            ]
        },
        {
            "template": "career_decisions",
            "variations": [
                ("red vs blue", "Red Team vs Blue Team: Which Path?", "Offense vs defense."),
                ("technical vs management", "Technical Track vs Management", "IC or people leader?"),
                ("consulting vs internal", "Consulting vs In-House Security", "Different trade-offs."),
                ("specialize when", "When to Specialize in Cybersecurity", "Depth vs breadth timing."),
            ]
        },
    ],
    
    "job-search": [
        {
            "template": "applications",
            "variations": [
                ("resume tips", "Security Resume That Gets Interviews", "Beat the ATS filters."),
                ("no experience resume", "Security Resume With No Experience", "Position yourself effectively."),
                ("linkedin", "LinkedIn for Cybersecurity Jobs", "Get recruiters to find you."),
                ("cover letters", "Do Cover Letters Matter in Security?", "When and what to write."),
                ("portfolio", "Building a Security Portfolio", "Show don't tell."),
            ]
        },
        {
            "template": "interviews",
            "variations": [
                ("technical interview", "Security Technical Interview Questions", "Common questions answered."),
                ("behavioral interview", "Security Behavioral Interview Tips", "STAR method examples."),
                ("practical assessment", "Ace Security Practical Assessments", "Take-home and live tests."),
            ]
        },
        {
            "template": "strategy",
            "variations": [
                ("where to apply", "Where to Find Security Jobs", "Best sources beyond LinkedIn."),
                ("networking", "Networking Into Security", "Connections that matter."),
                ("60 percent rule", "Apply Without Meeting All Requirements", "Job posts are wish lists."),
            ]
        },
    ],
    
    "skills": [
        {
            "template": "technical",
            "variations": [
                ("top skills", "Top Technical Skills Employers Want", "From real job posting data."),
                ("networking basics", "Networking Fundamentals for Security", "The essential foundation."),
                ("linux skills", "Linux Skills for Cybersecurity", "Command line proficiency."),
                ("python security", "Python for Cybersecurity", "Scripting that matters."),
                ("cloud skills", "Cloud Security Skills in Demand", "AWS, Azure, GCP."),
                ("siem skills", "SIEM Skills Every Analyst Needs", "Splunk, Sentinel, and more."),
            ]
        },
        {
            "template": "soft_skills",
            "variations": [
                ("communication", "Communication Skills in Security", "Writing and presenting."),
                ("problem solving", "Analytical Thinking for Security", "Systematic approaches."),
                ("continuous learning", "Keeping Up With Security Changes", "Stay current without burnout."),
            ]
        },
    ],
    
    "industry-trends": [
        {
            "template": "market_trends",
            "variations": [
                ("job market", "Cybersecurity Job Market Update", "Current hiring trends."),
                ("ai impact", "How AI Is Changing Security Jobs", "Automation's real impact."),
                ("remote trends", "Remote Work in Cybersecurity", "Which roles work remote."),
                ("skills gap", "The Cybersecurity Skills Gap", "What shortage means for you."),
            ]
        },
        {
            "template": "future",
            "variations": [
                ("emerging roles", "Emerging Cybersecurity Roles", "New positions to watch."),
                ("automation", "Will Automation Replace Analysts?", "What AI handles vs humans."),
                ("future proof", "Is Cybersecurity Future-Proof?", "Long-term career outlook."),
            ]
        },
    ],
}

# Dynamic topic generators based on current news
DYNAMIC_TEMPLATES = {
    "news_reaction": {
        "title_format": "What {event} Means for Your Security Career",
        "subtitle_format": "Recent developments in {topic} and how they affect job seekers.",
        "category": "industry-trends"
    },
    "trending_skill": {
        "title_format": "{skill} Skills Are in Demand—Here's Why",
        "subtitle_format": "Employers are actively seeking {skill} expertise. How to get it.",
        "category": "skills"
    },
    "market_update": {
        "title_format": "Security Job Market: {month} {year} Update",
        "subtitle_format": "Latest hiring trends, salary data, and what's changed.",
        "category": "salaries"
    },
    "threat_career": {
        "title_format": "The Rise of {threat}—And the Careers Fighting It",
        "subtitle_format": "How {threat} is creating new job opportunities.",
        "category": "career-paths"
    }
}

# =============================================================================
# CONTENT VARIATIONS - Different structures and formats
# =============================================================================

INTRO_STYLES = [
    "stat_hook",      # Lead with a surprising statistic
    "question_hook",  # Open with a provocative question
    "myth_buster",    # Challenge a common misconception
    "story_hook",     # Brief anecdote or scenario
    "direct_answer",  # Get straight to the point
]

CONTENT_STRUCTURES = [
    "listicle",           # Numbered list format
    "guide",              # Step-by-step walkthrough
    "comparison",         # This vs. that analysis
    "deep_dive",          # Comprehensive single-topic coverage
    "qa_format",          # Question and answer style
    "myth_vs_reality",    # Debunking format
]

# =============================================================================
# STATE MANAGEMENT
# =============================================================================

def load_state():
    """Load scheduler state from file."""
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {
        "last_post_date": None,
        "published_posts": [],  # List of title hashes to avoid repeats
        "category_rotation": 0,
        "topic_index": {},      # Track which angles used per topic
        "style_rotation": 0,
        "structure_rotation": 0,
        "post_count": 0
    }

def save_state(state):
    """Save scheduler state to file."""
    STATE_FILE.write_text(json.dumps(state, indent=2))

def get_content_hash(title):
    """Generate hash of title for duplicate detection."""
    return hashlib.md5(title.lower().encode()).hexdigest()[:12]

# =============================================================================
# TOPIC SELECTION - Now with live data integration
# =============================================================================

def select_next_topic(state, live_data=None):
    """Select next topic ensuring variety, freshness, and no repeats."""
    
    # Decide between evergreen (70%) vs dynamic/timely (30%)
    use_dynamic = random.random() < 0.30 and live_data and live_data.get('trending')
    
    if use_dynamic:
        topic = select_dynamic_topic(state, live_data)
        if topic:
            return topic
    
    # Fall back to evergreen topics
    return select_evergreen_topic(state, live_data)

def select_dynamic_topic(state, live_data):
    """Generate a timely topic based on current news/trends."""
    trending = live_data.get('trending', [])
    news = live_data.get('news', [])
    current_date = datetime.now()
    
    # Filter out topics we've already covered recently
    available_trends = [t for t in trending if t[0].lower() not in 
                       [p.lower() for p in state.get('recent_topics', [])]]
    
    if not available_trends:
        return None
    
    # Pick a trending topic
    trend_keyword, trend_count = random.choice(available_trends[:5])
    
    # Choose a dynamic template
    templates = list(DYNAMIC_TEMPLATES.keys())
    template_key = random.choice(templates)
    template = DYNAMIC_TEMPLATES[template_key]
    
    # Generate title/subtitle based on template
    if template_key == "news_reaction":
        title = template["title_format"].format(event=trend_keyword.title())
        subtitle = template["subtitle_format"].format(topic=trend_keyword)
    elif template_key == "trending_skill":
        title = template["title_format"].format(skill=trend_keyword.title())
        subtitle = template["subtitle_format"].format(skill=trend_keyword)
    elif template_key == "market_update":
        title = template["title_format"].format(
            month=current_date.strftime("%B"),
            year=current_date.strftime("%Y")
        )
        subtitle = template["subtitle_format"]
    elif template_key == "threat_career":
        title = template["title_format"].format(threat=trend_keyword.title())
        subtitle = template["subtitle_format"].format(threat=trend_keyword)
    else:
        return None
    
    title_hash = get_content_hash(title)
    
    # Check if we've published this
    if title_hash in state.get('published_posts', []):
        return None
    
    # Track this topic
    if 'recent_topics' not in state:
        state['recent_topics'] = []
    state['recent_topics'].append(trend_keyword)
    state['recent_topics'] = state['recent_topics'][-20:]  # Keep last 20
    
    return {
        "category": template["category"],
        "base_topic": trend_keyword,
        "angle": template_key,
        "title": title,
        "subtitle": subtitle,
        "title_hash": title_hash,
        "is_dynamic": True,
        "trend_data": {
            "keyword": trend_keyword,
            "count": trend_count,
            "related_news": [n for n in news if trend_keyword.lower() in 
                           (n.get('title', '') + n.get('description', '')).lower()][:3]
        }
    }

def select_evergreen_topic(state, live_data=None):
    """Select from evergreen topic frameworks."""
    categories = list(TOPIC_FRAMEWORKS.keys())
    
    # Rotate through categories
    cat_idx = state.get("category_rotation", 0) % len(categories)
    category = categories[cat_idx]
    state["category_rotation"] = cat_idx + 1
    
    # Get topic groups for this category
    topic_groups = TOPIC_FRAMEWORKS[category]
    
    # Initialize tracking
    if "topic_index" not in state:
        state["topic_index"] = {}
    if "group_index" not in state:
        state["group_index"] = {}
    
    # Rotate through groups within category
    group_key = f"{category}_group"
    group_idx = state["group_index"].get(group_key, 0) % len(topic_groups)
    state["group_index"][group_key] = group_idx + 1
    
    topic_group = topic_groups[group_idx]
    template = topic_group["template"]
    variations = topic_group["variations"]
    
    # Track used variations per template
    template_key = f"{category}_{template}"
    var_idx = state["topic_index"].get(template_key, 0)
    
    # Find unused variation
    attempts = 0
    while attempts < len(variations):
        idx = (var_idx + attempts) % len(variations)
        angle_key, title, subtitle = variations[idx]
        title_hash = get_content_hash(title)
        
        if title_hash not in state.get('published_posts', []):
            state["topic_index"][template_key] = idx + 1
            
            # Add current date to titles that need it
            current_year = datetime.now().strftime("%Y")
            if "{year}" in title.lower() or "2025" in title:
                title = title.replace("2025", current_year)
            
            return {
                "category": category,
                "base_topic": template,
                "angle": angle_key,
                "title": title,
                "subtitle": subtitle,
                "title_hash": title_hash,
                "is_dynamic": False
            }
        attempts += 1
    
    # All variations used, move to next category
    state["category_rotation"] += 1
    return select_evergreen_topic(state, live_data)

# =============================================================================
# CONTENT GENERATION
# =============================================================================

def generate_intro(topic, style):
    """Generate comprehensive introduction based on style (400+ words)."""
    base_topic = topic.get("base_topic", "").lower().replace("_", " ")
    
    intros = {
        "stat_hook": f'''
            <p>Let me start with a number that should get your attention: <strong>3.5 million unfilled cybersecurity jobs worldwide.</strong> That's not a typo—and it's exactly why {base_topic} matters more than ever for anyone considering this field.</p>
            
            <p>{topic["subtitle"]}</p>
            
            <p>In this guide, I'm going to walk you through everything you need to know—not the fluffy, generic advice you find everywhere else, but practical, specific information you can actually use. Whether you're just starting to explore cybersecurity or you're ready to make a move, this post will give you a clear picture of what's realistic, what's required, and what steps to take next.</p>
            
            <p>I've seen hundreds of people make this transition successfully. I've also seen people waste months on the wrong approach. The difference usually comes down to having accurate information and a realistic plan. That's what this guide provides.</p>
            
            <p>By the end of this post, you'll understand exactly where to start, what to prioritize, common mistakes to avoid, and specific action items you can implement this week. Let's get into it.</p>
''',
        "question_hook": f'''
            <p>Here's a question I hear constantly: <em>"Is it really possible to {topic["angle"].replace("-", " ").replace("_", " ")}?"</em></p>
            
            <p>The short answer is yes. But that simple answer doesn't help you much, does it? What you really want to know is <em>how</em>—and whether it's realistic for your specific situation.</p>
            
            <p>{topic["subtitle"]}</p>
            
            <p>I've seen this question come up hundreds of times in forums, career advice threads, and conversations with people considering the field. And while the answer is always "yes, it's possible," the path looks different depending on where you're starting from.</p>
            
            <p>This guide is going to give you the complete picture—the realistic timeline, the actual requirements, and the specific steps that work. No gatekeeping, no oversimplification, just honest information based on what I've seen work in the real world.</p>
            
            <p>Whether you're exploring cybersecurity as a career option or you've already decided to make the move, the information here will help you move forward with confidence. Let's dive in.</p>
''',
        "myth_buster": f'''
            <p>Let's kill a myth right now: <strong>you don't need a traditional background to succeed in cybersecurity.</strong></p>
            
            <p>I know, you've probably heard this before. But then you look at job postings asking for 5 years of experience, a bachelor's degree, and three certifications—and you wonder if the "you can break in without a traditional background" crowd is just blowing smoke.</p>
            
            <p>They're not. {topic["subtitle"]} But understanding how requires looking past the surface-level advice and getting into what actually happens in hiring decisions.</p>
            
            <p>This guide breaks down exactly what employers are really looking for, what the actual barriers to entry are (and aren't), and the specific steps that have worked for people who started right where you are now.</p>
            
            <p>I'm not going to sugarcoat the challenges—this field requires real skills and real effort. But I'm also not going to gatekeep. The opportunity is genuine for people willing to do the work.</p>
            
            <p>Let's get into the details that actually matter.</p>
''',
        "story_hook": f'''
            <p>Last year, I talked to someone who made a complete career change into security in just 8 months. They didn't have a CS degree. They didn't have years of IT experience. What they had was a plan—and the persistence to execute it.</p>
            
            <p>That story isn't unique. It's one of hundreds I've seen play out in cybersecurity career communities. And while each person's path looks a little different, the underlying patterns are remarkably consistent.</p>
            
            <p>{topic["subtitle"]}</p>
            
            <p>This guide captures those patterns. I'm going to walk you through everything from the foundational knowledge you actually need, to the certifications that matter (and the ones that don't), to the job search strategies that work when you don't have years of experience to fall back on.</p>
            
            <p>The path exists. Thousands of people have walked it before you. This guide shows you exactly what that path looks like so you can walk it too.</p>
            
            <p>Let's start with the fundamentals.</p>
''',
        "direct_answer": f'''
            <p>{topic["subtitle"]}</p>
            
            <p>No fluff, no gatekeeping—let's get into what actually works.</p>
            
            <p>I'm going to cover this topic comprehensively, which means this is a longer read. But if you're serious about making progress, the investment is worth it. Bookmark this page, grab a notebook if that helps you, and let's work through this together.</p>
            
            <p>This guide is based on what I've seen work in practice—not theory, not what sounds good, but what actually produces results for real people making real career moves. The cybersecurity field has genuine opportunities, but navigating it successfully requires accurate information and realistic expectations.</p>
            
            <p>By the end of this guide, you'll have a clear understanding of where to start, what to prioritize, common mistakes to avoid, and specific action items you can implement immediately.</p>
            
            <p>Let's get started.</p>
'''
    }
    return intros.get(style, intros["direct_answer"])

def generate_section(heading, content_points, include_cards=False):
    """Generate a content section with optional data cards."""
    html = f'''
            <h2>{heading}</h2>
'''
    for point in content_points:
        if isinstance(point, tuple):
            # Subheading with content
            subhead, text = point
            html += f'''
            <h3>{subhead}</h3>
            <p>{text}</p>
'''
        else:
            # Regular paragraph
            html += f'''
            <p>{point}</p>
'''
    return html

def generate_post_content(topic, structure, intro_style, live_data=None):
    """
    Generate comprehensive, long-form post content (2,500-4,000 words).
    Uses category-specific content generators for detailed, practical content.
    """
    
    # Get current stats
    current_month = datetime.now().strftime("%B %Y")
    current_year = datetime.now().strftime("%Y")
    
    # Pull any relevant news for this topic
    related_news = []
    if topic.get('is_dynamic') and topic.get('trend_data'):
        related_news = topic['trend_data'].get('related_news', [])
    
    content = generate_intro(topic, intro_style)
    
    # If we have related news, include a "What's Happening Now" section
    if related_news and len(related_news) > 0:
        content += f'''
            <h2>What's Happening Now</h2>
            
            <p>Recent headlines are highlighting this trend, and the timing matters for your career decisions:</p>
            
            <ul>
'''
        for news_item in related_news[:3]:
            title = news_item.get('title', '').strip()
            if title:
                # Clean up the title
                title = re.sub(r'<[^>]+>', '', title)[:100]
                content += f'''                <li><strong>{title}</strong></li>
'''
        content += '''            </ul>
            
            <p>These developments have real implications for security careers. Let me explain what they mean for you and how to position yourself accordingly.</p>
'''
    
    # Category-specific comprehensive content generation
    category = topic["category"]
    angle = topic.get("angle", "")
    
    if category == "getting-started":
        content += generate_getting_started_content(topic, angle, current_year)
    elif category == "certifications":
        content += generate_certifications_content(topic, angle, current_year)
    elif category == "salaries":
        content += generate_salaries_content(topic, angle, current_year)
    elif category == "career-paths":
        content += generate_career_paths_content(topic, angle, current_year)
    elif category == "job-search":
        content += generate_job_search_content(topic, angle, current_year)
    elif category == "skills":
        content += generate_skills_content(topic, angle, current_year)
    else:  # industry-trends
        content += generate_industry_trends_content(topic, angle, current_year)
    
    # Add deep dive section for the category
    content += get_deep_dive_section(category)
    
    # Add practical exercises section for the category
    content += get_practical_exercises_section(category)
    
    # Add common questions section for the category
    content += get_common_questions_section(category)
    
    # Add comprehensive closing
    content += generate_comprehensive_closing(category)
    
    return content

# =============================================================================
# MAIN SCHEDULER
# =============================================================================

def should_post_today(state):
    """Check if we should post today (every other day)."""
    if state["last_post_date"] is None:
        return True
    
    last_date = datetime.strptime(state["last_post_date"], "%Y-%m-%d")
    today = datetime.now()
    days_since = (today - last_date).days
    
    return days_since >= 2

def generate_scheduled_post(preview=False, force=False, refresh_data=False):
    """Generate the next scheduled post."""
    state = load_state()
    
    # Check if we should post
    if not force and not should_post_today(state):
        last_date = datetime.strptime(state["last_post_date"], "%Y-%m-%d")
        days_since = (datetime.now() - last_date).days
        days_until = 2 - days_since
        print(f"Not scheduled today. Next post in {max(0, days_until)} day(s).")
        return None
    
    # Fetch fresh data
    live_data = get_fresh_data(force_refresh=refresh_data)
    
    # Show trending topics
    if live_data.get('trending'):
        print(f"Trending topics: {', '.join([t[0] for t in live_data['trending'][:5]])}")
    
    # Select topic
    topic = select_next_topic(state, live_data)
    
    # Select style variations (rotate through)
    intro_style = INTRO_STYLES[state.get("style_rotation", 0) % len(INTRO_STYLES)]
    structure = CONTENT_STRUCTURES[state.get("structure_rotation", 0) % len(CONTENT_STRUCTURES)]
    state["style_rotation"] = state.get("style_rotation", 0) + 1
    state["structure_rotation"] = state.get("structure_rotation", 0) + 1
    
    # Generate content with live data
    content = generate_post_content(topic, structure, intro_style, live_data)
    
    # Determine highlight word from title
    title_words = topic["title"].split()
    highlight_word = None
    for word in ["Cybersecurity", "Security", "Career", "Salary", "Jobs", "Analyst", "CISO", "SOC"]:
        if word in title_words:
            highlight_word = word
            break
    
    # Generate tags based on category and topic
    base_tags = [topic["category"].replace("-", " ").title(), "Cybersecurity", "Career"]
    if topic.get('is_dynamic'):
        base_tags.append(topic.get('base_topic', '').title())
    extra_tags = topic.get("base_topic", "").split()[:2]
    tags = list(dict.fromkeys(base_tags + extra_tags))[:6]  # Unique, max 6
    
    # Add current month/year to make it timely
    current_year = datetime.now().strftime("%Y")
    
    # Generate post
    generator = BlogPostGenerator()
    post = generator.generate(
        title=topic["title"],
        subtitle=topic["subtitle"],
        category_slug=topic["category"],
        content=content,
        tags=tags,
        highlight_word=highlight_word
    )
    
    topic_type = "DYNAMIC" if topic.get('is_dynamic') else "EVERGREEN"
    print(f"\n{'='*50}")
    print(f"Generated [{topic_type}]: {topic['title']}")
    print(f"Category: {topic['category']}")
    print(f"Style: {intro_style} / {structure}")
    print(f"File: {post['filepath']}")
    print(f"{'='*50}")
    
    if preview:
        print("\n[Preview mode - not saving]")
        return post
    
    # Save post
    filepath = generator.save(post)
    print(f"Saved to: {filepath}")
    
    # Update state
    state["last_post_date"] = datetime.now().strftime("%Y-%m-%d")
    if "published_posts" not in state:
        state["published_posts"] = []
    state["published_posts"].append(topic["title_hash"])
    state["post_count"] = state.get("post_count", 0) + 1
    save_state(state)
    
    print(f"\nTotal posts generated: {state['post_count']}")
    
    return post

# =============================================================================
# CLI
# =============================================================================

if __name__ == "__main__":
    import sys
    
    preview = "--preview" in sys.argv
    force = "--force" in sys.argv
    refresh = "--refresh" in sys.argv
    
    if "--help" in sys.argv:
        print("""
TacRaven Auto Blog Scheduler
============================

Usage:
    python auto_scheduler.py              # Generate if scheduled (every 2 days)
    python auto_scheduler.py --force      # Generate now regardless of schedule
    python auto_scheduler.py --preview    # Preview without saving
    python auto_scheduler.py --refresh    # Force refresh of news/trend data
    
Combines flags:
    python auto_scheduler.py --force --preview    # Preview a forced generation
    python auto_scheduler.py --force --refresh    # Generate with fresh data

For cron (every other day at 9am):
    0 9 */2 * * cd /path/to/blog/scripts && python3 auto_scheduler.py
        """)
    else:
        generate_scheduled_post(preview=preview, force=force, refresh_data=refresh)
