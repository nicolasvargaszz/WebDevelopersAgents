# 🏗️ Automated Website Generation & Outreach System

## System Architecture Document

**Version:** 1.0  
**Date:** January 15, 2026  
**Author:** Nico Vargas

---

## 📋 Executive Summary

This document outlines a fully automated system designed to:
1. Identify local businesses without websites
2. Generate personalized website previews
3. Deploy them automatically
4. Send professional outreach proposals

The system leverages **GitHub Student Developer Pack** resources to minimize costs while maximizing scalability.

---

## 🏛️ High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                           ORCHESTRATION LAYER                                    │
│                    (GitHub Actions + DigitalOcean Droplet)                       │
└─────────────────────────────────────────────────────────────────────────────────┘
                                      │
          ┌───────────────────────────┼───────────────────────────┐
          ▼                           ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   AGENT 1       │       │   AGENT 2       │       │   AGENT 3       │
│   DISCOVERY     │──────▶│   ANALYSIS      │──────▶│   GENERATION    │
│   (Scraper)     │       │   (Qualifier)   │       │   (Builder)     │
└─────────────────┘       └─────────────────┘       └─────────────────┘
          │                       │                           │
          ▼                       ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  Google Maps    │       │  Business       │       │  HTML/CSS/JS    │
│  Data Extract   │       │  Intelligence   │       │  Templates      │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                                              │
          ┌───────────────────────────┬───────────────────────┘
          ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│   AGENT 4       │       │   AGENT 5       │       │   AGENT 6       │
│   DEPLOYMENT    │──────▶│   PREVIEW       │──────▶│   OUTREACH      │
│   (Publisher)   │       │   (Screenshot)  │       │   (Messenger)   │
└─────────────────┘       └─────────────────┘       └─────────────────┘
          │                       │                           │
          ▼                       ▼                           ▼
┌─────────────────┐       ┌─────────────────┐       ┌─────────────────┐
│  GitHub Pages   │       │  Polypane/      │       │  Email/WhatsApp │
│  Vercel/Netlify │       │  Puppeteer      │       │  Tracking       │
└─────────────────┘       └─────────────────┘       └─────────────────┘
                                      │
                                      ▼
                          ┌─────────────────────┐
                          │    AGENT 7         │
                          │    TRACKING        │
                          │    (Analytics)     │
                          └─────────────────────┘
                                      │
                                      ▼
                          ┌─────────────────────┐
                          │   PostgreSQL DB    │
                          │   (DigitalOcean)   │
                          └─────────────────────┘
```

---

## 🤖 Agent Roles & Responsibilities

### Agent 1: Discovery Agent (Scraper)
**Purpose:** Extract business data from Google Maps

| Responsibility | Details |
|---------------|---------|
| Location Search | Query Google Maps by city/neighborhood + category |
| Data Extraction | Name, address, phone, reviews, photos, hours |
| Website Detection | Identify businesses WITHOUT official websites |
| Rate Limiting | Respect Google's ToS, implement delays |
| Data Storage | Save raw data to PostgreSQL |

**Tech Stack:**
- Python + Playwright/Puppeteer
- Outscraper API (has free tier)
- SerpAPI (fallback, paid but reliable)
- DigitalOcean Droplet for execution

---

### Agent 2: Analysis Agent (Qualifier)
**Purpose:** Score and qualify businesses for outreach

| Responsibility | Details |
|---------------|---------|
| Business Scoring | Rate 1-100 based on conversion potential |
| Category Classification | Determine industry vertical |
| Priority Queue | Rank businesses by opportunity |
| Duplicate Detection | Avoid re-processing same businesses |

**Scoring Criteria:**
```
Score = (Reviews × 0.3) + (PhotoCount × 0.2) + (CategoryFit × 0.3) + (LocationTier × 0.2)

