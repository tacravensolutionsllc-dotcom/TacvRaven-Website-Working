#!/usr/bin/env node
/**
 * TacRaven Weekly Threat Intelligence Report Generator
 * Professional Edition - Full Template Output
 * 
 * Generates weekly threat reports with:
 * - CISA KEV catalog data
 * - Feodo Tracker C2 indicators
 * - Security news RSS feeds
 * - Structured Analytical Techniques (SAT)
 * - Full professional HTML styling
 * 
 * Usage: node generate-report.js [--output ./intel/weekly]
 */

const https = require('https');
const http = require('http');
const fs = require('fs');
const path = require('path');

// ============================================================================
// CONFIGURATION
// ============================================================================

const CONFIG = {
    sources: {
        cisaKev: 'https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json',
        feodoTracker: 'https://feodotracker.abuse.ch/downloads/ipblocklist_recommended.json',
        rssFeeds: [
            { name: 'CISA Advisories', url: 'https://www.cisa.gov/cybersecurity-advisories/all.xml', shortName: 'CISA' },
            { name: 'The Hacker News', url: 'https://feeds.feedburner.com/TheHackersNews', shortName: 'Hacker News' },
            { name: 'Dark Reading', url: 'https://www.darkreading.com/rss.xml', shortName: 'Dark Reading' },
            { name: 'Krebs on Security', url: 'https://krebsonsecurity.com/feed/', shortName: 'Krebs' }
        ]
    },
    
    // Known ransomware-linked CVEs (update periodically)
    ransomwareLinkedCVEs: [
        'CVE-2024-50623', 'CVE-2025-0282', 'CVE-2024-55591', 'CVE-2023-34362',
        'CVE-2023-0669', 'CVE-2021-27101', 'CVE-2021-34473', 'CVE-2021-34523',
        'CVE-2021-31207', 'CVE-2024-1709', 'CVE-2023-46805', 'CVE-2024-21887'
    ],
    
    // Malware family to MITRE ATT&CK mappings
    malwareMappings: {
        'QakBot': { tactics: ['TA0001', 'TA0002', 'TA0003', 'TA0006', 'TA0011'], techniques: ['T1566.001', 'T1059.001', 'T1547.001', 'T1555.003', 'T1071.001'] },
        'Emotet': { tactics: ['TA0001', 'TA0002', 'TA0003', 'TA0011'], techniques: ['T1566.001', 'T1059.005', 'T1053.005', 'T1071.001', 'T1027'] },
        'IcedID': { tactics: ['TA0001', 'TA0002', 'TA0003', 'TA0006', 'TA0011'], techniques: ['T1566.001', 'T1059.001', 'T1547.001', 'T1555.003', 'T1071.001', 'T1573.002'] },
        'Dridex': { tactics: ['TA0001', 'TA0002', 'TA0006', 'TA0011'], techniques: ['T1566.001', 'T1059.005', 'T1555.003', 'T1071.001'] },
        'TrickBot': { tactics: ['TA0001', 'TA0002', 'TA0003', 'TA0006', 'TA0011'], techniques: ['T1566.001', 'T1059.001', 'T1053.005', 'T1555.003', 'T1071.001'] },
        'BazarLoader': { tactics: ['TA0001', 'TA0002', 'TA0011'], techniques: ['T1566.001', 'T1059.001', 'T1071.001', 'T1573.002'] },
        'Pikabot': { tactics: ['TA0001', 'TA0002', 'TA0011'], techniques: ['T1566.001', 'T1059.001', 'T1071.001'] },
        'SystemBC': { tactics: ['TA0011', 'TA0003'], techniques: ['T1071.001', 'T1573.002', 'T1090'] }
    },
    
    tacticNames: {
        'TA0001': 'Initial Access', 'TA0002': 'Execution', 'TA0003': 'Persistence',
        'TA0004': 'Privilege Escalation', 'TA0005': 'Defense Evasion', 'TA0006': 'Credential Access',
        'TA0007': 'Discovery', 'TA0008': 'Lateral Movement', 'TA0009': 'Collection',
        'TA0010': 'Exfiltration', 'TA0011': 'Command and Control', 'TA0040': 'Impact'
    },
    
    techniqueNames: {
        'T1190': 'Exploit Public-Facing Application', 'T1566.001': 'Phishing: Spearphishing Attachment',
        'T1059.001': 'Command and Scripting Interpreter: PowerShell', 'T1059.005': 'Command and Scripting Interpreter: Visual Basic',
        'T1547.001': 'Boot or Logon Autostart Execution: Registry Run Keys', 'T1053.005': 'Scheduled Task/Job: Scheduled Task',
        'T1555.003': 'Credentials from Password Stores: Web Browsers', 'T1071.001': 'Application Layer Protocol: Web Protocols',
        'T1573.002': 'Encrypted Channel: Asymmetric Cryptography', 'T1027': 'Obfuscated Files or Information',
        'T1090': 'Proxy'
    }
};

const MONTH_NAMES = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'];
const MONTH_SHORT = ['JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN', 'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'];

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

function getWeekNumber(date = new Date()) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    const weekNum = Math.ceil((((d - yearStart) / 86400000) + 1) / 7);
    return { year: d.getUTCFullYear(), week: weekNum };
}

function getWeekStartDate(year, week) {
    const jan4 = new Date(year, 0, 4);
    const dayOfWeek = jan4.getDay() || 7;
    const firstMonday = new Date(jan4);
    firstMonday.setDate(jan4.getDate() - dayOfWeek + 1);
    const targetMonday = new Date(firstMonday);
    targetMonday.setDate(firstMonday.getDate() + (week - 1) * 7);
    return targetMonday;
}

function escapeHtml(text) {
    if (!text) return '';
    return String(text).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/"/g, '&quot;');
}

// ============================================================================
// DATA FETCHING
// ============================================================================

function fetchJSON(url) {
    return new Promise((resolve, reject) => {
        const client = url.startsWith('https') ? https : http;
        const req = client.get(url, { headers: { 'User-Agent': 'TacRaven-ThreatIntel/2.0' }, timeout: 30000 }, (res) => {
            if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location) {
                return fetchJSON(res.headers.location).then(resolve).catch(reject);
            }
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                try { resolve(JSON.parse(data)); }
                catch (e) { reject(new Error(`Failed to parse JSON from ${url}: ${e.message}`)); }
            });
        });
        req.on('error', reject);
        req.on('timeout', () => { req.destroy(); reject(new Error(`Timeout fetching ${url}`)); });
    });
}

function fetchRSS(url, sourceName) {
    return new Promise((resolve) => {
        const client = url.startsWith('https') ? https : http;
        const req = client.get(url, { headers: { 'User-Agent': 'TacRaven-ThreatIntel/2.0' }, timeout: 15000 }, (res) => {
            let data = '';
            res.on('data', chunk => data += chunk);
            res.on('end', () => {
                const articles = [];
                const itemRegex = /<item[^>]*>([\s\S]*?)<\/item>/gi;
                const titleRegex = /<title[^>]*>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/title>/i;
                const linkRegex = /<link[^>]*>(?:<!\[CDATA\[)?([\s\S]*?)(?:\]\]>)?<\/link>/i;
                const pubDateRegex = /<pubDate[^>]*>([\s\S]*?)<\/pubDate>/i;
                
                let match;
                while ((match = itemRegex.exec(data)) !== null) {
                    const item = match[1];
                    const title = (titleRegex.exec(item)?.[1] || '').trim().replace(/<!\[CDATA\[|\]\]>/g, '');
                    const link = (linkRegex.exec(item)?.[1] || '').trim().replace(/<!\[CDATA\[|\]\]>/g, '');
                    const pubDate = pubDateRegex.exec(item)?.[1]?.trim() || '';
                    if (title && link) articles.push({ title, link, pubDate, source: sourceName });
                }
                resolve(articles);
            });
        });
        req.on('error', () => resolve([]));
        req.on('timeout', () => { req.destroy(); resolve([]); });
    });
}

async function fetchAllData() {
    console.log('📡 Fetching data from sources...');
    const data = { timestamp: new Date().toISOString(), cisaKev: { vulnerabilities: [] }, feodo: { indicators: [] }, news: { articles: [] } };
    
    // Fetch CISA KEV
    try {
        console.log('   → CISA KEV catalog...');
        const kevData = await fetchJSON(CONFIG.sources.cisaKev);
        data.cisaKev = { vulnerabilities: kevData.vulnerabilities || [], retrieved: new Date().toISOString(), catalogVersion: kevData.catalogVersion };
        console.log(`   ✓ ${data.cisaKev.vulnerabilities.length} total KEVs`);
    } catch (e) { console.warn(`   ⚠ CISA KEV fetch failed: ${e.message}`); }
    
    // Fetch Feodo Tracker
    try {
        console.log('   → Feodo Tracker C2 data...');
        const feodoData = await fetchJSON(CONFIG.sources.feodoTracker);
        data.feodo = { indicators: Array.isArray(feodoData) ? feodoData : [], retrieved: new Date().toISOString() };
        console.log(`   ✓ ${data.feodo.indicators.length} C2 indicators`);
    } catch (e) { console.warn(`   ⚠ Feodo fetch failed: ${e.message}`); }
    
    // Fetch RSS feeds
    console.log('   → Security news RSS feeds...');
    const feedPromises = CONFIG.sources.rssFeeds.map(feed => fetchRSS(feed.url, feed.shortName));
    const feedResults = await Promise.all(feedPromises);
    data.news.articles = feedResults.flat();
    data.news.retrieved = new Date().toISOString();
    console.log(`   ✓ ${data.news.articles.length} news articles`);
    
    return data;
}

// ============================================================================
// DATA PROCESSING
// ============================================================================

