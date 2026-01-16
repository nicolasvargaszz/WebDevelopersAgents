-- ===========================================
-- Automation System Database Schema
-- ===========================================
-- PostgreSQL 15+
-- ===========================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For fuzzy text search

-- ===========================================
-- ENUM Types
-- ===========================================

CREATE TYPE business_status AS ENUM (
    'discovered',
    'analyzing',
    'qualified',
    'low_priority',
    'generating',
    'generated',
    'deploying',
    'deployed',
    'ready_for_outreach',
    'contacted',
    'responded',
    'converted',
    'rejected',
    'archived'
);

CREATE TYPE outreach_channel AS ENUM (
    'email',
    'whatsapp',
    'both',
    'manual'
);

CREATE TYPE outreach_status AS ENUM (
    'pending',
    'scheduled',
    'sent',
    'delivered',
    'opened',
    'clicked',
    'responded',
    'converted',
    'bounced',
    'failed',
    'unsubscribed'
);

CREATE TYPE conversion_type AS ENUM (
    'lead',
    'trial',
    'starter',
    'professional',
    'business',
    'custom'
);

CREATE TYPE event_type AS ENUM (
    'email_sent',
    'email_delivered',
    'email_opened',
    'email_clicked',
    'email_bounced',
    'whatsapp_sent',
    'whatsapp_delivered',
    'whatsapp_read',
    'website_visit',
    'form_submit',
    'response_received'
);

-- ===========================================
-- Core Tables
-- ===========================================

-- Businesses Table (Main entity)
CREATE TABLE businesses (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Google Maps Data
    google_place_id VARCHAR(255) UNIQUE,
    name VARCHAR(255) NOT NULL,
    normalized_name VARCHAR(255),  -- For deduplication
    
    -- Category
    primary_category VARCHAR(100),
    secondary_category VARCHAR(100),
    google_category VARCHAR(255),  -- Original from Google
    
    -- Location
    address TEXT,
    street_address VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(100),
    postal_code VARCHAR(20),
    country VARCHAR(100) DEFAULT 'México',
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    
    -- Contact
    phone VARCHAR(50),
    phone_normalized VARCHAR(20),  -- Digits only
    email VARCHAR(255),
    
    -- Google Maps Metrics
    rating DECIMAL(2, 1),
    review_count INTEGER DEFAULT 0,
    photo_count INTEGER DEFAULT 0,
    
    -- Media
    photo_urls TEXT[],
    logo_url VARCHAR(500),
    cover_photo_url VARCHAR(500),
    
    -- Website Detection
    has_website BOOLEAN DEFAULT FALSE,
    existing_website VARCHAR(500),
    website_status VARCHAR(50),  -- 'none', 'facebook_only', 'broken', 'active'
    
    -- Business Hours (JSON)
    hours JSONB,
    
    -- Scoring
    score INTEGER DEFAULT 0,
    score_breakdown JSONB,
    
    -- Processing
    status business_status DEFAULT 'discovered',
    status_history JSONB DEFAULT '[]',
    
    -- Metadata
    source VARCHAR(50) DEFAULT 'google_maps',
    raw_data JSONB,
    
    -- Timestamps
    discovered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    analyzed_at TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Soft delete
    is_active BOOLEAN DEFAULT TRUE,
    archived_at TIMESTAMP,
    archive_reason VARCHAR(255)
);

-- Websites Table (Generated websites)
CREATE TABLE websites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    
    -- Template
    template_id VARCHAR(100),
    template_name VARCHAR(255),
    template_category VARCHAR(100),
    
    -- Generated Content
    generated_html TEXT,
    generated_css TEXT,
    generated_js TEXT,
    
    -- AI Generated Copy
    hero_headline VARCHAR(255),
    hero_subtitle TEXT,
    about_text TEXT,
    services_list JSONB,
    cta_text VARCHAR(255),
    meta_title VARCHAR(255),
    meta_description TEXT,
    
    -- Assets
    assets JSONB,  -- List of downloaded/processed images
    
    -- Deployment - GitHub
    github_repo VARCHAR(255),
    github_pages_url VARCHAR(500),
    github_deployed_at TIMESTAMP,
    
    -- Deployment - Vercel (backup)
    vercel_project_id VARCHAR(255),
    vercel_url VARCHAR(500),
    vercel_deployed_at TIMESTAMP,
    
    -- Deployment - Netlify (backup)
    netlify_site_id VARCHAR(255),
    netlify_url VARCHAR(500),
    netlify_deployed_at TIMESTAMP,
    
    -- Active URL
    preview_url VARCHAR(500),
    custom_domain VARCHAR(255),
    ssl_status VARCHAR(50),
    
    -- Screenshots
    desktop_screenshot_url VARCHAR(500),
    mobile_screenshot_url VARCHAR(500),
    tablet_screenshot_url VARCHAR(500),
    mockup_image_url VARCHAR(500),
    combined_preview_url VARCHAR(500),
    
    -- Status
    status VARCHAR(50) DEFAULT 'generating',
    error_message TEXT,
    
    -- Metrics
    generation_time_ms INTEGER,
    deployment_time_ms INTEGER,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    deployed_at TIMESTAMP,
    last_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    
    -- Versioning
    version INTEGER DEFAULT 1,
    previous_version_id UUID REFERENCES websites(id)
);

