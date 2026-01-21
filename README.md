# TacRaven Weekly Threat Report Generator

**Fully autonomous** weekly threat intelligence report generation for TacRaven Solutions.

Runs every Monday via GitHub Actions — no manual intervention required.

## 🚀 Quick Start - GitHub Repository Setup

### Step 1: Repository Structure

Your GitHub repository should look like this after setup:

```
your-website-repo/
├── .github/
│   └── workflows/
│       └── weekly-report.yml      ← GitHub Actions workflow (runs every Monday)
├── intel/
│   ├── methodology.html           ← Your methodology page
│   └── weekly/
│       ├── index.html             ← Archive index (auto-updated each week)
│       └── 2026-W04.html          ← Reports (auto-generated each week)
├── scripts/
│   └── update-archive-index.js    ← Archive updater script
├── generate-report.js             ← Main generator script
├── package.json                   ← Node.js config
└── (your other website files)
```

### Step 2: Upload Files to GitHub

**Option A: Upload the entire package (easiest)**
1. Extract the zip file
2. Copy the contents of `weekly-report-generator/` into your website repository root
3. The folder structure is already correct

**Option B: Upload files individually**
1. Create folders: `.github/workflows/`, `intel/weekly/`, `scripts/`
2. Upload files to their locations:
   - `weekly-report.yml` → `.github/workflows/`
   - `index.html` (archive) → `intel/weekly/`
   - `2026-W04.html` (first report) → `intel/weekly/`
   - `methodology.html` → `intel/`
   - `generate-report.js` → repository root
   - `package.json` → repository root
   - `update-archive-index.js` → `scripts/`

### Step 3: Enable GitHub Actions

1. Go to your repository on GitHub
2. Click **Settings** → **Actions** → **General**
3. Under "Workflow permissions", select **"Read and write permissions"**
4. Check **"Allow GitHub Actions to create and approve pull requests"**
5. Click **Save**

### Step 4: Test the Workflow

1. Go to **Actions** tab in your repository
2. Click **"Weekly Threat Report Generation"** in the left sidebar
3. Click **"Run workflow"** button
4. Leave week_override empty (uses current week)
5. Click **"Run workflow"**

Watch the workflow run. If successful, you'll see new files in `intel/weekly/`.

---

## ⏰ Automated Schedule

The workflow runs automatically every **Monday at 4:30 AM UTC** (Sunday 11:30 PM EST).

To change the schedule, edit `.github/workflows/weekly-report.yml`:

```yaml
schedule:
  - cron: '30 4 * * 1'  # Minute Hour Day Month DayOfWeek
```

Examples:
- `'0 6 * * 1'` = Monday at 6:00 AM UTC
- `'30 12 * * 1'` = Monday at 12:30 PM UTC
- `'0 0 * * 2'` = Tuesday at midnight UTC

---

## 📊 What Gets Generated

Each week, the system automatically generates:

| File | Description |
|------|-------------|
| `intel/weekly/YYYY-WXX.html` | Full professional HTML report with all sections |
| `intel/weekly/YYYY-WXX.json` | Raw data in JSON format for programmatic access |
| `intel/weekly/index.html` | Updated archive with link to new report |

**Report includes:**
- BLUF (Bottom Line Up Front) key takeaways
- Executive Summary for leadership
- Threat level assessment with animated stats
- Week-over-week trend analysis with sparkline charts
- Top 5 threat drivers
- Structured Analytical Techniques (KAC, ACH)
- MITRE ATT&CK mapping
- Actionable patch priorities with ransomware tags
- C2 blocklist indicators
- Threat hunting suggestions

---

## 🔧 Data Sources

The generator fetches **live data** from:

- **CISA KEV Catalog** - Known Exploited Vulnerabilities
- **Feodo Tracker** - C2 server indicators (abuse.ch)
- **Security News RSS** - The Hacker News, Dark Reading, Krebs, CISA

---

## 📝 Important Notes

### Troubleshooting

**Workflow fails with "permission denied":**
- Enable write permissions in Settings → Actions → General

**No files generated:**
- Check the Actions log for errors
- Ensure data sources (CISA, Feodo) are accessible

**Archive not updating:**
- Ensure `intel/weekly/index.html` exists
- Check that `scripts/update-archive-index.js` is present

---

## 🔄 Manual Trigger

You can manually generate a report anytime:

1. Go to Actions → Weekly Threat Report Generation
2. Click "Run workflow"
3. Optionally enter a specific week (e.g., `2026-W05`)
4. Click "Run workflow"

---

## 📁 File Reference

| File | Purpose |
|------|---------|
| `generate-report.js` | Main generator - fetches data, creates professional report |
| `scripts/update-archive-index.js` | Updates archive with new report links |
| `.github/workflows/weekly-report.yml` | GitHub Actions automation config |
| `package.json` | Node.js configuration |
| `intel/weekly/index.html` | Archive page showing all reports |

---

## 🛡️ Security Notes

- The workflow only has write access to your repository
- No API keys or secrets are required
- All data sources are public

---

## 📞 Support

For issues with the generator, check:
1. GitHub Actions logs (Actions tab → workflow run → job details)
2. Ensure all files are in correct locations
3. Verify GitHub Pages is enabled if using for hosting

---

*TacRaven Solutions - Structured Threat Analysis*
