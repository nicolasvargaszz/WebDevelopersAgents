"""
Client Intake Form - Interactive Information Gathering
======================================================

Recopila información adicional del cliente para crear una página web
altamente personalizada y profesional.

Este programa pregunta al cliente sobre:
- Colores de marca y preferencias visuales
- Imágenes adicionales (logo, fotos propias)
- Visión, misión y valores
- Servicios específicos y diferenciales
- Promociones actuales
- Contenido de redes sociales

Usage:
    python -m agents.generation.client_intake_form
    python -m agents.generation.client_intake_form --business-id "0x945da89f7ce6aed5:0"
"""

import json
import os
import re
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
from typing import Optional, List, Dict
import sys


# ===========================================
# CONFIGURATION
# ===========================================

BASE_DIR = Path(__file__).parent.parent.parent
DATA_FILE = BASE_DIR / "discovered_businesses.json"
INTAKE_DATA_DIR = BASE_DIR / "intake_data"
INTAKE_DATA_DIR.mkdir(exist_ok=True)


# ===========================================
# COLORS & STYLING
# ===========================================

class Colors:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ===========================================
# DATA CLASSES
# ===========================================

@dataclass
class BrandColors:
    """Colores de la marca"""
    primary: str = "#2563eb"  # Blue default
    secondary: str = "#7c3aed"  # Purple default
    accent: str = "#f59e0b"  # Amber default
    background: str = "#ffffff"
    text: str = "#1f2937"
    
    def to_dict(self) -> dict:
        return {
            "primary": self.primary,
            "secondary": self.secondary,
            "accent": self.accent,
            "background": self.background,
            "text": self.text,
        }


@dataclass
class BusinessIdentity:
    """Identidad y propósito del negocio"""
    vision: str = ""
    mission: str = ""
    values: List[str] = field(default_factory=list)
    founding_year: Optional[int] = None
    founding_story: str = ""
    unique_selling_points: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "vision": self.vision,
            "mission": self.mission,
            "values": self.values,
            "founding_year": self.founding_year,
            "founding_story": self.founding_story,
            "unique_selling_points": self.unique_selling_points,
        }


@dataclass
class MediaAssets:
    """Assets visuales del negocio"""
    logo_url: Optional[str] = None
    custom_photos: List[str] = field(default_factory=list)
    video_url: Optional[str] = None
    instagram_handle: Optional[str] = None
    facebook_page: Optional[str] = None
    tiktok_handle: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "logo_url": self.logo_url,
            "custom_photos": self.custom_photos,
            "video_url": self.video_url,
            "instagram_handle": self.instagram_handle,
            "facebook_page": self.facebook_page,
            "tiktok_handle": self.tiktok_handle,
        }


@dataclass
class SpecialOffers:
    """Promociones y ofertas especiales"""
    current_promotions: List[Dict[str, str]] = field(default_factory=list)
    loyalty_program: Optional[str] = None
    seasonal_offers: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "current_promotions": self.current_promotions,
            "loyalty_program": self.loyalty_program,
            "seasonal_offers": self.seasonal_offers,
        }


@dataclass
class ContactPreferences:
    """Preferencias de contacto y comunicación"""
    preferred_contact_method: str = "whatsapp"  # whatsapp, phone, email, form
    whatsapp_number: Optional[str] = None
    email: Optional[str] = None
    response_time: str = "24 horas"
    booking_enabled: bool = False
    booking_url: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "preferred_contact_method": self.preferred_contact_method,
            "whatsapp_number": self.whatsapp_number,
            "email": self.email,
            "response_time": self.response_time,
            "booking_enabled": self.booking_enabled,
            "booking_url": self.booking_url,
        }


