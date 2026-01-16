"""
Generation Agent - Website Builder
Creates premium landing pages for businesses using Flask + Tailwind CSS

Usage:
    python -m agents.generation.builder --business-id <id>
    python -m agents.generation.builder --preview  # Launch preview server
"""

import json
import os
import re
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Optional
from urllib.parse import quote_plus

from flask import Flask, render_template, send_from_directory


# ===========================================
# CONFIGURATION
# ===========================================

BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "generated_sites"
DATA_FILE = BASE_DIR / "leads.json"

# Category color palettes (Tailwind classes)
CATEGORY_PALETTES = {
    # Food & Dining
    "restaurante": {
        "primary": "red-600",
        "primary_hover": "red-700",
        "secondary": "orange-500",
        "accent": "amber-400",
        "bg_gradient": "from-red-900 via-red-800 to-orange-900",
        "text_accent": "text-orange-400",
    },
    "parrilla": {
        "primary": "amber-600",
        "primary_hover": "amber-700",
        "secondary": "red-600",
        "accent": "yellow-500",
        "bg_gradient": "from-amber-900 via-red-900 to-stone-900",
        "text_accent": "text-amber-400",
    },
    "cafetería": {
        "primary": "amber-700",
        "primary_hover": "amber-800",
        "secondary": "stone-600",
        "accent": "amber-400",
        "bg_gradient": "from-amber-900 via-stone-800 to-stone-900",
        "text_accent": "text-amber-300",
    },
    "panadería": {
        "primary": "amber-600",
        "primary_hover": "amber-700",
        "secondary": "orange-400",
        "accent": "yellow-300",
        "bg_gradient": "from-amber-800 via-orange-800 to-stone-800",
        "text_accent": "text-amber-300",
    },
    "pizzería": {
        "primary": "red-600",
        "primary_hover": "red-700",
        "secondary": "green-600",
        "accent": "yellow-400",
        "bg_gradient": "from-red-900 via-stone-800 to-green-900",
        "text_accent": "text-red-400",
    },
    "heladería": {
        "primary": "pink-500",
        "primary_hover": "pink-600",
        "secondary": "cyan-400",
        "accent": "yellow-300",
        "bg_gradient": "from-pink-800 via-purple-800 to-cyan-800",
        "text_accent": "text-pink-300",
    },
    
    # Beauty & Wellness
    "salón de belleza": {
        "primary": "pink-600",
        "primary_hover": "pink-700",
        "secondary": "purple-500",
        "accent": "rose-400",
        "bg_gradient": "from-pink-900 via-purple-900 to-fuchsia-900",
        "text_accent": "text-pink-400",
    },
    "peluquería": {
        "primary": "violet-600",
        "primary_hover": "violet-700",
        "secondary": "purple-500",
        "accent": "fuchsia-400",
        "bg_gradient": "from-violet-900 via-purple-900 to-fuchsia-900",
        "text_accent": "text-violet-400",
    },
    "barbería": {
        "primary": "slate-700",
        "primary_hover": "slate-800",
        "secondary": "amber-600",
        "accent": "amber-400",
        "bg_gradient": "from-slate-900 via-stone-800 to-amber-900",
        "text_accent": "text-amber-400",
    },
    "spa": {
        "primary": "teal-600",
        "primary_hover": "teal-700",
        "secondary": "emerald-500",
        "accent": "cyan-400",
        "bg_gradient": "from-teal-900 via-emerald-900 to-cyan-900",
        "text_accent": "text-teal-400",
    },
    "gimnasio": {
        "primary": "orange-600",
        "primary_hover": "orange-700",
        "secondary": "red-600",
        "accent": "yellow-400",
        "bg_gradient": "from-orange-900 via-red-900 to-stone-900",
        "text_accent": "text-orange-400",
    },
    
    # Health & Medical
    "dentista": {
        "primary": "cyan-600",
        "primary_hover": "cyan-700",
        "secondary": "blue-500",
        "accent": "sky-400",
        "bg_gradient": "from-cyan-900 via-blue-900 to-sky-900",
        "text_accent": "text-cyan-400",
    },
    "clínica dental": {
        "primary": "sky-600",
        "primary_hover": "sky-700",
        "secondary": "cyan-500",
        "accent": "blue-400",
        "bg_gradient": "from-sky-900 via-cyan-900 to-blue-900",
        "text_accent": "text-sky-400",
    },
    "veterinario": {
        "primary": "emerald-600",
        "primary_hover": "emerald-700",
        "secondary": "teal-500",
        "accent": "green-400",
        "bg_gradient": "from-emerald-900 via-teal-900 to-green-900",
        "text_accent": "text-emerald-400",
    },
    "clínica médica": {
        "primary": "blue-600",
        "primary_hover": "blue-700",
        "secondary": "indigo-500",
        "accent": "sky-400",
        "bg_gradient": "from-blue-900 via-indigo-900 to-sky-900",
        "text_accent": "text-blue-400",
    },
    "farmacia": {
        "primary": "green-600",
        "primary_hover": "green-700",
        "secondary": "emerald-500",
        "accent": "lime-400",
        "bg_gradient": "from-green-900 via-emerald-900 to-teal-900",
        "text_accent": "text-green-400",
    },
    
    # Services
    "taller mecánico": {
        "primary": "blue-700",
        "primary_hover": "blue-800",
        "secondary": "slate-600",
        "accent": "orange-400",
        "bg_gradient": "from-blue-900 via-slate-800 to-stone-900",
        "text_accent": "text-blue-400",
    },
    "ferretería": {
        "primary": "orange-600",
        "primary_hover": "orange-700",
        "secondary": "amber-600",
        "accent": "yellow-400",
        "bg_gradient": "from-orange-900 via-amber-900 to-stone-900",
        "text_accent": "text-orange-400",
    },
    "lavadero": {
        "primary": "blue-500",
        "primary_hover": "blue-600",
        "secondary": "cyan-500",
        "accent": "sky-400",
        "bg_gradient": "from-blue-900 via-cyan-900 to-sky-900",
        "text_accent": "text-blue-400",
    },
    "cerrajería": {
        "primary": "amber-600",
        "primary_hover": "amber-700",
        "secondary": "stone-600",
        "accent": "yellow-400",
        "bg_gradient": "from-amber-900 via-stone-800 to-slate-900",
        "text_accent": "text-amber-400",
    },
    
    # Professional
    "abogado": {
        "primary": "slate-700",
        "primary_hover": "slate-800",
        "secondary": "stone-600",
        "accent": "amber-500",
        "bg_gradient": "from-slate-900 via-stone-800 to-neutral-900",
        "text_accent": "text-slate-400",
    },
    "contador": {
        "primary": "indigo-600",
        "primary_hover": "indigo-700",
        "secondary": "blue-600",
        "accent": "sky-400",
        "bg_gradient": "from-indigo-900 via-blue-900 to-slate-900",
        "text_accent": "text-indigo-400",
    },
    "inmobiliaria": {
        "primary": "emerald-600",
        "primary_hover": "emerald-700",
        "secondary": "teal-500",
        "accent": "green-400",
        "bg_gradient": "from-emerald-900 via-teal-900 to-slate-900",
        "text_accent": "text-emerald-400",
    },
    "floristería": {
        "primary": "rose-600",
        "primary_hover": "rose-700",
        "secondary": "pink-500",
        "accent": "fuchsia-400",
        "bg_gradient": "from-rose-900 via-pink-900 to-fuchsia-900",
        "text_accent": "text-rose-400",
    },
    
    # Default
    "default": {
        "primary": "indigo-600",
        "primary_hover": "indigo-700",
        "secondary": "purple-500",
        "accent": "violet-400",
        "bg_gradient": "from-indigo-900 via-purple-900 to-slate-900",
        "text_accent": "text-indigo-400",
    },
}