- Reviews: More reviews = established business = higher score
- PhotoCount: Active profile = cares about presence
- CategoryFit: Some categories convert better (restaurants, salons, etc.)
- LocationTier: Urban areas have more competition = need website more
```

**Tech Stack:**
- Python + pandas
- Azure Functions (serverless scoring)
- Custom ML model (optional, Phase 2)

---

### Agent 3: Generation Agent (Builder)
**Purpose:** Create personalized websites automatically

| Responsibility | Details |
|---------------|---------|
| Template Selection | Choose template based on business category |
| Content Generation | AI-generated copy specific to business |
| Asset Integration | Logo placeholder, Google Maps embed, photos |
| CTA Integration | WhatsApp button, call button, contact form |
| SEO Basics | Meta tags, Open Graph, structured data |

**Template Categories:**
```
├── restaurant/
│   ├── modern-food.html
│   ├── casual-dining.html
│   └── cafe-style.html
├── salon/
│   ├── beauty-minimal.html
│   └── barber-bold.html
├── retail/
│   ├── boutique.html
│   └── general-store.html
├── services/
│   ├── professional.html
│   ├── home-services.html
│   └── automotive.html
└── generic/
    └── business-card.html
```

**Tech Stack:**
- Jinja2 templating (Python)
- TailwindCSS (compiled)
- OpenAI API / Azure OpenAI (copy generation)
- Bootstrap Studio (manual premium templates)

---

### Agent 4: Deployment Agent (Publisher)
**Purpose:** Deploy generated websites to hosting

| Responsibility | Details |
|---------------|---------|
| Repo Creation | Create GitHub repo per business |
| File Upload | Push generated HTML/CSS/JS |
| GitHub Pages | Enable Pages, configure domain |
| DNS Management | Assign subdomain or custom path |
| SSL Verification | Ensure HTTPS is active |

**Deployment Strategy:**
```
Primary:   GitHub Pages (free, unlimited repos)
           └── Format: businessname.yourdomain.github.io
           
Secondary: Vercel (faster deploys, free tier)
           └── Format: businessname.vercel.app
           
Tertiary:  Netlify (backup, free tier)
           └── Format: businessname.netlify.app
           
Custom:    Azure Static Web Apps
           └── For premium clients (uses Azure credit)
```

**Tech Stack:**
- GitHub API (PyGithub)
- GitHub Actions for CI/CD
- Vercel CLI / API
- Netlify CLI / API

---

### Agent 5: Preview Agent (Screenshot Generator)
**Purpose:** Create visual mockups for outreach

| Responsibility | Details |
|---------------|---------|
| Desktop Screenshot | Full-page capture at 1920x1080 |
| Mobile Screenshot | Capture at 375x812 (iPhone) |
| Mockup Generation | Place screenshots in device frames |
| Image Optimization | Compress for email delivery |
| Gallery Creation | Multiple angles/views |

**Tech Stack:**
- Puppeteer / Playwright (screenshots)
- Polypane (multi-device preview)
- Sharp (image processing)
- Device mockup templates (Figma exports)

---

### Agent 6: Outreach Agent (Messenger)
**Purpose:** Send personalized proposals to businesses

| Responsibility | Details |
|---------------|---------|
| Email Composition | Generate personalized email |
| WhatsApp Message | Format for WhatsApp Business |
| Attachment Handling | Attach preview images |
| Send Scheduling | Optimal time delivery |
| Follow-up Queue | Schedule follow-ups |

**Email Template Structure:**
```
Subject: {BusinessName} - Su página web está lista para revisar 🌐

Estimado/a propietario/a de {BusinessName},

[Personalized opening based on business category]

He creado una página web profesional para {BusinessName} basándome 
en su información de Google Maps. 

✅ Lo que incluye su página web:
- Diseño profesional optimizado para móviles
- Botón de WhatsApp para contacto directo
- Mapa de Google con su ubicación
- Galería de fotos de su negocio
- Información de contacto y horarios

🎁 OFERTA ESPECIAL: Hosting GRATUITO por 1 año

👉 Vea su página web aquí: {preview_url}

📱 Vista previa en móvil: [imagen adjunta]

Si le interesa, responda a este correo o escríbame por WhatsApp 
al {my_whatsapp} y la activamos en menos de 24 horas.

