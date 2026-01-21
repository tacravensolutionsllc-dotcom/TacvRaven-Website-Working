#!/usr/bin/env node
/**
 * TacRaven Archive Index Updater
 * 
 * Automatically updates the archive index.html with all weekly reports
 * found in the intel/weekly directory.
 * 
 * Usage: node update-archive-index.js [--dir ./intel/weekly]
 */

const fs = require('fs');
const path = require('path');

// Get directory from args or use default
const args = process.argv.slice(2);
const dirIndex = args.indexOf('--dir');
const baseDir = dirIndex !== -1 ? args[dirIndex + 1] : './intel/weekly';

// Month names for display
const MONTH_NAMES = [
    'January', 'February', 'March', 'April', 'May', 'June',
    'July', 'August', 'September', 'October', 'November', 'December'
];

const MONTH_SHORT = [
    'JAN', 'FEB', 'MAR', 'APR', 'MAY', 'JUN',
    'JUL', 'AUG', 'SEP', 'OCT', 'NOV', 'DEC'
];

/**
 * Parse week string (YYYY-WXX) to get date info
 */
function parseWeekString(weekStr) {
    const match = weekStr.match(/(\d{4})-W(\d{2})/);
    if (!match) return null;
    
    const year = parseInt(match[1]);
    const week = parseInt(match[2]);
    
    // Calculate the Monday of the given ISO week
    const jan4 = new Date(year, 0, 4);
    const dayOfWeek = jan4.getDay() || 7;
    const firstMonday = new Date(jan4);
    firstMonday.setDate(jan4.getDate() - dayOfWeek + 1);
    
    const targetMonday = new Date(firstMonday);
    targetMonday.setDate(firstMonday.getDate() + (week - 1) * 7);
    
    return {
        year,
        week,
        date: targetMonday,
        monthName: MONTH_NAMES[targetMonday.getMonth()],
        monthShort: MONTH_SHORT[targetMonday.getMonth()],
        day: targetMonday.getDate()
    };
}

/**
 * Get stats from JSON file if available
 */
function getReportStats(jsonPath) {
    try {
        if (fs.existsSync(jsonPath)) {
            const data = JSON.parse(fs.readFileSync(jsonPath, 'utf-8'));
            return {
                kevCount: data.stats?.kevCount || 0,
                c2Count: data.stats?.c2Count || 0,
                ransomwareCount: data.stats?.ransomwareCount || 0
            };
        }
    } catch (e) {
        console.warn(`Could not read stats from ${jsonPath}: ${e.message}`);
    }
    return { kevCount: '?', c2Count: '?', ransomwareCount: '?' };
}

/**
 * Generate archive card HTML
 */
function generateArchiveCard(weekStr, info, stats) {
    const dateStr = `${info.monthName} ${info.day}, ${info.year}`;
    const weekId = `${info.monthShort} W${String(info.week).padStart(2, '0')}`;
    const title = `${info.monthName} ${info.year}, Week ${String(info.week).padStart(2, '0')} Threat Report`;
    const summary = `${stats.kevCount} KEV additions, ${stats.c2Count} C2 indicators`;
    
    return `                <a href="${weekStr}.html" class="archive-card">
                    <div class="archive-week">
                        <div class="archive-week-id">${weekId}</div>
                        <div class="archive-week-date">${dateStr}</div>
                    </div>
                    <div class="archive-content">
                        <h2 class="archive-title">${title}</h2>
                        <p class="archive-summary">${summary}</p>
                    </div>
                    <svg class="archive-arrow" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M5 12h14M12 5l7 7-7 7"/>
                    </svg>
                </a>`;
}

/**
 * Main function
 */
function main() {
    console.log('📋 Updating archive index...');
    console.log(`   Directory: ${baseDir}`);
    
    // Find all report HTML files (format: YYYY-WXX.html)
    const files = fs.readdirSync(baseDir)
        .filter(f => /^\d{4}-W\d{2}\.html$/.test(f))
        .sort()
        .reverse(); // Newest first
    
    console.log(`   Found ${files.length} report files`);
    
    if (files.length === 0) {
        console.log('   No report files found, skipping index update');
        return;
    }
    
    // Generate cards for each report
    const cards = [];
    for (const file of files) {
        const weekStr = file.replace('.html', '');
        const info = parseWeekString(weekStr);
        if (!info) {
            console.warn(`   Skipping invalid file: ${file}`);
            continue;
        }
        
        const jsonPath = path.join(baseDir, `${weekStr}.json`);
        const stats = getReportStats(jsonPath);
        
        cards.push(generateArchiveCard(weekStr, info, stats));
        console.log(`   ✓ ${weekStr}: ${info.monthName} ${info.day}, ${info.year}`);
    }
    
    // Read existing index.html
    const indexPath = path.join(baseDir, 'index.html');
    if (!fs.existsSync(indexPath)) {
        console.error(`❌ Index file not found: ${indexPath}`);
        console.log('   Please ensure index.html exists before running this script');
        process.exit(1);
    }
    
    let indexHtml = fs.readFileSync(indexPath, 'utf-8');
    
    // Find and replace the archive-grid content
    const gridStart = indexHtml.indexOf('<div class="archive-grid">');
    const gridEnd = indexHtml.indexOf('</div>', indexHtml.indexOf('</a>', gridStart) + 4) + 6;
    
    if (gridStart === -1) {
        console.error('❌ Could not find archive-grid in index.html');
        process.exit(1);
    }
    
    // Build new grid content
    const newGrid = `<div class="archive-grid">
${cards.join('\n')}
            </div>`;
    
    // Replace old grid with new
    indexHtml = indexHtml.substring(0, gridStart) + newGrid + indexHtml.substring(gridEnd);
    
    // Write updated index
    fs.writeFileSync(indexPath, indexHtml);
    console.log(`\n✅ Archive index updated with ${cards.length} reports`);
}

// Run
main();
