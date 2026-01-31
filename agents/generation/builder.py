"""
Generation Agent - Premium Website Builder v2.0
Creates agency-quality, $150+ landing pages for businesses

Design Philosophy:
- High-contrast, visually stunning designs
- Stock imagery for heroes (Unsplash), Google photos for gallery only
- Category-specific theming with proper color psychology
- Mobile-first responsive design with micro-interactions
- SEO-optimized with Schema.org markup

Usage:
    python -m agents.generation.builder --preview          # Launch preview server
    python -m agents.generation.builder --generate-all N   # Generate N sites
    python -m agents.generation.builder --intake-file path/to/intake.json
"""

import json
import os
import re
import shutil
import glob
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import quote_plus

from flask import Flask, render_template, send_from_directory
from jinja2 import Environment, FileSystemLoader

# Import the CopyWriter for rich content generation
from agents.generation.copy_writer import CopyWriter

# Import the new theme configuration system
from agents.generation.theme_config import (
    THEMES,
    FALLBACK_IMAGES,
    SERVICE_ICONS,
    CATEGORY_FEATURES,
    get_theme_for_category,
    get_fallback_images,
    get_service_icon,
)


# ===========================================
# CONFIGURATION
# ===========================================


BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "generated_sites"
DATA_FILE = BASE_DIR / "datos_definitivos_final.json"  # Usar solo negocios filtrados y limpios
INTAKE_DATA_DIR = BASE_DIR / "intake_data"

# Template to use for generation (premium template)
PREMIUM_TEMPLATE = "landing/premium.html"


# ===========================================
# DATA CLASSES
# ===========================================

