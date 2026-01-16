# 🚀 WebDevelopers Agents

> **Automated Lead Generation System** — Discovers local businesses without websites, generates personalized previews, and sends outreach proposals. Built with Python, Playwright, and AI.

[![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python&logoColor=white)](https://python.org)
[![Playwright](https://img.shields.io/badge/Playwright-Automation-green?logo=playwright&logoColor=white)](https://playwright.dev)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-336791?logo=postgresql&logoColor=white)](https://postgresql.org)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## 📊 Current Stats

| Metric | Value |
|--------|-------|
| 🏢 **Businesses Discovered** | 580+ |
| 🎯 **Qualified Leads** | 462 |
| 📍 **Locations Covered** | 13 cities |
| 📂 **Categories Scraped** | 25+ |

---

## 🎯 What It Does

```
┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  🔍 DISCOVER │────▶│  📊 ANALYZE  │────▶│  🎨 GENERATE │
│  Google Maps │     │  Score Leads │     │  Websites    │
└──────────────┘     └──────────────┘     └──────────────┘
                                                 │
┌──────────────┐     ┌──────────────┐            │
│  📧 OUTREACH │◀────│  🚀 DEPLOY   │◀───────────┘
│  Email/WA    │     │  GitHub Pages│
└──────────────┘     └──────────────┘
```

**The Problem:** Millions of local businesses don't have websites, losing customers daily.

**The Solution:** An automated system that:
1. 🔍 **Discovers** businesses without websites from Google Maps
2. 📊 **Scores** them by conversion potential (reviews, photos, category)
3. 🎨 **Generates** personalized website previews automatically
4. 🚀 **Deploys** them to free hosting (GitHub Pages)
5. 📧 **Sends** professional outreach with live preview links

---

## 🏗️ Architecture

```
webpageAutomatization/
├── 🤖 agents/
│   ├── discovery/          # Google Maps scraper
│   │   └── google_maps.py  # Playwright-based extraction
│   ├── analysis/           # Lead qualification
│   │   └── scorer.py       # Scoring algorithm
│   ├── generation/         # Website builder (WIP)
│   ├── deployment/         # GitHub Pages publisher (WIP)
│   └── outreach/           # Email/WhatsApp sender (WIP)
├── 📁 config/
│   ├── locations.json      # Target cities (Paraguay)
│   ├── categories.json     # Business categories
│   └── settings.py         # App configuration
├── 🗄️ database/
│   └── schema.sql          # PostgreSQL schema
├── 📊 Data Files
│   ├── discovered_businesses.json  # All scraped data
│   └── leads.json                  # Qualified leads
└── 🐳 Docker
    ├── Dockerfile
    └── docker-compose.yml
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|------------|
| **Scraping** | Python + Playwright |
| **Database** | PostgreSQL |
| **Queue** | Redis + Celery |
| **API** | FastAPI |
| **AI Copy** | OpenAI / Azure OpenAI |
| **Hosting** | GitHub Pages (free) |
| **Email** | Resend API |
| **Containers** | Docker |

---

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Node.js 18+ (for Playwright)

### Installation

```bash
# Clone the repo
git clone https://github.com/nicolasvargaszz/WebDevelopersAgents.git
cd WebDevelopersAgents

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### Run Discovery Agent

```bash
# Scrape businesses from Google Maps
python -m agents.discovery.google_maps

# Analyze results
python analyze_results.py
```

---

## 📈 Agent Details

### 1️⃣ Discovery Agent (✅ Complete)
Scrapes Google Maps for businesses without websites.

**Features:**
- 🌐 Multi-location search (13 Paraguay cities)
- 🏷️ 25+ business categories
- 🔍 Detects website status (none, social-only, active)
- 🛡️ Anti-detection measures (random delays, user agents)
- 💾 Deduplication by name and phone
- 📊 Incremental scraping (preserves existing data)

**Output:**
```json
{
  "name": "Café Corner S.R.L.",
  "category": "Cafetería",
  "address": "Carmelitas, Asunción",
  "phone": "0981 234567",
  "rating": 4.6,
  "review_count": 156,
  "has_website": false,
  "website_status": "none"
}
```

### 2️⃣ Analysis Agent (✅ Complete)
Scores and qualifies leads for outreach.

**Scoring Algorithm:**
```
Score = Reviews (20) + Rating (15) + Photos (10) + 
        Category (25) + Location (15) + Contact (10) + Activity (5)

🟢 GO (≥50)      → High priority lead
🟡 REVIEW (35-49) → Manual review needed  
🔴 NO_GO (<35)    → Skip
```

### 3️⃣ Generation Agent (🔄 In Progress)
Creates personalized websites from templates.

### 4️⃣ Deployment Agent (📋 Planned)
Publishes to GitHub Pages automatically.

### 5️⃣ Outreach Agent (📋 Planned)
Sends personalized emails with preview links.

---

## 📍 Coverage

### Paraguay 🇵🇾
| City | Businesses |
|------|------------|
| Asunción (Centro) | 97 |
| Luque | 66 |
| Villa Morra | 51 |
| Fernando de la Mora | 50 |
| San Lorenzo | 49 |
| Lambaré | 44 |
| + 7 more cities... | 223 |

### Categories
`Restaurants` `Dental Clinics` `Veterinaries` `Auto Shops` `Salons` `Gyms` `Bakeries` `Pharmacies` `Law Firms` `Real Estate` `Spas` `Car Washes` `Locksmiths` ...

---

## 💰 Business Model

```
┌─────────────────────────────────────────────────────┐
│  FREE PREVIEW                                       │
│  ✓ Live website preview                             │
│  ✓ 30-day hosting                                   │
│  ✗ Custom domain                                    │
└─────────────────────────────────────────────────────┘
          │
          ▼ Convert to...
┌─────────────────────────────────────────────────────┐
│  💼 STARTER ($99/year)                              │
│  ✓ Permanent hosting                                │
│  ✓ Custom subdomain                                 │
│  ✓ Contact form                                     │
│  ✓ Basic analytics                                  │
└─────────────────────────────────────────────────────┘
          │
          ▼ Upsell to...
┌─────────────────────────────────────────────────────┐
│  🚀 PROFESSIONAL ($299/year)                        │
│  ✓ Custom domain (.com)                             │
│  ✓ SEO optimization                                 │
│  ✓ Multi-page website                               │
│  ✓ Priority support                                 │
└─────────────────────────────────────────────────────┘
```

---

## 🗓️ Roadmap

- [x] **Phase 1:** Discovery Agent — Scrape Google Maps ✅
- [x] **Phase 2:** Analysis Agent — Score leads ✅
- [ ] **Phase 3:** Generation Agent — Build websites
- [ ] **Phase 4:** Deployment Agent — GitHub Pages
- [ ] **Phase 5:** Outreach Agent — Email campaigns
- [ ] **Phase 6:** Tracking Agent — Analytics dashboard

---

## 📊 Sample Output

```
📊 DISCOVERY RESULTS SUMMARY
==================================================
Total businesses scraped: 580

🎯 LEADS (no website):     364
📱 Social media only:      98
🌐 Has website (skip):     118

✅ Exported 462 leads to leads.json
```

---

## 🤝 Contributing

Contributions welcome! Please read the [Architecture Doc](SYSTEM_ARCHITECTURE.md) first.

```bash
# Fork the repo
# Create feature branch
git checkout -b feature/amazing-feature

# Commit changes
git commit -m "Add amazing feature"

# Push and create PR
git push origin feature/amazing-feature
```

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

---

## 👨‍💻 Author

**Nico Vargas**

[![GitHub](https://img.shields.io/badge/GitHub-nicolasvargaszz-black?logo=github)](https://github.com/nicolasvargaszz)

---

<p align="center">
  <i>Built with ☕ and Python</i>
</p>