Saludos cordiales,
{my_name}
Desarrollador Web Profesional
```

**Tech Stack:**
- Resend / SendGrid (email API, free tiers)
- Twilio (WhatsApp Business API)
- Azure Communication Services
- Custom tracking pixels

---

### Agent 7: Tracking Agent (Analytics)
**Purpose:** Monitor engagement and conversions

| Responsibility | Details |
|---------------|---------|
| Email Tracking | Open rates, click rates |
| Website Analytics | Visit tracking per preview |
| Response Detection | Monitor replies |
| Conversion Tracking | Lead → Client pipeline |
| Reporting | Daily/weekly dashboards |

**Metrics Tracked:**
```
Funnel Stage          │ Metric
──────────────────────┼────────────────────
Discovered            │ Total businesses found
Qualified             │ Score > 50
Generated             │ Website created
Deployed              │ Live URL available
Sent                  │ Outreach delivered
Opened                │ Email opened / WhatsApp read
Clicked               │ Preview link visited
Responded             │ Reply received
Converted             │ Became paying client
```

**Tech Stack:**
- PostgreSQL (DigitalOcean Managed DB)
- Plausible Analytics (self-hosted, privacy-friendly)
- Custom webhook endpoints
- Grafana (dashboards)

---

## 🛠️ Complete Tech Stack Summary

### By Resource (GitHub Student Benefits)

| Resource | Usage | Cost |
|----------|-------|------|
| **GitHub** | Code hosting, Pages, Actions | Free |
| **DigitalOcean** | VPS, Database, Workers | $200 credit |
| **Azure** | Functions, OpenAI, Storage | $100 credit |
| **Vercel** | Static hosting backup | Free tier |
| **Netlify** | Static hosting backup | Free tier |
| **Polypane** | Screenshot generation | Student license |
| **LambdaTest** | Cross-browser testing | Student access |
| **Bootstrap Studio** | Premium templates | Student license |

### By Function

| Function | Primary Tool | Backup |
|----------|-------------|--------|
| **Scraping** | Playwright + Python | Outscraper API |
| **Database** | PostgreSQL (DO) | SQLite (local) |
| **Queue** | Redis (DO) | BullMQ |
| **API Backend** | FastAPI (DO Droplet) | Azure Functions |
| **Website Gen** | Jinja2 + TailwindCSS | Bootstrap Studio |
| **AI Copy** | Azure OpenAI | OpenAI API |
| **Hosting** | GitHub Pages | Vercel |
| **Screenshots** | Puppeteer | Polypane |
| **Email** | Resend | SendGrid |
| **WhatsApp** | Twilio | Manual |
| **Analytics** | Plausible | Custom |

---

## 📁 Project Structure

```
webpageAutomatization/
├── README.md
├── SYSTEM_ARCHITECTURE.md
├── docker-compose.yml
├── .env.example
├── .github/
│   └── workflows/
│       ├── daily-discovery.yml
│       ├── process-queue.yml
│       └── deploy-sites.yml
│
├── agents/
│   ├── __init__.py
│   ├── discovery/
│   │   ├── __init__.py
│   │   ├── scraper.py
│   │   ├── google_maps.py
│   │   └── data_cleaner.py
│   │
│   ├── analysis/
│   │   ├── __init__.py
│   │   ├── scorer.py
│   │   ├── classifier.py
│   │   └── deduplicator.py
│   │
│   ├── generation/
│   │   ├── __init__.py
│   │   ├── builder.py
│   │   ├── copy_writer.py
│   │   └── asset_manager.py
│   │
│   ├── deployment/
│   │   ├── __init__.py
│   │   ├── github_publisher.py
│   │   ├── vercel_publisher.py
│   │   └── dns_manager.py
│   │
│   ├── preview/
│   │   ├── __init__.py
│   │   ├── screenshot.py
│   │   └── mockup_generator.py
│   │
│   ├── outreach/
│   │   ├── __init__.py
│   │   ├── email_sender.py
│   │   ├── whatsapp_sender.py
│   │   └── message_composer.py
│   │
│   └── tracking/
│       ├── __init__.py
│       ├── pixel_tracker.py
│       ├── analytics.py
│       └── reporter.py
│
├── templates/
│   ├── base.html
│   ├── restaurant/
│   ├── salon/
│   ├── retail/
│   ├── services/
│   └── generic/
│
├── assets/
│   ├── css/
│   ├── js/
│   ├── images/
│   └── mockups/
│
├── api/
│   ├── __init__.py
│   ├── main.py
│   ├── routes/
│   │   ├── businesses.py
│   │   ├── websites.py
│   │   ├── outreach.py
│   │   └── webhooks.py
│   └── models/
│       ├── business.py
│       ├── website.py
│       └── campaign.py
│
├── database/
│   ├── migrations/
│   ├── schema.sql
│   └── seeds/
│
├── scripts/
│   ├── setup.sh
│   ├── run_discovery.py
│   ├── process_queue.py
│   └── send_batch.py
│
├── config/
│   ├── settings.py
│   ├── categories.json
│   └── locations.json
│
└── tests/
    ├── test_discovery.py
    ├── test_generation.py
    └── test_deployment.py
