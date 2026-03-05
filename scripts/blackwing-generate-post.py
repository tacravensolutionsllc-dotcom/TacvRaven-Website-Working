#!/usr/bin/env python3
"""
Black Wing Dispatch - Post Generator
TacRaven Solutions LLC

Generates HTML blog posts using pre-written content pools.
CSS is EMBEDDED directly into each HTML file for guaranteed styling.
"""

import os
import sys
import json
import argparse
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from blackwing_content_generators import generate_content_for_category, select_next_topic, CATEGORIES

CONFIG = {
    "site_url": "https://tacraven.com",
    "author": "TacRaven",
    "twitter_handle": "@TacRavenSec",
    "ga_id": "G-PEYM947EG8",
}

# ============================================================================
# EMBEDDED CSS - Guaranteed to load with every post
# ============================================================================
EMBEDDED_CSS = """/* Black Wing Dispatch - Cyber Threat Intelligence */
/* TacRaven Solutions LLC */
/* Color scheme: Red, Black, Metallic Silver */

/* Reset and Base */
*, *::before, *::after {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    /* Primary Colors */
    --color-bg-primary: #0a0a0a;
    --color-bg-secondary: #0f0f0f;
    --color-bg-card: #121212;
    --color-bg-card-hover: #1a1a1a;
    
    /* Red Accent Colors */
    --color-red-primary: #dc2626;
    --color-red-light: #ef4444;
    --color-red-dark: #991b1b;
    --color-red-glow: rgba(220, 38, 38, 0.4);
    
    /* Metallic/Silver */
    --color-silver: #a8a8a8;
    --color-silver-light: #d4d4d4;
    --color-silver-dark: #737373;
    
    /* Borders */
    --color-border: #1f1f1f;
    --color-border-light: #2a2a2a;
    --color-border-red: rgba(220, 38, 38, 0.3);
    
    /* Text */
    --color-text-primary: #f5f5f5;
    --color-text-secondary: #a3a3a3;
    --color-text-muted: #525252;
    
    /* Category Colors */
    --color-apt: #dc2626;
    --color-ransomware: #f97316;
    --color-vulnerability: #3b82f6;
    --color-supply-chain: #8b5cf6;
    --color-threat-actor: #ec4899;
    --color-industrial: #06b6d4;
    --color-cloud: #10b981;
    --color-defense: #eab308;
    
    /* Typography */
    --font-primary: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
    --font-display: "Rajdhani", "Orbitron", -apple-system, sans-serif;
    --font-mono: "JetBrains Mono", "SF Mono", Monaco, Consolas, monospace;
    
    /* Layout */
    --max-width: 1280px;
    --content-width: 860px;
    --header-height: 64px;
    --ticker-height: 36px;
    
    /* Borders & Shadows */
    --radius-sm: 4px;
    --radius-md: 6px;
    --radius-lg: 8px;
    --shadow-red: 0 0 20px rgba(220, 38, 38, 0.2);
    --shadow-card: 0 4px 12px rgba(0, 0, 0, 0.4);
    
    /* Transitions */
    --transition-fast: 150ms ease;
    --transition-base: 200ms ease;
}

html {
    font-size: 16px;
    scroll-behavior: smooth;
}

body {
    font-family: var(--font-primary);
    background-color: var(--color-bg-primary);
    color: var(--color-text-primary);
    line-height: 1.6;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
}

/* Typography */
h1, h2, h3, h4, h5, h6 {
    font-weight: 600;
    line-height: 1.3;
    color: var(--color-text-primary);
}

h1 { font-size: 2.5rem; font-weight: 700; }
h2 { font-size: 1.5rem; margin-bottom: 1rem; }
h3 { font-size: 1.125rem; margin-bottom: 0.5rem; }

p {
    margin-bottom: 1rem;
    color: var(--color-text-secondary);
}

a {
    color: var(--color-red-light);
    text-decoration: none;
    transition: color var(--transition-fast);
}

a:hover { color: var(--color-red-primary); }

/* Container */
.container {
    width: 100%;
    max-width: var(--max-width);
    margin: 0 auto;
    padding: 0 1.5rem;
}

/* Header */
.site-header {
    background: rgba(0, 0, 0, 0.85);
    backdrop-filter: blur(12px);
    height: var(--header-height);
    position: sticky;
    top: 0;
    z-index: 100;
    border-bottom: 1px solid rgba(212, 160, 18, 0.1);
}

.header-content {
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 100%;
}

.logo {
    display: flex;
    align-items: center;
    text-decoration: none;
    font-size: 1.25rem;
    font-weight: 700;
    letter-spacing: 0.05em;
}

.logo-text { color: var(--color-text-primary); }
.logo-accent { color: var(--color-red-primary); }

.main-nav {
    display: flex;
    align-items: center;
    gap: 2rem;
}

.main-nav a {
    color: var(--color-text-secondary);
    font-size: 0.8125rem;
    font-weight: 500;
    text-decoration: none;
    transition: color var(--transition-fast);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.main-nav a:hover { color: var(--color-text-primary); }
.main-nav a.active { color: var(--color-text-primary); }

/* Navigation Dropdown */
.nav-dropdown { position: relative; }

.nav-dropdown-btn {
    background: none;
    border: none;
    color: var(--color-text-secondary);
    font-size: 0.8125rem;
    font-weight: 500;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 0.35rem;
    padding: 0;
    transition: color var(--transition-fast);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

.nav-dropdown-btn:hover,
.nav-dropdown-btn.active { color: var(--color-text-primary); }

.nav-dropdown-btn svg { transition: transform var(--transition-fast); }
.nav-dropdown:hover .nav-dropdown-btn svg { transform: rotate(180deg); }

.nav-dropdown-content {
    position: absolute;
    top: 100%;
    left: 50%;
    transform: translateX(-50%);
    margin-top: 0.75rem;
    background: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    min-width: 180px;
    padding: 0.5rem 0;
    opacity: 0;
    visibility: hidden;
    transition: all var(--transition-fast);
    z-index: 100;
    box-shadow: 0 10px 40px rgba(0, 0, 0, 0.5);
}

.nav-dropdown:hover .nav-dropdown-content {
    opacity: 1;
    visibility: visible;
}

.nav-dropdown-content a {
    display: block;
    padding: 0.625rem 1rem;
    color: var(--color-text-secondary);
    font-size: 0.8125rem;
    white-space: nowrap;
    text-transform: none;
    letter-spacing: 0;
}

.nav-dropdown-content a:hover {
    background: rgba(220, 38, 38, 0.1);
    color: var(--color-text-primary);
}

.nav-dropdown-content a.active {
    color: var(--color-red-light);
    background: rgba(220, 38, 38, 0.05);
}

.btn-contact {
    position: relative;
    background: linear-gradient(135deg, rgba(212, 160, 73, 0.1) 0%, transparent 50%);
    color: #d4a849;
    padding: 0.5rem 1.5rem;
    border-radius: var(--radius-sm);
    font-size: 0.8125rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    transition: all 0.3s ease;
    border: 1px solid #d4a849;
    overflow: hidden;
    box-shadow: 0 0 10px rgba(212, 160, 73, 0.2);
}

.btn-contact:hover {
    background: linear-gradient(135deg, #d4a849 0%, #b8942e 100%);
    color: var(--color-bg-primary);
    border-color: #d4a849;
    box-shadow: 0 0 20px rgba(212, 160, 73, 0.5), 0 4px 15px rgba(212, 160, 73, 0.3);
    transform: translateY(-2px);
}

/* RavenEye Ticker */
.raveneye {
    background: #1a0a0a;
    position: sticky;
    top: var(--header-height);
    z-index: 99;
    overflow: hidden;
}

.raveneye::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 50%;
    height: 100%;
    background: linear-gradient(90deg, transparent 0%, rgba(220, 38, 38, 0.03) 40%, rgba(220, 38, 38, 0.08) 50%, rgba(220, 38, 38, 0.03) 60%, transparent 100%);
    animation: scanLine 4s linear infinite;
    pointer-events: none;
}

.raveneye::after {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background-image: linear-gradient(rgba(220, 38, 38, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(220, 38, 38, 0.03) 1px, transparent 1px);
    background-size: 20px 20px;
    pointer-events: none;
}

@keyframes scanLine {
    0% { left: -50%; }
    100% { left: 100%; }
}

.raveneye-glow {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, var(--color-red-primary) 20%, var(--color-red-primary) 80%, transparent 100%);
    box-shadow: 0 0 10px var(--color-red-primary), 0 0 20px rgba(220, 38, 38, 0.5);
}

.raveneye-bottom {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    height: 1px;
    background: linear-gradient(90deg, transparent 0%, rgba(220, 38, 38, 0.5) 30%, var(--color-red-primary) 50%, rgba(220, 38, 38, 0.5) 70%, transparent 100%);
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
    border-right: 1px solid var(--color-red-primary);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 3px;
    color: var(--color-red-primary);
    text-transform: uppercase;
    z-index: 2;
    position: relative;
    overflow: visible;
}

.raveneye-label::after {
    content: '';
    position: absolute;
    right: 0;
    top: 50%;
    transform: translateY(-50%);
    width: 3px;
    height: 60%;
    background: var(--color-red-primary);
    box-shadow: 0 0 8px var(--color-red-primary), 0 0 15px rgba(220, 38, 38, 0.5);
    animation: labelPulse 2s ease-in-out infinite;
}

@keyframes labelPulse {
    0%, 100% { opacity: 1; height: 60%; }
    50% { opacity: 0.7; height: 40%; }
}

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
    fill: var(--color-red-primary);
    filter: drop-shadow(0 0 4px var(--color-red-primary));
    animation: eyePulse 3s ease-in-out infinite;
}

@keyframes eyePulse {
    0%, 100% { opacity: 1; filter: drop-shadow(0 0 4px var(--color-red-primary)); }
    50% { opacity: 0.8; filter: drop-shadow(0 0 8px var(--color-red-primary)) drop-shadow(0 0 12px rgba(220, 38, 38, 0.5)); }
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
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    border-radius: 50%;
    background: conic-gradient(from 0deg, transparent 0deg, rgba(220, 38, 38, 0.5) 15deg, transparent 30deg);
    animation: radarSweep 2s linear infinite;
}

@keyframes radarSweep {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}

.raveneye-radar-pulse {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    width: 6px;
    height: 6px;
    border: 1px solid rgba(220, 38, 38, 0.8);
    border-radius: 50%;
    animation: radarPulse 2s ease-out infinite;
}

@keyframes radarPulse {
    0% { width: 6px; height: 6px; opacity: 0.8; }
    100% { width: 50px; height: 50px; opacity: 0; }
}

.raveneye-radar-pulse:nth-child(2) { animation-delay: 0.6s; }
.raveneye-radar-pulse:nth-child(3) { animation-delay: 1.2s; }

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
    top: 0;
    bottom: 0;
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
    0% { transform: translateX(0); }
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
    left: 12px;
    top: 50%;
    transform: translateY(-50%);
    width: 4px;
    height: 4px;
    background: var(--color-red-primary);
    border-radius: 50%;
    box-shadow: 0 0 6px var(--color-red-primary);
    opacity: 0.6;
}

.raveneye-item:hover { background: rgba(220, 38, 38, 0.1); }

.raveneye-item:hover::before {
    opacity: 1;
    box-shadow: 0 0 10px var(--color-red-primary), 0 0 15px rgba(220, 38, 38, 0.5);
}

.raveneye-badge {
    flex-shrink: 0;
    padding: 4px 10px;
    border-radius: 3px;
    font-size: 9px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    transition: all 0.3s ease;
}

.raveneye-badge--kev {
    background: rgba(220, 38, 38, 0.2);
    color: #ff6b6b;
    border: 1px solid var(--color-red-primary);
    box-shadow: 0 0 8px rgba(220, 38, 38, 0.3);
}

.raveneye-badge--critical {
    background: linear-gradient(135deg, #d4a849 0%, #b48210 100%);
    color: #0a0a0a;
    box-shadow: 0 0 8px rgba(212, 160, 18, 0.4);
}

.raveneye-badge--alert {
    background: transparent;
    color: #e8c547;
    border: 1px solid rgba(212, 160, 18, 0.5);
}

.raveneye-text {
    font-size: 13px;
    font-weight: 500;
    color: rgba(255, 255, 255, 0.9);
    transition: color 0.3s ease;
}

.raveneye-item:hover .raveneye-text { color: var(--color-text-primary); }

.raveneye-cta {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 0 20px;
    height: 100%;
    background: rgba(220, 38, 38, 0.1);
    border-left: 1px solid rgba(220, 38, 38, 0.3);
    font-size: 11px;
    font-weight: 600;
    color: var(--color-red-primary);
    text-decoration: none;
    text-transform: uppercase;
    letter-spacing: 1px;
    transition: all 0.3s ease;
}

.raveneye-cta:hover {
    background: rgba(220, 38, 38, 0.2);
    color: #ff6b6b;
}

.raveneye-cta svg {
    width: 14px;
    height: 14px;
    transition: transform 0.3s ease;
}

.raveneye-cta:hover svg { transform: translateX(3px); }

/* Blog Post Page Styles */
.threat-brief { flex-grow: 1; }

.brief-header {
    background: radial-gradient(ellipse at center top, rgba(220, 38, 38, 0.08) 0%, transparent 50%),
                linear-gradient(180deg, var(--color-bg-secondary) 0%, var(--color-bg-primary) 100%);
    padding: 3rem 0;
    border-bottom: 1px solid var(--color-border);
    position: relative;
    overflow: hidden;
}

.brief-header::after {
    content: "";
    position: absolute;
    inset: 0;
    background-image: 
        repeating-linear-gradient(0deg, transparent, transparent 49px, rgba(220, 38, 38, 0.08) 49px, rgba(220, 38, 38, 0.08) 50px),
        repeating-linear-gradient(90deg, transparent, transparent 49px, rgba(220, 38, 38, 0.08) 49px, rgba(220, 38, 38, 0.08) 50px),
        radial-gradient(circle at 0% 0%, rgba(220, 38, 38, 0.1) 0%, transparent 25%),
        radial-gradient(circle at 100% 100%, rgba(220, 38, 38, 0.1) 0%, transparent 25%);
    background-size: 100% 100%;
    pointer-events: none;
    z-index: 0;
}

.brief-header > .container {
    position: relative;
    z-index: 1;
}

.brief-header-content {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 2rem;
}

.brief-header-text {
    flex: 1;
    min-width: 0;
}

.brief-header-logo { flex-shrink: 0; }

.brief-logo {
    display: block;
    width: 320px;
    height: auto;
    filter: drop-shadow(0 0 35px rgba(220, 38, 38, 0.5));
    mask-image: radial-gradient(ellipse 80% 80% at center, black 30%, transparent 65%);
    -webkit-mask-image: radial-gradient(ellipse 80% 80% at center, black 30%, transparent 65%);
    opacity: 0.95;
}

.brief-header::before {
    content: "";
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 1px;
    height: 40px;
    background: linear-gradient(180deg, var(--color-red-primary) 0%, transparent 100%);
    z-index: 1;
}

.brief-share {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    margin-top: 1.25rem;
}

.brief-share .share-label {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.brief-share .share-btn {
    width: 36px;
    height: 36px;
    border-radius: var(--radius-md);
    border: 1px solid var(--color-border-light);
    background: var(--color-bg-card);
    color: var(--color-text-muted);
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    transition: all var(--transition-fast);
    text-decoration: none;
}

.brief-share .share-btn:hover {
    border-color: var(--color-red-primary);
    color: var(--color-red-light);
    background: rgba(220, 38, 38, 0.1);
    transform: translateY(-2px);
}

.brief-share .share-btn svg {
    width: 18px;
    height: 18px;
}

.breadcrumb {
    font-size: 0.8125rem;
    margin-bottom: 1.5rem;
}

.breadcrumb a { color: var(--color-text-muted); }
.breadcrumb a:hover { color: var(--color-red-light); }
.breadcrumb .separator { color: var(--color-text-muted); margin: 0 0.5rem; }
.breadcrumb .current { color: var(--color-red-light); }

.brief-header h1 {
    font-size: 2.25rem;
    margin-bottom: 1rem;
    max-width: var(--content-width);
    line-height: 1.3;
}

.brief-metadata {
    display: flex;
    align-items: center;
    flex-wrap: wrap;
    gap: 0.75rem;
    font-size: 0.8125rem;
    color: var(--color-text-muted);
}

.brief-metadata .separator { color: var(--color-border-light); }
.brief-metadata time { color: var(--color-text-secondary); }

.category-label {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.075em;
}

.category-dot {
    width: 6px;
    height: 6px;
    border-radius: 50%;
}

.category-label.apt { color: var(--color-apt); }
.category-label.apt .category-dot { background-color: var(--color-apt); }
.category-label.ransomware { color: var(--color-ransomware); }
.category-label.ransomware .category-dot { background-color: var(--color-ransomware); }
.category-label.vulnerability { color: var(--color-vulnerability); }
.category-label.vulnerability .category-dot { background-color: var(--color-vulnerability); }
.category-label.supply-chain { color: var(--color-supply-chain); }
.category-label.supply-chain .category-dot { background-color: var(--color-supply-chain); }
.category-label.threat-actor { color: var(--color-threat-actor); }
.category-label.threat-actor .category-dot { background-color: var(--color-threat-actor); }
.category-label.industrial-control { color: var(--color-industrial); }
.category-label.industrial-control .category-dot { background-color: var(--color-industrial); }
.category-label.cloud-security { color: var(--color-cloud); }
.category-label.cloud-security .category-dot { background-color: var(--color-cloud); }
.category-label.defense { color: var(--color-defense); }
.category-label.defense .category-dot { background-color: var(--color-defense); }

/* Brief Content */
.brief-content { padding: 3rem 0; }

.content-wrapper {
    display: grid;
    grid-template-columns: 220px 1fr;
    gap: 3rem;
    align-items: start;
}

/* Table of Contents */
.table-of-contents {
    position: sticky;
    top: calc(var(--header-height) + 2rem);
}

.table-of-contents h2 {
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--color-text-muted);
    margin: 0 0 1rem 0;
    padding: 0;
    border: none;
}

.table-of-contents nav {
    display: flex;
    flex-direction: column;
}

.table-of-contents nav a {
    font-size: 0.8125rem;
    color: var(--color-text-secondary);
    padding: 0.5rem 0;
    padding-left: 1rem;
    border-left: 2px solid var(--color-border);
    transition: all var(--transition-fast);
}

.table-of-contents nav a:hover {
    color: var(--color-text-primary);
    border-left-color: var(--color-red-primary);
}

/* Content Body */
.content-body { max-width: var(--content-width); }
.content-body section { margin-bottom: 2.5rem; }

.content-body h2 {
    font-size: 1.5rem;
    margin-top: 2.5rem;
    margin-bottom: 1rem;
    padding-bottom: 0.75rem;
    border-bottom: 1px solid var(--color-border);
    color: var(--color-text-primary);
}

.content-body section:first-child h2 { margin-top: 0; }

.content-body h3 {
    font-size: 1.125rem;
    margin-top: 2rem;
    margin-bottom: 0.75rem;
    color: var(--color-red-light);
}

.content-body p {
    font-size: 1rem;
    line-height: 1.8;
    margin-bottom: 1.25rem;
    color: var(--color-text-secondary);
}

.content-body ul,
.content-body ol {
    margin-bottom: 1.25rem;
    padding-left: 1.5rem;
    color: var(--color-text-secondary);
}

.content-body li {
    margin-bottom: 0.5rem;
    line-height: 1.7;
}

.reference-list {
    list-style: none;
    padding-left: 0;
}

.reference-list li {
    padding: 0.875rem 0;
    border-bottom: 1px solid var(--color-border);
}

.reference-list li:last-child { border-bottom: none; }

.reference-list a {
    color: var(--color-text-secondary);
    font-size: 0.9375rem;
}

.reference-list a:hover { color: var(--color-red-light); }

/* Footer */
.site-footer {
    background-color: var(--color-bg-secondary);
    border-top: 1px solid var(--color-border);
    padding: 3rem 0 1.5rem;
    margin-top: auto;
}

.footer-content {
    display: flex;
    justify-content: space-between;
    padding-bottom: 2rem;
    border-bottom: 1px solid var(--color-border);
}

.footer-brand .logo-text,
.footer-brand .logo-accent { font-size: 1.125rem; }

.footer-tagline {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    margin-top: 0.5rem;
    margin-bottom: 0;
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.footer-links {
    display: flex;
    gap: 4rem;
}

.footer-column h3 {
    font-size: 0.6875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: var(--color-text-muted);
    margin: 0 0 1rem 0;
}

.footer-column a {
    display: block;
    font-size: 0.875rem;
    color: var(--color-text-secondary);
    padding: 0.25rem 0;
}

.footer-column a:hover { color: var(--color-red-light); }

.footer-bottom {
    padding-top: 1.5rem;
    text-align: center;
}

.footer-bottom p {
    font-size: 0.75rem;
    color: var(--color-text-muted);
    margin: 0;
}

/* Back to Top Button */
.back-to-top {
    position: fixed;
    bottom: 2rem;
    right: 2rem;
    width: 48px;
    height: 48px;
    background: var(--color-red-primary);
    border: none;
    border-radius: 50%;
    color: var(--color-text-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    opacity: 0;
    visibility: hidden;
    transform: translateY(20px);
    transition: all 0.3s ease;
    z-index: 1000;
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.4);
}

.back-to-top.visible {
    opacity: 1;
    visibility: visible;
    transform: translateY(0);
}

.back-to-top:hover {
    background: var(--color-red-light);
    transform: translateY(-4px);
    box-shadow: 0 6px 20px rgba(220, 38, 38, 0.5);
}

.back-to-top svg {
    width: 24px;
    height: 24px;
}

/* Responsive Design */
@media (max-width: 1024px) {
    .content-wrapper { grid-template-columns: 1fr; }

    .table-of-contents {
        position: static;
        margin-bottom: 2rem;
        padding: 1.25rem;
        background-color: var(--color-bg-card);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-lg);
    }

    .table-of-contents nav {
        flex-direction: row;
        flex-wrap: wrap;
        gap: 0.5rem;
    }

    .table-of-contents nav a {
        border-left: none;
        padding: 0.375rem 0.75rem;
        background-color: var(--color-bg-secondary);
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        font-size: 0.75rem;
    }

    .table-of-contents nav a:hover { border-color: var(--color-red-primary); }
}

@media (max-width: 768px) {
    html { font-size: 15px; }

    .brief-header-content {
        flex-direction: column-reverse;
        text-align: center;
    }
    
    .brief-logo {
        width: 200px;
        margin-bottom: 1rem;
    }
    
    .brief-share { justify-content: center; }

    .header-content {
        flex-direction: column;
        gap: 1rem;
        padding: 1rem 0;
    }

    .site-header { height: auto; }

    .main-nav {
        gap: 1rem;
        flex-wrap: wrap;
        justify-content: center;
    }

    .footer-content {
        flex-direction: column;
        gap: 2rem;
    }

    .footer-links {
        flex-direction: column;
        gap: 1.5rem;
    }

    .brief-header h1 { font-size: 1.75rem; }

    .brief-metadata {
        flex-direction: column;
        align-items: flex-start;
        gap: 0.5rem;
    }

    .brief-metadata .separator { display: none; }
}

@media (max-width: 480px) {
    .container { padding: 0 1rem; }
    .brief-header { padding: 2rem 0; }
    .brief-content { padding: 2rem 0; }
}

/* Print Styles */
@media print {
    .site-header, .table-of-contents, .site-footer, .raveneye { display: none; }
    body { background-color: #fff; color: #000; }
    .brief-header, .brief-content { background: #fff; }
    h1, h2, h3 { color: #000; }
    p { color: #333; }
    a { color: #000; text-decoration: underline; }
    .content-wrapper { display: block; }
}
"""