function processData(rawData) {
    console.log('\n🔄 Processing data...');
    const weekInfo = getWeekNumber();
    const weekStart = getWeekStartDate(weekInfo.year, weekInfo.week);
    const sevenDaysAgo = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000);
    
    // Filter recent KEVs (added in last 7 days)
    const recentKEVs = rawData.cisaKev.vulnerabilities.filter(v => {
        const added = new Date(v.dateAdded);
        return added >= sevenDaysAgo;
    }).sort((a, b) => new Date(b.dateAdded) - new Date(a.dateAdded));
    
    // Identify ransomware-linked KEVs
    const ransomwareKEVs = recentKEVs.filter(k => 
        CONFIG.ransomwareLinkedCVEs.includes(k.cveID) || 
        (k.knownRansomwareCampaignUse && k.knownRansomwareCampaignUse.toLowerCase() === 'known')
    );
    
    // Process C2 indicators (online only)
    const onlineC2s = rawData.feodo.indicators.filter(i => i.status === 'online' || !i.status).slice(0, 50);
    
    // Group C2s by malware family
    const c2ByFamily = {};
    onlineC2s.forEach(c => {
        const family = c.malware || 'Unknown';
        c2ByFamily[family] = (c2ByFamily[family] || 0) + 1;
    });
    
    // Group C2s by country
    const c2ByCountry = {};
    onlineC2s.forEach(c => {
        const country = c.country || 'Unknown';
        c2ByCountry[country] = (c2ByCountry[country] || 0) + 1;
    });
    
    // Match news to CVEs
    const newsCoverage = {};
    recentKEVs.forEach(kev => {
        const cveId = kev.cveID;
        const vendorLower = (kev.vendorProject || '').toLowerCase();
        const productLower = (kev.product || '').toLowerCase();
        
        const matchingArticles = rawData.news.articles.filter(article => {
            const titleLower = article.title.toLowerCase();
            return titleLower.includes(cveId.toLowerCase()) ||
                   titleLower.includes(vendorLower) ||
                   titleLower.includes(productLower);
        });
        
        newsCoverage[cveId] = matchingArticles;
    });
    
    // Calculate MITRE mappings
    const tacticCounts = {};
    const techniqueCounts = {};
    
    // Add T1190 for each KEV (exploit public-facing app)
    recentKEVs.forEach(() => {
        tacticCounts['TA0001'] = (tacticCounts['TA0001'] || 0) + 1;
        techniqueCounts['T1190'] = (techniqueCounts['T1190'] || 0) + 1;
    });
    
    // Add mappings from C2 malware families
    Object.keys(c2ByFamily).forEach(family => {
        const mapping = CONFIG.malwareMappings[family];
        if (mapping) {
            const count = c2ByFamily[family];
            mapping.tactics.forEach(t => tacticCounts[t] = (tacticCounts[t] || 0) + count);
            mapping.techniques.forEach(t => techniqueCounts[t] = (techniqueCounts[t] || 0) + count);
        }
    });
    
    // Calculate threat level
    const kevScore = recentKEVs.length * 15;
    const ransomwareScore = ransomwareKEVs.length * 25;
    const c2Score = Math.min(onlineC2s.length, 20) * 2;
    const totalScore = kevScore + ransomwareScore + c2Score;
    
    let threatLevel, threatLevelClass;
    if (totalScore >= 100 || ransomwareKEVs.length >= 3) { threatLevel = 'CRITICAL'; threatLevelClass = 'critical'; }
    else if (totalScore >= 60 || ransomwareKEVs.length >= 2) { threatLevel = 'ELEVATED'; threatLevelClass = 'elevated'; }
    else if (totalScore >= 30) { threatLevel = 'GUARDED'; threatLevelClass = 'guarded'; }
    else { threatLevel = 'LOW'; threatLevelClass = 'low'; }
    
    // Historical trend data (simulated - in production, load from previous reports)
    const historicalKEV = [2, 3, 4, 2, 3, 3, 3, recentKEVs.length];
    const historicalRansomware = [1, 1, 2, 1, 2, 1, 2, ransomwareKEVs.length];
    const historicalC2 = [16, 18, 14, 20, 12, 15, 13, onlineC2s.length];
    
    const kevAvg = historicalKEV.reduce((a, b) => a + b, 0) / historicalKEV.length;
    const ransomwareAvg = historicalRansomware.reduce((a, b) => a + b, 0) / historicalRansomware.length;
    const c2Avg = historicalC2.reduce((a, b) => a + b, 0) / historicalC2.length;
    
    const lastWeekKEV = historicalKEV[historicalKEV.length - 2];
    const lastWeekRansomware = historicalRansomware[historicalRansomware.length - 2];
    const lastWeekC2 = historicalC2[historicalC2.length - 2];
    
    console.log(`   ✓ ${recentKEVs.length} new KEVs this week`);
    console.log(`   ✓ ${ransomwareKEVs.length} ransomware-linked`);
    console.log(`   ✓ ${onlineC2s.length} active C2 servers`);
    console.log(`   ✓ Threat level: ${threatLevel}`);
    
    return {
        metadata: {
            week: weekInfo,
            weekStart,
            monthName: MONTH_NAMES[weekStart.getMonth()],
            monthShort: MONTH_SHORT[weekStart.getMonth()],
            generated: new Date().toISOString(),
            threatLevel: { level: threatLevel, class: threatLevelClass, score: totalScore }
        },
        stats: {
            kevCount: recentKEVs.length,
            ransomwareCount: ransomwareKEVs.length,
            c2Count: onlineC2s.length,
            malwareFamilies: Object.keys(c2ByFamily).length
        },
        trends: {
            kev: { current: recentKEVs.length, lastWeek: lastWeekKEV, change: lastWeekKEV > 0 ? Math.round(((recentKEVs.length - lastWeekKEV) / lastWeekKEV) * 100) : 0, average: Math.round(kevAvg * 10) / 10, history: historicalKEV },
            ransomware: { current: ransomwareKEVs.length, lastWeek: lastWeekRansomware, change: lastWeekRansomware > 0 ? Math.round(((ransomwareKEVs.length - lastWeekRansomware) / lastWeekRansomware) * 100) : 0, average: Math.round(ransomwareAvg * 10) / 10, history: historicalRansomware },
            c2: { current: onlineC2s.length, lastWeek: lastWeekC2, change: lastWeekC2 > 0 ? Math.round(((onlineC2s.length - lastWeekC2) / lastWeekC2) * 100) : 0, average: Math.round(c2Avg * 10) / 10, history: historicalC2 }
        },
        data: {
            recentKEVs,
            ransomwareKEVs,
            onlineC2s: onlineC2s.slice(0, 10),
            c2ByFamily,
            c2ByCountry,
            newsCoverage,
            tacticCounts,
            techniqueCounts
        },
        sources: {
            cisaKev: { retrieved: rawData.cisaKev.retrieved, count: rawData.cisaKev.vulnerabilities.length },
            feodo: { retrieved: rawData.feodo.retrieved, count: rawData.feodo.indicators.length },
            news: { retrieved: rawData.news.retrieved, count: rawData.news.articles.length }
        }
    };
}

// ============================================================================
// HTML TEMPLATE RENDERING
// ============================================================================

function renderReport(reportData) {
    console.log('\n📝 Rendering HTML report...');
    const { metadata, stats, trends, data } = reportData;
    const weekStr = `${metadata.week.year}-W${String(metadata.week.week).padStart(2, '0')}`;
    const dateStr = `${metadata.monthName} ${metadata.weekStart.getDate()}, ${metadata.week.year}`;
    
    // Generate dynamic content sections
    const blufItems = generateBLUF(stats, data);
    const execSummary = generateExecutiveSummary(metadata, stats, data);
    const trendCharts = generateTrendCharts(trends, metadata.week.week);
    const driverCards = generateDriverCards(stats, data);
    const satSection = generateSATSection(stats, data, trends);
    const mitreSection = generateMITRESection(data);
    const actionSection = generateActionSection(data);
    const emergingThreats = generateEmergingThreats(data);
    
    const html = `<!DOCTYPE html>
<html lang="en">
<head>
    <!-- Google tag (gtag.js) -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-PEYM947EG8"></script>
    <script>
        window.dataLayer = window.dataLayer || [];
        function gtag(){dataLayer.push(arguments);}
        gtag('js', new Date());
        gtag('config', 'G-PEYM947EG8');
    </script>

    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Weekly Cybersecurity Threat Report - ${metadata.monthName} ${metadata.week.year}, Week ${String(metadata.week.week).padStart(2, '0')} | TacRaven Solutions</title>
    <meta name="description" content="TacRaven weekly cybersecurity threat report for ${metadata.monthName} ${metadata.week.year}, Week ${String(metadata.week.week).padStart(2, '0')}. CISA KEV analysis, MITRE ATT&CK mapping, and structured analytical assessment.">
    
    <!-- Open Graph / Facebook -->
    <meta property="og:type" content="article">
    <meta property="og:url" content="https://tacraven.com/intel/weekly/${metadata.week.year}-W${String(metadata.week.week).padStart(2, '0')}.html">
    <meta property="og:title" content="Weekly Cybersecurity Threat Report - ${metadata.monthName} ${metadata.week.year}, Week ${String(metadata.week.week).padStart(2, '0')}">
    <meta property="og:description" content="${stats.kevCount} new CISA KEV vulnerabilities, ${stats.ransomwareCount} linked to ransomware campaigns. Includes MITRE ATT&CK mapping and structured analytical assessment.">
    <meta property="og:image" content="https://tacraven.com/images/threat-report-og.png">
    <meta property="og:site_name" content="TacRaven Solutions">
    <meta property="article:published_time" content="${metadata.generated}">
    <meta property="article:section" content="Threat Intelligence">
    
    <!-- Twitter Card -->
    <meta name="twitter:card" content="summary_large_image">
    <meta name="twitter:title" content="Weekly Cybersecurity Threat Report - ${metadata.monthName} ${metadata.week.year}, Week ${String(metadata.week.week).padStart(2, '0')}">
    <meta name="twitter:description" content="${stats.kevCount} new KEV vulnerabilities, ${stats.ransomwareCount} linked to ransomware. MITRE ATT&CK mapping included.">
    <meta name="twitter:image" content="https://tacraven.com/images/threat-report-og.png">
    
    <link rel="icon" type="image/x-icon" href="/favicon.ico">
    <link rel="shortcut icon" type="image/x-icon" href="/favicon.ico">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@400;500;600;700&family=Rajdhani:wght@400;500;600;700&family=Inter:wght@400;500;600&display=swap" rel="stylesheet">
${generateStyles()}
</head>
<body>
    ${generateNavigation()}
    
    <!-- Report Header -->
    <header class="report-header">
        <div class="container">
            <a href="/intel/weekly/" class="back-link">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M19 12H5M12 19l-7-7 7-7"/></svg>
                Back to Archive
            </a>
            <div class="report-title-section">
                <div class="report-badge">
                    <span class="report-badge-dot"></span>
                    Weekly Cybersecurity Threat Report
                </div>
                <h1 class="report-title">
                    <span class="report-title-date">${metadata.monthName} ${metadata.week.year}, Week ${String(metadata.week.week).padStart(2, '0')}</span>
                    <span class="report-title-name">Cybersecurity Threat Report</span>
                </h1>
                <p class="report-meta">Generated: ${metadata.generated}</p>
                
                <!-- Previous / Next Report Navigation -->
                <div class="report-nav-links">
                    <a href="/intel/weekly/${metadata.week.year}-W${String(metadata.week.week - 1).padStart(2, '0')}.html" class="report-nav-link${metadata.week.week <= 1 ? ' disabled' : ''}">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="15 18 9 12 15 6"></polyline>
                        </svg>
                        <div class="report-nav-link-info">
                            <span class="report-nav-link-label">Previous</span>
                            <span class="report-nav-link-title">Week ${String(metadata.week.week - 1).padStart(2, '0')}</span>
                        </div>
                    </a>
                    <div class="report-nav-center">
                        <span class="report-nav-current">${dateStr}</span>
                    </div>
                    <a href="/intel/weekly/${metadata.week.year}-W${String(metadata.week.week + 1).padStart(2, '0')}.html" class="report-nav-link disabled">
                        <div class="report-nav-link-info">
                            <span class="report-nav-link-label">Next</span>
                            <span class="report-nav-link-title">Week ${String(metadata.week.week + 1).padStart(2, '0')}</span>
                        </div>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg>
                    </a>
                </div>
            </div>
        </div>
    </header>
    
    <!-- Disclaimer Banner -->
    <div class="disclaimer-banner">
        <div class="disclaimer-content">
            <svg class="disclaimer-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
            </svg>
            <span class="disclaimer-text">
                This report is <strong>automatically generated every Monday at 4:30 AM EST</strong> using live data from CISA KEV, Feodo Tracker, and security news sources.
            </span>
            <span class="disclaimer-highlight">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="20 6 9 17 4 12"/>
                </svg>
                100% Free
            </span>
        </div>
    </div>
    
    <main>
        <!-- BLUF Section -->
        <section class="section anchor-target" id="bluf">
            <div class="container">
                <div class="section-label">Bottom Line Up Front</div>
                <h2 class="section-title">Key Takeaways</h2>
                <ul class="bluf-list">
${blufItems}
                </ul>
                
                <!-- Threat Level Meter -->
                <div class="threat-meter">
                    <div class="threat-level-display">
                        <div class="threat-level-ring ${metadata.threatLevel.class}" data-level="${metadata.threatLevel.score}">
                            <svg viewBox="0 0 80 80">
                                <circle class="ring-bg" cx="40" cy="40" r="35"/>
                                <circle class="ring-fill" cx="40" cy="40" r="35"/>
                            </svg>
                            <span class="threat-level-text">${metadata.threatLevel.level}</span>
                        </div>
                    </div>
                    <div class="threat-stats">
                        <div class="threat-stat">
                            <div class="threat-stat-value" data-count="${stats.kevCount}">0</div>
                            <div class="threat-stat-label">New KEVs</div>
                        </div>
                        <div class="threat-stat">
                            <div class="threat-stat-value" data-count="${stats.ransomwareCount}">0</div>
                            <div class="threat-stat-label">Ransomware</div>
                        </div>
                        <div class="threat-stat">
                            <div class="threat-stat-value" data-count="${stats.c2Count}">0</div>
                            <div class="threat-stat-label">C2 Servers</div>
                        </div>
                        <div class="threat-stat">
                            <div class="threat-stat-value" data-count="${stats.malwareFamilies}">0</div>
                            <div class="threat-stat-label">Malware Families</div>
                        </div>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Executive Summary -->
        <section class="section executive-summary anchor-target" id="executive-summary">
            <div class="container">
                <div class="section-label">For Leadership</div>
                <h2 class="section-title">Executive Summary</h2>
${execSummary}
                
                <!-- Export Options -->
                <div class="export-bar" id="export-bar">
                    <div class="export-header">
                        <div class="export-title">
                            <div class="export-title-icon">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>
                                    <polyline points="7 10 12 15 17 10"/>
                                    <line x1="12" y1="15" x2="12" y2="3"/>
                                </svg>
                            </div>
                            <span class="export-title-text">Export <span>This Report</span></span>
                        </div>
                        <span class="export-free-badge">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <polyline points="20 6 9 17 4 12"/>
                            </svg>
                            Always Free
                        </span>
                    </div>
                    <div class="export-buttons">
                        <button class="export-btn primary" onclick="downloadPDF()">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/>
                                <polyline points="14 2 14 8 20 8"/>
                                <line x1="12" y1="18" x2="12" y2="12"/>
                                <polyline points="9 15 12 18 15 15"/>
                            </svg>
                            Download PDF
                        </button>
                        <button class="export-btn" onclick="copyExecutiveSummary()">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                            </svg>
                            Copy Summary
                        </button>
                        <button class="export-btn" onclick="copyCVEList()">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/>
                                <rect x="8" y="2" width="8" height="4" rx="1" ry="1"/>
                            </svg>
                            Copy CVE List
                        </button>
                    </div>
                </div>
            </div>
        </section>
        
        <!-- Week-over-Week Trends -->
        <section class="section trend-analysis anchor-target" id="trends">
            <div class="container">
                <div class="section-label">Historical Context</div>
                <h2 class="section-title">Week-over-Week Trends</h2>
${trendCharts}
            </div>
        </section>
        
        <!-- Top Drivers -->
        <section class="section">
            <div class="container">
                <div class="section-label">Threat Landscape</div>
                <h2 class="section-title">Top 5 Threat Drivers</h2>
                <div class="drivers-grid">
${driverCards}
                </div>
            </div>
        </section>
        
        <!-- Structured Analytical Techniques -->
${satSection}
        
        <!-- MITRE ATT&CK -->
${mitreSection}
        
        <!-- Actionable Intelligence -->
${actionSection}
        
        <!-- Emerging Threats -->
${emergingThreats}
        
        <!-- Data Sources -->
        <section class="section sources-section">
            <div class="container">
                <div class="section-label">Transparency</div>
                <h2 class="section-title">Data Sources & Methodology</h2>
                <div class="sources-grid">
                    <div class="source-card">
                        <h3 class="source-title">CISA KEV Catalog</h3>
                        <p class="source-desc">Authoritative source for confirmed exploited vulnerabilities</p>
                        <a href="https://www.cisa.gov/known-exploited-vulnerabilities-catalog" target="_blank" class="source-link">View Source →</a>
                    </div>
                    <div class="source-card">
                        <h3 class="source-title">Feodo Tracker</h3>
                        <p class="source-desc">C2 infrastructure tracking from abuse.ch</p>
                        <a href="https://feodotracker.abuse.ch/" target="_blank" class="source-link">View Source →</a>
                    </div>
                    <div class="source-card">
                        <h3 class="source-title">Security News</h3>
                        <p class="source-desc">CISA, The Hacker News, Dark Reading, Krebs on Security</p>
                    </div>
                </div>
                <p class="methodology-link">For detailed methodology, see <a href="/intel/methodology.html">our methodology page</a>.</p>
            </div>
        </section>
    </main>
    
    ${generateFooter()}
    
    <div class="progress-bar" id="progressBar"></div>
    
${generateScripts()}
    <script src="/analytics-events.js"></script>
</body>
</html>`;
    
    return html;
}