```

---

## 🔄 Automation Flow (Step-by-Step)

### Phase 1: Discovery (Daily, Automated)

```
┌─────────────────────────────────────────────────────────────────┐
│ TRIGGER: GitHub Actions Cron (daily at 2:00 AM)                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Load target locations from config/locations.json        │
│         Example: ["Mexico City", "Guadalajara", "Monterrey"]    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: For each location, query Google Maps categories:        │
│         - "restaurantes cerca de {location}"                    │
│         - "salones de belleza cerca de {location}"              │
│         - "talleres mecánicos cerca de {location}"              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: For each result, extract:                               │
│         - Business name                                         │
│         - Address                                               │
│         - Phone number                                          │
│         - Rating & review count                                 │
│         - Photos (URLs)                                         │
│         - Website field (check if empty/missing)               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Filter businesses WITHOUT websites                      │
│         - No website field                                      │
│         - Only Facebook/Instagram link                          │
│         - Broken/non-functional website                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Save to database with status = "discovered"             │
│         - Deduplicate against existing records                  │
│         - Assign unique business_id                             │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 2: Analysis & Scoring (Hourly)

```
┌─────────────────────────────────────────────────────────────────┐
│ TRIGGER: GitHub Actions Cron (every hour)                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Query businesses with status = "discovered"             │
│         Limit: 100 per batch                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Calculate opportunity score:                            │
│                                                                 │
│   def calculate_score(business):                                │
│       review_score = min(business.reviews / 100, 1) * 30        │
│       photo_score = min(business.photos / 10, 1) * 20           │
│       category_score = CATEGORY_WEIGHTS[business.category] * 30 │
│       location_score = LOCATION_TIERS[business.city] * 20       │
│       return review_score + photo_score + category_score +      │
│              location_score                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Classify business category (if not clear):              │
│         - Use AI classification based on name + existing data   │
│         - Assign primary_category and secondary_category        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Update status based on score:                           │
│         - Score >= 50: status = "qualified"                     │
│         - Score < 50:  status = "low_priority"                  │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 3: Website Generation (On-Demand)

```
┌─────────────────────────────────────────────────────────────────┐
│ TRIGGER: Queue processor (continuous on DO Droplet)             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Dequeue next qualified business                         │
│         ORDER BY score DESC, created_at ASC                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Select template based on category:                      │
│         template = CATEGORY_TEMPLATES[business.primary_category]│
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Generate personalized copy using AI:                    │
│                                                                 │
│   prompt = f"""                                                 │
│   Generate website copy for {business.name}, a                  │
│   {business.category} located in {business.address}.            │
│   They have {business.reviews} reviews with {business.rating}   │
│   stars. Create:                                                │
│   1. Hero headline (max 10 words)                               │
│   2. Business description (50 words)                            │
│   3. Services list (5 items)                                    │
│   4. Call-to-action text                                        │
│   Tone: Professional, local, trustworthy.                       │
│   Language: Spanish.                                            │
│   """                                                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Render template with:                                   │
│         - Generated copy                                        │
│         - Business photos (downloaded & optimized)              │
│         - Google Maps embed (coordinates)                       │
│         - WhatsApp button (with business phone)                 │
│         - Contact information                                   │
│         - Business hours                                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Save generated files to /tmp/{business_id}/             │
│         - index.html                                            │
│         - styles.css                                            │
│         - script.js                                             │
│         - /images/                                              │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Update status = "generated"                             │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 4: Deployment (Automatic after Generation)

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Create GitHub repository:                               │
│         repo_name = sanitize(business.name)                     │
│         gh.create_repo(f"preview-{repo_name}")                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Push generated files to repository                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Enable GitHub Pages:                                    │
│         - Branch: main                                          │
│         - Folder: / (root)                                      │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Wait for deployment (poll status)                       │
│         Max wait: 5 minutes                                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Verify site is live:                                    │
│         GET https://{username}.github.io/preview-{repo_name}/   │
│         Assert status == 200                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Save URL to database, status = "deployed"               │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 5: Screenshot Generation

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Launch headless browser (Puppeteer)                     │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Navigate to deployed URL                                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Capture screenshots:                                    │
│         - Desktop: 1920x1080, full page                         │
│         - Mobile: 375x812, full page                            │
│         - Tablet: 768x1024, above fold                          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Generate device mockups:                                │
│         - Place desktop screenshot in iMac frame                │
│         - Place mobile screenshot in iPhone frame               │
│         - Create combined preview image                         │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Optimize images:                                        │
│         - Compress to <500KB per image                          │
│         - Generate thumbnail versions                           │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Upload to storage (GitHub repo or DO Spaces)            │
│         Save URLs to database, status = "ready_for_outreach"    │
└─────────────────────────────────────────────────────────────────┘
```

### Phase 6: Outreach

```
┌─────────────────────────────────────────────────────────────────┐
│ STEP 1: Query businesses with status = "ready_for_outreach"     │
│         Check: Not contacted in last 30 days                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 2: Generate personalized email:                            │
│         - Use business data for personalization                 │
│         - Include preview URL with tracking params              │
│         - Attach mockup images                                  │
│         - Add tracking pixel                                    │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 3: Determine contact method:                               │
│         - If email available: Send email                        │
│         - If phone only: Queue for WhatsApp                     │
│         - If neither: Skip (or use contact form)                │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 4: Send message:                                           │
│         - Email: via Resend API                                 │
│         - WhatsApp: via Twilio or manual queue                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 5: Log outreach:                                           │
│         - Timestamp                                             │
│         - Channel (email/whatsapp)                              │
│         - Message ID                                            │
│         - Status = "sent"                                       │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ STEP 6: Schedule follow-up:                                     │
│         - If no response in 3 days: First follow-up             │
│         - If no response in 7 days: Second follow-up            │
│         - If no response in 14 days: Mark as "no_response"      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 💾 Database Schema