def create_post_html(post_data):
    """Generate full HTML for a blog post with EMBEDDED CSS."""
    
    title = post_data["title"]
    slug = post_data["slug"]
    date = post_data["date"]
    category = post_data["category"]
    content = post_data["content"]
    meta_description = post_data["meta_description"]
    keywords = post_data["keywords"]
    reading_time = post_data["reading_time"]
    
    date_obj = datetime.strptime(date, "%Y-%m-%d")
    formatted_date = date_obj.strftime("%B %d, %Y")
    iso_date = f"{date}T08:00:00-05:00"
    year = date_obj.strftime("%Y")
    
    post_url = f"{CONFIG['site_url']}/intel/blackwing/{year}/{date_obj.strftime('%m')}/{slug}.html"
    logo_url = f"{CONFIG['site_url']}/assets/images/blackwingdispatch-logo.png"
    
    safe_title = title.replace('"', '&quot;').replace("'", "&#39;")
    safe_description = meta_description.replace('"', '&quot;')
    keywords_str = ", ".join(keywords)
    
    category_classes = {
        "APT Activity": "apt",
        "Ransomware": "ransomware",
        "Vulnerability": "vulnerability",
        "Supply Chain": "supply-chain",
        "Threat Actor": "threat-actor",
        "Industrial Control": "industrial-control",
        "Cloud Security": "cloud-security",
        "Defense": "defense",
    }
    cat_class = category_classes.get(category, "defense")
    
    html = f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{safe_title} | Black Wing Dispatch</title>
    <meta name="description" content="{safe_description}">
    <meta name="keywords" content="{keywords_str}, cybersecurity, threat analysis, TacRaven">
    <meta name="author" content="{CONFIG['author']}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{post_url}">
    
    <meta property="og:type" content="article">
    <meta property="og:title" content="{safe_title}">
    <meta property="og:description" content="{safe_description}">
    <meta property="og:url" content="{post_url}">
    <meta property="og:site_name" content="TacRaven Solutions">
    <meta property="og:image" content="{logo_url}">
    <meta property="article:published_time" content="{iso_date}">
    <meta property="article:section" content="{category}">
    
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="{safe_title}">
    <meta name="twitter:description" content="{safe_description}">
    <meta name="twitter:site" content="{CONFIG['twitter_handle']}">
    
    <!-- EMBEDDED CSS - Guaranteed to load -->
    <style>
{EMBEDDED_CSS}
    </style>
    
    <script async src="https://www.googletagmanager.com/gtag/js?id={CONFIG['ga_id']}"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){{dataLayer.push(arguments);}}
        gtag('js', new Date());
        gtag('config', '{CONFIG['ga_id']}');
    </script>
