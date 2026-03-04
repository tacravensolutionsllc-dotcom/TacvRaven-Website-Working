#!/usr/bin/env python3
"""
update_headers.py
Injects the new BlackWing nav + RavenEye ticker into every HTML file in a directory.

Usage:
    python3 update_headers.py --repo /path/to/repo [--dry-run]
"""

import os
import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime

# ─────────────────────────────────────────────────────────────────────────────
# TEMPLATE BLOCKS  (extracted from index-with-blackwing-nav.html)
# ─────────────────────────────────────────────────────────────────────────────

NAV_CSS = """
        /* ========================================
           RAVENEYE RADAR EFFECT
           ======================================== */
        .raveneye-icon-wrapper {
            position: relative;
            display: flex;
            align-items: center;
            justify-content: center;
            width: 18px;
            height: 18px;
            overflow: visible;
        }

        .raveneye-icon-wrapper svg {
            position: relative;
            z-index: 2;
            width: 18px;
            height: 18px;
            fill: var(--red);
            filter: drop-shadow(0 0 4px var(--red));
            animation: eyePulse 3s ease-in-out infinite;
        }

        @keyframes eyePulse {
            0%, 100% { opacity: 1; filter: drop-shadow(0 0 4px var(--red)); }
            50% { opacity: 0.8; filter: drop-shadow(0 0 8px var(--red)) drop-shadow(0 0 12px rgba(220, 38, 38, 0.5)); }
        }

        .raveneye-radar {
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            width: 50px;
            height: 50px;
            pointer-events: none;
            z-index: 1;
        }

        .raveneye-radar-sweep {
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            border-radius: 50%;
            background: conic-gradient(from 0deg, transparent 0deg, rgba(220, 38, 38, 0.5) 15deg, transparent 30deg);
            animation: radarSweep 2s linear infinite;
        }

        .raveneye-radar-pulse {
            position: absolute;
            top: 50%; left: 50%;
            transform: translate(-50%, -50%);
            width: 6px; height: 6px;
            border: 1px solid rgba(220, 38, 38, 0.8);
            border-radius: 50%;
            animation: radarPulse 2s ease-out infinite;
        }

        @keyframes radarPulse {
            0%   { width: 6px;  height: 6px;  opacity: 0.8; }
            100% { width: 50px; height: 50px; opacity: 0; }
        }

        .raveneye-radar-pulse:nth-child(2) { animation-delay: 0.6s; }
        .raveneye-radar-pulse:nth-child(3) { animation-delay: 1.2s; }

        /* ========================================
           NAVIGATION
           ======================================== */
        .nav {
            position: fixed;
            top: 0; left: 0; right: 0;
            z-index: 1000;
            padding: 20px 0;
            transition: all 0.3s ease;
            background: rgba(0, 0, 0, 0.85);
            backdrop-filter: blur(12px);
            border-bottom: 1px solid rgba(212, 160, 18, 0.1);
        }

        .nav.scrolled {
            background: rgba(0, 0, 0, 0.95);
            padding: 12px 0;
            border-bottom: 1px solid rgba(212, 160, 18, 0.2);
        }

        .nav-container {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .nav-logo {
            display: flex;
            align-items: center;
            gap: 12px;
            text-decoration: none;
        }

        .nav-logo-text {
            font-family: var(--font-display);
            font-size: 24px;
            font-weight: 700;
            color: var(--white);
            letter-spacing: 2px;
        }

        .nav-logo-text span { color: var(--gold); }

        .nav-menu {
            display: flex;
            align-items: center;
            gap: 8px;
            list-style: none;
        }

        .nav-link {
            font-family: var(--font-heading);
            font-size: 15px;
            font-weight: 500;
            color: var(--gray-300);
            text-decoration: none;
            padding: 10px 16px;
            transition: all 0.3s ease;
            position: relative;
        }

        .nav-link::after {
            content: '';
            position: absolute;
            bottom: 0; left: 50%;
            transform: translateX(-50%);
            width: 0; height: 2px;
            background: var(--gold);
            transition: width 0.3s ease;
        }

        .nav-link:hover,
        .nav-link.active { color: var(--white); }

        .nav-link:hover::after,
        .nav-link.active::after { width: 30px; }

        .nav-cta { padding: 10px 24px; font-size: 14px; }

        /* Mobile Menu */
        .mobile-menu-btn {
            display: none;
            flex-direction: column;
            gap: 5px;
            background: none; border: none;
            cursor: pointer; padding: 10px;
            z-index: 1001;
        }

        .mobile-menu-btn span {
            display: block;
            width: 24px; height: 2px;
            background: var(--white);
            transition: all 0.3s ease;
        }

        .mobile-menu {
            display: none;
            position: fixed;
            top: 0; left: 0; right: 0; bottom: 0;
            background: var(--black);
            z-index: 999;
            padding: 100px 24px 40px;
            opacity: 0; visibility: hidden;
            transition: all 0.3s ease;
            overflow-y: auto;
            -webkit-overflow-scrolling: touch;
        }

        .mobile-menu.active { opacity: 1; visibility: visible; }

        .mobile-nav-link {
            display: block;
            font-family: var(--font-heading);
            font-size: 24px; font-weight: 600;
            color: var(--white);
            text-decoration: none;
            padding: 16px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.1);
            transition: color 0.3s ease;
        }

        .mobile-nav-link:hover { color: var(--gold); }

        @media (max-width: 900px) {
            .nav-menu, .nav-cta { display: none; }
            .mobile-menu-btn { display: flex; }
            .mobile-menu { display: block; }
        }

        /* ========================================
           NAV DROPDOWN
           ======================================== */
        .nav-dropdown {
            position: relative;
            display: inline-block;
        }
        .nav-dropdown .nav-link {
            display: flex;
            align-items: center;
            gap: 4px;
            cursor: pointer;
        }
        .nav-dropdown .nav-link svg {
            width: 10px; height: 10px;
            transition: transform 0.2s ease;
        }
        .nav-dropdown:hover .nav-link svg { transform: rotate(180deg); }
        .nav-dropdown-content {
            position: absolute;
            top: 100%; left: 50%;
            transform: translateX(-50%);
            background: rgba(15, 15, 15, 0.98);
            border: 1px solid rgba(212, 160, 18, 0.2);
            border-radius: 8px;
            min-width: 200px;
            padding: 8px 0;
            opacity: 0; visibility: hidden;
            transition: all 0.2s ease;
            z-index: 1000;
            box-shadow: 0 10px 40px rgba(0,0,0,0.5);
            margin-top: 8px;
        }
        .nav-dropdown:hover .nav-dropdown-content { opacity: 1; visibility: visible; }
        .nav-dropdown-content a {
            display: block;
            padding: 10px 20px;
            color: #ccc;
            text-decoration: none;
            font-size: 14px;
            transition: all 0.2s ease;
        }
        .nav-dropdown-content a:hover {
            background: rgba(212, 160, 18, 0.1);
            color: #d4a012;
        }
        .nav-dropdown-content a.featured { color: #ef4444; font-weight: 600; }
        .nav-dropdown-content a.featured:hover {
            background: rgba(239, 68, 68, 0.1);
            color: #f87171;
        }

        /* ========================================
           RAVENEYE FIXED TICKER
           ======================================== */
        .raveneye {
            background: #1a0a0a;
            position: fixed;
            top: 80px; left: 0; right: 0;
            z-index: 999;
            overflow: hidden;
            transition: top 0.3s ease;
        }

        .raveneye.scrolled { top: 62px; }

        .raveneye::before {
            content: '';
            position: absolute;
            top: 0; left: -100%;
            width: 50%; height: 100%;
            background: linear-gradient(90deg, transparent 0%, rgba(220, 38, 38, 0.03) 40%, rgba(220, 38, 38, 0.08) 50%, rgba(220, 38, 38, 0.03) 60%, transparent 100%);
            animation: scanLine 4s linear infinite;
            pointer-events: none;
        }

        .raveneye::after {
            content: '';
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: linear-gradient(rgba(220, 38, 38, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(220, 38, 38, 0.03) 1px, transparent 1px);
            background-size: 20px 20px;
            pointer-events: none;
        }

        .raveneye-glow {
            position: absolute;
            top: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, var(--red) 20%, var(--red) 80%, transparent 100%);
            box-shadow: 0 0 10px var(--red), 0 0 20px rgba(220, 38, 38, 0.5);
        }

        .raveneye-bottom {
            position: absolute;
            bottom: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, rgba(220, 38, 38, 0.5) 30%, var(--red) 50%, rgba(220, 38, 38, 0.5) 70%, transparent 100%);
        }

        .raveneye-container {
            display: flex;
            align-items: center;
            height: 46px;
            position: relative;
            z-index: 1;
        }

        .raveneye-label {
            flex-shrink: 0;
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 0 20px;
            height: 100%;
            background: linear-gradient(135deg, #0d0000 0%, #1a0505 100%);
            border-right: 1px solid var(--red);
            font-family: var(--font-display);
            font-size: 11px; font-weight: 600;
            letter-spacing: 3px;
            color: var(--red);
            text-transform: uppercase;
            z-index: 2;
            position: relative;
            overflow: visible;
        }

        .raveneye-label::after {
            content: '';
            position: absolute;
            right: 0; top: 50%;
            transform: translateY(-50%);
            width: 3px; height: 60%;
            background: var(--red);
            box-shadow: 0 0 8px var(--red), 0 0 15px rgba(220, 38, 38, 0.5);
            animation: labelPulse 2s ease-in-out infinite;
        }

        @keyframes labelPulse {
            0%, 100% { opacity: 1; height: 60%; }
            50% { opacity: 0.7; height: 40%; }
        }

        .raveneye-track {
            flex: 1;
            overflow: hidden;
            position: relative;
            height: 100%;
        }

        .raveneye-track::before,
        .raveneye-track::after {
            content: '';
            position: absolute;
            top: 0; bottom: 0;
            width: 80px;
            z-index: 1;
            pointer-events: none;
        }

        .raveneye-track::before {
            left: 0;
            background: linear-gradient(90deg, #1a0a0a 0%, transparent 100%);
        }

        .raveneye-track::after {
            right: 0;
            background: linear-gradient(270deg, #1a0a0a 0%, transparent 100%);
        }

        .raveneye-scroll {
            display: flex;
            align-items: center;
            height: 100%;
            animation: raveneyeScroll 60s linear infinite;
            width: max-content;
        }

        .raveneye-scroll:hover { animation-play-state: paused; }

        @keyframes raveneyeScroll {
            0%   { transform: translateX(0); }
            100% { transform: translateX(-50%); }
        }

        .raveneye-item {
            display: flex;
            align-items: center;
            gap: 12px;
            padding: 0 40px;
            height: 100%;
            white-space: nowrap;
            border-right: 1px solid rgba(220, 38, 38, 0.15);
            cursor: pointer;
            transition: all 0.3s ease;
            position: relative;
            text-decoration: none;
            color: inherit;
        }

        .raveneye-item::before {
            content: '';
            position: absolute;
            left: 12px; top: 50%;
            transform: translateY(-50%);
            width: 4px; height: 4px;
            background: var(--red);
            border-radius: 50%;
            box-shadow: 0 0 6px var(--red);
            opacity: 0.6;
        }

        .raveneye-item:hover { background: rgba(220, 38, 38, 0.1); }

        .raveneye-item:hover::before {
            opacity: 1;
            box-shadow: 0 0 10px var(--red), 0 0 15px rgba(220, 38, 38, 0.5);
        }

        .raveneye-badge {
            flex-shrink: 0;
            padding: 4px 10px;
            border-radius: 3px;
            font-family: var(--font-display);
            font-size: 9px; font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.3s ease;
        }

        .raveneye-badge--kev {
            background: rgba(220, 38, 38, 0.2);
            color: #ff6b6b;
            border: 1px solid var(--red);
            box-shadow: 0 0 8px rgba(220, 38, 38, 0.3);
        }

        .raveneye-item:hover .raveneye-badge--kev {
            background: rgba(220, 38, 38, 0.3);
            box-shadow: 0 0 12px rgba(220, 38, 38, 0.5);
        }

        .raveneye-badge--critical {
            background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
            color: var(--black);
            box-shadow: 0 0 8px rgba(212, 160, 18, 0.4);
        }

        .raveneye-item:hover .raveneye-badge--critical {
            box-shadow: 0 0 12px rgba(212, 160, 18, 0.6);
        }

        .raveneye-badge--alert {
            background: transparent;
            color: var(--gold-light);
            border: 1px solid rgba(212, 160, 18, 0.5);
        }

        .raveneye-item:hover .raveneye-badge--alert {
            border-color: var(--gold);
            box-shadow: 0 0 8px rgba(212, 160, 18, 0.3);
        }

        .raveneye-text {
            font-family: var(--font-body);
            font-size: 13px; font-weight: 500;
            color: rgba(255, 255, 255, 0.9);
            transition: color 0.3s ease;
        }

        .raveneye-item:hover .raveneye-text { color: var(--white); }

        .raveneye-source {
            font-family: var(--font-heading);
            font-size: 10px;
            color: rgba(220, 38, 38, 0.6);
            text-transform: uppercase;
            letter-spacing: 1px;
            padding-left: 12px;
            border-left: 1px solid rgba(220, 38, 38, 0.2);
            transition: all 0.3s ease;
        }

        .raveneye-item:hover .raveneye-source {
            color: rgba(220, 38, 38, 0.9);
            border-left-color: rgba(220, 38, 38, 0.4);
        }

        .raveneye-cta {
            flex-shrink: 0;
            display: flex;
            align-items: center;
            gap: 6px;
            padding: 0 20px;
            height: 100%;
            background: rgba(220, 38, 38, 0.1);
            border-left: 1px solid rgba(220, 38, 38, 0.3);
            font-family: var(--font-heading);
            font-size: 11px; font-weight: 600;
            color: var(--red);
            text-decoration: none;
            text-transform: uppercase;
            letter-spacing: 1px;
            transition: all 0.3s ease;
        }

        .raveneye-cta:hover { background: rgba(220, 38, 38, 0.2); color: #ff6b6b; }

        .raveneye-cta svg { width: 14px; height: 14px; transition: transform 0.3s ease; }
        .raveneye-cta:hover svg { transform: translateX(3px); }
"""