```sql
-- Core Tables

CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    google_place_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    category VARCHAR(100),
    subcategory VARCHAR(100),
    address TEXT,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'Mexico',
    phone VARCHAR(50),
    email VARCHAR(255),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    rating DECIMAL(2, 1),
    review_count INTEGER DEFAULT 0,
    photo_count INTEGER DEFAULT 0,
    photo_urls TEXT[], -- Array of URLs
    has_website BOOLEAN DEFAULT FALSE,
    existing_website VARCHAR(500),
    score INTEGER DEFAULT 0,
    status VARCHAR(50) DEFAULT 'discovered',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE websites (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id),
    template_used VARCHAR(100),
    generated_html TEXT,
    generated_css TEXT,
    github_repo VARCHAR(255),
    preview_url VARCHAR(500),
    vercel_url VARCHAR(500),
    desktop_screenshot VARCHAR(500),
    mobile_screenshot VARCHAR(500),
    mockup_image VARCHAR(500),
    status VARCHAR(50) DEFAULT 'generating',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP
);

CREATE TABLE outreach_campaigns (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id),
    website_id UUID REFERENCES websites(id),
    channel VARCHAR(50), -- 'email', 'whatsapp', 'both'
    email_subject VARCHAR(255),
    email_body TEXT,
    whatsapp_message TEXT,
    tracking_id VARCHAR(100) UNIQUE,
    status VARCHAR(50) DEFAULT 'pending',
    sent_at TIMESTAMP,
    opened_at TIMESTAMP,
    clicked_at TIMESTAMP,
    responded_at TIMESTAMP,
    response_type VARCHAR(50), -- 'interested', 'not_interested', 'ask_price'
    follow_up_count INTEGER DEFAULT 0,
    last_follow_up TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE tracking_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    campaign_id UUID REFERENCES outreach_campaigns(id),
    event_type VARCHAR(50), -- 'open', 'click', 'visit', 'response'
    event_data JSONB,
    ip_address VARCHAR(45),
    user_agent TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE conversions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    business_id UUID REFERENCES businesses(id),
    campaign_id UUID REFERENCES outreach_campaigns(id),
    conversion_type VARCHAR(50), -- 'lead', 'trial', 'paid'
    revenue DECIMAL(10, 2),
    notes TEXT,
    converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_businesses_status ON businesses(status);
CREATE INDEX idx_businesses_score ON businesses(score DESC);
CREATE INDEX idx_businesses_city ON businesses(city);
CREATE INDEX idx_websites_status ON websites(status);
CREATE INDEX idx_campaigns_status ON outreach_campaigns(status);
CREATE INDEX idx_tracking_campaign ON tracking_events(campaign_id);
```