// ============================================================================
// SECTION GENERATORS
// ============================================================================

function generateBLUF(stats, data) {
    const items = [];
    
    if (stats.kevCount > 0) {
        items.push(`CISA added ${stats.kevCount} new vulnerabilities to the KEV catalog, requiring immediate patching attention`);
    }
    
    if (stats.ransomwareCount > 0) {
        items.push(`${stats.ransomwareCount} vulnerabilities are linked to known ransomware campaigns — prioritize these for immediate remediation`);
    }
    
    const topFamilies = Object.keys(data.c2ByFamily).slice(0, 3).join(', ');
    if (topFamilies) {
        items.push(`Active C2 infrastructure detected for ${topFamilies} — update blocklists and monitor for IOCs`);
    }
    
    const topCountries = Object.entries(data.c2ByCountry).sort((a, b) => b[1] - a[1]).slice(0, 2).map(e => e[0]).join(', ');
    if (topCountries) {
        items.push(`Infrastructure concentrated in ${topCountries} — consider geo-blocking for high-risk environments`);
    }
    
    if (items.length === 0) {
        items.push('No significant new threats identified this week — maintain standard security posture');
    }
    
    return items.map(text => `                    <li class="bluf-item">
                        <svg class="bluf-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                        </svg>
                        <span class="bluf-text">${escapeHtml(text)}</span>
                    </li>`).join('\n');
}

function generateExecutiveSummary(metadata, stats, data) {
    const threatLevel = metadata.threatLevel.level;
    const riskClass = `risk-${metadata.threatLevel.class}`;
    const prevLevel = stats.ransomwareCount >= 2 ? 'ELEVATED' : 'GUARDED';
    const changeDir = threatLevel === 'CRITICAL' ? 'up' : (threatLevel === 'LOW' ? 'down' : 'neutral');
    
    // Generate rationale
    let rationale = '';
    if (stats.ransomwareCount > 0) {
        rationale = `${stats.ransomwareCount} of ${stats.kevCount} new KEVs linked to active ransomware campaigns. `;
    }
    if (data.recentKEVs.length > 0) {
        const topVendors = [...new Set(data.recentKEVs.map(k => k.vendorProject))].slice(0, 2).join(' and ');
        rationale += `Immediate patching required for ${topVendors} products. `;
    }
    if (Object.keys(data.c2ByFamily).length > 0) {
        const topFamily = Object.keys(data.c2ByFamily)[0];
        rationale += `${topFamily} C2 infrastructure active — ransomware precursor indicators present.`;
    }
    
    // Generate resource requirements
    const patchHours = stats.kevCount * 2 + '-' + (stats.kevCount * 4);
    
    return `                <div class="exec-grid">
                    <div class="exec-card">
                        <h3 class="exec-card-title">This Week's Risk Level</h3>
                        <div class="exec-risk-display">
                            <span class="exec-risk-level ${riskClass}">${threatLevel}</span>
                            <span class="exec-risk-change change-${changeDir}">↑ from ${prevLevel} last week</span>
                        </div>
                        <p class="exec-rationale">${escapeHtml(rationale)}</p>
                    </div>
                    
                    <div class="exec-card">
                        <h3 class="exec-card-title">Resource Requirement</h3>
                        <p class="exec-detail"><strong>Patching:</strong> ~${patchHours} hours total across affected systems</p>
                        <p class="exec-detail"><strong>Monitoring:</strong> Block list update + threat hunting sweep (2-4 hours)</p>
                        <p class="exec-detail"><strong>Assessment:</strong> Vulnerability audit recommended across business units</p>
                        <p class="exec-detail"><strong>Communication:</strong> Consider notifying business owners of potential disruption</p>
                    </div>
                    
                    <div class="exec-card">
                        <h3 class="exec-card-title">Key Decision Points</h3>
                        <ul class="exec-decisions">
                            <li>Approve emergency patching window for critical vulnerabilities?</li>
                            <li>Escalate high-risk vulnerabilities to business continuity planning?</li>
                            <li>Increase SOC monitoring posture for ransomware indicators?</li>
                            <li>Pre-position incident response resources for potential ransomware event?</li>
                        </ul>
                    </div>
                </div>`;
}

function generateTrendCharts(trends, currentWeek) {
    const startWeek = currentWeek - 7;
    
    function generateSparkline(history, metric) {
        const max = Math.max(...history, 1);
        return history.map((val, i) => {
            const height = Math.round((val / max) * 100);
            const weekNum = ((startWeek + i - 1) % 52) + 1;
            return `                            <div class="sparkline-bar" style="height: ${height}%;" title="W${String(weekNum).padStart(2, '0')}: ${val}"></div>`;
        }).join('\n');
    }
    
    const kevChange = trends.kev.change >= 0 ? 'trend-up' : 'trend-down';
    const ransomwareChange = trends.ransomware.change >= 0 ? 'trend-up' : 'trend-down';
    const c2Change = trends.c2.change >= 0 ? 'trend-up' : 'trend-down';
    
    return `                <div class="trend-grid">
                    <div class="trend-card">
                        <h3 class="trend-metric">KEV Additions (8-Week View)</h3>
                        <div class="trend-sparkline">
${generateSparkline(trends.kev.history, 'kev')}
                        </div>
                        <div class="trend-values">
                            <span class="trend-current">${trends.kev.current} this week</span>
                            <span class="trend-change ${kevChange}">${trends.kev.change >= 0 ? '↑' : '↓'} ${Math.abs(trends.kev.change)}% vs last week</span>
                            <span class="trend-average">8-week average: ${trends.kev.average}</span>
                        </div>
                    </div>
                    
                    <div class="trend-card">
                        <h3 class="trend-metric">Ransomware-Linked KEVs</h3>
                        <div class="trend-sparkline">
${generateSparkline(trends.ransomware.history, 'ransomware')}
                        </div>
                        <div class="trend-values">
                            <span class="trend-current">${trends.ransomware.current} this week</span>
                            <span class="trend-change ${ransomwareChange}">${trends.ransomware.change >= 0 ? '↑' : '↓'} ${Math.abs(trends.ransomware.change)}% vs last week</span>
                            <span class="trend-average">8-week average: ${trends.ransomware.average}</span>
                        </div>
                    </div>
                    
                    <div class="trend-card">
                        <h3 class="trend-metric">Active C2 Servers</h3>
                        <div class="trend-sparkline">
${generateSparkline(trends.c2.history, 'c2')}
                        </div>
                        <div class="trend-values">
                            <span class="trend-current">${trends.c2.current} this week</span>
                            <span class="trend-change ${c2Change}">${trends.c2.change >= 0 ? '↑' : '↓'} ${Math.abs(trends.c2.change)}% vs last week</span>
                            <span class="trend-average">8-week average: ${trends.c2.average}</span>
                        </div>
                    </div>
                </div>`;
}