# ===========================================
# DATA CLASSES
# ===========================================

@dataclass
class BusinessData:
    """Structured business data for template rendering"""
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
    
    # Generated content (placeholders for now)
    headline: str = ""
    description: str = ""
    services: list = None
    cta_text: str = "Contáctanos Ahora"
    
    # Computed
    whatsapp_link: str = ""
    phone_link: str = ""
    maps_embed_url: str = ""
    hero_image: str = ""
    palette: dict = None
    
    def __post_init__(self):
        self.services = self.services or []
        self._compute_links()
        self._select_palette()
        self._generate_placeholder_content()
    
    def _compute_links(self):
        """Generate WhatsApp, phone, and maps links"""
        # Clean phone number
        phone_clean = re.sub(r'[^\d+]', '', self.phone or '')
        if phone_clean and not phone_clean.startswith('+'):
            phone_clean = '+595' + phone_clean.lstrip('0')
        
        # WhatsApp link with pre-filled message
        message = f"Hola, vi su página web y me gustaría más información sobre {self.name}"
        self.whatsapp_link = f"https://wa.me/{phone_clean}?text={quote_plus(message)}"
        
        # Phone link
        self.phone_link = f"tel:{phone_clean}"
        
        # Google Maps embed
        if self.latitude and self.longitude:
            self.maps_embed_url = (
                f"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3000!2d{self.longitude}!3d{self.latitude}"
                f"!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2z{self.latitude}!5e0!3m2!1ses!2spy!4v1"
            )
        else:
            # Fallback: search by name
            query = quote_plus(f"{self.name} {self.city} Paraguay")
            self.maps_embed_url = f"https://www.google.com/maps/embed/v1/place?key=AIzaSyBFw0Qbyq9zTFTd-tUY6dZWTgaQzuU17R8&q={query}"
        
        # Hero image
        if self.photo_urls and len(self.photo_urls) > 0:
            # Get the highest resolution image
            self.hero_image = self.photo_urls[0].replace('w80-', 'w1200-').replace('h142-', 'h800-')
        else:
            self.hero_image = "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1200"
    
    def _select_palette(self):
        """Select color palette based on category"""
        category_lower = (self.category or '').lower()
        
        # Try to match category
        for key, palette in CATEGORY_PALETTES.items():
            if key in category_lower:
                self.palette = palette
                return
        
        # Default palette
        self.palette = CATEGORY_PALETTES["default"]
    
    def _generate_placeholder_content(self):
        """Generate placeholder content (will be replaced by AI later)"""
        if not self.headline:
            self.headline = f"Bienvenidos a {self.name}"
        
        if not self.description:
            self.description = (
                f"Somos {self.name}, su mejor opción en {self.category or 'servicios profesionales'} "
                f"en {self.city}. Con años de experiencia y dedicación, nos comprometemos a "
                f"brindarle la mejor atención y calidad que usted merece."
            )
        
        if not self.services:
            self.services = [
                "Atención personalizada",
                "Profesionales capacitados",
                "Precios competitivos",
                "Ubicación conveniente",
                "Horarios flexibles",
            ]


