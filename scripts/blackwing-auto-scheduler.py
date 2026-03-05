#!/usr/bin/env python3
"""
Black Wing Dispatch - Auto Scheduler
TacRaven Solutions LLC

Generates blog posts on schedule without API dependencies.
Uses topic rotation, category modules, and RSS trends.

Schedule: Every 3 days
Estimated content duration: 2.5 - 5 years
"""

import json
import os
import hashlib
import random
from datetime import datetime, timedelta
from pathlib import Path
import urllib.request
import xml.etree.ElementTree as ET

# Configuration
CONFIG = {
    "site_url": "https://tacravensolutions.com",
    "posts_dir": "intel/posts",
    "manifest_file": "intel/posts/posts.json",
    "state_file": "scheduler_state.json",
    "rss_cache_file": "data_cache.json",
    "trend_probability": 0.3,
    "posting_interval_days": 3,  # Post every 3 days
    "rss_feeds": [
        "https://www.cisa.gov/cybersecurity-advisories/all.xml",
        "https://feeds.feedburner.com/TheHackersNews",
        "https://www.bleepingcomputer.com/feed/",
        "https://krebsonsecurity.com/feed/",
    ]
}

# Topic categories with evergreen topics
CATEGORIES = {
    "APT Activity": [
        "Nation-State Threat Actors Targeting Critical Infrastructure",
        "APT Techniques for Initial Access in Enterprise Networks",
        "Living Off the Land: How APTs Avoid Detection",
        "Supply Chain Compromises by Advanced Threat Groups",
        "Credential Harvesting Techniques Used by State Actors",
        "APT Persistence Mechanisms in Windows Environments",
        "Command and Control Infrastructure Patterns",
        "Lateral Movement Techniques in Targeted Attacks",
    ],
    "Ransomware": [
        "Ransomware Affiliate Programs and Their Evolution",
        "Double Extortion Tactics in Modern Ransomware",
        "Ransomware Initial Access Vectors to Watch",
        "Defending Against Ransomware in Healthcare",
        "Ransomware Recovery Planning and Execution",
        "The Business Model Behind Ransomware Operations",
        "Ransomware Targeting Industrial Control Systems",
        "Negotiation Tactics and Ransomware Payments",
    ],
    "Vulnerability": [
        "Critical Vulnerabilities in Network Edge Devices",
        "Zero-Day Exploitation Trends and Defense",
        "Patch Management Strategies for Enterprise",
        "Vulnerability Prioritization Using EPSS and KEV",
        "Browser Vulnerabilities and Exploitation Chains",
        "Cloud Service Vulnerabilities and Misconfigurations",
        "Authentication Bypass Vulnerabilities in Enterprise Software",
        "Memory Corruption Vulnerabilities in 2026",
    ],
    "Supply Chain": [
        "Open Source Dependency Risks and Mitigation",
        "Software Supply Chain Attack Methodologies",
        "Protecting CI/CD Pipelines from Compromise",
        "Third-Party Risk Management for Security Teams",
        "Detecting Malicious Packages in Package Managers",
        "Hardware Supply Chain Security Considerations",
        "Code Signing and Software Integrity Verification",
        "Vendor Security Assessment Best Practices",
    ],
    "Threat Actor": [
        "Financially Motivated Threat Groups to Watch",
        "Hacktivism and Its Impact on Organizations",
        "Initial Access Brokers and the Cybercrime Ecosystem",
        "Threat Actor Infrastructure and Operational Patterns",
        "Attribution Challenges in Cyber Threat Analysis",
        "Emerging Threat Groups and Their Capabilities",
        "Cybercrime Forums and Underground Markets",
        "Threat Actor Tool Development Trends",
    ],
    "Industrial Control": [
        "ICS Security in the Energy Sector",
        "Protecting Water and Wastewater Systems",
        "OT Network Segmentation Best Practices",
        "Remote Access Security for Industrial Environments",
        "ICS Protocol Vulnerabilities and Mitigations",
        "Safety System Security in Critical Infrastructure",
        "Legacy System Protection in OT Environments",
        "Incident Response for Industrial Control Systems",
    ],
    "Cloud Security": [
        "Cloud Identity and Access Management Hardening",
        "Detecting Threats in Cloud Environments",
        "Kubernetes Security Fundamentals",
        "Cloud Storage Security and Data Protection",
        "Serverless Security Considerations",
        "Multi-Cloud Security Architecture",
        "Cloud Logging and Monitoring Strategies",
        "Container Security Best Practices",
    ],
    "Defense": [
        "Detection Engineering for Modern Threats",
        "Building an Effective Threat Hunting Program",
        "Security Operations Center Optimization",
        "Endpoint Detection and Response Deployment",
        "Network Security Monitoring Fundamentals",
        "Incident Response Planning and Execution",
        "Security Awareness Training That Works",
        "Purple Team Exercises for Security Validation",
    ],
}