# The CSS variables that must exist (only injected if missing)
REQUIRED_CSS_VARS = """
        :root {
            --black: #0a0a0a;
            --black-light: #0f0f0f;
            --black-card: #111111;
            --white: #ffffff;
            --gray-300: #d1d5db;
            --gray-400: #9ca3af;
            --gray-500: #6b7280;
            --gray-800: #1a1a1a;
            --gold: #d4a012;
            --gold-light: #f0c040;
            --gold-dark: #a07800;
            --red: #dc2626;
            --red-dark: #7f1d1d;
            --blue: #3b82f6;
            --green: #22c55e;
            --font-display: 'Orbitron', sans-serif;
            --font-heading: 'Rajdhani', sans-serif;
            --font-body: 'Inter', sans-serif;
        }
"""

# Required Google Fonts (injected if missing)
GOOGLE_FONTS_LINK = '<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@300;400;500;600&display=swap" rel="stylesheet">'

NAV_HTML = """    <!-- Navigation -->
    <nav class="nav" id="nav">
        <div class="container nav-container">
            <a href="/index.html" class="nav-logo">
                <div class="nav-logo-text">TAC<span>RAVEN</span></div>
            </a>
            <ul class="nav-menu">
                <li><a href="/index.html" class="nav-link">Home</a></li>
                <li><a href="/about.html" class="nav-link">About</a></li>
                <li class="nav-dropdown">
                    <a class="nav-link">Blog <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg></a>
                    <div class="nav-dropdown-content">
                        <a href="/Blog.html">Cyber Careers</a>
                        <a href="/intel/blackwing/index.html" class="featured">Black Wing Dispatch</a>
                    </div>
                </li>
                <li><a href="/learning-hub.html" class="nav-link">Learning Hub</a></li>
                <li><a href="/threat-map.html" class="nav-link">Threat Map</a></li>
                <li><a href="/intel/weekly/" class="nav-link">Weekly Reports</a></li>
                <li><a href="/cyber-news.html" class="nav-link">News</a></li>
                <li><a href="/tools.html" class="nav-link">Tools</a></li>
                <li><a href="/pricing.html" class="nav-link">Programs</a></li>
            </ul>
            <a href="#contact" class="btn btn-primary nav-cta">Contact</a>
            <button class="mobile-menu-btn" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </nav>

    <!-- Mobile Menu -->
    <div class="mobile-menu" id="mobile-menu">
        <a href="/index.html" class="mobile-nav-link">Home</a>
        <a href="/about.html" class="mobile-nav-link">About</a>
        <a href="/Blog.html" class="mobile-nav-link">Cyber Careers Blog</a>
        <a href="/intel/blackwing/index.html" class="mobile-nav-link" style="color: #ef4444;">Black Wing Dispatch</a>
        <a href="/learning-hub.html" class="mobile-nav-link">Learning Hub</a>
        <a href="/threat-map.html" class="mobile-nav-link">Threat Map</a>
        <a href="/intel/weekly/" class="mobile-nav-link">Weekly Reports</a>
        <a href="/cyber-news.html" class="mobile-nav-link">News</a>
        <a href="/tools.html" class="mobile-nav-link">Tools</a>
        <a href="/pricing.html" class="mobile-nav-link">Programs</a>
        <a href="#contact" class="mobile-nav-link">Contact</a>
    </div>

    <!-- RavenEye Threat Ticker -->
    <div class="raveneye" id="raveneye">
        <div class="raveneye-glow"></div>
        <div class="raveneye-bottom"></div>
        <div class="raveneye-container">
            <div class="raveneye-label">
                <div class="raveneye-icon-wrapper">
                    <div class="raveneye-radar">
                        <div class="raveneye-radar-sweep"></div>
                        <div class="raveneye-radar-pulse"></div>
                        <div class="raveneye-radar-pulse"></div>
                        <div class="raveneye-radar-pulse"></div>
                    </div>
                    <svg viewBox="0 0 24 24"><path d="M12 4.5C7 4.5 2.73 7.61 1 12c1.73 4.39 6 7.5 11 7.5s9.27-3.11 11-7.5c-1.73-4.39-6-7.5-11-7.5zM12 17c-2.76 0-5-2.24-5-5s2.24-5 5-5 5 2.24 5 5-2.24 5-5 5zm0-8c-1.66 0-3 1.34-3 3s1.34 3 3 3 3-1.34 3-3-1.34-3-3-3z"/></svg>
                </div>
                RavenEye
            </div>
            <div class="raveneye-track">
                <div class="raveneye-scroll" id="raveneye-scroll">
                    <!-- Items populated by JS -->
                </div>
            </div>
            <a href="/cyber-news.html" class="raveneye-cta">
                Full Feed
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <polyline points="12 5 19 12 12 19"/>
                </svg>
            </a>
        </div>
    </div>
"""