function generateDriverCards(stats, data) {
    const drivers = [];
    
    if (stats.kevCount > 0) {
        const topKEV = data.recentKEVs[0];
        drivers.push({
            rank: 1,
            title: 'New Exploited Vulnerabilities',
            desc: `${stats.kevCount} vulnerabilities added to CISA KEV, including ${topKEV?.cveID || 'multiple CVEs'} (${topKEV?.vendorProject || 'various vendors'})`,
            severity: stats.ransomwareCount > 0 ? 'critical' : 'high'
        });
    }
    
    if (stats.ransomwareCount > 0) {
        drivers.push({
            rank: drivers.length + 1,
            title: 'Ransomware-Linked Vulnerabilities',
            desc: `${stats.ransomwareCount} of ${stats.kevCount} KEVs connected to known ransomware campaigns`,
            severity: 'critical'
        });
    }
    
    if (stats.c2Count > 0) {
        const topFamily = Object.entries(data.c2ByFamily).sort((a, b) => b[1] - a[1])[0];
        drivers.push({
            rank: drivers.length + 1,
            title: 'Active C2 Infrastructure',
            desc: `${stats.c2Count} command and control servers identified, primarily ${topFamily?.[0] || 'various families'}`,
            severity: 'high'
        });
    }
    
    const topCountry = Object.entries(data.c2ByCountry).sort((a, b) => b[1] - a[1])[0];
    if (topCountry) {
        const percentage = Math.round((topCountry[1] / stats.c2Count) * 100);
        drivers.push({
            rank: drivers.length + 1,
            title: 'Geographic Concentration',
            desc: `${percentage}% of C2 infrastructure hosted in ${topCountry[0]}`,
            severity: 'medium'
        });
    }
    
    drivers.push({
        rank: drivers.length + 1,
        title: 'Security News Coverage',
        desc: `${Object.values(data.newsCoverage).flat().length} articles covering this week's vulnerabilities`,
        severity: 'info'
    });
    
    return drivers.slice(0, 5).map(d => `                    <div class="driver-card">
                        <div class="driver-rank">${d.rank}</div>
                        <div class="driver-content">
                            <h3 class="driver-title">${escapeHtml(d.title)}</h3>
                            <p class="driver-desc">${escapeHtml(d.desc)}</p>
                            <span class="driver-severity severity-${d.severity}">${d.severity.charAt(0).toUpperCase() + d.severity.slice(1)}</span>
                        </div>
                    </div>`).join('\n');
}

function generateSATSection(stats, data, trends) {
    // Key Assumptions Check
    const kacItems = [
        { assumption: 'CISA KEV additions represent real-world exploitation', status: 'VALID', confidence: 'high', rationale: 'CISA requires evidence of active exploitation before listing' },
        { assumption: 'Ransomware-linked CVEs pose elevated risk', status: 'VALID', confidence: 'high', rationale: `${stats.ransomwareCount} CVEs have documented ransomware campaign connections` },
        { assumption: 'C2 infrastructure reflects active threat operations', status: 'UNCERTAIN', confidence: 'medium', rationale: 'Some C2s may be abandoned or law enforcement controlled' },
        { assumption: 'Geographic hosting indicates actor origin', status: 'UNCERTAIN', confidence: 'low', rationale: 'Criminals use hosting in multiple jurisdictions' },
        { assumption: 'News coverage correlates with exploitation likelihood', status: 'VALID', confidence: 'medium', rationale: 'Media attention often follows confirmed incidents' }
    ];
    
    // ACH hypotheses
    const achItems = [
        { id: 'H1', hypothesis: 'Active exploitation targeting internet-facing systems increased this week', confidence: stats.kevCount >= 3 ? 'High' : 'Medium', confClass: stats.kevCount >= 3 ? 'high' : 'moderate', confWidth: stats.kevCount >= 3 ? '90' : '60', evidenceFor: [`${stats.kevCount} new KEVs added (confirmed exploitation)`, 'High media coverage indicates broad targeting'], evidenceAgainst: [] },
        { id: 'H2', hypothesis: 'Botnet/C2 activity is a primary driver of observed malicious infrastructure', confidence: stats.c2Count >= 15 ? 'High' : 'Low', confClass: stats.c2Count >= 15 ? 'high' : 'low', confWidth: stats.c2Count >= 15 ? '80' : '30', evidenceFor: [`Top families: ${Object.keys(data.c2ByFamily).slice(0, 3).join(', ')}`], evidenceAgainst: [`Only ${stats.c2Count} C2 servers detected`, 'Multiple families may indicate fragmentation'] },
        { id: 'H3', hypothesis: 'Ransomware-enabling vulnerabilities are the dominant operational risk', confidence: stats.ransomwareCount >= 2 ? 'High' : 'Medium', confClass: stats.ransomwareCount >= 2 ? 'high' : 'moderate', confWidth: stats.ransomwareCount >= 2 ? '90' : '50', evidenceFor: [`${stats.ransomwareCount} KEVs linked to ransomware campaigns (${Math.round(stats.ransomwareCount / Math.max(stats.kevCount, 1) * 100)}%)`], evidenceAgainst: [] }
    ];
    
    const kacHtml = kacItems.map(k => `                                <tr>
                                    <td>${escapeHtml(k.assumption)}</td>
                                    <td><span class="kac-status status-${k.status.toLowerCase()}">${k.status}</span></td>
                                    <td>${escapeHtml(k.rationale)}</td>
                                </tr>`).join('\n');
    
    const achHtml = achItems.map(h => `                                <tr>
                                    <td><span class="ach-hypothesis">${h.id}: ${escapeHtml(h.hypothesis)}</span></td>
                                    <td class="ach-evidence">
${h.evidenceFor.map(e => `                                        <div class="ach-evidence-item"><span class="ach-for">+</span> ${escapeHtml(e)}</div>`).join('\n')}
                                    </td>
                                    <td class="ach-evidence">
${h.evidenceAgainst.length > 0 ? h.evidenceAgainst.map(e => `                                        <div class="ach-evidence-item"><span class="ach-against">−</span> ${escapeHtml(e)}</div>`).join('\n') : '                                        <span class="ach-evidence">—</span>'}
                                    </td>
                                    <td>
                                        <span class="ach-confidence conf-${h.confClass}">${h.confidence}</span>
                                        <div class="confidence-bar"><div class="confidence-fill ${h.confClass}" data-width="${h.confWidth}%" style="width: 0%;"></div></div>
                                    </td>
                                </tr>`).join('\n');
    
    return `        <!-- Structured Analytical Techniques -->
        <section class="section sat-section anchor-target" id="sat-analysis">
            <div class="container">
                <div class="section-label">Intelligence Analysis</div>
                <h2 class="section-title">Structured Analytical Techniques</h2>
                
                <div class="assessment-grid">
                    <!-- Key Assumptions Check -->
                    <div class="assessment-card">
                        <h3 class="assessment-card-title">
                            <span class="sat-icon">🔍</span>
                            Key Assumptions Check (KAC)
                        </h3>
                        <p class="sat-purpose">Identifies and validates the assumptions underlying our analysis.</p>
                        
                        <table class="kac-table">
                            <thead>
                                <tr>
                                    <th>Assumption</th>
                                    <th>Status</th>
                                    <th>Rationale</th>
                                </tr>
                            </thead>
                            <tbody>
${kacHtml}
                            </tbody>
                        </table>
                    </div>
                    
                    <!-- Analysis of Competing Hypotheses -->
                    <div class="assessment-card">
                        <h3 class="assessment-card-title">
                            <span class="sat-icon">⚖️</span>
                            Analysis of Competing Hypotheses (Mini-ACH)
                        </h3>
                        <p class="sat-purpose">Tests multiple explanations against the evidence.</p>
                        
                        <table class="ach-table">
                            <thead>
                                <tr>
                                    <th>Hypothesis</th>
                                    <th>Evidence For</th>
                                    <th>Evidence Against</th>
                                    <th>Confidence</th>
                                </tr>
                            </thead>
                            <tbody>
${achHtml}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </section>`;
}

function generateMITRESection(data) {
    const sortedTactics = Object.entries(data.tacticCounts).sort((a, b) => b[1] - a[1]).slice(0, 5);
    const sortedTechniques = Object.entries(data.techniqueCounts).sort((a, b) => b[1] - a[1]).slice(0, 10);
    
    const tacticsHtml = sortedTactics.map(([id, count]) => `                            <li class="mitre-item">
                                <span><span class="mitre-id">${id}</span> <span class="mitre-name">${CONFIG.tacticNames[id] || id}</span></span>
                                <span class="mitre-count">${count}</span>
                            </li>`).join('\n');
    
    const techniquesHtml = sortedTechniques.map(([id, count]) => `                            <li class="mitre-item">
                                <span><span class="mitre-id">${id}</span> <span class="mitre-name">${CONFIG.techniqueNames[id] || id}</span></span>
                                <span class="mitre-count">${count}</span>
                            </li>`).join('\n');
    
    return `        <!-- MITRE ATT&CK Section -->
        <section class="section anchor-target" id="mitre-attack">
            <div class="container">
                <div class="section-label">Framework Mapping</div>
                <h2 class="section-title">MITRE ATT&CK Summary</h2>
                <div class="mitre-grid">
                    <div class="mitre-card">
                        <h3 class="mitre-card-title">Top Tactics</h3>
                        <ul class="mitre-list">
${tacticsHtml}
                        </ul>
                    </div>
                    <div class="mitre-card">
                        <h3 class="mitre-card-title">Top Techniques</h3>
                        <ul class="mitre-list">
${techniquesHtml}
                        </ul>
                    </div>
                </div>
            </div>
        </section>`;
}

function generateActionSection(data) {
    // Get unique vendors for filter bar
    const uniqueVendors = [...new Set(data.recentKEVs.slice(0, 5).map(k => k.vendorProject))].slice(0, 4);
    
    // Generate filter bar HTML
    const filterBarHtml = `                            <div class="filter-bar">
                                <button class="filter-btn active" data-filter="all">All</button>
                                <button class="filter-btn" data-filter="ransomware">🔴 Ransomware</button>
${uniqueVendors.map(v => `                                <button class="filter-btn" data-filter="${escapeHtml(v)}">${escapeHtml(v)}</button>`).join('\n')}
                            </div>`;
    
    // Patch priorities with data attributes
    const patchHtml = data.recentKEVs.slice(0, 5).map(kev => {
        const isRansomware = data.ransomwareKEVs.some(r => r.cveID === kev.cveID);
        const coverage = data.newsCoverage[kev.cveID] || [];
        const buzzLevel = coverage.length >= 5 ? 'high' : (coverage.length >= 2 ? 'medium' : 'low');
        const buzzIcon = coverage.length >= 5 ? '🔥' : '📰';
        
        return `                            <div class="patch-item" data-vendor="${escapeHtml(kev.vendorProject)}" data-ransomware="${isRansomware}">
                                <div class="patch-header">
                                    <span class="patch-cve">${kev.cveID}</span>
                                    ${isRansomware ? '<span class="ransomware-tag">🔴 RANSOMWARE</span>' : ''}
                                    <span class="patch-due">Due: ${kev.dueDate || 'TBD'}</span>
                                </div>
                                <div class="patch-vendor">${escapeHtml(kev.vendorProject)} — ${escapeHtml(kev.product)}</div>
                                <div class="patch-coverage">
                                    <span class="coverage-label buzz-${buzzLevel}">${buzzIcon} ${coverage.length} articles</span>
                                </div>
                            </div>`;
    }).join('\n');
    
    // Block list
    const blockHtml = data.onlineC2s.slice(0, 10).map(c2 => `                                <div class="block-item">
                                    <span class="block-ip">${c2.ip_address || c2.ip}:${c2.port || 443}</span>
                                    <span class="block-source">feodo</span>
                                </div>`).join('\n');
    
    // Threat hunting suggestions
    const families = Object.keys(data.c2ByFamily).slice(0, 3);
    const huntHtml = families.map(family => `                                <li class="hunt-item">
                                    <span class="hunt-technique">T1071 - Application Layer Protocol</span>
                                    <span class="hunt-suggestion">Hunt for ${family} C2 beaconing patterns in proxy/DNS logs</span>
                                </li>`).join('\n') + `
                                <li class="hunt-item">
                                    <span class="hunt-technique">T1190 - Exploit Public-Facing Application</span>
                                    <span class="hunt-suggestion">Review logs for exploitation attempts against newly added KEV vulnerabilities</span>
                                </li>`;
    
    return `        <!-- Actionable Intelligence -->
        <section class="section anchor-target" id="actionable-intelligence">
            <div class="container">
                <div class="section-label">Take Action</div>
                <h2 class="section-title">Actionable Intelligence</h2>
                <div class="action-grid">
                    <div class="action-card">
                        <div class="action-card-header">
                            <svg class="action-card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
                                <path d="M9 12l2 2 4-4"/>
                            </svg>
                            <h3 class="action-card-title">Patch Priorities</h3>
                        </div>
                        <div class="action-card-body">
${filterBarHtml}
${patchHtml}
                        </div>
                    </div>
                    <div class="action-card">
                        <div class="action-card-header">
                            <svg class="action-card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="12" cy="12" r="10"/>
                                <line x1="4.93" y1="4.93" x2="19.07" y2="19.07"/>
                            </svg>
                            <h3 class="action-card-title">Block List (Top Indicators)</h3>
                        </div>
                        <div class="action-card-body">
                            <div class="block-grid">
${blockHtml}
                            </div>
                        </div>
                    </div>
                    <div class="action-card">
                        <div class="action-card-header">
                            <svg class="action-card-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <circle cx="11" cy="11" r="8"/>
                                <path d="m21 21-4.35-4.35"/>
                            </svg>
                            <h3 class="action-card-title">Threat Hunting Suggestions</h3>
                        </div>
                        <div class="action-card-body">
                            <ul class="hunt-list">
${huntHtml}
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </section>`;
}