@dataclass
class BusinessData:
    """Structured business data for premium template rendering"""
    name: str
    category: str
    address: str
    city: str
    phone: str
    rating: float
    review_count: int
    photo_urls: list
    latitude: float
    longitude: float
    # New fields from datos_definitivos.json
    about_summary: str = ""
    plus_code: str = ""
    website_url: str = ""
    has_website: bool = False
    opening_hours: dict = field(default_factory=dict)
    review_topics: dict = field(default_factory=dict)
    rating_distribution: dict = field(default_factory=dict)
    reviews: list = field(default_factory=list)
    social_media: dict = field(default_factory=dict)
    # Generated content
    headline: str = ""
    tagline: str = ""
    description: str = ""
    backstory: str = ""
    features: list = field(default_factory=list)
    services: list = field(default_factory=list)
    customer_promise: str = ""
    faqs: list = field(default_factory=list)
    cta_text: str = "Reservar Ahora"
    # Intake data - Client personalization
    intake_data: dict = field(default_factory=dict)
    brand_colors: dict = field(default_factory=dict)
    business_identity: dict = field(default_factory=dict)
    custom_services: list = field(default_factory=list)
    promotions: list = field(default_factory=list)
    loyalty_program: str = ""
    contact_preferences: dict = field(default_factory=dict)
    logo_url: str = ""
    custom_photos: list = field(default_factory=list)
    video_url: str = ""
    # Computed fields
    whatsapp_link: str = ""
    phone_link: str = ""
    maps_embed_url: str = ""
    street_view_url: str = ""
    hero_image: str = ""
    gallery_images: list = field(default_factory=list)
    theme: dict = field(default_factory=dict)
    custom_css: str = ""
    def __post_init__(self):
        self._apply_intake_data()
        self._compute_links()
        self._select_theme()
        self._apply_custom_colors()
        self._select_hero_image()
        self._prepare_gallery()
        self._generate_content()
        self._select_features()
        self._set_default_hours()
    
    def _apply_intake_data(self):
        """Apply intake form data to business properties"""
        if not self.intake_data:
            return
        
        # Brand colors
        self.brand_colors = self.intake_data.get('brand_colors', {})
        
        # Business identity (vision, mission, values, etc.)
        self.business_identity = self.intake_data.get('business_identity', {})
        
        # Custom services from intake
        self.custom_services = self.intake_data.get('custom_services', [])
        
        # Promotions
        offers = self.intake_data.get('special_offers', {})
        self.promotions = offers.get('current_promotions', [])
        self.loyalty_program = offers.get('loyalty_program', '')
        
        # Media assets
        media = self.intake_data.get('media_assets', {})
        self.logo_url = media.get('logo_url') or ''
        self.custom_photos = media.get('custom_photos', [])
        self.video_url = media.get('video_url') or ''
        
        # Social media
        self.social_media = {
            'instagram': media.get('instagram_handle') or '',
            'facebook': media.get('facebook_page') or '',
            'tiktok': media.get('tiktok_handle') or '',
        }
        
        # Contact preferences
        self.contact_preferences = self.intake_data.get('contact_preferences', {})
        
        # Override phone with WhatsApp number if provided
        if self.contact_preferences.get('whatsapp_number'):
            self.phone = self.contact_preferences['whatsapp_number']
        
        # Opening hours
        self.opening_hours = self.intake_data.get('opening_hours', {})
    
    def _set_default_hours(self):
        """Set default opening hours if not provided"""
        if not self.opening_hours:
            self.opening_hours = {
                'monday': {'open': '08:00', 'close': '18:00'},
                'tuesday': {'open': '08:00', 'close': '18:00'},
                'wednesday': {'open': '08:00', 'close': '18:00'},
                'thursday': {'open': '08:00', 'close': '18:00'},
                'friday': {'open': '08:00', 'close': '18:00'},
                'saturday': {'open': '09:00', 'close': '13:00'},
                'sunday': None,  # Closed
            }
    
    def _apply_custom_colors(self):
        """Generate custom CSS variables from brand colors"""
        if not self.brand_colors:
            return
        
        primary = self.brand_colors.get('primary', '')
        secondary = self.brand_colors.get('secondary', '')
        accent = self.brand_colors.get('accent', '')
        
        if primary or secondary or accent:
            self.custom_css = f"""
    :root {{
        --color-primary: {primary or '#2563eb'};
        --color-secondary: {secondary or '#7c3aed'};
        --color-accent: {accent or '#f59e0b'};
    }}
    
    /* Brand Color Utility Classes */
    .btn-custom {{ background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)) !important; }}
    .text-custom-primary {{ color: var(--color-primary) !important; }}
    .text-custom-accent {{ color: var(--color-accent) !important; }}
    .border-custom {{ border-color: var(--color-primary) !important; }}
    .bg-custom-gradient {{ background: linear-gradient(135deg, var(--color-primary), var(--color-secondary)) !important; }}
    """
    
    def _compute_links(self):
        """Generate WhatsApp, phone, y link a Google Maps"""
        phone_clean = re.sub(r'[^0-9+]', '', self.phone or '')
        if phone_clean and not phone_clean.startswith('+'):
            phone_clean = '+595' + phone_clean.lstrip('0')
        message = f"Hola, vi su página web y me gustaría más información sobre {self.name}"
        self.whatsapp_link = f"https://wa.me/{phone_clean}?text={quote_plus(message)}"
        self.phone_link = f"tel:{phone_clean}"
        # Generar link directo a Google Maps
        plus_code = getattr(self, 'plus_code', None)
        address = getattr(self, 'address', None)
        if plus_code:
            self.google_maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(plus_code)}"
        elif address:
            self.google_maps_url = f"https://www.google.com/maps/search/?api=1&query={quote_plus(address)}"
        else:
            self.google_maps_url = "https://www.google.com/maps"
    
    def _select_theme(self):
        """Select theme configuration using the new theme system"""
        self.theme = get_theme_for_category(self.category)
    
    def _select_hero_image(self):
        """Select Unsplash stock hero image based on category"""
        images = get_fallback_images(self.category)
        self.hero_image = images.get('hero', FALLBACK_IMAGES['default']['hero'])
    
    def _prepare_gallery(self):
        """Prepare gallery images - solo las fotos ya filtradas en el JSON limpio"""
        gallery = []
        # Solo usar las fotos que ya están filtradas
        if self.custom_photos:
            gallery.extend(self.custom_photos[:4])
        if self.photo_urls:
            gallery.extend(self.photo_urls[:4])
        self.gallery_images = gallery[:4]
    
    def _generate_content(self):
        """Generate fallback content if not provided"""
        # Priority: Intake vision > backstory > generated
        if self.business_identity.get('vision') and not self.tagline:
            self.tagline = self.business_identity['vision']
        
        # Use founding story or backstory as description
        if self.business_identity.get('founding_story'):
            self.description = self.business_identity['founding_story']
        elif self.backstory and not self.description:
            self.description = self.backstory
        
        if not self.headline:
            self.headline = self.name
        
        if not self.tagline:
            taglines = {
                "parrilla": "El auténtico sabor del asado paraguayo",
                "dentista": "Tu sonrisa en las mejores manos",
                "odontología": "Cuidamos tu salud dental",
                "barbería": "Donde el estilo se encuentra con la tradición",
                "peluquería": "Tu belleza, nuestra pasión",
                "spa": "Tu refugio de paz y bienestar",
                "gimnasio": "Transforma tu cuerpo, transforma tu vida",
                "veterinaria": "Cuidamos a quienes más quieres",
                "restaurante": "Una experiencia gastronómica única",
                "taller": "Tu vehículo en manos expertas",
                "cafetería": "El mejor café de la ciudad",
                "panadería": "Horneando felicidad cada día",
            }
            category_lower = (self.category or '').lower()
            for key, tagline in taglines.items():
                if key in category_lower:
                    self.tagline = tagline
                    break
            else:
                self.tagline = f"Excelencia en {self.category or 'servicios'} en {self.city}"
        
        if not self.description:
            self.description = (
                f"En {self.name} nos dedicamos a ofrecer el mejor servicio de {self.category or 'la zona'} "
                f"en {self.city}. Con años de experiencia y un equipo comprometido, garantizamos "
                f"una experiencia excepcional para cada uno de nuestros clientes."
            )
        
        # Add mission if available
        if self.business_identity.get('mission'):
            self.customer_promise = self.business_identity['mission']
    
    def _select_features(self):
        """Select features - prioritizing custom services from intake"""
        # Priority 1: Custom services from intake form
        if self.custom_services:
            self.features = [
                {
                    "icon": get_service_icon(s.get("name", "")),
                    "title": s.get("name", "Servicio"),
                    "desc": s.get("description", "")[:100],
                    "price": s.get("price", "")
                }
                for s in self.custom_services[:6]
            ]
            return
        
        # Priority 2: Services from CopyWriter
        if self.services:
            self.features = [
                {
                    "icon": get_service_icon(s.get("title", "")),
                    "title": s["title"],
                    "desc": s["description"][:100]
                }
                for s in self.services[:4]
            ]
            return
        
        # Priority 3: Category-based default features
        category_lower = (self.category or '').lower()
        
        for key, features in CATEGORY_FEATURES.items():
            if key in category_lower:
                self.features = features
                return
        
        self.features = CATEGORY_FEATURES.get("default", [])