# ===========================================
# FLASK APPLICATION
# ===========================================

def create_app(business: BusinessData = None) -> Flask:
    """Create Flask application for website generation"""
    
    app = Flask(
        __name__,
        template_folder=str(TEMPLATES_DIR),
        static_folder=str(TEMPLATES_DIR / "static"),
    )
    
    # Store business data in app config
    app.config['BUSINESS'] = business
    
    @app.route('/')
    def index():
        """Render the landing page"""
        biz = app.config.get('BUSINESS')
        if not biz:
            return "No business data loaded", 404
        
        return render_template(
            'landing/index.html',
            business=biz,
            palette=biz.palette,
        )
    
    @app.route('/preview/<int:lead_index>')
    def preview_lead(lead_index: int):
        """Preview a specific lead by index"""
        leads = load_leads()
        if lead_index < 0 or lead_index >= len(leads):
            return f"Lead index {lead_index} out of range (0-{len(leads)-1})", 404
        
        business = create_business_from_lead(leads[lead_index])
        return render_template(
            'landing/index.html',
            business=business,
            palette=business.palette,
        )
    
    @app.route('/leads')
    def list_leads():
        """List all leads with preview links"""
        leads = load_leads()
        return render_template(
            'admin/lead_list.html',
            leads=leads[:50],  # Limit to first 50
            total=len(leads),
        )
    
    @app.route('/static/<path:filename>')
    def serve_static(filename):
        """Serve static files"""
        return send_from_directory(str(TEMPLATES_DIR / "static"), filename)
    
    return app


# ===========================================
# DATA LOADING
# ===========================================