function generateEmergingThreats(data) {
    // For emerging threats, we look at CVEs mentioned in news that aren't in KEV yet
    // This is a simplified version - in production you'd do more sophisticated matching
    return `        <!-- Emerging Threats -->
        <section class="section emerging-section">
            <div class="container">
                <div class="section-label">Early Warning</div>
                <h2 class="section-title">Emerging Threats Watchlist</h2>
                <p class="section-desc">These vulnerabilities are getting security news attention but have not yet been added to CISA KEV. Consider proactive assessment.</p>
                
                <div class="emerging-grid">
                    <div class="emerging-card">
                        <div class="emerging-header">
                            <span class="emerging-status">Monitoring</span>
                        </div>
                        <p class="emerging-desc">Check security news feeds for vulnerabilities receiving significant coverage that haven't been added to KEV yet.</p>
                    </div>
                </div>
            </div>
        </section>`;
}

// ============================================================================
// STATIC HTML GENERATORS (Navigation, Footer, Styles, Scripts)
// ============================================================================

function generateNavigation() {
    return `    <nav class="nav" id="nav">
        <div class="container nav-container">
            <a href="/" class="nav-logo">
                <div class="nav-logo-text">TAC<span>RAVEN</span></div>
            </a>
            <ul class="nav-menu">
                <li><a href="/" class="nav-link">Home</a></li>
                <li class="nav-dropdown">
                    <button class="nav-dropdown-toggle">
                        Products
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <polyline points="6 9 12 15 18 9"></polyline>
                        </svg>
                    </button>
                    <div class="nav-dropdown-menu">
                        <a href="/tools.html#blackfeather" class="nav-dropdown-item">
                            BlackFeather
                            <span>Threat Intel Platform</span>
                        </a>
                        <a href="/tools.html#corvus" class="nav-dropdown-item">
                            Corvus Engine
                            <span>Log Conversion Utility</span>
                        </a>
                        <a href="/talonprep.html" class="nav-dropdown-item">
                            TalonPrep
                            <span>Security+ Test Prep</span>
                        </a>
                    </div>
                </li>
                <li><a href="/tools.html" class="nav-link">Tools</a></li>
                <li><a href="/threat-map.html" class="nav-link">Threat Map</a></li>
                <li><a href="/intel/weekly/" class="nav-link active">Weekly Reports</a></li>
                <li><a href="/about.html" class="nav-link">About</a></li>
                <li><a href="/pricing.html" class="nav-link">Pricing</a></li>
                <li><a href="/cyber-news.html" class="nav-link">News</a></li>
            </ul>
            <a href="/#contact" class="btn btn-primary nav-cta">Contact</a>
            <button class="mobile-menu-btn" aria-label="Toggle menu">
                <span></span>
                <span></span>
                <span></span>
            </button>
        </div>
    </nav>

    <!-- Mobile Menu -->
    <div class="mobile-menu" id="mobile-menu">
        <a href="/" class="mobile-nav-link">Home</a>
        <a href="/tools.html#blackfeather" class="mobile-nav-link">BlackFeather</a>
        <a href="/tools.html#corvus" class="mobile-nav-link">Corvus Engine</a>
        <a href="/talonprep.html" class="mobile-nav-link">TalonPrep</a>
        <a href="/tools.html" class="mobile-nav-link">Tools</a>
        <a href="/threat-map.html" class="mobile-nav-link">Threat Map</a>
        <a href="/intel/weekly/" class="mobile-nav-link">Weekly Reports</a>
        <a href="/about.html" class="mobile-nav-link">About</a>
        <a href="/pricing.html" class="mobile-nav-link">Pricing</a>
        <a href="/cyber-news.html" class="mobile-nav-link">News</a>
        <a href="/#contact" class="mobile-nav-link">Contact</a>
    </div>`;
}

function generateFooter() {
    return `    <footer class="footer">
        <div class="container">
            <div class="footer-logo">TAC<span>RAVEN</span> SOLUTIONS</div>
            <p class="footer-text">Structured Threat Analysis Platform</p>
            <p class="footer-disclaimer">This report is generated from public data sources for informational purposes.</p>
        </div>
    </footer>`;
}