---

## 🚀 Deployment Strategy

### Infrastructure Setup (Using GitHub Student Resources)

#### 1. DigitalOcean Droplet (Main Worker)
```yaml
Droplet Configuration:
  Name: automation-worker
  Image: Ubuntu 22.04 LTS
  Size: Basic, 2GB RAM, 1 vCPU ($12/month)
  Region: Closest to target market
  
Software Stack:
  - Python 3.11
  - Node.js 18 LTS
  - PostgreSQL client
  - Redis
  - Docker
  - Playwright browsers
  
Purpose:
  - Run discovery agent
  - Process generation queue
  - Execute screenshot capture
  - Handle outreach sending
```

#### 2. DigitalOcean Managed PostgreSQL
```yaml
Database Configuration:
  Name: automation-db
  Engine: PostgreSQL 15
  Size: Basic, 1GB RAM ($15/month)
  
Features:
  - Automatic backups
  - SSL connections
  - Connection pooling
```

#### 3. GitHub Infrastructure
```yaml
Repositories:
  - webpageAutomatization (main codebase)
  - preview-* (generated preview sites)
  - website-templates (shared templates)

GitHub Actions:
  - Daily discovery cron
  - Hourly scoring cron
  - Deployment workflows

GitHub Pages:
  - Host all preview sites
  - Free SSL certificates
  - Unlimited repositories
```

#### 4. Azure Functions (Optional Scaling)
```yaml
Functions:
  - ai-copy-generator (OpenAI wrapper)
  - email-tracker (pixel endpoint)
  - webhook-handler (Twilio callbacks)

Benefits:
  - Serverless scaling
  - Pay per execution
  - Uses $100 student credit
```

### Cost Breakdown (Monthly)

| Service | Cost | Notes |
|---------|------|-------|
| DO Droplet | $12 | From $200 credit |
| DO PostgreSQL | $15 | From $200 credit |
| GitHub Pages | $0 | Free unlimited |
| Vercel | $0 | Free tier (100 deploys/day) |
| Resend Email | $0 | Free tier (100 emails/day) |
| Azure Functions | $0 | From $100 credit |
| OpenAI API | ~$5-10 | Pay as you go |
| **Total** | **~$32-37** | Covered by credits for 6+ months |

---

## 📅 MVP Roadmap (30 Days)

### Week 1: Foundation (Days 1-7)

| Day | Task | Deliverable |
|-----|------|-------------|
| 1 | Project setup, repo structure | GitHub repo initialized |
| 2 | Database schema, DO PostgreSQL | Database running |
| 3 | Discovery agent v1 (Google Maps) | Basic scraper working |
| 4 | Discovery agent v2 (data cleaning) | Clean data pipeline |
| 5 | Analysis agent (scoring) | Scoring algorithm |
| 6 | Templates (2-3 categories) | HTML/CSS templates |
| 7 | Testing & debugging | Stable discovery flow |

**Milestone:** Can discover 100 businesses/day and score them