# Intro variations for content rotation
INTRO_VARIATIONS = [
    "Welcome back to Dark Wing Dispatch. This week I want to dig into {topic} because recent public reporting has caught my attention.",
    "Dark Wing Dispatch here. {topic} has been generating significant discussion in the security community lately, and I want to share my perspective.",
    "This week on Dark Wing Dispatch, I am focusing on {topic}. Based on recent advisories and disclosures, this deserves attention.",
    "Welcome to another edition of Dark Wing Dispatch. Today I am covering {topic}, a subject that has implications for organizations across sectors.",
    "Dark Wing Dispatch checking in. {topic} is something every security team should be thinking about right now.",
]

# Structure variations
STRUCTURE_VARIATIONS = [
    ["introduction", "background", "technical_breakdown", "indicators", "attack_patterns", "impact", "recommendations", "conclusion", "resources"],
    ["introduction", "background", "technical_breakdown", "attack_patterns", "indicators", "impact", "recommendations", "conclusion", "resources"],
    ["introduction", "technical_breakdown", "background", "indicators", "attack_patterns", "recommendations", "impact", "conclusion", "resources"],
]


def load_state():
    """Load scheduler state from file."""
    if os.path.exists(CONFIG["state_file"]):
        with open(CONFIG["state_file"], "r") as f:
            return json.load(f)
    return {
        "published_posts": [],
        "category_rotation": 0,
        "topic_rotation": {},
        "last_run": None,
        "intro_rotation": 0,
        "structure_rotation": 0,
    }


def save_state(state):
    """Save scheduler state to file."""
    with open(CONFIG["state_file"], "w") as f:
        json.dump(state, f, indent=2)


def get_post_hash(title):
    """Generate hash for duplicate detection."""
    return hashlib.md5(title.lower().encode()).hexdigest()[:12]


def fetch_rss_trends():
    """Fetch trending topics from RSS feeds."""
    trends = []
    
    for feed_url in CONFIG["rss_feeds"]:
        try:
            req = urllib.request.Request(
                feed_url,
                headers={"User-Agent": "TacRaven-DarkWingDispatch/1.0"}
            )
            with urllib.request.urlopen(req, timeout=10) as response:
                content = response.read()
                root = ET.fromstring(content)
                
                # Handle both RSS and Atom feeds
                items = root.findall(".//item") or root.findall(".//{http://www.w3.org/2005/Atom}entry")
                
                for item in items[:5]:
                    title = item.find("title")
                    if title is None:
                        title = item.find("{http://www.w3.org/2005/Atom}title")
                    
                    if title is not None and title.text:
                        trends.append({
                            "title": title.text.strip(),
                            "source": feed_url,
                        })
        except Exception as e:
            print(f"Warning: Could not fetch {feed_url}: {e}")
    
    return trends


def extract_trend_topic(trends, state):
    """Extract a topic from trends that has not been covered."""
    keywords = [
        "ransomware", "apt", "vulnerability", "cve", "breach", "attack",
        "malware", "phishing", "zero-day", "exploit", "critical", "warning",
        "advisory", "threat", "hacker", "compromise", "infrastructure"
    ]
    
    for trend in trends:
        title_lower = trend["title"].lower()
        
        # Check if it matches security keywords
        if any(kw in title_lower for kw in keywords):
            # Check if not already published
            post_hash = get_post_hash(trend["title"])
            if post_hash not in state["published_posts"]:
                return trend["title"]
    
    return None


def select_topic(state):
    """Select next topic using rotation and trends."""
    # Try trending topic 30% of the time
    if random.random() < CONFIG["trend_probability"]:
        trends = fetch_rss_trends()
        trend_topic = extract_trend_topic(trends, state)
        if trend_topic:
            # Determine category from trend
            category = categorize_trend(trend_topic)
            return trend_topic, category, True
    
    # Fall back to evergreen rotation
    categories = list(CATEGORIES.keys())
    category = categories[state["category_rotation"] % len(categories)]
    
    # Get topic rotation for this category
    topic_index = state["topic_rotation"].get(category, 0)
    topics = CATEGORIES[category]
    topic = topics[topic_index % len(topics)]
    
    # Check if already published
    post_hash = get_post_hash(topic)
    attempts = 0
    while post_hash in state["published_posts"] and attempts < len(topics):
        topic_index += 1
        topic = topics[topic_index % len(topics)]
        post_hash = get_post_hash(topic)
        attempts += 1
    
    # Update rotations
    state["topic_rotation"][category] = topic_index + 1
    state["category_rotation"] += 1
    
    return topic, category, False