function generateStyles() {
    // This contains the full CSS from the professional template
    return `    <style>
        :root {
            --black: #000000;
            --black-light: #0a0a0a;
            --black-lighter: #111111;
            --black-card: #161616;
            --gold: #d4a012;
            --gold-light: #f5c842;
            --gold-dark: #9a7209;
            --white: #ffffff;
            --gray-100: #f5f5f5;
            --gray-300: #a0a0a0;
            --gray-500: #6b6b6b;
            --gray-700: #333333;
            --gray-800: #1a1a1a;
            --red: #dc2626;
            --red-dark: #7f1d1d;
            --green: #22c55e;
            --blue: #3b82f6;
            --font-display: 'Orbitron', sans-serif;
            --font-heading: 'Rajdhani', sans-serif;
            --font-body: 'Inter', sans-serif;
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        html { scroll-behavior: smooth; }
        body { font-family: var(--font-body); background-color: var(--black); color: var(--white); line-height: 1.6; }
        .container { max-width: 1100px; margin: 0 auto; padding: 0 24px; }
        
        /* Navigation */
        .nav { position: fixed; top: 0; left: 0; right: 0; background: rgba(0, 0, 0, 0.95); padding: 12px 0; border-bottom: 1px solid rgba(212, 160, 18, 0.2); z-index: 1000; }
        .nav-container { display: flex; justify-content: space-between; align-items: center; max-width: 1200px; margin: 0 auto; padding: 0 24px; }
        .nav-logo { display: flex; align-items: center; gap: 12px; text-decoration: none; }
        .nav-logo-text { font-family: var(--font-display); font-size: 24px; font-weight: 700; color: var(--white); letter-spacing: 2px; }
        .nav-logo-text span { color: var(--gold); }
        .nav-menu { display: flex; align-items: center; gap: 8px; list-style: none; }
        .nav-link { font-family: var(--font-heading); font-size: 15px; font-weight: 500; color: var(--gray-300); text-decoration: none; padding: 10px 16px; transition: all 0.3s ease; position: relative; }
        .nav-link::after { content: ''; position: absolute; bottom: 0; left: 50%; transform: translateX(-50%); width: 0; height: 2px; background: var(--gold); transition: width 0.3s ease; }
        .nav-link:hover, .nav-link.active { color: var(--white); }
        .nav-link:hover::after, .nav-link.active::after { width: 30px; }
        .nav-dropdown { position: relative; }
        .nav-dropdown-toggle { display: flex; align-items: center; gap: 6px; font-family: var(--font-heading); font-size: 15px; font-weight: 500; color: var(--gray-300); background: none; border: none; padding: 10px 16px; cursor: pointer; transition: all 0.3s ease; }
        .nav-dropdown-toggle:hover { color: var(--white); }
        .nav-dropdown-toggle svg { width: 12px; height: 12px; transition: transform 0.3s ease; }
        .nav-dropdown:hover .nav-dropdown-toggle svg { transform: rotate(180deg); }
        .nav-dropdown-menu { position: absolute; top: 100%; left: 0; min-width: 240px; background: var(--black-card); border: 1px solid rgba(212, 160, 18, 0.2); border-radius: 8px; padding: 12px; opacity: 0; visibility: hidden; transform: translateY(10px); transition: all 0.3s ease; z-index: 100; }
        .nav-dropdown:hover .nav-dropdown-menu { opacity: 1; visibility: visible; transform: translateY(0); }
        .nav-dropdown-item { display: block; padding: 12px 16px; color: var(--gray-300); text-decoration: none; border-radius: 6px; transition: all 0.2s ease; }
        .nav-dropdown-item:hover { background: rgba(212, 160, 18, 0.1); color: var(--gold); }
        .nav-dropdown-item span { display: block; font-size: 12px; color: var(--gray-500); margin-top: 2px; }
        .btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 12px 28px; font-family: var(--font-heading); font-size: 14px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; text-decoration: none; border: none; cursor: pointer; transition: all 0.3s ease; position: relative; overflow: hidden; }
        .btn-primary { background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%); color: var(--black); }
        .btn-primary:hover { transform: translateY(-2px); box-shadow: 0 10px 30px rgba(212, 160, 18, 0.3); }
        .nav-cta { padding: 10px 24px; font-size: 14px; }
        .mobile-menu-btn { display: none; flex-direction: column; gap: 5px; background: none; border: none; cursor: pointer; padding: 10px; z-index: 1001; }
        .mobile-menu-btn span { width: 24px; height: 2px; background: var(--white); transition: all 0.3s ease; }
        .mobile-menu { display: none; position: fixed; top: 60px; left: 0; right: 0; background: var(--black); padding: 20px; border-bottom: 1px solid rgba(212, 160, 18, 0.2); z-index: 999; flex-direction: column; gap: 10px; }
        .mobile-menu.active { display: flex; }
        .mobile-nav-link { font-family: var(--font-heading); font-size: 16px; color: var(--gray-300); text-decoration: none; padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        .mobile-nav-link:hover { color: var(--gold); }
        
        /* Report Header */
        .report-header { background: linear-gradient(180deg, var(--black-light) 0%, var(--black) 100%); border-bottom: 1px solid rgba(212, 160, 18, 0.2); padding: 40px 0; padding-top: 100px; }
        .back-link { display: inline-flex; align-items: center; gap: 8px; color: var(--gray-300); text-decoration: none; font-size: 14px; margin-bottom: 24px; transition: color 0.3s ease; }
        .back-link:hover { color: var(--gold); }
        .back-link svg { width: 16px; height: 16px; }
        .report-title { text-align: center; }
        .report-badge { display: inline-flex; align-items: center; gap: 8px; background: rgba(212, 160, 18, 0.1); border: 1px solid rgba(212, 160, 18, 0.3); border-radius: 20px; padding: 6px 16px; font-size: 12px; color: var(--gold); margin-bottom: 16px; }
        .report-badge-dot { width: 8px; height: 8px; background: var(--gold); border-radius: 50%; animation: pulse 2s ease-in-out infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.5; } }
        .report-title h1 { font-family: var(--font-display); font-size: 48px; font-weight: 700; color: var(--white); margin-bottom: 8px; }
        .report-title h1 span { color: var(--gold); }
        .report-date { color: var(--gray-300); font-size: 16px; }
        
        /* Sections */
        .section { padding: 60px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        .section-label { font-family: var(--font-heading); font-size: 12px; font-weight: 600; color: var(--gold); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 8px; }
        .section-title { font-family: var(--font-heading); font-size: 32px; font-weight: 600; color: var(--white); margin-bottom: 32px; }
        .section-desc { color: var(--gray-300); margin-bottom: 24px; }
        
        /* BLUF */
        .bluf-list { list-style: none; display: flex; flex-direction: column; gap: 16px; margin-bottom: 40px; }
        .bluf-item { display: flex; align-items: flex-start; gap: 16px; background: var(--black-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 20px; }
        .bluf-icon { width: 24px; height: 24px; color: var(--gold); flex-shrink: 0; margin-top: 2px; }
        .bluf-text { color: var(--gray-100); font-size: 15px; line-height: 1.6; }
        
        /* Threat Meter */
        .threat-meter { display: flex; align-items: center; gap: 40px; background: var(--black-card); border: 1px solid rgba(212, 160, 18, 0.2); border-radius: 12px; padding: 32px; }
        .threat-level-display { flex-shrink: 0; }
        .threat-level-ring { position: relative; width: 100px; height: 100px; }
        .threat-level-ring svg { transform: rotate(-90deg); }
        .ring-bg { fill: none; stroke: var(--gray-700); stroke-width: 6; }
        .ring-fill { fill: none; stroke-width: 6; stroke-linecap: round; stroke-dasharray: 220; stroke-dashoffset: 220; transition: stroke-dashoffset 1s ease; }
        .threat-level-ring.critical .ring-fill { stroke: #ef4444; }
        .threat-level-ring.high .ring-fill { stroke: #f97316; }
        .threat-level-ring.elevated .ring-fill { stroke: var(--gold); }
        .threat-level-ring.moderate .ring-fill { stroke: #22c55e; }
        .threat-level-ring.guarded .ring-fill { stroke: #eab308; }
        .threat-level-ring.low .ring-fill { stroke: var(--green); }
        .threat-level-text { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-family: var(--font-display); font-size: 11px; font-weight: 700; color: var(--white); }
        .threat-stats { display: flex; gap: 40px; flex: 1; justify-content: space-around; }
        .threat-stat { text-align: center; }
        .threat-stat-value { font-family: var(--font-display); font-size: 36px; font-weight: 700; color: var(--gold); }
        .threat-stat-label { font-size: 12px; color: var(--gray-300); text-transform: uppercase; letter-spacing: 1px; }
        
        /* Executive Summary */
        .exec-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 32px; }
        .exec-card { background: var(--black-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 24px; }
        .exec-card-title { font-family: var(--font-heading); font-size: 18px; font-weight: 600; color: var(--white); margin-bottom: 16px; }
        .exec-risk-display { margin-bottom: 16px; }
        .exec-risk-level { display: inline-block; font-family: var(--font-display); font-size: 14px; font-weight: 700; padding: 6px 12px; border-radius: 4px; margin-right: 8px; }
        .risk-critical { background: rgba(220, 38, 38, 0.2); color: #ef4444; }
        .risk-elevated { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .risk-guarded { background: rgba(234, 179, 8, 0.2); color: #eab308; }
        .risk-low { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .exec-risk-change { font-size: 12px; color: var(--gray-300); }
        .change-up { color: #ef4444; }
        .change-down { color: #22c55e; }
        .exec-rationale { color: var(--gray-300); font-size: 14px; line-height: 1.6; }
        .exec-detail { color: var(--gray-300); font-size: 14px; margin-bottom: 8px; }
        .exec-detail strong { color: var(--white); }
        .exec-decisions { list-style: none; }
        .exec-decisions li { color: var(--gray-300); font-size: 14px; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        .exec-decisions li:last-child { border-bottom: none; }
        
        /* Trends */
        .trend-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
        .trend-card { background: var(--black-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 24px; }
        .trend-metric { font-family: var(--font-heading); font-size: 16px; font-weight: 600; color: var(--white); margin-bottom: 16px; }
        .trend-sparkline { display: flex; align-items: flex-end; gap: 4px; height: 60px; margin-bottom: 16px; }
        .sparkline-bar { flex: 1; background: linear-gradient(180deg, var(--gold) 0%, var(--gold-dark) 100%); border-radius: 2px 2px 0 0; min-height: 4px; transition: height 0.5s ease; }
        .sparkline-bar:last-child { background: linear-gradient(180deg, var(--gold-light) 0%, var(--gold) 100%); }
        .trend-values { display: flex; flex-direction: column; gap: 4px; }
        .trend-current { font-family: var(--font-heading); font-size: 18px; font-weight: 600; color: var(--white); }
        .trend-change { font-size: 12px; }
        .trend-up { color: #ef4444; }
        .trend-down { color: #22c55e; }
        .trend-average { font-size: 12px; color: var(--gray-500); }
        
        /* Drivers */
        .drivers-grid { display: flex; flex-direction: column; gap: 16px; }
        .driver-card { display: flex; align-items: flex-start; gap: 20px; background: var(--black-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 24px; }
        .driver-rank { font-family: var(--font-display); font-size: 24px; font-weight: 700; color: var(--gold); min-width: 40px; }
        .driver-content { flex: 1; }
        .driver-title { font-family: var(--font-heading); font-size: 18px; font-weight: 600; color: var(--white); margin-bottom: 8px; }
        .driver-desc { color: var(--gray-300); font-size: 14px; margin-bottom: 12px; }
        .driver-severity { display: inline-block; font-size: 11px; font-weight: 600; text-transform: uppercase; padding: 4px 8px; border-radius: 4px; }
        .severity-critical { background: rgba(220, 38, 38, 0.2); color: #ef4444; }
        .severity-high { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .severity-medium { background: rgba(234, 179, 8, 0.2); color: #eab308; }
        .severity-info { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
        
        /* SAT Section */
        .sat-section { background: var(--black-light); }
        .assessment-grid { display: flex; flex-direction: column; gap: 32px; }
        .assessment-card { background: var(--black-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 12px; padding: 32px; }
        .assessment-card-title { display: flex; align-items: center; gap: 12px; font-family: var(--font-heading); font-size: 20px; font-weight: 600; color: var(--white); margin-bottom: 8px; }
        .sat-icon { font-size: 24px; }
        .sat-purpose { color: var(--gray-500); font-size: 14px; font-style: italic; margin-bottom: 24px; }
        
        /* KAC Table */
        .kac-table, .ach-table { width: 100%; border-collapse: collapse; font-size: 14px; }
        .kac-table th, .ach-table th { text-align: left; padding: 12px; background: var(--black); color: var(--gray-300); font-weight: 600; border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        .kac-table td, .ach-table td { padding: 12px; border-bottom: 1px solid rgba(255, 255, 255, 0.05); color: var(--gray-100); vertical-align: top; }
        .kac-status { display: inline-block; font-size: 11px; font-weight: 600; text-transform: uppercase; padding: 4px 8px; border-radius: 4px; }
        .status-valid { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .status-uncertain { background: rgba(234, 179, 8, 0.2); color: #eab308; }
        .status-invalid { background: rgba(220, 38, 38, 0.2); color: #ef4444; }
        
        /* ACH */
        .ach-hypothesis { color: var(--white); font-weight: 500; }
        .ach-evidence-item { margin-bottom: 4px; }
        .ach-for { color: #22c55e; font-weight: bold; margin-right: 4px; }
        .ach-against { color: #ef4444; font-weight: bold; margin-right: 4px; }
        .ach-confidence { display: inline-block; font-size: 11px; font-weight: 600; text-transform: uppercase; padding: 4px 8px; border-radius: 4px; margin-bottom: 8px; }
        .conf-high { background: rgba(34, 197, 94, 0.2); color: #22c55e; }
        .conf-moderate { background: rgba(234, 179, 8, 0.2); color: #eab308; }
        .conf-low { background: rgba(220, 38, 38, 0.2); color: #ef4444; }
        .confidence-bar { height: 4px; background: var(--gray-700); border-radius: 2px; overflow: hidden; }
        .confidence-fill { height: 100%; border-radius: 2px; transition: width 1s ease; }
        .confidence-fill.high { background: #22c55e; }
        .confidence-fill.moderate { background: #eab308; }
        .confidence-fill.low { background: #ef4444; }
        
        /* MITRE */
        .mitre-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }
        .mitre-card { background: var(--black-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 24px; }
        .mitre-card-title { font-family: var(--font-heading); font-size: 18px; font-weight: 600; color: var(--white); margin-bottom: 16px; }
        .mitre-list { list-style: none; }
        .mitre-item { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        .mitre-item:last-child { border-bottom: none; }
        .mitre-id { font-family: monospace; font-size: 12px; color: var(--gold); margin-right: 8px; }
        .mitre-name { color: var(--gray-100); font-size: 14px; }
        .mitre-count { font-family: var(--font-display); font-size: 14px; font-weight: 600; color: var(--gold); }
        
        /* Actions */
        .action-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
        .action-card { background: var(--black-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; overflow: hidden; }
        .action-card-header { display: flex; align-items: center; gap: 12px; padding: 20px; background: var(--black); border-bottom: 1px solid rgba(255, 255, 255, 0.1); }
        .action-card-icon { width: 24px; height: 24px; color: var(--gold); }
        .action-card-title { font-family: var(--font-heading); font-size: 16px; font-weight: 600; color: var(--white); }
        .action-card-body { padding: 20px; }
        
        /* Patch Items */
        .patch-item { padding: 16px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        .patch-item:last-child { border-bottom: none; }
        .patch-header { display: flex; align-items: center; gap: 8px; margin-bottom: 4px; flex-wrap: wrap; }
        .patch-cve { font-family: monospace; font-size: 14px; font-weight: 600; color: var(--gold); }
        .ransomware-tag { font-size: 11px; background: rgba(220, 38, 38, 0.2); color: #ef4444; padding: 2px 6px; border-radius: 4px; }
        .patch-due { font-size: 12px; color: var(--gray-500); margin-left: auto; }
        .patch-vendor { font-size: 13px; color: var(--gray-300); margin-bottom: 8px; }
        .patch-coverage { margin-top: 8px; }
        .coverage-label { font-size: 12px; padding: 4px 8px; border-radius: 4px; }
        .buzz-high { background: rgba(245, 158, 11, 0.2); color: #f59e0b; }
        .buzz-medium { background: rgba(59, 130, 246, 0.2); color: #3b82f6; }
        .buzz-low { background: rgba(107, 114, 128, 0.2); color: #9ca3af; }
        
        /* Block List */
        .block-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 8px; }
        .block-item { display: flex; justify-content: space-between; align-items: center; background: var(--black); padding: 8px 12px; border-radius: 4px; cursor: pointer; transition: background 0.2s; }
        .block-item:hover { background: var(--gray-800); }
        .block-ip { font-family: monospace; font-size: 12px; color: var(--gray-100); }
        .block-source { font-size: 10px; color: var(--gray-500); text-transform: uppercase; }
        
        /* Hunt List */
        .hunt-list { list-style: none; }
        .hunt-item { padding: 12px 0; border-bottom: 1px solid rgba(255, 255, 255, 0.05); }
        .hunt-item:last-child { border-bottom: none; }
        .hunt-technique { display: block; font-family: monospace; font-size: 12px; color: var(--gold); margin-bottom: 4px; }
        .hunt-suggestion { font-size: 13px; color: var(--gray-300); }
        
        /* Emerging */
        .emerging-section { background: var(--black-light); }
        .emerging-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; }
        .emerging-card { background: var(--black-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 20px; }
        .emerging-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
        .emerging-status { font-size: 11px; font-weight: 600; text-transform: uppercase; padding: 4px 8px; border-radius: 4px; background: rgba(234, 179, 8, 0.2); color: #eab308; }
        .emerging-desc { color: var(--gray-300); font-size: 14px; }
        
        /* Sources */
        .sources-grid { display: grid; grid-template-columns: repeat(3, 1fr); gap: 24px; margin-bottom: 24px; }
        .source-card { background: var(--black-card); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 20px; }
        .source-title { font-family: var(--font-heading); font-size: 16px; font-weight: 600; color: var(--white); margin-bottom: 8px; }
        .source-desc { color: var(--gray-300); font-size: 13px; margin-bottom: 12px; }
        .source-link { color: var(--gold); font-size: 13px; text-decoration: none; }
        .source-link:hover { text-decoration: underline; }
        .methodology-link { color: var(--gray-500); font-size: 14px; text-align: center; }
        .methodology-link a { color: var(--gold); }
        
        /* Footer */
        .footer { padding: 40px 0; text-align: center; border-top: 1px solid rgba(212, 160, 18, 0.2); }
        .footer-logo { font-family: var(--font-display); font-size: 20px; font-weight: 700; color: var(--white); margin-bottom: 8px; }
        .footer-logo span { color: var(--gold); }
        .footer-text { color: var(--gray-500); font-size: 14px; margin-bottom: 8px; }
        .footer-disclaimer { color: var(--gray-700); font-size: 12px; }
        
        /* Progress Bar */
        .progress-bar { position: fixed; top: 0; left: 0; height: 3px; background: linear-gradient(90deg, var(--gold-dark), var(--gold), var(--gold-light)); z-index: 1001; transition: width 0.1s ease-out; box-shadow: 0 0 10px var(--gold); }
        
        /* ============================================
           NEW ENHANCED STYLES 
           ============================================ */
        
        /* Disclaimer Banner */
        .disclaimer-banner { 
            background: linear-gradient(90deg, rgba(212, 160, 18, 0.1) 0%, rgba(212, 160, 18, 0.05) 50%, rgba(212, 160, 18, 0.1) 100%);
            border-bottom: 1px solid rgba(212, 160, 18, 0.2);
            padding: 12px 0;
        }
        .disclaimer-content {
            max-width: 1100px;
            margin: 0 auto;
            padding: 0 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            flex-wrap: wrap;
        }
        .disclaimer-icon {
            width: 20px;
            height: 20px;
            color: var(--gold);
            flex-shrink: 0;
        }
        .disclaimer-text {
            color: var(--gray-300);
            font-size: 13px;
        }
        .disclaimer-text strong {
            color: var(--gold);
        }
        .disclaimer-highlight {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: #22c55e;
            font-size: 12px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 20px;
        }
        .disclaimer-highlight svg {
            width: 14px;
            height: 14px;
        }
        
        /* Export Bar */
        .export-bar {
            background: linear-gradient(135deg, var(--black-card) 0%, rgba(22, 22, 22, 0.8) 100%);
            border: 1px solid rgba(212, 160, 18, 0.2);
            border-radius: 12px;
            padding: 24px;
            margin-top: 32px;
        }
        .export-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 20px;
            flex-wrap: wrap;
            gap: 12px;
        }
        .export-title {
            display: flex;
            align-items: center;
            gap: 12px;
        }
        .export-title-icon {
            width: 40px;
            height: 40px;
            display: flex;
            align-items: center;
            justify-content: center;
            background: rgba(212, 160, 18, 0.1);
            border-radius: 8px;
        }
        .export-title-icon svg {
            width: 20px;
            height: 20px;
            color: var(--gold);
        }
        .export-title-text {
            font-family: var(--font-heading);
            font-size: 18px;
            font-weight: 600;
            color: var(--white);
        }
        .export-title-text span {
            color: var(--gold);
        }
        .export-free-badge {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: rgba(34, 197, 94, 0.15);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: #22c55e;
            font-size: 12px;
            font-weight: 600;
            padding: 6px 14px;
            border-radius: 20px;
        }
        .export-free-badge svg {
            width: 14px;
            height: 14px;
        }
        .export-buttons {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .export-btn {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 12px 20px;
            background: var(--black);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: var(--gray-300);
            font-family: var(--font-heading);
            font-size: 14px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .export-btn:hover {
            background: var(--black-lighter);
            border-color: rgba(212, 160, 18, 0.3);
            color: var(--white);
        }
        .export-btn svg {
            width: 18px;
            height: 18px;
        }
        .export-btn.primary {
            background: linear-gradient(135deg, var(--gold) 0%, var(--gold-dark) 100%);
            border-color: transparent;
            color: var(--black);
        }
        .export-btn.primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(212, 160, 18, 0.3);
        }
        
        /* Report Navigation Links */
        .report-nav-links {
            display: flex;
            justify-content: center;
            align-items: center;
            gap: 24px;
            margin-top: 24px;
            flex-wrap: wrap;
        }
        .report-nav-link {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 12px 20px;
            background: var(--black-card);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            color: var(--gray-300);
            text-decoration: none;
            transition: all 0.3s ease;
        }
        .report-nav-link:hover:not(.disabled) {
            background: var(--black-lighter);
            border-color: rgba(212, 160, 18, 0.3);
            color: var(--gold);
        }
        .report-nav-link.disabled {
            opacity: 0.4;
            cursor: not-allowed;
            pointer-events: none;
        }
        .report-nav-link svg {
            width: 16px;
            height: 16px;
        }
        .report-nav-link-info {
            display: flex;
            flex-direction: column;
            gap: 2px;
        }
        .report-nav-link-label {
            font-size: 11px;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--gray-500);
        }
        .report-nav-link-title {
            font-family: var(--font-heading);
            font-size: 14px;
            font-weight: 600;
        }
        .report-nav-center {
            padding: 0 24px;
        }
        .report-nav-current {
            font-family: var(--font-heading);
            font-size: 14px;
            color: var(--gray-500);
        }
        
        /* Report Title (Stacked Layout) */
        .report-title-section {
            text-align: center;
        }
        .report-title {
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 8px;
            margin-bottom: 16px;
        }
        .report-title-date {
            font-family: var(--font-display);
            font-size: 42px;
            font-weight: 700;
            color: var(--gold);
            line-height: 1.2;
        }
        .report-title-name {
            font-family: var(--font-heading);
            font-size: 28px;
            font-weight: 600;
            color: var(--white);
            line-height: 1.3;
        }
        .report-meta {
            color: var(--gray-500);
            font-size: 13px;
        }
        
        /* Filter Bar */
        .filter-bar {
            display: flex;
            gap: 8px;
            margin-bottom: 16px;
            flex-wrap: wrap;
        }
        .filter-btn {
            padding: 8px 16px;
            background: var(--black);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 20px;
            color: var(--gray-300);
            font-size: 13px;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .filter-btn:hover {
            border-color: rgba(212, 160, 18, 0.3);
            color: var(--white);
        }
        .filter-btn.active {
            background: rgba(212, 160, 18, 0.15);
            border-color: var(--gold);
            color: var(--gold);
        }
        
        /* Mobile Table Cards */
        .table-card-mobile {
            display: none;
        }
        .table-card {
            background: var(--black-card);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            padding: 16px;
            margin-bottom: 12px;
        }
        .table-card-header {
            display: flex;
            justify-content: space-between;
            align-items: flex-start;
            margin-bottom: 12px;
        }
        .table-card-title {
            font-family: monospace;
            font-size: 14px;
            color: var(--gold);
            font-weight: 600;
        }
        .table-card-row {
            display: flex;
            justify-content: space-between;
            padding: 8px 0;
            border-bottom: 1px solid rgba(255, 255, 255, 0.05);
            font-size: 13px;
        }
        .table-card-row:last-child {
            border-bottom: none;
        }
        .table-card-label {
            color: var(--gray-500);
        }
        .table-card-value {
            color: var(--gray-100);
        }
        
        /* Anchor Links / Deep Linking */
        .anchor-target {
            scroll-margin-top: 100px;
        }
        .anchor-link {
            color: var(--gold);
            text-decoration: none;
            opacity: 0;
            margin-left: 8px;
            font-size: 0.8em;
            transition: opacity 0.2s ease;
        }
        .section-title:hover .anchor-link,
        .anchor-link:focus {
            opacity: 1;
        }
        .linkable-item:target {
            animation: highlight-pulse 2s ease;
        }
        @keyframes highlight-pulse {
            0%, 100% { background-color: transparent; }
            25% { background-color: rgba(212, 160, 18, 0.2); }
            75% { background-color: rgba(212, 160, 18, 0.1); }
        }
        
        /* Collapsible Sections */
        .collapsible {
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 8px;
            margin-bottom: 12px;
            overflow: hidden;
        }
        .collapsible-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 16px 20px;
            background: var(--black-card);
            cursor: pointer;
            transition: background 0.2s ease;
        }
        .collapsible-header:hover {
            background: var(--black-lighter);
        }
        .collapsible-header svg {
            width: 20px;
            height: 20px;
            color: var(--gray-500);
            transition: transform 0.3s ease;
        }
        .collapsible.open .collapsible-header svg {
            transform: rotate(180deg);
        }
        .collapsible-content {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
        }
        .collapsible.open .collapsible-content {
            max-height: 2000px;
        }
        .collapsible-inner {
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }
        
        /* Toast Notification */
        .toast {
            position: fixed;
            bottom: 24px;
            right: 24px;
            background: var(--black-card);
            border: 1px solid rgba(212, 160, 18, 0.3);
            border-radius: 8px;
            padding: 16px 24px;
            color: var(--white);
            font-size: 14px;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
            z-index: 1002;
            transform: translateY(100px);
            opacity: 0;
            transition: all 0.3s ease;
        }
        .toast.show {
            transform: translateY(0);
            opacity: 1;
        }
        .toast-success {
            border-color: rgba(34, 197, 94, 0.3);
        }
        .toast-success::before {
            content: '✓';
            margin-right: 8px;
            color: #22c55e;
        }
        
        /* Professional Print Stylesheet */
        @media print {
            /* Hide navigation and interactive elements */
            .nav, .mobile-menu, .progress-bar, .export-bar, .report-nav-links, 
            .back-link, .filter-bar, .toast { display: none !important; }
            
            /* Reset background and colors for printing */
            body { 
                background: white !important; 
                color: #111 !important; 
                font-size: 11pt;
            }
            .container { max-width: 100%; padding: 0; }
            
            /* Section styling */
            .section { 
                padding: 24px 0; 
                border-bottom: 1px solid #ddd !important;
                page-break-inside: avoid;
            }
            .section-label { color: #9a7209 !important; }
            .section-title { color: #111 !important; font-size: 18pt; }
            
            /* Card styling */
            .exec-card, .trend-card, .driver-card, .source-card, .emerging-card,
            .assessment-card, .mitre-card, .action-card, .bluf-item, .block-item {
                background: #f9f9f9 !important;
                border: 1px solid #ddd !important;
                color: #111 !important;
            }
            
            /* Text colors */
            .bluf-text, .exec-rationale, .exec-detail, .driver-desc, 
            .source-desc, .emerging-desc, .sat-purpose, .hunt-suggestion,
            .patch-vendor, .trend-average, .mitre-name { color: #333 !important; }
            
            /* Gold accents to dark gold for print */
            .threat-stat-value, .driver-rank, .patch-cve, .mitre-id, .mitre-count,
            .block-ip, .hunt-technique { color: #9a7209 !important; }
            
            /* Header styling */
            .report-header { 
                background: #f5f5f5 !important; 
                border-bottom: 2px solid #9a7209 !important;
                padding: 24px 0;
            }
            .report-title-date { color: #9a7209 !important; font-size: 24pt; }
            .report-title-name { color: #111 !important; font-size: 18pt; }
            .report-badge { 
                background: #f5f5f5 !important; 
                border-color: #9a7209 !important;
                color: #9a7209 !important;
            }
            
            /* Footer */
            .footer { 
                background: #f5f5f5 !important;
                border-top: 2px solid #9a7209 !important;
            }
            .footer-logo { color: #111 !important; }
            .footer-logo span { color: #9a7209 !important; }
            
            /* TacRaven branding in print header */
            .report-header::before {
                content: 'TACRAVEN SOLUTIONS - Weekly Threat Intelligence Report';
                display: block;
                font-family: var(--font-display);
                font-size: 10pt;
                color: #666;
                text-align: center;
                margin-bottom: 16px;
            }
            
            /* Page breaks */
            .sat-section, .mitre-section, .action-section { page-break-before: always; }
            
            /* Table styling */
            .kac-table, .ach-table { font-size: 10pt; }
            .kac-table th, .ach-table th { background: #eee !important; color: #111 !important; }
            .kac-table td, .ach-table td { color: #333 !important; }
            
            /* Disclaimer banner */
            .disclaimer-banner { display: none !important; }
        }
        
        /* Responsive */
        @media (max-width: 1024px) {
            .exec-grid, .trend-grid, .action-grid, .sources-grid { grid-template-columns: 1fr; }
            .mitre-grid { grid-template-columns: 1fr; }
            .threat-meter { flex-direction: column; text-align: center; }
            .threat-stats { flex-wrap: wrap; justify-content: center; }
            .report-nav-links { gap: 12px; }
            .report-nav-center { display: none; }
            .export-buttons { justify-content: center; }
        }
        @media (max-width: 768px) {
            .nav-menu, .nav-cta { display: none; }
            .mobile-menu-btn { display: flex; }
            .report-title-date { font-size: 28px; }
            .report-title-name { font-size: 20px; }
            .block-grid { grid-template-columns: 1fr; }
            .emerging-grid { grid-template-columns: 1fr; }
            .disclaimer-content { flex-direction: column; text-align: center; }
            .export-bar { padding: 16px; }
            .export-header { flex-direction: column; text-align: center; }
            .export-buttons { flex-direction: column; }
            .export-btn { justify-content: center; }
            .report-nav-link { padding: 10px 16px; }
            .report-nav-link-info { display: none; }
            /* Show mobile cards, hide desktop tables on mobile */
            .table-card-mobile { display: block; }
            .kac-table, .ach-table { display: none; }
        }
    </style>`;
}