# ===========================================
# FLASK APP
# ===========================================

def create_app(business: BusinessData = None) -> Flask:
    """Create Flask application for preview and generation"""
    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_DIR),
        static_folder=str(TEMPLATES_DIR / "static"),
    )
    
    app.config['business'] = business
    
    @app.route('/')
    def index():
        biz = app.config.get('business')
        if not biz:
            return "No business data loaded", 404
        
        # Use the new premium template
        return render_template(
            PREMIUM_TEMPLATE,
            business=biz,
            theme=biz.theme,
        )
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(str(TEMPLATES_DIR / "static"), filename)
    
    return app


# ===========================================
# LEAD DATA LOADING
# ===========================================

def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:50]


def load_leads() -> list:
    """Load businesses from datos_definitivos.json"""
    if not DATA_FILE.exists():
        return []
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_intake_data(filepath: Path = None, business_name: str = None, google_place_id: str = None) -> Optional[dict]:
    """
    Load intake form data for a business.
    
    Args:
        filepath: Direct path to intake JSON file
        business_name: Business name to search for
        google_place_id: Google Place ID to search for
    
    Returns:
        Intake data dict or None if not found
    """
    if filepath:
        if filepath.exists():
            with open(filepath, 'r', encoding='utf-8') as f:
                return json.load(f)
        return None
    
    if not INTAKE_DATA_DIR.exists():
        return None
    
    # Search by google_place_id first (most accurate)
    if google_place_id:
        for intake_file in INTAKE_DATA_DIR.glob("*.json"):
            try:
                with open(intake_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if data.get('business_id') == google_place_id:
                        return data
            except:
                continue
    
    # Fallback: search by business name
    if business_name:
        safe_name = slugify(business_name)
        matches = list(INTAKE_DATA_DIR.glob(f"*{safe_name}*.json"))
        
        if matches:
            latest = max(matches, key=lambda p: p.stat().st_mtime)
            with open(latest, 'r', encoding='utf-8') as f:
                return json.load(f)
    
    return None


def find_lead_by_name(name: str) -> Optional[dict]:
    """Find a lead by business name (partial match)"""
    leads = load_leads()
    name_lower = name.lower()
    
    for lead in leads:
        if name_lower in lead.get('name', '').lower():
            return lead
    
    return None


def find_lead_by_google_id(google_place_id: str) -> Optional[dict]:
    """Find a lead by Google Place ID"""
    leads = load_leads()
    
    for lead in leads:
        if lead.get('google_place_id') == google_place_id:
            return lead
    
    return None


# Global CopyWriter instance
_copy_writer = None

def get_copy_writer() -> CopyWriter:
    """Get or create the global CopyWriter instance"""
    global _copy_writer
    if _copy_writer is None:
        _copy_writer = CopyWriter()
    return _copy_writer


def create_business_from_lead(lead: dict, intake_data: dict = None) -> BusinessData:
    """
    Convert a business dict from datos_definitivos.json to BusinessData object with rich content.
    """
    address = lead.get('address') or ''
    phone = lead.get('phone') or ''
    writer = get_copy_writer()
    content = writer.generate_content(lead)
    if not intake_data:
        intake_data = load_intake_data(business_name=lead.get('name'))
    return BusinessData(
        name=lead.get('name') or 'Mi Negocio',
        category=lead.get('category') or '',
        address=address.strip().lstrip('\n') if address else '',
        city=lead.get('city') or 'Asunción',
        phone=phone.strip().lstrip('\n') if phone else '',
        rating=lead.get('rating') or 0,
        review_count=lead.get('review_count') or lead.get('user_ratings_total') or 0,
        photo_urls=lead.get('photo_urls') or [],
        latitude=lead.get('latitude') or -25.2867,
        longitude=lead.get('longitude') or -57.647,
        about_summary=lead.get('about_summary', ''),
        plus_code=lead.get('plus_code', ''),
        website_url=lead.get('website_url', ''),
        has_website=lead.get('has_website', False),
        opening_hours=lead.get('opening_hours', {}),
        review_topics=lead.get('review_topics', {}),
        rating_distribution=lead.get('rating_distribution', {}),
        reviews=lead.get('reviews', []),
        social_media=lead.get('social_media', {}),
        # Rich content from CopyWriter
        headline=content.get('headline', ''),
        tagline=content.get('tagline', ''),
        backstory=content.get('backstory', ''),
        services=content.get('services', []),
        customer_promise=content.get('customer_promise', ''),
        faqs=content.get('faqs', []),
        cta_text=content.get('cta_text', 'Contáctanos'),
        # Intake data for personalization
        intake_data=intake_data or {},
    )


def create_business_from_intake(intake_filepath: Path) -> BusinessData:
    """
    Create BusinessData primarily from intake form.
    
    Args:
        intake_filepath: Path to intake JSON file
    
    Returns:
        BusinessData object with intake data as primary source
    """
    with open(intake_filepath, 'r', encoding='utf-8') as f:
        intake_data = json.load(f)
    
    business_name = intake_data.get('business_name', '')
    google_place_id = intake_data.get('business_id')
    
    # Try to find matching lead data
    lead = None
    if google_place_id:
        lead = find_lead_by_google_id(google_place_id)
    
    if not lead and business_name:
        lead = find_lead_by_name(business_name)
    
    if lead:
        return create_business_from_lead(lead, intake_data)
    else:
        # Create from intake only
        return BusinessData(
            name=business_name or 'Mi Negocio',
            category=intake_data.get('category', ''),
            address='',
            city='Asunción',
            phone='',
            rating=0,
            review_count=0,
            photo_urls=[],
            latitude=-25.2867,
            longitude=-57.647,
            intake_data=intake_data,
        )


# ===========================================
# STATIC SITE GENERATION
# ===========================================

def generate_static_site(business: BusinessData, output_path: Path) -> Path:
    """Generate a static HTML site for a business"""
    output_path.mkdir(parents=True, exist_ok=True)
    
    app = create_app(business)
    
    with app.app_context():
        html_content = render_template(
            PREMIUM_TEMPLATE,
            business=business,
            theme=business.theme,
        )
    
    index_file = output_path / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    return output_path


def generate_all_sites(limit: int = None) -> int:
    """Generate static sites for all leads"""
    leads = load_leads()
    
    if limit:
        leads = leads[:limit]
    
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    
    for i, lead in enumerate(leads):
        try:
            business = create_business_from_lead(lead)
            slug = slugify(business.name)
            output_path = OUTPUT_DIR / f"{i:04d}-{slug}"
            
            generate_static_site(business, output_path)
            print(f"✅ Generated: {business.name} → {output_path}")
            
        except Exception as e:
            print(f"❌ Error generating {lead.get('name', 'Unknown')}: {e}")
    
    print(f"\n✅ Generated {len(leads)} sites in {OUTPUT_DIR}")
    return len(leads)


# ===========================================
# CLI
# ===========================================

def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Generate premium landing pages for businesses',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Preview a business by index
  python -m agents.generation.builder --preview --business-id 0x945da89f7ce6aed5:0
  
  # Generate site using intake form data
  python -m agents.generation.builder --intake-file intake_data/intake_maison-mint.json
  
  # Generate and preview with intake data
  python -m agents.generation.builder --intake-file intake_data/example.json --preview
  
  # Generate all sites (first N)
  python -m agents.generation.builder --generate-all 10
        """
    )
    parser.add_argument('--preview', action='store_true', help='Launch preview server')
    parser.add_argument('--generate-all', type=int, metavar='N', help='Generate N static sites')
    parser.add_argument('--generate', action='store_true', help='Generate static site')
    parser.add_argument('--business-id', type=str, help='Google Place ID')
    parser.add_argument('--intake-file', type=str, help='Path to intake form JSON file')
    parser.add_argument('--port', type=int, default=5001, help='Preview server port')
    parser.add_argument('--output', type=str, help='Custom output directory')
    
    args = parser.parse_args()
    
    # MODE 1: Generate from intake file
    if args.intake_file:
        intake_path = Path(args.intake_file)
        
        if not intake_path.exists():
            print(f"❌ Intake file not found: {intake_path}")
            return
        
        print(f"\n📋 Loading intake data from: {intake_path}")
        business = create_business_from_intake(intake_path)
        
        # Show intake data status
        has_colors = bool(business.brand_colors)
        has_identity = bool(business.business_identity.get('vision') or business.business_identity.get('mission'))
        has_services = bool(business.custom_services)
        has_promos = bool(business.promotions)
        has_social = any(business.social_media.values())
        
        print(f"   ✓ Business: {business.name}")
        print(f"   ✓ Category: {business.category}")
        print(f"   ✓ Theme: {business.theme.get('name', 'default')} ({business.theme.get('mode', 'dark')} mode)")
        print(f"   {'✓' if has_colors else '○'} Custom Colors: {'Yes' if has_colors else 'Default'}")
        print(f"   {'✓' if has_identity else '○'} Vision/Mission: {'Yes' if has_identity else 'No'}")
        print(f"   {'✓' if has_services else '○'} Custom Services: {len(business.custom_services)} items")
        print(f"   {'✓' if has_promos else '○'} Promotions: {len(business.promotions)} active")
        print(f"   {'✓' if has_social else '○'} Social Media: {'Yes' if has_social else 'No'}")
        
        if args.generate or not args.preview:
            slug = slugify(business.name)
            output_path = Path(args.output) if args.output else OUTPUT_DIR / f"custom-{slug}"
            
            generate_static_site(business, output_path)
            print(f"\n✅ Generated: {business.name}")
            print(f"   Output: {output_path}")
            print(f"   Open: file://{output_path}/index.html")
        
        if args.preview:
            print(f"\n🚀 Starting preview server for: {business.name}")
            print(f"   URL: http://localhost:{args.port}\n")
            
            app = create_app(business)
            app.run(debug=True, port=args.port, host='0.0.0.0')
        
        return
    
    # MODE 2: Generate all sites
    if args.generate_all:
        generate_all_sites(args.generate_all)
        return
    
    # MODE 3: Preview/Generate from leads.json
    if args.preview or args.business_id is not None or args.generate:
        leads = load_leads()
        if not leads:
            print("❌ No leads found in leads.json")
            return
        
        if args.business_id:
            lead = find_lead_by_google_id(args.business_id)
            if not lead:
                print(f"❌ Business with ID '{args.business_id}' not found")
                return
        else:
            lead = leads[0]
        
        google_id = lead.get('google_place_id')
        intake_data = load_intake_data(google_place_id=google_id, business_name=lead.get('name'))
        if intake_data:
            print(f"✓ Found matching intake data for {lead.get('name')}")
        
        business = create_business_from_lead(lead, intake_data)
        
        if args.generate:
            slug = slugify(business.name)
            google_id_short = lead.get('google_place_id', 'unknown')[:16].replace(':', '-')
            output_path = Path(args.output) if args.output else OUTPUT_DIR / f"{google_id_short}-{slug}"
            
            generate_static_site(business, output_path)
            print(f"\n✅ Generated: {business.name}")
            print(f"   Output: {output_path}")
        
        if args.preview or not args.generate:
            print(f"\n🚀 Starting preview server for: {business.name}")
            print(f"   Category: {business.category}")
            print(f"   Theme: {business.theme.get('name', 'default')} mode")
            print(f"   URL: http://localhost:{args.port}\n")
            
            app = create_app(business)
            app.run(debug=True, port=args.port, host='0.0.0.0')
        
        return
    
    parser.print_help()


if __name__ == '__main__':
    main()