def categorize_trend(title):
    """Determine category for a trending topic."""
    title_lower = title.lower()
    
    category_keywords = {
        "APT Activity": ["apt", "nation-state", "state-sponsored", "espionage"],
        "Ransomware": ["ransomware", "ransom", "lockbit", "blackcat", "alphv"],
        "Vulnerability": ["cve", "vulnerability", "zero-day", "patch", "exploit"],
        "Supply Chain": ["supply chain", "dependency", "npm", "pypi", "package"],
        "Threat Actor": ["threat actor", "hacker", "group", "gang", "crew"],
        "Industrial Control": ["ics", "scada", "ot", "industrial", "plc"],
        "Cloud Security": ["cloud", "aws", "azure", "kubernetes", "container"],
        "Defense": ["defense", "detection", "response", "hunting", "soc"],
    }
    
    for category, keywords in category_keywords.items():
        if any(kw in title_lower for kw in keywords):
            return category
    
    return "Threat Actor"  # Default


def generate_slug(title):
    """Generate URL-friendly slug from title."""
    slug = title.lower()
    slug = "".join(c if c.isalnum() or c == " " else "" for c in slug)
    slug = "-".join(slug.split())
    return slug[:60].rstrip("-")


def generate_post_content(topic, category, state, is_trend=False):
    """Generate full post content without API."""
    from content_generators import generate_content_for_category
    
    # Select intro variation
    intro_index = state["intro_rotation"] % len(INTRO_VARIATIONS)
    intro_template = INTRO_VARIATIONS[intro_index]
    state["intro_rotation"] += 1
    
    # Select structure variation
    structure_index = state["structure_rotation"] % len(STRUCTURE_VARIATIONS)
    structure = STRUCTURE_VARIATIONS[structure_index]
    state["structure_rotation"] += 1
    
    # Generate content sections
    content = generate_content_for_category(
        topic=topic,
        category=category,
        intro_template=intro_template,
        structure=structure,
        is_trend=is_trend,
    )
    
    return content


def main():
    """Main scheduler entry point."""
    print("Black Wing Dispatch - Auto Scheduler")
    print("=" * 40)
    print(f"Posting interval: Every {CONFIG['posting_interval_days']} days")
    print()
    
    # Load state
    state = load_state()
    print(f"Loaded state: {len(state['published_posts'])} posts published")
    
    # Select topic
    topic, category, is_trend = select_topic(state)
    print(f"Selected topic: {topic}")
    print(f"Category: {category}")
    print(f"From trends: {is_trend}")
    
    # Check for duplicate
    post_hash = get_post_hash(topic)
    if post_hash in state["published_posts"]:
        print("Warning: Topic already published, selecting alternative...")
        topic, category, is_trend = select_topic(state)
        post_hash = get_post_hash(topic)
    
    # Generate content
    print("Generating content...")
    content = generate_post_content(topic, category, state, is_trend)
    
    # Generate metadata
    today = datetime.now()
    date_str = today.strftime("%Y-%m-%d")
    year = today.strftime("%Y")
    month = today.strftime("%m")
    slug = generate_slug(topic)
    
    # Ensure unique slug
    post_path = Path(CONFIG["posts_dir"]) / year / month / f"{slug}.html"
    counter = 1
    while post_path.exists():
        slug = f"{generate_slug(topic)}-{counter}"
        post_path = Path(CONFIG["posts_dir"]) / year / month / f"{slug}.html"
        counter += 1
    
    # Create post using generate_post.py
    from generate_post import create_post_html
    
    post_data = {
        "title": topic,
        "slug": slug,
        "date": date_str,
        "category": category,
        "content": content["body"],
        "excerpt": content["excerpt"],
        "meta_description": content["meta_description"],
        "keywords": content["keywords"],
        "reading_time": content["reading_time"],
    }
    
    html = create_post_html(post_data)
    
    # Write file
    post_path.parent.mkdir(parents=True, exist_ok=True)
    with open(post_path, "w") as f:
        f.write(html)
    
    print(f"Created: {post_path}")
    
    # Update state
    state["published_posts"].append(post_hash)
    state["last_run"] = date_str
    save_state(state)
    
    print("Done!")
    return str(post_path)


if __name__ == "__main__":
    main()