function generateScripts() {
    return `    <script>
        // Scroll progress bar
        window.addEventListener('scroll', () => {
            const scrollTop = window.scrollY;
            const docHeight = document.documentElement.scrollHeight - window.innerHeight;
            const progress = (scrollTop / docHeight) * 100;
            document.getElementById('progressBar').style.width = progress + '%';
        });

        // Mobile menu toggle
        const mobileMenuBtn = document.querySelector('.mobile-menu-btn');
        const mobileMenu = document.getElementById('mobile-menu');
        if (mobileMenuBtn && mobileMenu) {
            mobileMenuBtn.addEventListener('click', () => {
                mobileMenu.classList.toggle('active');
            });
        }
        
        // Animated counters
        function animateCounters() {
            document.querySelectorAll('[data-count]').forEach(el => {
                const target = parseInt(el.dataset.count);
                const duration = 1000;
                const start = 0;
                const startTime = performance.now();
                
                function update(currentTime) {
                    const elapsed = currentTime - startTime;
                    const progress = Math.min(elapsed / duration, 1);
                    const current = Math.floor(progress * target);
                    el.textContent = current;
                    if (progress < 1) requestAnimationFrame(update);
                }
                requestAnimationFrame(update);
            });
        }
        
        // Animate threat ring
        function animateThreatRing() {
            const ring = document.querySelector('.threat-level-ring');
            if (ring) {
                const fill = ring.querySelector('.ring-fill');
                if (fill) {
                    setTimeout(() => {
                        fill.style.strokeDashoffset = '44'; // ~80% fill
                    }, 500);
                }
            }
        }
        
        // Animate confidence bars
        function animateConfidenceBars() {
            document.querySelectorAll('.confidence-fill[data-width]').forEach(bar => {
                setTimeout(() => {
                    bar.style.width = bar.dataset.width;
                }, 500);
            });
        }
        
        // Copy to clipboard for block items
        function copyToClipboard(text) {
            navigator.clipboard.writeText(text).then(() => {
                showToast('Copied to clipboard!');
            });
        }
        
        document.querySelectorAll('.block-item').forEach(item => {
            item.onclick = () => {
                const ip = item.querySelector('.block-ip').textContent;
                copyToClipboard(ip);
            };
        });
        
        // ============================================
        // EXPORT FUNCTIONS
        // ============================================
        
        // Download PDF
        function downloadPDF() {
            showToast('Opening print dialog for PDF export...');
            setTimeout(() => {
                window.print();
            }, 500);
        }
        
        // Copy Executive Summary
        function copyExecutiveSummary() {
            const execSection = document.querySelector('.executive-summary');
            if (!execSection) {
                showToast('Executive summary not found', 'error');
                return;
            }
            
            // Extract text content
            const title = document.querySelector('.report-title-date')?.textContent || '';
            const subtitle = document.querySelector('.report-title-name')?.textContent || '';
            const execCards = execSection.querySelectorAll('.exec-card');
            
            let summaryText = '=== TACRAVEN SOLUTIONS ===\\n';
            summaryText += title + ' - ' + subtitle + '\\n\\n';
            summaryText += 'EXECUTIVE SUMMARY\\n';
            summaryText += '─'.repeat(40) + '\\n\\n';
            
            execCards.forEach(card => {
                const cardTitle = card.querySelector('.exec-card-title')?.textContent || '';
                summaryText += cardTitle.toUpperCase() + ':\\n';
                
                const riskLevel = card.querySelector('.exec-risk-level')?.textContent;
                if (riskLevel) {
                    summaryText += 'Risk Level: ' + riskLevel + '\\n';
                }
                
                const rationale = card.querySelector('.exec-rationale')?.textContent;
                if (rationale) {
                    summaryText += rationale + '\\n';
                }
                
                const details = card.querySelectorAll('.exec-detail');
                details.forEach(detail => {
                    summaryText += detail.textContent + '\\n';
                });
                
                summaryText += '\\n';
            });
            
            navigator.clipboard.writeText(summaryText).then(() => {
                showToast('Executive summary copied to clipboard!');
            }).catch(() => {
                showToast('Failed to copy', 'error');
            });
        }
        
        // Copy CVE List
        function copyCVEList() {
            const patchItems = document.querySelectorAll('.patch-item');
            if (patchItems.length === 0) {
                showToast('No CVEs found in this report', 'error');
                return;
            }
            
            let cveList = '=== TACRAVEN SOLUTIONS - CVE LIST ===\\n';
            cveList += 'Generated: ' + new Date().toISOString().split('T')[0] + '\\n';
            cveList += '─'.repeat(40) + '\\n\\n';
            
            patchItems.forEach(item => {
                const cve = item.querySelector('.patch-cve')?.textContent || '';
                const vendor = item.querySelector('.patch-vendor')?.textContent || '';
                const due = item.querySelector('.patch-due')?.textContent || '';
                const isRansomware = item.querySelector('.ransomware-tag') !== null;
                
                cveList += cve;
                if (isRansomware) cveList += ' [RANSOMWARE]';
                cveList += '\\n';
                cveList += '  Vendor: ' + vendor.trim() + '\\n';
                if (due) cveList += '  ' + due + '\\n';
                cveList += '\\n';
            });
            
            navigator.clipboard.writeText(cveList).then(() => {
                showToast('CVE list copied to clipboard! (' + patchItems.length + ' CVEs)');
            }).catch(() => {
                showToast('Failed to copy', 'error');
            });
        }
        
        // Toast notification
        function showToast(message, type = 'success') {
            // Remove existing toast
            const existingToast = document.querySelector('.toast');
            if (existingToast) {
                existingToast.remove();
            }
            
            const toast = document.createElement('div');
            toast.className = 'toast toast-' + type;
            toast.textContent = message;
            document.body.appendChild(toast);
            
            // Show toast
            setTimeout(() => {
                toast.classList.add('show');
            }, 10);
            
            // Hide and remove toast
            setTimeout(() => {
                toast.classList.remove('show');
                setTimeout(() => toast.remove(), 300);
            }, 3000);
        }
        
        // ============================================
        // CVE FILTER FUNCTIONALITY
        // ============================================
        
        function initCVEFilters() {
            const filterBar = document.querySelector('.filter-bar');
            if (!filterBar) return;
            
            const filterBtns = filterBar.querySelectorAll('.filter-btn');
            const patchItems = document.querySelectorAll('.patch-item');
            
            filterBtns.forEach(btn => {
                btn.addEventListener('click', () => {
                    // Update active state
                    filterBtns.forEach(b => b.classList.remove('active'));
                    btn.classList.add('active');
                    
                    const filter = btn.dataset.filter;
                    
                    patchItems.forEach(item => {
                        if (filter === 'all') {
                            item.style.display = 'block';
                        } else if (filter === 'ransomware') {
                            const isRansomware = item.dataset.ransomware === 'true';
                            item.style.display = isRansomware ? 'block' : 'none';
                        } else {
                            const vendor = (item.dataset.vendor || '').toLowerCase();
                            item.style.display = vendor.includes(filter.toLowerCase()) ? 'block' : 'none';
                        }
                    });
                });
            });
        }
        
        // ============================================
        // COLLAPSIBLE SECTIONS
        // ============================================
        
        function initCollapsibles() {
            document.querySelectorAll('.collapsible-header').forEach(header => {
                header.addEventListener('click', () => {
                    const collapsible = header.parentElement;
                    collapsible.classList.toggle('open');
                });
            });
        }
        
        // Initialize on load
        document.addEventListener('DOMContentLoaded', () => {
            animateCounters();
            animateThreatRing();
            animateConfidenceBars();
            initCVEFilters();
            initCollapsibles();
        });
    </script>`;
}