</head>
<body>
    <header class="site-header">
        <div class="container">
            <div class="header-content">
                <a href="{CONFIG['site_url']}/index.html" class="logo">
                    <span class="logo-text">TAC</span><span class="logo-accent">RAVEN</span>
                </a>
                <nav class="main-nav" aria-label="Main navigation">
                    <a href="{CONFIG['site_url']}/index.html">Home</a>
                    <a href="{CONFIG['site_url']}/about.html">About</a>
                    <div class="nav-dropdown">
                        <button class="nav-dropdown-btn active">Blog <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 9l6 6 6-6"/></svg></button>
                        <div class="nav-dropdown-content">
                            <a href="{CONFIG['site_url']}/Blog.html">Cyber Careers</a>
                            <a href="{CONFIG['site_url']}/intel/blackwing/index.html" class="active">Black Wing Dispatch</a>
                        </div>
                    </div>
                    <a href="{CONFIG['site_url']}/learning-hub.html">Learning Hub</a>
                    <a href="{CONFIG['site_url']}/threat-map.html">Threat Map</a>
                    <a href="{CONFIG['site_url']}/intel/weekly/">Weekly Reports</a>
                    <a href="{CONFIG['site_url']}/cyber-news.html">News</a>
                    <a href="{CONFIG['site_url']}/tools.html">Tools</a>
                    <a href="{CONFIG['site_url']}/pricing.html">Programs</a>
                    <a href="{CONFIG['site_url']}/index.html#contact" class="btn-contact">Contact</a>
                </nav>
            </div>
        </div>
    </header>

    <!-- RavenEye Threat Ticker -->
    <div class="raveneye">
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
                <div class="raveneye-scroll">
                    <div class="raveneye-item">
                        <span class="raveneye-badge raveneye-badge--critical">Zero-Day</span>
                        <span class="raveneye-text">Microsoft Patches Critical Zero-Day in Windows Kernel</span>
                    </div>
                    <div class="raveneye-item">
                        <span class="raveneye-badge raveneye-badge--critical">Critical</span>
                        <span class="raveneye-text">Ivanti VPN Zero-Day Actively Exploited in the Wild</span>
                    </div>
                    <div class="raveneye-item">
                        <span class="raveneye-badge raveneye-badge--kev">KEV</span>
                        <span class="raveneye-text">CVE-2024-21887: Ivanti Connect Secure</span>
                    </div>
                    <div class="raveneye-item">
                        <span class="raveneye-badge raveneye-badge--alert">Alert</span>
                        <span class="raveneye-text">APT Groups Targeting Critical Infrastructure</span>
                    </div>
                    <div class="raveneye-item">
                        <span class="raveneye-badge raveneye-badge--critical">Zero-Day</span>
                        <span class="raveneye-text">Microsoft Patches Critical Zero-Day in Windows Kernel</span>
                    </div>
                    <div class="raveneye-item">
                        <span class="raveneye-badge raveneye-badge--critical">Critical</span>
                        <span class="raveneye-text">Ivanti VPN Zero-Day Actively Exploited in the Wild</span>
                    </div>
                </div>
            </div>
            <a href="{CONFIG['site_url']}/cyber-news.html" class="raveneye-cta">
                Full Feed
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="5" y1="12" x2="19" y2="12"/>
                    <polyline points="12 5 19 12 12 19"/>
                </svg>
            </a>
        </div>
    </div>

    <main class="threat-brief">
        <article>
            <header class="brief-header">
                <div class="container">
                    <div class="brief-header-content">
                        <div class="brief-header-text">
                            <nav class="breadcrumb">
                                <a href="{CONFIG['site_url']}/index.html">TacRaven</a>
                                <span class="separator">›</span>
                                <a href="{CONFIG['site_url']}/intel/blackwing/index.html">Black Wing Dispatch</a>
                                <span class="separator">›</span>
                                <span class="current">{category}</span>
                            </nav>
                            <h1>{title}</h1>
                            <div class="brief-metadata">
                                <span class="category-label {cat_class}">
                                    <span class="category-dot"></span>
                                    {category}
                                </span>
                                <span class="separator">|</span>
                                <time datetime="{date}">{formatted_date}</time>
                                <span class="separator">|</span>
                                <span>{reading_time} min read</span>
                            </div>
                            <div class="brief-share">
                                <span class="share-label">Share:</span>
                                <a href="https://twitter.com/intent/tweet?url={post_url}&text={safe_title}" target="_blank" class="share-btn" title="Share on Twitter">
                                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>
                                </a>
                                <a href="https://www.linkedin.com/sharing/share-offsite/?url={post_url}" target="_blank" class="share-btn" title="Share on LinkedIn">
                                    <svg viewBox="0 0 24 24" fill="currentColor"><path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/></svg>
                                </a>
                            </div>
                        </div>
                        <div class="brief-header-logo">
                            <img src="{logo_url}" alt="Black Wing Dispatch" class="brief-logo">
                        </div>
                    </div>
                </div>
            </header>

            <div class="brief-content">
                <div class="container">
                    <div class="content-wrapper">
                        <aside class="table-of-contents">
                            <h2>Contents</h2>
                            <nav>
                                <a href="#introduction">Introduction</a>
                                <a href="#background">Background</a>
                                <a href="#technical">Technical Breakdown</a>
                                <a href="#indicators">Key Indicators</a>
                                <a href="#patterns">Attack Patterns</a>
                                <a href="#impact">Real World Impact</a>
                                <a href="#recommendations">Recommendations</a>
                                <a href="#thoughts">Final Thoughts</a>
                                <a href="#resources">Resources</a>
                            </nav>
                        </aside>

                        <div class="content-body">
{content}
                        </div>
                    </div>
                </div>
            </div>
        </article>
    </main>

    <footer class="site-footer">
        <div class="container">
            <div class="footer-content">
                <div class="footer-brand">
                    <a href="{CONFIG['site_url']}/index.html" class="logo">
                        <span class="logo-text">TAC</span><span class="logo-accent">RAVEN</span>
                    </a>
                    <p class="footer-tagline">Cybersecurity Education & Threat Intelligence</p>
                </div>
                <div class="footer-links">
                    <div class="footer-column">
                        <h3>Resources</h3>
                        <a href="{CONFIG['site_url']}/Blog.html">Careers Blog</a>
                        <a href="{CONFIG['site_url']}/intel/blackwing/index.html">Black Wing Dispatch</a>
                        <a href="{CONFIG['site_url']}/tools.html">Tools</a>
                    </div>
                    <div class="footer-column">
                        <h3>Company</h3>
                        <a href="{CONFIG['site_url']}/about.html">About</a>
                        <a href="{CONFIG['site_url']}/index.html#contact">Contact</a>
                    </div>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; {datetime.now().year} TacRaven Solutions LLC. All rights reserved.</p>
            </div>
        </div>
    </footer>

    <button class="back-to-top" id="backToTop" aria-label="Back to top">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 15l-6-6-6 6"/>
        </svg>
    </button>

    <script>
        const backToTop = document.getElementById('backToTop');
        window.addEventListener('scroll', () => {{
            if (window.scrollY > 300) {{
                backToTop.classList.add('visible');
            }} else {{
                backToTop.classList.remove('visible');
            }}
        }});
        backToTop.addEventListener('click', () => {{
            window.scrollTo({{ top: 0, behavior: 'smooth' }});
        }});
    </script>