### Week 2: Generation (Days 8-14)

| Day | Task | Deliverable |
|-----|------|-------------|
| 8 | Generation agent (template rendering) | Jinja2 pipeline |
| 9 | AI copy integration (OpenAI) | Dynamic copy |
| 10 | Asset management (photos) | Image pipeline |
| 11 | Deployment agent (GitHub Pages) | Auto-deploy |
| 12 | Screenshot agent (Puppeteer) | Screenshot capture |
| 13 | Mockup generation | Device frames |
| 14 | End-to-end testing | Full pipeline test |

**Milestone:** Can generate and deploy 10 websites automatically

### Week 3: Outreach (Days 15-21)

| Day | Task | Deliverable |
|-----|------|-------------|
| 15 | Email templates | Spanish email copy |
| 16 | Email sender (Resend) | Email delivery |
| 17 | Tracking pixel | Open tracking |
| 18 | Click tracking | Link tracking |
| 19 | WhatsApp templates | Message copy |
| 20 | Dashboard v1 (basic) | Status overview |
| 21 | Follow-up system | Auto follow-ups |

**Milestone:** Can send 50 personalized outreach messages/day

### Week 4: Polish & Scale (Days 22-30)

| Day | Task | Deliverable |
|-----|------|-------------|
| 22 | More templates (5 total) | Category coverage |
| 23 | Error handling | Robust system |
| 24 | Monitoring & alerts | Uptime monitoring |
| 25 | Performance optimization | Faster pipeline |
| 26 | Documentation | User guide |
| 27 | A/B testing setup | Email variants |
| 28 | Analytics dashboard | Conversion tracking |
| 29 | Load testing | Capacity validation |
| 30 | Launch preparation | Go-live checklist |

**Milestone:** Production-ready system processing 50+ businesses/day

---

## 💰 Monetization Strategy

### Pricing Tiers

```
┌─────────────────────────────────────────────────────────────────┐
│  FREE TIER (Lead Magnet)                                        │
├─────────────────────────────────────────────────────────────────┤
│  ✓ Preview website (view only)                                  │
│  ✓ GitHub Pages subdomain                                       │
│  ✓ Basic template                                               │
│  ✓ WhatsApp button                                              │
│  ✓ Google Maps embed                                            │
│  ✗ Custom domain                                                │
│  ✗ Email contact form                                           │
│  ✗ Analytics                                                    │
│                                                                 │
│  Duration: 30-day preview, then archived                        │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  STARTER - $99/year (or $15/month)                              │
├─────────────────────────────────────────────────────────────────┤
│  ✓ Everything in Free                                           │
│  ✓ Permanent hosting                                            │
│  ✓ Custom subdomain (business.tudominio.com)                    │
│  ✓ Contact form with email notifications                        │
│  ✓ Basic analytics (visits, clicks)                             │
│  ✓ 1 content update/month                                       │
│  ✓ WhatsApp support                                             │
│                                                                 │
│  Best for: Small shops, independent professionals               │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  PROFESSIONAL - $299/year (or $35/month)                        │
├─────────────────────────────────────────────────────────────────┤
│  ✓ Everything in Starter                                        │
│  ✓ Custom domain (.com, .mx)                                    │
│  ✓ Premium template selection                                   │
│  ✓ SEO optimization                                             │
│  ✓ Google Business integration                                  │
│  ✓ Multi-page website (up to 5 pages)                          │
│  ✓ Monthly content updates                                      │
│  ✓ Priority support                                             │
│                                                                 │
│  Best for: Established local businesses                         │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│  BUSINESS - $599/year (or $65/month)                            │
├─────────────────────────────────────────────────────────────────┤
│  ✓ Everything in Professional                                   │
│  ✓ E-commerce integration (simple catalog)                      │
│  ✓ Online booking/reservations                                  │
│  ✓ Advanced analytics                                           │
│  ✓ Social media links                                           │
│  ✓ Blog functionality                                           │
│  ✓ Unlimited content updates                                    │
│  ✓ Dedicated account manager                                    │
│                                                                 │
│  Best for: Growing businesses, restaurants, salons              │
└─────────────────────────────────────────────────────────────────┘
```