NAV_JS = """
        // ── BlackWing Nav + RavenEye ──────────────────────────────────────────
        (function() {
            var nav = document.getElementById('nav');
            var raveneye = document.getElementById('raveneye');
            var backToTop = document.getElementById('back-to-top');

            window.addEventListener('scroll', function() {
                var scrollY = window.scrollY;
                if (scrollY > 50) {
                    if (nav) nav.classList.add('scrolled');
                    if (raveneye) raveneye.classList.add('scrolled');
                } else {
                    if (nav) nav.classList.remove('scrolled');
                    if (raveneye) raveneye.classList.remove('scrolled');
                }
                if (backToTop) {
                    if (scrollY > 500) backToTop.classList.add('visible');
                    else backToTop.classList.remove('visible');
                }
            });

            if (backToTop) {
                backToTop.addEventListener('click', function() {
                    window.scrollTo({ top: 0, behavior: 'smooth' });
                });
            }

            // Mobile menu toggle
            var mobileMenuBtn = document.querySelector('.mobile-menu-btn');
            var mobileMenu = document.getElementById('mobile-menu');
            if (mobileMenuBtn && mobileMenu) {
                mobileMenuBtn.addEventListener('click', function() {
                    mobileMenuBtn.classList.toggle('active');
                    mobileMenu.classList.toggle('active');
                    document.body.style.overflow = mobileMenu.classList.contains('active') ? 'hidden' : '';
                });
                document.querySelectorAll('.mobile-nav-link').forEach(function(link) {
                    link.addEventListener('click', function() {
                        mobileMenuBtn.classList.remove('active');
                        mobileMenu.classList.remove('active');
                        document.body.style.overflow = '';
                    });
                });
            }

            // RavenEye ticker
            var raveneyeData = [
                { badge: 'KEV',      badgeType: 'kev',      text: 'CVE-2024-3400: PAN-OS Command Injection, Due: Jan 20',         source: 'CISA KEV',    url: 'https://www.cisa.gov/known-exploited-vulnerabilities-catalog' },
                { badge: 'ZERO-DAY', badgeType: 'critical', text: 'Microsoft Patches Critical Zero-Day in Windows Kernel',         source: 'Hacker News', url: 'https://thehackernews.com/' },
                { badge: 'CRITICAL', badgeType: 'critical', text: 'Ivanti VPN Zero-Day Actively Exploited in the Wild',             source: 'Dark Reading', url: 'https://www.darkreading.com/' },
                { badge: 'KEV',      badgeType: 'kev',      text: 'CVE-2024-21887: Ivanti Connect Secure, Due: Jan 22',            source: 'CISA KEV',    url: 'https://www.cisa.gov/known-exploited-vulnerabilities-catalog' },
                { badge: 'ALERT',    badgeType: 'alert',    text: 'Ransomware Group Targets Healthcare Sector',                     source: 'Krebs',       url: 'https://krebsonsecurity.com/' },
                { badge: 'CRITICAL', badgeType: 'critical', text: 'CISA Emergency Directive: Disconnect Affected Devices',          source: 'CISA',        url: 'https://www.cisa.gov/news-events/directives' },
            ];

            var container = document.getElementById('raveneye-scroll');
            if (container) {
                var html = raveneyeData.map(function(item) {
                    return '<a href="' + item.url + '" target="_blank" rel="noopener noreferrer" class="raveneye-item">'
                        + '<span class="raveneye-badge raveneye-badge--' + item.badgeType + '">' + item.badge + '</span>'
                        + '<span class="raveneye-text">' + item.text + '</span>'
                        + '<span class="raveneye-source">' + item.source + '</span>'
                        + '</a>';
                }).join('');
                container.innerHTML = html + html; // duplicate for seamless loop
            }
        })();
        // ─────────────────────────────────────────────────────────────────────
"""


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def backup_file(path: Path, backup_dir: Path):
    rel = path.name
    dest = backup_dir / rel
    # avoid collisions
    counter = 0
    while dest.exists():
        counter += 1
        dest = backup_dir / f"{path.stem}_{counter}{path.suffix}"
    shutil.copy2(path, dest)