</body>
</html>'''
    
    return html


def generate_post(category=None, output_dir=None):
    """Generate a new blog post."""
    
    state_file = Path(__file__).parent / "content_state.json"
    state = {}
    if state_file.exists():
        with open(state_file, 'r') as f:
            state = json.load(f)
    
    today = datetime.now()
    
    force_category = os.environ.get("FORCE_CATEGORY", "").strip() or category
    topic, selected_category = select_next_topic(state, force_category)
    
    print(f"Generating: {topic}")
    print(f"Category: {selected_category}")
    
    content_data = generate_content_for_category(selected_category, topic)
    
    slug = topic.lower()
    for char in [':', "'", '"', ',', '.', '?', '!', '(', ')', '[', ']']:
        slug = slug.replace(char, '')
    slug = '-'.join(slug.split())
    slug = slug.replace('--', '-')
    slug = slug.replace(' ', '-')[:60]
    
    post_data = {
        "title": topic,
        "slug": slug,
        "date": today.strftime("%Y-%m-%d"),
        "category": selected_category,
        "content": content_data["body"],
        "excerpt": content_data["excerpt"],
        "meta_description": content_data["meta_description"],
        "keywords": content_data["keywords"],
        "reading_time": content_data["reading_time"],
    }
    
    html = create_post_html(post_data)
    
    if output_dir:
        website_root = Path(output_dir)
    else:
        website_root = Path(__file__).parent.parent.parent / "website"
    
    year = today.strftime("%Y")
    month = today.strftime("%m")
    
    post_dir = website_root / "intel" / "blackwing" / year / month
    post_dir.mkdir(parents=True, exist_ok=True)
    
    post_path = post_dir / f"{slug}.html"
    
    with open(post_path, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"Generated: {post_path}")
    
    state["used_topics"] = state.get("used_topics", [])
    state["used_topics"].append(topic)
    state["used_topics"] = state["used_topics"][-50:]
    state["last_generated"] = today.isoformat()
    state["last_category"] = selected_category
    state["recent_categories"] = state.get("recent_categories", [])
    state["recent_categories"].append(selected_category)
    state["recent_categories"] = state["recent_categories"][-5:]
    
    with open(state_file, 'w') as f:
        json.dump(state, f, indent=2)
    
    return post_path


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Black Wing Dispatch post')
    parser.add_argument('--category', help='Force specific category')
    parser.add_argument('--output-dir', help='Website repository root directory')
    args = parser.parse_args()
    
    generate_post(category=args.category, output_dir=args.output_dir)