### Revenue Projections

```
Assumptions (Conservative):
- 100 businesses contacted/week
- 5% response rate = 5 responses/week
- 20% conversion to paid = 1 client/week
- Average ticket: $150/year (mix of tiers)

Monthly Revenue:
- Month 1: 4 clients × $150 = $600
- Month 3: 12 clients × $150 = $1,800
- Month 6: 24 clients × $150 = $3,600
- Month 12: 48 clients × $150 = $7,200

Annual Recurring Revenue (Year 1): ~$43,200

At Scale (Year 2+):
- 200 businesses contacted/week
- 100+ active clients
- ARR: $15,000 - $25,000
```

### Upsell Opportunities

1. **Custom Design** - $500 one-time
   - Fully custom design beyond templates
   
2. **Logo Design** - $150 one-time
   - Professional logo for businesses without one
   
3. **Photography** - $200 one-time
   - Professional photos for website
   
4. **Google Ads Management** - $100/month
   - Setup and manage Google Ads campaigns
   
5. **Social Media Setup** - $100 one-time
   - Create Facebook/Instagram business pages

---

## ⚖️ Legal & Ethical Considerations

### Data Collection
- Only scrape publicly available information
- Respect robots.txt directives
- Implement rate limiting (max 1 request/second)
- Store data securely with encryption

### Outreach
- Include unsubscribe option in all emails
- Comply with anti-spam laws (CAN-SPAM, GDPR equivalent)
- Don't send more than 2 follow-ups
- Respect "no contact" requests immediately

### Website Generation
- Clearly mark previews as "draft/preview"
- Include disclaimer that site is not live
- Don't impersonate the business
- Remove preview if business requests

### Terms of Service
- Create clear ToS for clients
- Explain hosting terms
- Define content ownership
- Outline cancellation policy

---

## 🔧 Configuration Files

### Environment Variables (.env.example)

```bash
# Database
DATABASE_URL=postgresql://user:password@host:5432/automation

# GitHub
GITHUB_TOKEN=ghp_xxxxxxxxxxxx
GITHUB_USERNAME=your-username
GITHUB_ORG=your-organization

# OpenAI
OPENAI_API_KEY=sk-xxxxxxxxxxxx

# Azure
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_KEY=xxxxxxxxxxxx
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Email (Resend)
RESEND_API_KEY=re_xxxxxxxxxxxx
FROM_EMAIL=contacto@tudominio.com

# WhatsApp (Twilio)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxx
TWILIO_WHATSAPP_NUMBER=+14155238886

# Tracking
TRACKING_DOMAIN=https://track.tudominio.com
TRACKING_SECRET=random-secret-key

# Scraping
GOOGLE_MAPS_API_KEY=AIzaxxxxxxxxxxxx
OUTSCRAPER_API_KEY=xxxxxxxxxxxx

# Feature Flags
ENABLE_WHATSAPP=false
ENABLE_AI_COPY=true
MAX_DAILY_OUTREACH=50
```

---

## 📊 Success Metrics & KPIs

### Discovery Phase
- Businesses discovered per day
- Businesses without websites (%)
- Data quality score

### Generation Phase
- Websites generated per day
- Template usage distribution
- Generation success rate

### Deployment Phase
- Deployment success rate
- Average time to deploy
- Site uptime percentage

### Outreach Phase
- Emails sent per day
- Open rate (target: >25%)
- Click rate (target: >10%)
- Response rate (target: >5%)

### Conversion Phase
- Lead to trial conversion
- Trial to paid conversion
- Average revenue per client
- Customer lifetime value

---

## 🎯 Next Steps

1. **Immediate (Today)**
   - Set up GitHub repository structure
   - Configure DigitalOcean account with student credits
   - Create PostgreSQL database

2. **This Week**
   - Implement discovery agent MVP
   - Create 3 initial templates
   - Test end-to-end flow manually

3. **This Month**
   - Complete all 7 agents
   - Process first 100 businesses
   - Send first outreach batch
   - Track first conversions

---

*Document maintained by: Automation System*  
*Last updated: January 15, 2026*