def has_nav(html: str) -> bool:
    return bool(re.search(r'<nav\b', html, re.IGNORECASE))


def has_raveneye(html: str) -> bool:
    return bool(re.search(r'class=["\']raveneye["\']|id=["\']raveneye["\']', html))


def inject_css(html: str) -> str:
    """Insert NAV_CSS before </style> (the last one before </head>)."""
    # Find position of last </style> that appears before </head>
    head_end = html.lower().find('</head>')
    if head_end == -1:
        return html  # no head – skip

    chunk = html[:head_end]
    style_close = chunk.rfind('</style>')
    if style_close == -1:
        # No existing style block – inject a new one just before </head>
        injection = f'<style>{NAV_CSS}\n</style>\n'
        return html[:head_end] + injection + html[head_end:]

    insert_pos = style_close  # insert just before </style>
    return html[:insert_pos] + NAV_CSS + '\n        ' + html[insert_pos:]


def inject_fonts(html: str) -> str:
    """Ensure Google Fonts for Orbitron / Rajdhani / Inter are present."""
    if 'Orbitron' in html:
        return html
    head_end = html.lower().find('</head>')
    if head_end == -1:
        return html
    return html[:head_end] + '  ' + GOOGLE_FONTS_LINK + '\n' + html[head_end:]