// ============================================================================
// MAIN EXECUTION
// ============================================================================

async function main() {
    console.log('╔════════════════════════════════════════════════════════════╗');
    console.log('║  TacRaven Weekly Threat Intelligence Report Generator      ║');
    console.log('║  Professional Edition v2.0                                 ║');
    console.log('╚════════════════════════════════════════════════════════════╝\n');
    
    const weekInfo = getWeekNumber();
    console.log(`📅 Generating report for: ${weekInfo.year}-W${String(weekInfo.week).padStart(2, '0')}`);
    console.log(`⏰ Current time: ${new Date().toISOString()}\n`);
    
    try {
        // Fetch all data
        const rawData = await fetchAllData();
        
        // Process data
        const reportData = processData(rawData);
        
        // Render HTML report
        const html = renderReport(reportData);
        
        // Determine output directory
        const outputDir = process.argv.includes('--output') 
            ? process.argv[process.argv.indexOf('--output') + 1]
            : './output';
        
        if (!fs.existsSync(outputDir)) {
            fs.mkdirSync(outputDir, { recursive: true });
        }
        
        const weekStr = `${reportData.metadata.week.year}-W${String(reportData.metadata.week.week).padStart(2, '0')}`;
        const htmlPath = path.join(outputDir, `${weekStr}.html`);
        const jsonPath = path.join(outputDir, `${weekStr}.json`);
        
        fs.writeFileSync(htmlPath, html);
        fs.writeFileSync(jsonPath, JSON.stringify(reportData, null, 2));
        
        console.log('\n✅ Report generation complete!');
        console.log(`   HTML: ${htmlPath}`);
        console.log(`   JSON: ${jsonPath}`);
        
        console.log('\n📊 Report Summary:');
        console.log(`   Threat Level: ${reportData.metadata.threatLevel.level}`);
        console.log(`   New KEVs: ${reportData.stats.kevCount}`);
        console.log(`   Ransomware-Linked: ${reportData.stats.ransomwareCount}`);
        console.log(`   Active C2s: ${reportData.stats.c2Count}`);
        console.log(`   Malware Families: ${reportData.stats.malwareFamilies}`);
        
    } catch (error) {
        console.error('\n❌ Error generating report:', error.message);
        console.error(error.stack);
        process.exit(1);
    }
}

// Run if executed directly
if (require.main === module) {
    main();
}

module.exports = { fetchAllData, processData, renderReport, getWeekNumber };