-- Outreach Campaigns Table
CREATE TABLE outreach_campaigns (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    website_id UUID REFERENCES websites(id) ON DELETE SET NULL,
    
    -- Campaign Details
    campaign_name VARCHAR(255),
    channel outreach_channel DEFAULT 'email',
    
    -- Email Content
    email_subject VARCHAR(255),
    email_body TEXT,
    email_html TEXT,
    email_attachments JSONB,
    
    -- WhatsApp Content
    whatsapp_message TEXT,
    whatsapp_media_urls TEXT[],
    
    -- Tracking
    tracking_id VARCHAR(100) UNIQUE DEFAULT uuid_generate_v4()::text,
    tracking_pixel_url VARCHAR(500),
    
    -- Recipient Info
    recipient_email VARCHAR(255),
    recipient_phone VARCHAR(50),
    recipient_name VARCHAR(255),
    
    -- Delivery
    status outreach_status DEFAULT 'pending',
    scheduled_at TIMESTAMP,
    sent_at TIMESTAMP,
    delivered_at TIMESTAMP,
    
    -- Engagement
    opened_at TIMESTAMP,
    open_count INTEGER DEFAULT 0,
    clicked_at TIMESTAMP,
    click_count INTEGER DEFAULT 0,
    responded_at TIMESTAMP,
    
    -- Response
    response_type VARCHAR(50),
    response_content TEXT,
    
    -- Follow-ups
    follow_up_count INTEGER DEFAULT 0,
    last_follow_up_at TIMESTAMP,
    next_follow_up_at TIMESTAMP,
    max_follow_ups INTEGER DEFAULT 2,
    
    -- A/B Testing
    variant VARCHAR(50),
    ab_test_id UUID,
    
    -- External IDs
    email_provider_id VARCHAR(255),  -- Resend message ID
    twilio_message_sid VARCHAR(255),
    
    -- Error Handling
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tracking Events Table
CREATE TABLE tracking_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    campaign_id UUID REFERENCES outreach_campaigns(id) ON DELETE CASCADE,
    business_id UUID REFERENCES businesses(id) ON DELETE CASCADE,
    website_id UUID REFERENCES websites(id) ON DELETE SET NULL,
    
    -- Event Details
    event_type event_type NOT NULL,
    event_name VARCHAR(100),
    event_data JSONB,
    
    -- Source
    source VARCHAR(50),  -- 'email', 'whatsapp', 'website', 'api'
    
    -- Client Info
    ip_address VARCHAR(45),
    user_agent TEXT,
    referer VARCHAR(500),
    
    -- Geo (from IP)
    geo_country VARCHAR(100),
    geo_city VARCHAR(100),
    
    -- Device Info
    device_type VARCHAR(50),
    browser VARCHAR(100),
    os VARCHAR(100),
    
    -- Timestamp
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Conversions Table
CREATE TABLE conversions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    business_id UUID NOT NULL REFERENCES businesses(id) ON DELETE CASCADE,
    campaign_id UUID REFERENCES outreach_campaigns(id) ON DELETE SET NULL,
    website_id UUID REFERENCES websites(id) ON DELETE SET NULL,
    
    -- Conversion Details
    conversion_type conversion_type NOT NULL,
    plan_name VARCHAR(100),
    
    -- Revenue
    revenue_amount DECIMAL(10, 2),
    currency VARCHAR(3) DEFAULT 'MXN',
    payment_method VARCHAR(50),
    
    -- Subscription
    subscription_start TIMESTAMP,
    subscription_end TIMESTAMP,
    is_recurring BOOLEAN DEFAULT TRUE,
    
    -- Client Info
    client_name VARCHAR(255),
    client_email VARCHAR(255),
    client_phone VARCHAR(50),
    
    -- Notes
    notes TEXT,
    
    -- Attribution
    attribution_source VARCHAR(100),
    attribution_campaign UUID,
    
    -- Status
    status VARCHAR(50) DEFAULT 'active',
    cancelled_at TIMESTAMP,
    cancellation_reason TEXT,
    
    -- Timestamps
    converted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Templates Table (Website templates)
CREATE TABLE templates (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    
    -- Files
    html_template TEXT NOT NULL,
    css_styles TEXT,
    js_scripts TEXT,
    
    -- Preview
    preview_image_url VARCHAR(500),
    preview_url VARCHAR(500),
    
    -- Configuration
    variables JSONB,  -- Required template variables
    config JSONB,     -- Template-specific config
    
    -- Metadata
    author VARCHAR(255),
    version VARCHAR(20) DEFAULT '1.0.0',
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    is_premium BOOLEAN DEFAULT FALSE,
    
    -- Stats
    usage_count INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Locations Table (Target locations for scraping)
CREATE TABLE locations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Location
    name VARCHAR(255) NOT NULL,
    city VARCHAR(100),
    state VARCHAR(100),
    country VARCHAR(100) DEFAULT 'México',
    
    -- Coordinates (center point)
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    radius_km INTEGER DEFAULT 10,
    
    -- Scraping Config
    categories_to_scrape TEXT[],
    priority INTEGER DEFAULT 1,
    
    -- Stats
    businesses_found INTEGER DEFAULT 0,
    last_scraped_at TIMESTAMP,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Categories Table (Business categories)
CREATE TABLE categories (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    name_es VARCHAR(255),  -- Spanish name
    
    -- Hierarchy
    parent_id VARCHAR(100) REFERENCES categories(id),
    
    -- Scraping
    google_search_terms TEXT[],
    
    -- Scoring
    conversion_weight DECIMAL(3, 2) DEFAULT 1.0,
    
    -- Template
    default_template_id VARCHAR(100) REFERENCES templates(id),
    
    -- Stats
    businesses_count INTEGER DEFAULT 0,
    
    -- Status
    is_active BOOLEAN DEFAULT TRUE
);

-- Jobs Table (Background job tracking)
CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    
    -- Job Info
    job_type VARCHAR(100) NOT NULL,
    job_name VARCHAR(255),
    
    -- Input
    input_data JSONB,
    
    -- Status
    status VARCHAR(50) DEFAULT 'pending',
    progress INTEGER DEFAULT 0,
    
    -- Output
    output_data JSONB,
    error_message TEXT,
    
    -- Timing
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    
    -- Worker
    worker_id VARCHAR(100),
    
    -- Timestamps
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ===========================================
-- Indexes
-- ===========================================

-- Businesses indexes
CREATE INDEX idx_businesses_status ON businesses(status);
CREATE INDEX idx_businesses_score ON businesses(score DESC);
CREATE INDEX idx_businesses_city ON businesses(city);
CREATE INDEX idx_businesses_category ON businesses(primary_category);
CREATE INDEX idx_businesses_discovered_at ON businesses(discovered_at DESC);
CREATE INDEX idx_businesses_normalized_name ON businesses USING gin(normalized_name gin_trgm_ops);
CREATE INDEX idx_businesses_active ON businesses(is_active) WHERE is_active = TRUE;

-- Websites indexes
CREATE INDEX idx_websites_business ON websites(business_id);
CREATE INDEX idx_websites_status ON websites(status);
CREATE INDEX idx_websites_preview_url ON websites(preview_url);
CREATE INDEX idx_websites_created ON websites(created_at DESC);

-- Outreach indexes
CREATE INDEX idx_outreach_business ON outreach_campaigns(business_id);
CREATE INDEX idx_outreach_status ON outreach_campaigns(status);
CREATE INDEX idx_outreach_tracking ON outreach_campaigns(tracking_id);
CREATE INDEX idx_outreach_scheduled ON outreach_campaigns(scheduled_at) WHERE status = 'scheduled';
CREATE INDEX idx_outreach_follow_up ON outreach_campaigns(next_follow_up_at) WHERE next_follow_up_at IS NOT NULL;

-- Tracking indexes
CREATE INDEX idx_tracking_campaign ON tracking_events(campaign_id);
CREATE INDEX idx_tracking_business ON tracking_events(business_id);
CREATE INDEX idx_tracking_type ON tracking_events(event_type);
CREATE INDEX idx_tracking_created ON tracking_events(created_at DESC);

-- Conversions indexes
CREATE INDEX idx_conversions_business ON conversions(business_id);
CREATE INDEX idx_conversions_type ON conversions(conversion_type);
CREATE INDEX idx_conversions_date ON conversions(converted_at DESC);

-- Jobs indexes
CREATE INDEX idx_jobs_type ON jobs(job_type);
CREATE INDEX idx_jobs_status ON jobs(status);
CREATE INDEX idx_jobs_created ON jobs(created_at DESC);

-- ===========================================
-- Functions
-- ===========================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Function to normalize business name for deduplication
CREATE OR REPLACE FUNCTION normalize_business_name(name TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN LOWER(
        REGEXP_REPLACE(
            REGEXP_REPLACE(name, '[^a-zA-Z0-9áéíóúñü\s]', '', 'g'),
            '\s+', ' ', 'g'
        )
    );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function to normalize phone number
CREATE OR REPLACE FUNCTION normalize_phone(phone TEXT)
RETURNS TEXT AS $$
BEGIN
    RETURN REGEXP_REPLACE(phone, '[^0-9]', '', 'g');
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- ===========================================
-- Triggers
-- ===========================================

-- Auto-update timestamps
CREATE TRIGGER update_businesses_timestamp
    BEFORE UPDATE ON businesses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_websites_timestamp
    BEFORE UPDATE ON websites
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_outreach_timestamp
    BEFORE UPDATE ON outreach_campaigns
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_jobs_timestamp
    BEFORE UPDATE ON jobs
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Auto-normalize business name
CREATE OR REPLACE FUNCTION set_normalized_name()
RETURNS TRIGGER AS $$
BEGIN
    NEW.normalized_name = normalize_business_name(NEW.name);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER normalize_business_name_trigger
    BEFORE INSERT OR UPDATE OF name ON businesses
    FOR EACH ROW
    EXECUTE FUNCTION set_normalized_name();

-- Auto-normalize phone
CREATE OR REPLACE FUNCTION set_normalized_phone()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.phone IS NOT NULL THEN
        NEW.phone_normalized = normalize_phone(NEW.phone);
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER normalize_phone_trigger
    BEFORE INSERT OR UPDATE OF phone ON businesses
    FOR EACH ROW
    EXECUTE FUNCTION set_normalized_phone();

-- ===========================================
-- Views
-- ===========================================

-- View: Businesses ready for outreach
CREATE VIEW v_ready_for_outreach AS
SELECT 
    b.id,
    b.name,
    b.city,
    b.phone,
    b.email,
    b.score,
    b.primary_category,
    w.preview_url,
    w.mockup_image_url
FROM businesses b
JOIN websites w ON w.business_id = b.id
WHERE b.status = 'ready_for_outreach'
  AND b.is_active = TRUE
  AND w.status = 'deployed'
  AND NOT EXISTS (
      SELECT 1 FROM outreach_campaigns oc 
      WHERE oc.business_id = b.id 
        AND oc.sent_at > NOW() - INTERVAL '30 days'
  )
ORDER BY b.score DESC;

-- View: Campaign performance
CREATE VIEW v_campaign_performance AS
SELECT 
    DATE(oc.sent_at) as date,
    COUNT(*) as sent,
    COUNT(*) FILTER (WHERE oc.opened_at IS NOT NULL) as opened,
    COUNT(*) FILTER (WHERE oc.clicked_at IS NOT NULL) as clicked,
    COUNT(*) FILTER (WHERE oc.responded_at IS NOT NULL) as responded,
    COUNT(*) FILTER (WHERE c.id IS NOT NULL) as converted,
    ROUND(100.0 * COUNT(*) FILTER (WHERE oc.opened_at IS NOT NULL) / NULLIF(COUNT(*), 0), 2) as open_rate,
    ROUND(100.0 * COUNT(*) FILTER (WHERE oc.clicked_at IS NOT NULL) / NULLIF(COUNT(*), 0), 2) as click_rate,
    ROUND(100.0 * COUNT(*) FILTER (WHERE oc.responded_at IS NOT NULL) / NULLIF(COUNT(*), 0), 2) as response_rate
FROM outreach_campaigns oc
LEFT JOIN conversions c ON c.campaign_id = oc.id
WHERE oc.sent_at IS NOT NULL
GROUP BY DATE(oc.sent_at)
ORDER BY date DESC;

-- View: Pipeline funnel
CREATE VIEW v_pipeline_funnel AS
SELECT
    'discovered' as stage,
    1 as stage_order,
    COUNT(*) as count
FROM businesses WHERE status = 'discovered'
UNION ALL
SELECT 'qualified', 2, COUNT(*) FROM businesses WHERE status = 'qualified'
UNION ALL
SELECT 'generated', 3, COUNT(*) FROM businesses WHERE status IN ('generated', 'deploying', 'deployed')
UNION ALL
SELECT 'ready_for_outreach', 4, COUNT(*) FROM businesses WHERE status = 'ready_for_outreach'
UNION ALL
SELECT 'contacted', 5, COUNT(*) FROM businesses WHERE status = 'contacted'
UNION ALL
SELECT 'responded', 6, COUNT(*) FROM businesses WHERE status = 'responded'
UNION ALL
SELECT 'converted', 7, COUNT(*) FROM businesses WHERE status = 'converted'
ORDER BY stage_order;

-- ===========================================
-- Initial Data
-- ===========================================

-- Insert default categories
INSERT INTO categories (id, name, name_es, google_search_terms, conversion_weight) VALUES
('restaurant', 'Restaurant', 'Restaurante', ARRAY['restaurantes', 'comida', 'food'], 1.2),
('cafe', 'Café', 'Cafetería', ARRAY['cafetería', 'café', 'coffee'], 1.1),
('salon', 'Hair Salon', 'Salón de Belleza', ARRAY['salón de belleza', 'estética', 'peluquería'], 1.3),
('barber', 'Barber Shop', 'Barbería', ARRAY['barbería', 'barber'], 1.2),
('gym', 'Gym', 'Gimnasio', ARRAY['gimnasio', 'gym', 'fitness'], 1.0),
('dental', 'Dental Clinic', 'Clínica Dental', ARRAY['dentista', 'dental', 'odontología'], 1.4),
('medical', 'Medical Clinic', 'Clínica Médica', ARRAY['clínica', 'médico', 'doctor'], 1.3),
('automotive', 'Auto Shop', 'Taller Mecánico', ARRAY['taller mecánico', 'mecánico', 'automotriz'], 1.1),
('retail', 'Retail Store', 'Tienda', ARRAY['tienda', 'boutique', 'store'], 1.0),
('bakery', 'Bakery', 'Panadería', ARRAY['panadería', 'bakery', 'pastelería'], 1.1),
('pharmacy', 'Pharmacy', 'Farmacia', ARRAY['farmacia', 'pharmacy'], 0.8),
('real_estate', 'Real Estate', 'Inmobiliaria', ARRAY['inmobiliaria', 'bienes raíces'], 1.5),
('legal', 'Law Firm', 'Despacho Legal', ARRAY['abogado', 'legal', 'notaría'], 1.4),
('accounting', 'Accounting', 'Contabilidad', ARRAY['contador', 'contabilidad'], 1.3),
('veterinary', 'Veterinary', 'Veterinaria', ARRAY['veterinaria', 'veterinario'], 1.2),
('pet_store', 'Pet Store', 'Tienda de Mascotas', ARRAY['mascotas', 'pet shop'], 1.0),
('florist', 'Florist', 'Florería', ARRAY['florería', 'flores'], 1.0),
('laundry', 'Laundry', 'Lavandería', ARRAY['lavandería', 'laundry', 'tintorería'], 0.9),
('hotel', 'Hotel', 'Hotel', ARRAY['hotel', 'hospedaje'], 1.2),
('spa', 'Spa', 'Spa', ARRAY['spa', 'masajes'], 1.3)
ON CONFLICT (id) DO NOTHING;

-- Insert default locations (Mexico major cities)
INSERT INTO locations (name, city, state, country, latitude, longitude, radius_km, priority, categories_to_scrape) VALUES
('Ciudad de México Centro', 'Ciudad de México', 'CDMX', 'México', 19.4326, -99.1332, 15, 1, ARRAY['restaurant', 'salon', 'dental', 'retail']),
('Guadalajara Centro', 'Guadalajara', 'Jalisco', 'México', 20.6597, -103.3496, 12, 2, ARRAY['restaurant', 'salon', 'dental', 'retail']),
('Monterrey Centro', 'Monterrey', 'Nuevo León', 'México', 25.6866, -100.3161, 12, 2, ARRAY['restaurant', 'salon', 'dental', 'retail']),
('Puebla Centro', 'Puebla', 'Puebla', 'México', 19.0414, -98.2063, 10, 3, ARRAY['restaurant', 'salon', 'retail']),
('Tijuana Centro', 'Tijuana', 'Baja California', 'México', 32.5149, -117.0382, 10, 3, ARRAY['restaurant', 'salon', 'retail'])
ON CONFLICT DO NOTHING;
