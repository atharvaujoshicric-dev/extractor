# ContactMine — B2B Contact Intelligence Tool

Extract names, mobile numbers, and designations of key personnel from any company.
Filter by role, export to Excel. Like Apollo.io / ContactOut — but yours.

---

## Features

- 🔍 **Multi-source extraction** — Scrapes company website, Google, LinkedIn
- 👤 **Name + Designation + Phone + Email** per contact
- 🏷️ **Smart categorization** — C-Suite, VP, Director, Manager, Engineer, Sales, etc.
- 🎛️ **Designation filter chips** — filter instantly by role category
- 📊 **Excel export** — color-coded by category, with summary sheet
- 📋 **One-click copy** — copy phone/email with one click
- 🧪 **Demo mode** — realistic sample data when scraping isn't available

---

## Quick Start

### Windows
```
Double-click: start.bat
```

### Mac / Linux
```bash
chmod +x start.sh
./start.sh
```

### Manual Start
```bash
# Terminal 1 — Backend
cd backend
pip install -r requirements.txt
python app.py

# Browser — Frontend
Open frontend/index.html in your browser
```

---

## How It Works

### Extraction Pipeline
1. **Company Website** — scrapes `/team`, `/about`, `/contact`, `/leadership` pages
2. **Google Search** — searches for company contacts with designation keywords
3. **LinkedIn via Google** — finds LinkedIn profiles through Google indexing
4. **Fallback** — realistic demo data if scraping is blocked

### Designation Categories
| Category | Roles Detected |
|----------|---------------|
| C-Suite | CEO, CTO, CFO, COO, CMO |
| VP / SVP | Vice President, SVP, EVP |
| Director | Director, Head of X |
| Manager | Manager, MGR |
| Engineer | Engineer, Developer, Architect |
| Sales | Sales, Account Executive, BD |
| Marketing | Marketing, Growth, SEO |
| HR / People | HR, Recruiter, Talent |
| Finance | Finance, Accountant |
| Operations | Operations, Supply Chain |
| Founder | Founder, Co-Founder, Owner |

---

## Project Structure

```
contact-extractor/
├── backend/
│   ├── app.py              # Flask API server
│   └── requirements.txt    # Python dependencies
├── frontend/
│   └── index.html          # Full UI (single file)
├── start.sh                # Mac/Linux launcher
├── start.bat               # Windows launcher
└── README.md
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/extract` | Extract contacts for a company |
| POST | `/api/export` | Export contacts to Excel |
| GET | `/api/designations` | Get all designation categories |
| GET | `/health` | Health check |

### Extract Request
```json
{
  "company_name": "Infosys",
  "city": "Bangalore",
  "domain": "infosys.com",
  "use_demo": false
}
```

---

## Notes

- **Demo mode ON** = instant results with realistic generated data  
- **Demo mode OFF** = real scraping (may be blocked by Google/LinkedIn rate limits)  
- For production use, consider adding rotating proxies and a CAPTCHA solver  
- No AI API keys required — 100% rule-based extraction  