@dataclass
class ClientIntakeData:
    """Todos los datos recopilados del cliente"""
    business_name: str = ""
    business_id: Optional[str] = None
    category: str = ""
    
    # Secciones principales
    brand_colors: BrandColors = field(default_factory=BrandColors)
    business_identity: BusinessIdentity = field(default_factory=BusinessIdentity)
    media_assets: MediaAssets = field(default_factory=MediaAssets)
    special_offers: SpecialOffers = field(default_factory=SpecialOffers)
    contact_preferences: ContactPreferences = field(default_factory=ContactPreferences)
    
    # Servicios personalizados
    custom_services: List[Dict[str, str]] = field(default_factory=list)
    
    # Metadata
    completed_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "business_name": self.business_name,
            "business_id": self.business_id,
            "category": self.category,
            "brand_colors": self.brand_colors.to_dict(),
            "business_identity": self.business_identity.to_dict(),
            "media_assets": self.media_assets.to_dict(),
            "special_offers": self.special_offers.to_dict(),
            "contact_preferences": self.contact_preferences.to_dict(),
            "custom_services": self.custom_services,
            "completed_at": self.completed_at,
        }


# ===========================================
# INTERACTIVE FORM
# ===========================================

class ClientIntakeForm:
    """Formulario interactivo para recopilar información del cliente"""
    
    def __init__(self, google_place_id: str = None):
        self.data = ClientIntakeData()
        self.business_data = None
        
        # Si se proporciona google_place_id, cargar datos del negocio
        if google_place_id:
            self.business_data = self.load_business_by_google_id(google_place_id)
            if self.business_data:
                self.data.business_name = self.business_data.get('name', '')
                self.data.business_id = google_place_id
                self.data.category = self.business_data.get('category', '')
                print(f"{Colors.GREEN}✓ Datos cargados para: {self.data.business_name}{Colors.ENDC}")
                print(f"  Categoría: {self.data.category}")
                print(f"  Google Place ID: {google_place_id}\n")
    
    def load_business_by_google_id(self, google_place_id: str) -> Optional[dict]:
        """Carga los datos del negocio desde discovered_businesses.json"""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                businesses = json.load(f)
                
            for business in businesses:
                if business.get('google_place_id') == google_place_id:
                    return business
            
            print(f"{Colors.RED}❌ No se encontró negocio con Google Place ID: {google_place_id}{Colors.ENDC}")
            return None
        except Exception as e:
            print(f"{Colors.RED}❌ Error cargando datos: {e}{Colors.ENDC}")
            return None
        
    def print_header(self, text: str):
        """Imprime un encabezado decorado"""
        print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.CYAN}{text.center(60)}{Colors.ENDC}")
        print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.ENDC}\n")
    
    def print_section(self, text: str):
        """Imprime un título de sección"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}▶ {text}{Colors.ENDC}")
        print(f"{Colors.BLUE}{'─'*60}{Colors.ENDC}\n")
    
    def ask(self, question: str, default: str = "", required: bool = False) -> str:
        """Pregunta al usuario con opción de valor por defecto"""
        if default:
            prompt = f"{Colors.YELLOW}❓ {question}{Colors.ENDC}\n   {Colors.CYAN}(Default: {default}){Colors.ENDC}\n   → "
        else:
            prompt = f"{Colors.YELLOW}❓ {question}{Colors.ENDC}\n   → "
        
        while True:
            response = input(prompt).strip()
            
            if not response and default:
                return default
            elif not response and required:
                print(f"{Colors.RED}⚠️  Este campo es obligatorio. Por favor ingresa un valor.{Colors.ENDC}\n")
                continue
            elif not response:
                return ""
            else:
                return response
    
    def ask_yes_no(self, question: str, default: bool = False) -> bool:
        """Pregunta sí/no al usuario"""
        default_text = "S/n" if default else "s/N"
        response = self.ask(f"{question} [{default_text}]", "").lower()
        
        if not response:
            return default
        return response in ['s', 'si', 'sí', 'y', 'yes']
    
    def ask_list(self, question: str, min_items: int = 0) -> List[str]:
        """Pide al usuario que ingrese múltiples items"""
        print(f"{Colors.YELLOW}❓ {question}{Colors.ENDC}")
        print(f"{Colors.CYAN}   (Ingresa un item por línea, línea vacía para terminar){Colors.ENDC}\n")
        
        items = []
        counter = 1
        
        while True:
            item = input(f"   {counter}. → ").strip()
            if not item:
                if len(items) >= min_items:
                    break
                elif min_items > 0:
                    print(f"{Colors.RED}   ⚠️  Debes ingresar al menos {min_items} item(s).{Colors.ENDC}")
                    continue
                else:
                    break
            items.append(item)
            counter += 1
        
        return items
    
    def ask_color(self, question: str, default: str) -> str:
        """Pide un color en formato hexadecimal"""
        while True:
            color = self.ask(question, default)
            
            # Validar formato hex
            if re.match(r'^#[0-9A-Fa-f]{6}$', color):
                return color
            else:
                print(f"{Colors.RED}⚠️  Color inválido. Use formato hexadecimal (#RRGGBB) como #2563eb{Colors.ENDC}\n")
    
    def validate_image_url(self, url: str) -> bool:
        """Valida que una URL sea una imagen directa (no una URL de búsqueda de Google)"""
        if not url:
            return True  # Empty is allowed
        
        # Detectar URLs de Google Search/redirect que NO funcionan como imágenes
        invalid_patterns = [
            'google.com/url?',
            'google.com/search?',
            'google.com/imgres?',
            'bing.com/images/search',
            'duckduckgo.com/',
        ]
        
        for pattern in invalid_patterns:
            if pattern in url.lower():
                return False
        
        # Verificar que sea una URL válida
        if not url.startswith(('http://', 'https://')):
            return False
        
        return True
    
    def ask_image_url(self, question: str, required: bool = False) -> str:
        """Pide una URL de imagen válida"""
        print(f"{Colors.CYAN}   ⚠️  Importante: Usa URLs DIRECTAS de imagen (que terminen en .jpg, .png, .webp){Colors.ENDC}")
        print(f"{Colors.CYAN}   ✓  Ejemplos válidos:{Colors.ENDC}")
        print(f"      • https://i.imgur.com/abc123.jpg")
        print(f"      • https://drive.google.com/uc?export=view&id=FILE_ID")
        print(f"      • https://tu-sitio.com/images/logo.png")
        print(f"{Colors.RED}   ✗  NO funcionan: URLs de búsqueda de Google (www.google.com/url?...){Colors.ENDC}\n")
        
        while True:
            url = self.ask(question, "")
            
            if not url:
                if required:
                    print(f"{Colors.RED}⚠️  Este campo es obligatorio.{Colors.ENDC}\n")
                    continue
                return ""
            
            if self.validate_image_url(url):
                return url
            else:
                print(f"{Colors.RED}⚠️  Esta URL parece ser una URL de búsqueda de Google, no funcionará como imagen.{Colors.ENDC}")
                print(f"{Colors.YELLOW}   Consejo: Abre la imagen en otra pestaña y copia la URL directa de la imagen.{Colors.ENDC}\n")
                
                if self.ask_yes_no("¿Deseas usarla de todos modos?", default=False):
                    return url
    
    def ask_image_urls_list(self, question: str) -> List[str]:
        """Pide múltiples URLs de imágenes con validación"""
        print(f"\n{Colors.YELLOW}❓ {question}{Colors.ENDC}")
        print(f"{Colors.CYAN}   ⚠️  Usa URLs DIRECTAS de imagen (no URLs de búsqueda de Google){Colors.ENDC}")
        print(f"{Colors.CYAN}   Ingresa una URL por línea, línea vacía para terminar{Colors.ENDC}\n")
        
        urls = []
        counter = 1
        
        while True:
            url = input(f"   {counter}. → ").strip()
            if not url:
                break
            
            if not self.validate_image_url(url):
                print(f"{Colors.RED}   ⚠️  Esta URL parece ser de búsqueda de Google, puede no funcionar como imagen.{Colors.ENDC}")
                if not self.ask_yes_no("   ¿Agregarla de todos modos?", default=False):
                    continue
            
            urls.append(url)
            counter += 1
        
        return urls
    
    def select_business(self) -> Optional[dict]:
        """Permite al usuario seleccionar un negocio de la lista"""
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                businesses = json.load(f)
            
            # Filtrar negocios sin website
            no_website = [b for b in businesses if not b.get('has_website', True)]
            
            if not no_website:
                print(f"{Colors.RED}No hay negocios sin website disponibles.{Colors.ENDC}")
                return None
            
            print(f"\n{Colors.GREEN}Encontrados {len(no_website)} negocios sin website:{Colors.ENDC}\n")
            
            # Mostrar primeros 20
            for i, business in enumerate(no_website[:20], 1):
                name = business.get('name', 'Sin nombre')
                category = business.get('category', 'Sin categoría')
                rating = business.get('rating', 0)
                reviews = business.get('review_count', 0)
                
                print(f"{Colors.CYAN}{i:2d}.{Colors.ENDC} {Colors.BOLD}{name}{Colors.ENDC}")
                print(f"    {category} • ⭐ {rating} ({reviews} reseñas)")
            
            if len(no_website) > 20:
                print(f"\n{Colors.YELLOW}... y {len(no_website) - 20} más{Colors.ENDC}")
            
            # Pedir selección
            while True:
                choice = input(f"\n{Colors.YELLOW}Selecciona un negocio (1-{min(20, len(no_website))}) o 0 para crear uno nuevo: {Colors.ENDC}").strip()
                
                if choice == '0':
                    return None
                
                try:
                    idx = int(choice) - 1
                    if 0 <= idx < min(20, len(no_website)):
                        return no_website[idx]
                    else:
                        print(f"{Colors.RED}Número inválido. Intenta de nuevo.{Colors.ENDC}")
                except ValueError:
                    print(f"{Colors.RED}Por favor ingresa un número válido.{Colors.ENDC}")
        
        except FileNotFoundError:
            print(f"{Colors.RED}No se encontró el archivo de datos: {DATA_FILE}{Colors.ENDC}")
            return None
    
    def run(self, business_data: Optional[dict] = None):
        """Ejecuta el formulario completo"""
        self.print_header("🎨 FORMULARIO DE PERSONALIZACIÓN WEB")
        
        print(f"{Colors.GREEN}¡Bienvenido! Vamos a crear una página web increíble para tu negocio.{Colors.ENDC}")
        print(f"{Colors.CYAN}Este proceso toma aproximadamente 10-15 minutos.{Colors.ENDC}")
        
        # Si ya tenemos business_data cargado en __init__ (por google_place_id), úsalo
        if self.business_data and not business_data:
            business_data = self.business_data
            print(f"\n{Colors.GREEN}✓ Usando datos precargados del negocio{Colors.ENDC}")
        
        # Seleccionar o crear negocio solo si no hay datos
        if not business_data and not self.data.business_name:
            business_data = self.select_business()
        
        if business_data:
            # Solo actualizar si no fue establecido en __init__
            if not self.data.business_name:
                self.data.business_name = business_data.get('name', '')
            if not self.data.category:
                self.data.category = business_data.get('category', '')
            if not self.data.business_id:
                self.data.business_id = business_data.get('google_place_id', '')
            print(f"\n{Colors.GREEN}✓ Negocio: {Colors.BOLD}{self.data.business_name}{Colors.ENDC}")
            print(f"  Categoría: {self.data.category}")
        elif not self.data.business_name:
            self.data.business_name = self.ask("Nombre del negocio", required=True)
            self.data.category = self.ask("Categoría del negocio (ej: restaurante, salón de belleza)", required=True)
        
        # ===========================================
        # SECCIÓN 1: COLORES DE MARCA
        # ===========================================
        self.print_section("1️⃣  COLORES DE MARCA")
        
        print(f"{Colors.CYAN}Los colores definen la personalidad de tu marca.{Colors.ENDC}")
        print(f"{Colors.CYAN}Ejemplos: #2563eb (azul), #dc2626 (rojo), #16a34a (verde){Colors.ENDC}\n")
        
        if self.ask_yes_no("¿Deseas personalizar los colores de tu marca?", default=True):
            self.data.brand_colors.primary = self.ask_color(
                "Color primario (principal de tu marca)", 
                self.data.brand_colors.primary
            )
            self.data.brand_colors.secondary = self.ask_color(
                "Color secundario (acento o complemento)", 
                self.data.brand_colors.secondary
            )
            self.data.brand_colors.accent = self.ask_color(
                "Color de acento (botones, destacados)", 
                self.data.brand_colors.accent
            )
        
        # ===========================================
        # SECCIÓN 2: IDENTIDAD DEL NEGOCIO
        # ===========================================
        self.print_section("2️⃣  IDENTIDAD Y PROPÓSITO")
        
        if self.ask_yes_no("¿Deseas agregar la visión de tu negocio?", default=True):
            print(f"{Colors.CYAN}Ejemplo: 'Ser el restaurante líder en parrilla paraguaya, reconocido por nuestra calidad'{Colors.ENDC}\n")
            self.data.business_identity.vision = self.ask("Visión del negocio")
        
        if self.ask_yes_no("¿Deseas agregar la misión de tu negocio?", default=True):
            print(f"{Colors.CYAN}Ejemplo: 'Ofrecer experiencias gastronómicas únicas con ingredientes locales y atención excepcional'{Colors.ENDC}\n")
            self.data.business_identity.mission = self.ask("Misión del negocio")
        
        if self.ask_yes_no("¿Deseas agregar valores de tu negocio?", default=True):
            print(f"{Colors.CYAN}Ejemplo: 'Calidad', 'Tradición', 'Innovación'{Colors.ENDC}\n")
            self.data.business_identity.values = self.ask_list("Valores del negocio", min_items=0)
        
        if self.ask_yes_no("¿Tienes una historia de fundación para compartir?", default=False):
            year = self.ask("¿En qué año se fundó el negocio?")
            if year:
                try:
                    self.data.business_identity.founding_year = int(year)
                except ValueError:
                    pass
            
            self.data.business_identity.founding_story = self.ask(
                "Cuenta brevemente la historia de cómo nació tu negocio"
            )
        
        if self.ask_yes_no("¿Qué te hace diferente de la competencia? (USPs)", default=True):
            print(f"{Colors.CYAN}Ejemplo: 'Carnes premium seleccionadas', 'Más de 20 años de experiencia'{Colors.ENDC}\n")
            self.data.business_identity.unique_selling_points = self.ask_list(
                "¿Qué te hace único?", 
                min_items=1
            )
        
        # ===========================================
        # SECCIÓN 3: RECURSOS MULTIMEDIA
        # ===========================================
        self.print_section("3️⃣  IMÁGENES Y MULTIMEDIA")
        
        if self.ask_yes_no("¿Tienes un logo que podamos usar?", default=False):
            self.data.media_assets.logo_url = self.ask_image_url("URL del logo")
        
        if self.ask_yes_no("¿Tienes fotos propias del negocio que quieras incluir?", default=False):
            self.data.media_assets.custom_photos = self.ask_image_urls_list("URLs de fotos personalizadas")
        
        if self.ask_yes_no("¿Tienes un video promocional? (YouTube, Vimeo)", default=False):
            self.data.media_assets.video_url = self.ask("URL del video")
        
        # Redes sociales
        self.print_section("3️⃣ .1  REDES SOCIALES")
        
        if business_data and business_data.get('social_media'):
            social = business_data['social_media']
            if social.get('instagram'):
                self.data.media_assets.instagram_handle = social['instagram']
            if social.get('facebook'):
                self.data.media_assets.facebook_page = social['facebook']
            if social.get('tiktok'):
                self.data.media_assets.tiktok_handle = social['tiktok']
            print(f"{Colors.GREEN}✓ Redes sociales detectadas automáticamente desde Google Maps{Colors.ENDC}")
        else:
            if self.ask_yes_no("¿Tienes Instagram?", default=True):
                handle = self.ask("Usuario de Instagram (sin @)")
                if handle:
                    self.data.media_assets.instagram_handle = f"@{handle.lstrip('@')}"
            
            if self.ask_yes_no("¿Tienes Facebook?", default=True):
                self.data.media_assets.facebook_page = self.ask("URL de tu página de Facebook")
            
            if self.ask_yes_no("¿Tienes TikTok?", default=False):
                handle = self.ask("Usuario de TikTok (sin @)")
                if handle:
                    self.data.media_assets.tiktok_handle = f"@{handle.lstrip('@')}"
        
        # ===========================================
        # SECCIÓN 4: SERVICIOS PERSONALIZADOS
        # ===========================================
        self.print_section("4️⃣  SERVICIOS Y PRODUCTOS")
        
        if self.ask_yes_no("¿Quieres agregar servicios/productos específicos?", default=True):
            print(f"{Colors.CYAN}Ejemplo para un salón: 'Corte de cabello', 'Coloración', 'Tratamientos capilares'{Colors.ENDC}\n")
            
            services = []
            while True:
                service_name = self.ask("Nombre del servicio/producto (vacío para terminar)")
                if not service_name:
                    break
                
                service_desc = self.ask("Breve descripción del servicio", "")
                service_price = self.ask("Precio (opcional, ej: '₲ 50.000' o 'Desde ₲ 30.000')", "")
                
                services.append({
                    "name": service_name,
                    "description": service_desc,
                    "price": service_price,
                })
            
            self.data.custom_services = services
        
        # ===========================================
        # SECCIÓN 5: PROMOCIONES
        # ===========================================
        self.print_section("5️⃣  PROMOCIONES Y OFERTAS")
        
        if self.ask_yes_no("¿Tienes promociones activas actualmente?", default=False):
            promos = []
            while True:
                promo_title = self.ask("Título de la promoción (vacío para terminar)")
                if not promo_title:
                    break
                
                promo_desc = self.ask("Descripción de la promoción")
                promo_valid = self.ask("Válido hasta (opcional)", "")
                
                promos.append({
                    "title": promo_title,
                    "description": promo_desc,
                    "valid_until": promo_valid,
                })
            
            self.data.special_offers.current_promotions = promos
        
        if self.ask_yes_no("¿Tienes un programa de fidelidad o membresía?", default=False):
            self.data.special_offers.loyalty_program = self.ask("Describe tu programa de fidelidad")
        
        # ===========================================
        # SECCIÓN 6: CONTACTO Y RESERVAS
        # ===========================================
        self.print_section("6️⃣  CONTACTO Y RESERVAS")
        
        # WhatsApp
        if business_data and business_data.get('phone'):
            phone = business_data['phone'].strip()
            phone_clean = re.sub(r'[^\d+]', '', phone)
            if self.ask_yes_no(f"¿Usamos tu número de WhatsApp detectado: {phone}?", default=True):
                self.data.contact_preferences.whatsapp_number = phone_clean
        else:
            whatsapp = self.ask("Número de WhatsApp (con código de país, ej: +595981123456)")
            if whatsapp:
                self.data.contact_preferences.whatsapp_number = whatsapp
        
        # Email
        email = self.ask("Email de contacto (opcional)")
        if email:
            self.data.contact_preferences.email = email
        
        # Método preferido
        print(f"\n{Colors.CYAN}¿Cuál es tu método de contacto preferido?{Colors.ENDC}")
        print("1. WhatsApp")
        print("2. Teléfono")
        print("3. Email")
        print("4. Formulario web")
        
        method_choice = self.ask("Selecciona (1-4)", "1")
        methods = {
            "1": "whatsapp",
            "2": "phone",
            "3": "email",
            "4": "form"
        }
        self.data.contact_preferences.preferred_contact_method = methods.get(method_choice, "whatsapp")
        
        # Reservas
        if self.ask_yes_no("¿Aceptas reservas online?", default=False):
            self.data.contact_preferences.booking_enabled = True
            booking_url = self.ask("URL del sistema de reservas (opcional)")
            if booking_url:
                self.data.contact_preferences.booking_url = booking_url
        
        # Tiempo de respuesta
        self.data.contact_preferences.response_time = self.ask(
            "¿En cuánto tiempo respondes normalmente?",
            "24 horas"
        )
        
        # ===========================================
        # FINALIZACIÓN
        # ===========================================
        self.print_header("✅ FORMULARIO COMPLETADO")
        
        print(f"{Colors.GREEN}¡Excelente! Hemos recopilado toda la información necesaria.{Colors.ENDC}\n")
        
        # Resumen
        print(f"{Colors.BOLD}📋 RESUMEN:{Colors.ENDC}\n")
        print(f"   Negocio: {Colors.BOLD}{self.data.business_name}{Colors.ENDC}")
        print(f"   Categoría: {self.data.category}")
        print(f"   Colores: {self.data.brand_colors.primary}, {self.data.brand_colors.secondary}")
        print(f"   Servicios personalizados: {len(self.data.custom_services)}")
        print(f"   Promociones activas: {len(self.data.special_offers.current_promotions)}")
        print(f"   Redes sociales: {bool(self.data.media_assets.instagram_handle or self.data.media_assets.facebook_page)}")
        print(f"   WhatsApp configurado: {bool(self.data.contact_preferences.whatsapp_number)}")
        
        return self.data
    
    def save(self, filepath: Optional[Path] = None) -> Path:
        """Guarda los datos recopilados en un archivo JSON"""
        if not filepath:
            # Generar nombre de archivo basado en el nombre del negocio
            safe_name = re.sub(r'[^\w\s-]', '', self.data.business_name.lower())
            safe_name = re.sub(r'[-\s]+', '-', safe_name)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"intake_{safe_name}_{timestamp}.json"
            filepath = INTAKE_DATA_DIR / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.data.to_dict(), f, ensure_ascii=False, indent=2)
        
        print(f"\n{Colors.GREEN}✓ Datos guardados en: {filepath}{Colors.ENDC}")
        return filepath


# ===========================================
# CLI
# ===========================================

def main():
    """Ejecuta el formulario de intake"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Formulario de personalización para generación de sitios web"
    )
    parser.add_argument(
        '--business-id',
        help='Google Place ID del negocio (ejemplo: 0x945da89f7ce6aed5:0)'
    )
    
    args = parser.parse_args()
    
    # Crear y ejecutar formulario
    form = ClientIntakeForm(google_place_id=args.business_id)
    
    try:
        data = form.run()
        
        # Guardar datos
        if form.ask_yes_no("\n¿Deseas guardar esta información?", default=True):
            filepath = form.save()
            
            print(f"\n{Colors.CYAN}🚀 Próximo paso:{Colors.ENDC}")
            print(f"   Ejecuta el generador con este archivo:")
            print(f"   {Colors.BOLD}python -m agents.generation.builder --intake-file {filepath}{Colors.ENDC}")
            if args.business_id:
                print(f"\n   O directamente con el Google Place ID:")
                print(f"   {Colors.BOLD}python -m agents.generation.builder --business-id {args.business_id} --generate{Colors.ENDC}\n")
    
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}⚠️  Formulario cancelado por el usuario.{Colors.ENDC}")
        sys.exit(0)
    except Exception as e:
        print(f"\n{Colors.RED}❌ Error: {e}{Colors.ENDC}")
        sys.exit(1)


if __name__ == "__main__":
    main()