def inject_css_vars(html: str) -> str:
    """Ensure :root CSS variables are present."""
    if '--gold:' in html and '--red:' in html:
        return html
    # Insert at beginning of first <style> block
    style_open = html.find('<style')
    if style_open == -1:
        return html
    style_content_start = html.find('>', style_open) + 1
    return html[:style_content_start] + '\n' + REQUIRED_CSS_VARS + html[style_content_start:]


def remove_old_nav(html: str) -> str:
    """Remove existing <nav> block, mobile-menu div, and raveneye div."""

    # Remove <nav ...> ... </nav>  (non-greedy)
    html = re.sub(r'<!--\s*Navigation\s*-->\s*', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<nav\b[^>]*>.*?</nav>', '', html, flags=re.DOTALL | re.IGNORECASE)

    # Remove mobile-menu div
    html = re.sub(r'<!--\s*Mobile Menu\s*-->\s*', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<div[^>]+id=["\']mobile-menu["\'][^>]*>.*?</div>', '', html,
                  flags=re.DOTALL | re.IGNORECASE)

    # Remove raveneye div
    html = re.sub(r'<!--\s*RavenEye[^>]*-->\s*', '', html, flags=re.IGNORECASE)
    html = re.sub(r'<div[^>]+(?:id=["\']raveneye["\']|class=["\']raveneye["\'])[^>]*>.*?</div>',
                  '', html, flags=re.DOTALL | re.IGNORECASE)

    return html


def inject_nav_html(html: str) -> str:
    """Insert NAV_HTML right after <body> opening tag."""
    body_match = re.search(r'<body[^>]*>', html, re.IGNORECASE)
    if not body_match:
        return html
    insert_pos = body_match.end()
    return html[:insert_pos] + '\n' + NAV_HTML + html[insert_pos:]


def remove_old_nav_js(html: str) -> str:
    """Remove previously injected BlackWing Nav JS block (idempotent)."""
    return re.sub(
        r'\s*// ── BlackWing Nav \+ RavenEye ─+.*?// ─+\s*',
        '',
        html,
        flags=re.DOTALL
    )


def inject_nav_js(html: str) -> str:
    """Inject NAV_JS before the first </script> that closes a block in <body>,
    or before </body> if no script exists."""
    # Find first </script> after <body>
    body_start = html.lower().find('<body')
    if body_start == -1:
        return html

    script_close = html.find('</script>', body_start)
    if script_close != -1:
        # Find the opening <script> tag of that block
        script_open = html.rfind('<script', body_start, script_close)
        if script_open != -1:
            # Insert INSIDE that script block, at the very start
            inner_start = html.find('>', script_open) + 1
            return html[:inner_start] + NAV_JS + html[inner_start:]

    # Fallback: insert before </body>
    body_end = html.lower().rfind('</body>')
    if body_end == -1:
        return html
    return html[:body_end] + '<script>' + NAV_JS + '</script>\n' + html[body_end:]


def mark_active_link(html: str, filepath: Path) -> str:
    """Set active class on the nav-link that matches this file."""
    # Determine which nav item to mark active based on filename
    name = filepath.stem.lower()
    mapping = {
        'index':        '/index.html',
        'about':        '/about.html',
        'blog':         '/Blog.html',
        'learning-hub': '/learning-hub.html',
        'threat-map':   '/threat-map.html',
        'cyber-news':   '/cyber-news.html',
        'tools':        '/tools.html',
        'pricing':      '/pricing.html',
    }
    active_href = mapping.get(name)
    if not active_href:
        return html

    # Add 'active' class to matching nav-link (desktop menu)
    pattern = r'(href=["\']' + re.escape(active_href) + r'["\'][^>]*class=["\']nav-link)(["\'])'
    html = re.sub(pattern, r'\1 active\2', html)
    # Also handle href before class
    pattern2 = r'(class=["\']nav-link)(["\'])([^>]*href=["\']' + re.escape(active_href) + r'["\'])'
    html = re.sub(pattern2, r'\1 active\2\3', html)
    return html


def process_file(path: Path, backup_dir: Path, dry_run: bool) -> dict:
    result = {'file': str(path), 'status': 'ok', 'changes': []}

    try:
        html = path.read_text(encoding='utf-8', errors='replace')
    except Exception as e:
        result['status'] = 'error'
        result['error'] = str(e)
        return result

    original = html

    # 1. Ensure fonts
    if 'Orbitron' not in html:
        html = inject_fonts(html)
        result['changes'].append('fonts injected')

    # 2. Ensure CSS variables
    if '--gold:' not in html:
        html = inject_css_vars(html)
        result['changes'].append('CSS vars injected')

    # 3. Inject nav CSS (always replace to keep fresh)
    # Remove old nav CSS block if previously injected
    html = re.sub(r'/\*\s*={5,}\s*RAVENEYE RADAR EFFECT.*?RAVENEYE FIXED TICKER.*?raveneye-cta:hover svg.*?\}\s*', 
                  '', html, flags=re.DOTALL)
    html = inject_css(html)
    result['changes'].append('nav/raveneye CSS injected')

    # 4. Remove old nav HTML
    html = remove_old_nav(html)

    # 5. Inject new nav HTML
    html = inject_nav_html(html)
    result['changes'].append('nav HTML replaced')

    # 6. Mark active link
    html = mark_active_link(html, path)

    # 7. Remove old nav JS (idempotent)
    html = remove_old_nav_js(html)

    # 8. Inject nav JS
    html = inject_nav_js(html)
    result['changes'].append('nav JS injected')

    if html == original:
        result['status'] = 'unchanged'
        result['changes'] = []
        return result

    if not dry_run:
        backup_file(path, backup_dir)
        path.write_text(html, encoding='utf-8')

    return result


# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description='Inject BlackWing nav + RavenEye into HTML files')
    parser.add_argument('--repo', required=True, help='Path to the git repo root')
    parser.add_argument('--dry-run', action='store_true', help='Preview changes without writing')
    parser.add_argument('--exclude', nargs='*', default=[], help='Filenames to skip (no path)')
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    if not repo.is_dir():
        print(f'ERROR: {repo} is not a directory')
        sys.exit(1)

    # Default exclusions: node_modules, .git, vendor, third-party
    skip_dirs = {'.git', 'node_modules', 'vendor', '.github'}
    skip_files = set(args.exclude)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_dir = repo / f'_header_backup_{timestamp}'
    if not args.dry_run:
        backup_dir.mkdir(exist_ok=True)
        print(f'Backups → {backup_dir}')

    html_files = []
    for html_path in repo.rglob('*.html'):
        if any(part in skip_dirs for part in html_path.parts):
            continue
        if html_path.name in skip_files:
            continue
        html_files.append(html_path)

    html_files.sort()
    print(f'Found {len(html_files)} HTML file(s) in {repo}')
    if args.dry_run:
        print('DRY RUN – no files will be written\n')

    ok = skipped = errors = 0
    for fp in html_files:
        res = process_file(fp, backup_dir, args.dry_run)
        rel = fp.relative_to(repo)
        if res['status'] == 'error':
            print(f'  ✗ ERROR  {rel}: {res.get("error")}')
            errors += 1
        elif res['status'] == 'unchanged':
            print(f'  – SKIP   {rel} (no changes needed)')
            skipped += 1
        else:
            tag = 'DRY' if args.dry_run else 'OK '
            print(f'  ✓ {tag}    {rel}: {", ".join(res["changes"])}')
            ok += 1

    print(f'\nDone. Updated: {ok}  Skipped: {skipped}  Errors: {errors}')
    if not args.dry_run and ok > 0:
        print(f'Original files backed up to: {backup_dir}')


if __name__ == '__main__':
    main()