def load_leads() -> list[dict]:
    """Load leads from JSON file"""
    if not DATA_FILE.exists():
        return []
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


def create_business_from_lead(lead: dict) -> BusinessData:
    """Convert a lead dict to BusinessData object"""
    # Safely handle None values
    address = lead.get('address') or ''
    phone = lead.get('phone') or ''
    
    return BusinessData(
        name=lead.get('name') or 'Mi Negocio',
        category=lead.get('category') or '',
        address=address.strip().lstrip('\n') if address else '',
        city=lead.get('city') or 'Asunción',
        phone=phone.strip().lstrip('\n') if phone else '',
        rating=lead.get('rating') or 0,
        review_count=lead.get('review_count') or 0,
        photo_urls=lead.get('photo_urls') or [],
        latitude=lead.get('latitude') or -25.2867,
        longitude=lead.get('longitude') or -57.647,
    )


# ===========================================
# STATIC SITE GENERATION
# ===========================================

def generate_static_site(business: BusinessData, output_path: Path) -> Path:
    """Generate a static HTML site for a business"""
    
    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Create Flask app and render template
    app = create_app(business)
    
    with app.app_context():
        html_content = render_template(
            'landing/index.html',
            business=business,
            palette=business.palette,
        )
    
    # Write HTML file
    index_file = output_path / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Copy static assets if needed
    static_src = TEMPLATES_DIR / "static"
    static_dst = output_path / "static"
    if static_src.exists():
        shutil.copytree(static_src, static_dst, dirs_exist_ok=True)
    
    return output_path


def generate_all_sites(limit: int = 10) -> list[Path]:
    """Generate static sites for all qualified leads"""
    leads = load_leads()
    generated = []
    
    for i, lead in enumerate(leads[:limit]):
        business = create_business_from_lead(lead)
        
        # Create safe folder name
        safe_name = re.sub(r'[^\w\s-]', '', business.name)[:50].strip().replace(' ', '-').lower()
        output_path = OUTPUT_DIR / f"{i:04d}-{safe_name}"
        
        try:
            generate_static_site(business, output_path)
            generated.append(output_path)
            print(f"✅ Generated: {business.name} → {output_path}")
        except Exception as e:
            print(f"❌ Failed: {business.name} → {e}")
    
    return generated


# ===========================================
# CLI ENTRY POINT
# ===========================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Website Generation Agent')
    parser.add_argument('--preview', action='store_true', help='Launch preview server')
    parser.add_argument('--port', type=int, default=5000, help='Server port')
    parser.add_argument('--lead-index', type=int, help='Generate for specific lead index')
    parser.add_argument('--generate-all', type=int, metavar='LIMIT', help='Generate static sites for N leads')
    
    args = parser.parse_args()
    
    if args.generate_all:
        print(f"🚀 Generating static sites for {args.generate_all} leads...")
        generated = generate_all_sites(limit=args.generate_all)
        print(f"\n✅ Generated {len(generated)} sites in {OUTPUT_DIR}")
    
    elif args.preview:
        # Load first lead for preview
        leads = load_leads()
        if not leads:
            print("❌ No leads found. Run discovery first.")
            return
        
        business = create_business_from_lead(leads[0])
        app = create_app(business)
        
        print(f"\n🚀 Preview Server Starting...")
        print(f"   → Main preview: http://localhost:{args.port}/")
        print(f"   → Lead list:    http://localhost:{args.port}/leads")
        print(f"   → Specific:     http://localhost:{args.port}/preview/<index>")
        print(f"\n   Press Ctrl+C to stop.\n")
        
        app.run(debug=True, port=args.port, host='0.0.0.0')
    
    elif args.lead_index is not None:
        # Generate for specific lead
        leads = load_leads()
        if args.lead_index >= len(leads):
            print(f"❌ Lead index {args.lead_index} out of range")
            return
        
        business = create_business_from_lead(leads[args.lead_index])
        safe_name = re.sub(r'[^\w\s-]', '', business.name)[:50].strip().replace(' ', '-').lower()
        output_path = OUTPUT_DIR / safe_name
        
        generate_static_site(business, output_path)
        print(f"✅ Generated: {output_path}")
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
