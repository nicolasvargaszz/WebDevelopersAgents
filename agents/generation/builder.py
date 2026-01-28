"""
Generation Agent - Premium Website Builder
Creates high-end, $1,000-look landing pages for businesses

Design Philosophy:
- Massive typography with generous whitespace
- Stock imagery for heroes (Unsplash), Google photos for gallery
- Category-specific theming (Dark/Light modes, fonts, accents)
- Long-scroll structure with sticky navbar

Usage:
    python -m agents.generation.builder --preview          # Launch preview server
    python -m agents.generation.builder --generate-all N   # Generate N sites
"""

import json
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional, List, Dict
from urllib.parse import quote_plus

from flask import Flask, render_template, send_from_directory

# Import the CopyWriter for rich content generation
from agents.generation.copy_writer import CopyWriter


# ===========================================
# CONFIGURATION
# ===========================================

BASE_DIR = Path(__file__).parent.parent.parent
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "generated_sites"
DATA_FILE = BASE_DIR / "leads.json"


# ===========================================
# STOCK IMAGES (High-quality Unsplash)
# ===========================================

STOCK_IMAGES = {
    # Food & Dining
    "parrilla": "https://images.unsplash.com/photo-1544025162-d76694265947?w=1920&q=80",
    "asado": "https://images.unsplash.com/photo-1544025162-d76694265947?w=1920&q=80",
    "restaurante": "https://images.unsplash.com/photo-1517248135467-4c7edcad34c4?w=1920&q=80",
    "cafetería": "https://images.unsplash.com/photo-1501339847302-ac426a4a7cbb?w=1920&q=80",
    "café": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=1920&q=80",
    "panadería": "https://images.unsplash.com/photo-1509440159596-0249088772ff?w=1920&q=80",
    "pizzería": "https://images.unsplash.com/photo-1513104890138-7c749659a591?w=1920&q=80",
    "heladería": "https://images.unsplash.com/photo-1501443762994-82bd5dace89a?w=1920&q=80",
    "carnicería": "https://images.unsplash.com/photo-1607623814075-e51df1bdc82f?w=1920&q=80",
    "burger": "https://images.unsplash.com/photo-1568901346375-23c9450c58cd?w=1920&q=80",
    
    # Beauty & Wellness
    "salón de belleza": "https://images.unsplash.com/photo-1560066984-138dadb4c035?w=1920&q=80",
    "peluquería": "https://images.unsplash.com/photo-1522337360788-8b13dee7a37e?w=1920&q=80",
    "barbería": "https://images.unsplash.com/photo-1585747860715-2ba37e788b70?w=1920&q=80",
    "spa": "https://images.unsplash.com/photo-1544161515-4ab6ce6db874?w=1920&q=80",
    "belleza": "https://images.unsplash.com/photo-1487412947147-5cebf100ffc2?w=1920&q=80",
    "uñas": "https://images.unsplash.com/photo-1604654894610-df63bc536371?w=1920&q=80",
    "estética": "https://images.unsplash.com/photo-1570172619644-dfd03ed5d881?w=1920&q=80",
    
    # Health & Medical
    "dentista": "https://images.unsplash.com/photo-1606811841689-23dfddce3e95?w=1920&q=80",
    "odontología": "https://images.unsplash.com/photo-1588776814546-1ffcf47267a5?w=1920&q=80",
    "veterinario": "https://images.unsplash.com/photo-1628009368231-7bb7cfcb0def?w=1920&q=80",
    "veterinaria": "https://images.unsplash.com/photo-1548767797-d8c844163c4c?w=1920&q=80",
    "clínica": "https://images.unsplash.com/photo-1519494026892-80bbd2d6fd0d?w=1920&q=80",
    "farmacia": "https://images.unsplash.com/photo-1585435557343-3b092031a831?w=1920&q=80",
    "médico": "https://images.unsplash.com/photo-1666214280557-f1b5022eb634?w=1920&q=80",
    
    # Fitness
    "gimnasio": "https://images.unsplash.com/photo-1534438327276-14e5300c3a48?w=1920&q=80",
    "gym": "https://images.unsplash.com/photo-1571902943202-507ec2618e8f?w=1920&q=80",
    "fitness": "https://images.unsplash.com/photo-1517836357463-d25dfeac3438?w=1920&q=80",
    
    # Services
    "taller": "https://images.unsplash.com/photo-1619642751034-765dfdf7c58e?w=1920&q=80",
    "mecánico": "https://images.unsplash.com/photo-1487754180451-c456f719a1fc?w=1920&q=80",
    "ferretería": "https://images.unsplash.com/photo-1504148455328-c376907d081c?w=1920&q=80",
    "lavadero": "https://images.unsplash.com/photo-1520340356584-f9917d1eea6f?w=1920&q=80",
    "cerrajería": "https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1920&q=80",
    
    # Professional
    "abogado": "https://images.unsplash.com/photo-1589829545856-d10d557cf95f?w=1920&q=80",
    "jurídico": "https://images.unsplash.com/photo-1505664194779-8beaceb93744?w=1920&q=80",
    "contador": "https://images.unsplash.com/photo-1554224155-6726b3ff858f?w=1920&q=80",
    "contable": "https://images.unsplash.com/photo-1450101499163-c8848c66ca85?w=1920&q=80",
    "inmobiliaria": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1920&q=80",
    "remax": "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=1920&q=80",
    
    # Retail
    "floristería": "https://images.unsplash.com/photo-1487530811176-3780de880c2d?w=1920&q=80",
    "flores": "https://images.unsplash.com/photo-1490750967868-88aa4486c946?w=1920&q=80",
    "librería": "https://images.unsplash.com/photo-1507842217343-583bb7270b66?w=1920&q=80",
    "óptica": "https://images.unsplash.com/photo-1574258495973-f010dfbb5371?w=1920&q=80",
    
    # Default
    "default": "https://images.unsplash.com/photo-1497366216548-37526070297c?w=1920&q=80",
}


# ===========================================
# THEME CONFIG (The "Expensive" Look)
# ===========================================

THEME_CONFIG = {
    # Dark & Luxurious - Parrilla/Asado
    "parrilla": {
        "mode": "dark",
        "bg_primary": "bg-slate-950",
        "bg_secondary": "bg-slate-900",
        "bg_card": "bg-slate-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-slate-300",
        "text_muted": "text-slate-400",
        "accent": "amber-500",
        "accent_text": "text-amber-500",
        "accent_bg": "bg-amber-500",
        "accent_hover": "hover:bg-amber-600",
        "accent_border": "border-amber-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-slate-950/95",
        "cta_gradient": "from-amber-600 to-orange-600",
    },
    "asado": {
        "mode": "dark",
        "bg_primary": "bg-slate-950",
        "bg_secondary": "bg-slate-900",
        "bg_card": "bg-slate-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-slate-300",
        "text_muted": "text-slate-400",
        "accent": "amber-500",
        "accent_text": "text-amber-500",
        "accent_bg": "bg-amber-500",
        "accent_hover": "hover:bg-amber-600",
        "accent_border": "border-amber-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-slate-950/95",
        "cta_gradient": "from-amber-600 to-orange-600",
    },
    
    # Clean & Professional - Dentist
    "dentista": {
        "mode": "light",
        "bg_primary": "bg-white",
        "bg_secondary": "bg-slate-50",
        "bg_card": "bg-white",
        "text_primary": "text-slate-900",
        "text_secondary": "text-slate-600",
        "text_muted": "text-slate-500",
        "accent": "teal-600",
        "accent_text": "text-teal-600",
        "accent_bg": "bg-teal-600",
        "accent_hover": "hover:bg-teal-700",
        "accent_border": "border-teal-200",
        "gradient_hero": "from-black/70 via-black/50 to-black/70",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-white/95",
        "cta_gradient": "from-teal-600 to-cyan-600",
    },
    "odontología": {
        "mode": "light",
        "bg_primary": "bg-white",
        "bg_secondary": "bg-slate-50",
        "bg_card": "bg-white",
        "text_primary": "text-slate-900",
        "text_secondary": "text-slate-600",
        "text_muted": "text-slate-500",
        "accent": "cyan-600",
        "accent_text": "text-cyan-600",
        "accent_bg": "bg-cyan-600",
        "accent_hover": "hover:bg-cyan-700",
        "accent_border": "border-cyan-200",
        "gradient_hero": "from-black/70 via-black/50 to-black/70",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-white/95",
        "cta_gradient": "from-cyan-600 to-blue-600",
    },
    
    # Elegant & Warm - Beauty/Salon
    "belleza": {
        "mode": "dark",
        "bg_primary": "bg-stone-950",
        "bg_secondary": "bg-stone-900",
        "bg_card": "bg-stone-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-stone-300",
        "text_muted": "text-stone-400",
        "accent": "rose-500",
        "accent_text": "text-rose-400",
        "accent_bg": "bg-rose-500",
        "accent_hover": "hover:bg-rose-600",
        "accent_border": "border-rose-500/30",
        "gradient_hero": "from-black/70 via-black/50 to-black/70",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-stone-950/95",
        "cta_gradient": "from-rose-500 to-pink-600",
    },
    "salón": {
        "mode": "dark",
        "bg_primary": "bg-stone-950",
        "bg_secondary": "bg-stone-900",
        "bg_card": "bg-stone-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-stone-300",
        "text_muted": "text-stone-400",
        "accent": "rose-500",
        "accent_text": "text-rose-400",
        "accent_bg": "bg-rose-500",
        "accent_hover": "hover:bg-rose-600",
        "accent_border": "border-rose-500/30",
        "gradient_hero": "from-black/70 via-black/50 to-black/70",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-stone-950/95",
        "cta_gradient": "from-rose-500 to-pink-600",
    },
    "peluquería": {
        "mode": "dark",
        "bg_primary": "bg-neutral-950",
        "bg_secondary": "bg-neutral-900",
        "bg_card": "bg-neutral-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-neutral-300",
        "text_muted": "text-neutral-400",
        "accent": "violet-500",
        "accent_text": "text-violet-400",
        "accent_bg": "bg-violet-500",
        "accent_hover": "hover:bg-violet-600",
        "accent_border": "border-violet-500/30",
        "gradient_hero": "from-black/70 via-black/50 to-black/70",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-neutral-950/95",
        "cta_gradient": "from-violet-500 to-purple-600",
    },
    
    # Masculine & Bold - Barbershop
    "barbería": {
        "mode": "dark",
        "bg_primary": "bg-zinc-950",
        "bg_secondary": "bg-zinc-900",
        "bg_card": "bg-zinc-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-zinc-300",
        "text_muted": "text-zinc-400",
        "accent": "amber-500",
        "accent_text": "text-amber-400",
        "accent_bg": "bg-amber-500",
        "accent_hover": "hover:bg-amber-600",
        "accent_border": "border-amber-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-zinc-950/95",
        "cta_gradient": "from-amber-500 to-orange-600",
    },
    "barber": {
        "mode": "dark",
        "bg_primary": "bg-zinc-950",
        "bg_secondary": "bg-zinc-900",
        "bg_card": "bg-zinc-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-zinc-300",
        "text_muted": "text-zinc-400",
        "accent": "amber-500",
        "accent_text": "text-amber-400",
        "accent_bg": "bg-amber-500",
        "accent_hover": "hover:bg-amber-600",
        "accent_border": "border-amber-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-zinc-950/95",
        "cta_gradient": "from-amber-500 to-orange-600",
    },
    
    # Calming & Natural - Spa
    "spa": {
        "mode": "dark",
        "bg_primary": "bg-emerald-950",
        "bg_secondary": "bg-emerald-900",
        "bg_card": "bg-emerald-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-emerald-200",
        "text_muted": "text-emerald-300",
        "accent": "teal-400",
        "accent_text": "text-teal-400",
        "accent_bg": "bg-teal-500",
        "accent_hover": "hover:bg-teal-600",
        "accent_border": "border-teal-500/30",
        "gradient_hero": "from-black/60 via-black/40 to-black/60",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-emerald-950/95",
        "cta_gradient": "from-teal-500 to-emerald-600",
    },
    
    # Fresh & Natural - Veterinary
    "veterinaria": {
        "mode": "light",
        "bg_primary": "bg-white",
        "bg_secondary": "bg-green-50",
        "bg_card": "bg-white",
        "text_primary": "text-slate-900",
        "text_secondary": "text-slate-600",
        "text_muted": "text-slate-500",
        "accent": "emerald-600",
        "accent_text": "text-emerald-600",
        "accent_bg": "bg-emerald-600",
        "accent_hover": "hover:bg-emerald-700",
        "accent_border": "border-emerald-200",
        "gradient_hero": "from-black/60 via-black/40 to-black/60",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-white/95",
        "cta_gradient": "from-emerald-600 to-green-600",
    },
    "veterinario": {
        "mode": "light",
        "bg_primary": "bg-white",
        "bg_secondary": "bg-green-50",
        "bg_card": "bg-white",
        "text_primary": "text-slate-900",
        "text_secondary": "text-slate-600",
        "text_muted": "text-slate-500",
        "accent": "emerald-600",
        "accent_text": "text-emerald-600",
        "accent_bg": "bg-emerald-600",
        "accent_hover": "hover:bg-emerald-700",
        "accent_border": "border-emerald-200",
        "gradient_hero": "from-black/60 via-black/40 to-black/60",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-white/95",
        "cta_gradient": "from-emerald-600 to-green-600",
    },
    
    # Energetic - Gym/Fitness
    "gimnasio": {
        "mode": "dark",
        "bg_primary": "bg-neutral-950",
        "bg_secondary": "bg-neutral-900",
        "bg_card": "bg-neutral-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-neutral-300",
        "text_muted": "text-neutral-400",
        "accent": "red-500",
        "accent_text": "text-red-500",
        "accent_bg": "bg-red-600",
        "accent_hover": "hover:bg-red-700",
        "accent_border": "border-red-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-neutral-950/95",
        "cta_gradient": "from-red-600 to-orange-600",
    },
    "gym": {
        "mode": "dark",
        "bg_primary": "bg-neutral-950",
        "bg_secondary": "bg-neutral-900",
        "bg_card": "bg-neutral-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-neutral-300",
        "text_muted": "text-neutral-400",
        "accent": "red-500",
        "accent_text": "text-red-500",
        "accent_bg": "bg-red-600",
        "accent_hover": "hover:bg-red-700",
        "accent_border": "border-red-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-neutral-950/95",
        "cta_gradient": "from-red-600 to-orange-600",
    },
    "fitness": {
        "mode": "dark",
        "bg_primary": "bg-neutral-950",
        "bg_secondary": "bg-neutral-900",
        "bg_card": "bg-neutral-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-neutral-300",
        "text_muted": "text-neutral-400",
        "accent": "orange-500",
        "accent_text": "text-orange-500",
        "accent_bg": "bg-orange-600",
        "accent_hover": "hover:bg-orange-700",
        "accent_border": "border-orange-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-neutral-950/95",
        "cta_gradient": "from-orange-600 to-red-600",
    },
    
    # Industrial - Mechanic/Hardware
    "taller": {
        "mode": "dark",
        "bg_primary": "bg-slate-950",
        "bg_secondary": "bg-slate-900",
        "bg_card": "bg-slate-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-slate-300",
        "text_muted": "text-slate-400",
        "accent": "blue-500",
        "accent_text": "text-blue-400",
        "accent_bg": "bg-blue-600",
        "accent_hover": "hover:bg-blue-700",
        "accent_border": "border-blue-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-slate-950/95",
        "cta_gradient": "from-blue-600 to-cyan-600",
    },
    "mecánico": {
        "mode": "dark",
        "bg_primary": "bg-slate-950",
        "bg_secondary": "bg-slate-900",
        "bg_card": "bg-slate-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-slate-300",
        "text_muted": "text-slate-400",
        "accent": "blue-500",
        "accent_text": "text-blue-400",
        "accent_bg": "bg-blue-600",
        "accent_hover": "hover:bg-blue-700",
        "accent_border": "border-blue-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-slate-950/95",
        "cta_gradient": "from-blue-600 to-cyan-600",
    },
    "ferretería": {
        "mode": "dark",
        "bg_primary": "bg-orange-950",
        "bg_secondary": "bg-orange-900",
        "bg_card": "bg-orange-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-orange-200",
        "text_muted": "text-orange-300",
        "accent": "amber-500",
        "accent_text": "text-amber-400",
        "accent_bg": "bg-amber-500",
        "accent_hover": "hover:bg-amber-600",
        "accent_border": "border-amber-500/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-orange-950/95",
        "cta_gradient": "from-amber-500 to-orange-600",
    },
    
    # Fresh & Clean - Restaurants
    "restaurante": {
        "mode": "dark",
        "bg_primary": "bg-stone-950",
        "bg_secondary": "bg-stone-900",
        "bg_card": "bg-stone-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-stone-300",
        "text_muted": "text-stone-400",
        "accent": "orange-500",
        "accent_text": "text-orange-400",
        "accent_bg": "bg-orange-500",
        "accent_hover": "hover:bg-orange-600",
        "accent_border": "border-orange-500/30",
        "gradient_hero": "from-black/70 via-black/50 to-black/70",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-stone-950/95",
        "cta_gradient": "from-orange-500 to-red-600",
    },
    
    # Professional - Legal/Accounting
    "abogado": {
        "mode": "dark",
        "bg_primary": "bg-slate-950",
        "bg_secondary": "bg-slate-900",
        "bg_card": "bg-slate-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-slate-300",
        "text_muted": "text-slate-400",
        "accent": "amber-600",
        "accent_text": "text-amber-500",
        "accent_bg": "bg-amber-600",
        "accent_hover": "hover:bg-amber-700",
        "accent_border": "border-amber-600/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-slate-950/95",
        "cta_gradient": "from-amber-600 to-yellow-600",
    },
    "jurídico": {
        "mode": "dark",
        "bg_primary": "bg-slate-950",
        "bg_secondary": "bg-slate-900",
        "bg_card": "bg-slate-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-slate-300",
        "text_muted": "text-slate-400",
        "accent": "amber-600",
        "accent_text": "text-amber-500",
        "accent_bg": "bg-amber-600",
        "accent_hover": "hover:bg-amber-700",
        "accent_border": "border-amber-600/30",
        "gradient_hero": "from-black/80 via-black/60 to-black/80",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-slate-950/95",
        "cta_gradient": "from-amber-600 to-yellow-600",
    },
    "contador": {
        "mode": "light",
        "bg_primary": "bg-white",
        "bg_secondary": "bg-slate-50",
        "bg_card": "bg-white",
        "text_primary": "text-slate-900",
        "text_secondary": "text-slate-600",
        "text_muted": "text-slate-500",
        "accent": "indigo-600",
        "accent_text": "text-indigo-600",
        "accent_bg": "bg-indigo-600",
        "accent_hover": "hover:bg-indigo-700",
        "accent_border": "border-indigo-200",
        "gradient_hero": "from-black/70 via-black/50 to-black/70",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-white/95",
        "cta_gradient": "from-indigo-600 to-blue-600",
    },
    
    # Elegant - Real Estate
    "inmobiliaria": {
        "mode": "light",
        "bg_primary": "bg-white",
        "bg_secondary": "bg-slate-50",
        "bg_card": "bg-white",
        "text_primary": "text-slate-900",
        "text_secondary": "text-slate-600",
        "text_muted": "text-slate-500",
        "accent": "emerald-600",
        "accent_text": "text-emerald-600",
        "accent_bg": "bg-emerald-600",
        "accent_hover": "hover:bg-emerald-700",
        "accent_border": "border-emerald-200",
        "gradient_hero": "from-black/60 via-black/40 to-black/60",
        "font_heading": "font-serif",
        "font_body": "font-sans",
        "navbar_bg": "bg-white/95",
        "cta_gradient": "from-emerald-600 to-teal-600",
    },
    "remax": {
        "mode": "light",
        "bg_primary": "bg-white",
        "bg_secondary": "bg-red-50",
        "bg_card": "bg-white",
        "text_primary": "text-slate-900",
        "text_secondary": "text-slate-600",
        "text_muted": "text-slate-500",
        "accent": "red-600",
        "accent_text": "text-red-600",
        "accent_bg": "bg-red-600",
        "accent_hover": "hover:bg-red-700",
        "accent_border": "border-red-200",
        "gradient_hero": "from-black/60 via-black/40 to-black/60",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-white/95",
        "cta_gradient": "from-red-600 to-blue-600",
    },
    
    # Default - Clean Modern
    "default": {
        "mode": "dark",
        "bg_primary": "bg-slate-950",
        "bg_secondary": "bg-slate-900",
        "bg_card": "bg-slate-900/80",
        "text_primary": "text-white",
        "text_secondary": "text-slate-300",
        "text_muted": "text-slate-400",
        "accent": "indigo-500",
        "accent_text": "text-indigo-400",
        "accent_bg": "bg-indigo-600",
        "accent_hover": "hover:bg-indigo-700",
        "accent_border": "border-indigo-500/30",
        "gradient_hero": "from-black/70 via-black/50 to-black/70",
        "font_heading": "font-sans",
        "font_body": "font-sans",
        "navbar_bg": "bg-slate-950/95",
        "cta_gradient": "from-indigo-600 to-purple-600",
    },
}


# ===========================================
# CATEGORY FEATURES (SVG Icons + Text)
# ===========================================

CATEGORY_FEATURES = {
    "parrilla": [
        {"icon": "fire", "title": "Parrilla al Carbón", "desc": "Carnes asadas a la perfección con fuego de leña"},
        {"icon": "star", "title": "Cortes Premium", "desc": "Selección de los mejores cortes de carne"},
        {"icon": "users", "title": "Ambiente Familiar", "desc": "Espacio acogedor para toda la familia"},
        {"icon": "clock", "title": "Horario Extendido", "desc": "Abierto para almuerzos y cenas"},
    ],
    "dentista": [
        {"icon": "shield", "title": "Tecnología Avanzada", "desc": "Equipos de última generación"},
        {"icon": "heart", "title": "Atención Personalizada", "desc": "Tratamientos adaptados a cada paciente"},
        {"icon": "check", "title": "Profesionales Certificados", "desc": "Equipo altamente capacitado"},
        {"icon": "clock", "title": "Horarios Flexibles", "desc": "Turnos que se adaptan a tu agenda"},
    ],
    "odontología": [
        {"icon": "shield", "title": "Tecnología Avanzada", "desc": "Equipos de última generación"},
        {"icon": "heart", "title": "Atención Personalizada", "desc": "Tratamientos adaptados a cada paciente"},
        {"icon": "check", "title": "Profesionales Certificados", "desc": "Equipo altamente capacitado"},
        {"icon": "clock", "title": "Horarios Flexibles", "desc": "Turnos que se adaptan a tu agenda"},
    ],
    "barbería": [
        {"icon": "scissors", "title": "Cortes Clásicos y Modernos", "desc": "Estilistas expertos en todas las tendencias"},
        {"icon": "star", "title": "Productos Premium", "desc": "Utilizamos las mejores marcas del mercado"},
        {"icon": "clock", "title": "Sin Esperas", "desc": "Reserva tu turno y llega a tiempo"},
        {"icon": "users", "title": "Ambiente Exclusivo", "desc": "Un espacio diseñado para el caballero moderno"},
    ],
    "veterinaria": [
        {"icon": "heart", "title": "Amor por las Mascotas", "desc": "Tratamos a tu mascota como familia"},
        {"icon": "shield", "title": "Atención de Emergencias", "desc": "Disponibles cuando más nos necesitas"},
        {"icon": "check", "title": "Vacunación Completa", "desc": "Programa de vacunación preventiva"},
        {"icon": "star", "title": "Profesionales Expertos", "desc": "Veterinarios con años de experiencia"},
    ],
    "spa": [
        {"icon": "heart", "title": "Relajación Total", "desc": "Escapa del estrés diario"},
        {"icon": "star", "title": "Tratamientos Premium", "desc": "Las mejores técnicas de bienestar"},
        {"icon": "shield", "title": "Productos Naturales", "desc": "Ingredientes orgánicos y seguros"},
        {"icon": "clock", "title": "Ambiente Tranquilo", "desc": "Tu oasis de paz en la ciudad"},
    ],
    "gimnasio": [
        {"icon": "fire", "title": "Entrenamiento Intenso", "desc": "Programas diseñados para resultados"},
        {"icon": "users", "title": "Instructores Certificados", "desc": "Te guiamos en cada paso"},
        {"icon": "star", "title": "Equipos de Primera", "desc": "Máquinas modernas y bien mantenidas"},
        {"icon": "clock", "title": "Horario Extendido", "desc": "Entrena cuando mejor te convenga"},
    ],
    "restaurante": [
        {"icon": "star", "title": "Cocina de Autor", "desc": "Platos únicos creados por nuestro chef"},
        {"icon": "heart", "title": "Ingredientes Frescos", "desc": "Seleccionamos lo mejor cada día"},
        {"icon": "users", "title": "Ambiente Acogedor", "desc": "El lugar perfecto para cada ocasión"},
        {"icon": "clock", "title": "Reservas Online", "desc": "Asegura tu mesa con anticipación"},
    ],
    "taller": [
        {"icon": "shield", "title": "Diagnóstico Preciso", "desc": "Identificamos el problema exacto"},
        {"icon": "check", "title": "Repuestos Originales", "desc": "Solo usamos piezas de calidad"},
        {"icon": "clock", "title": "Entrega Rápida", "desc": "Tu vehículo listo cuando lo necesitas"},
        {"icon": "star", "title": "Garantía de Servicio", "desc": "Respaldamos nuestro trabajo"},
    ],
    "default": [
        {"icon": "star", "title": "Calidad Garantizada", "desc": "Nos comprometemos con la excelencia"},
        {"icon": "heart", "title": "Atención Personalizada", "desc": "Cada cliente es especial para nosotros"},
        {"icon": "shield", "title": "Confianza", "desc": "Años de experiencia nos respaldan"},
        {"icon": "clock", "title": "Disponibilidad", "desc": "Estamos cuando nos necesitas"},
    ],
}


# ===========================================
# SVG ICONS
# ===========================================

SVG_ICONS = {
    "fire": '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 18.657A8 8 0 016.343 7.343S7 9 9 10c0-2 .5-5 2.986-7C14 5 16.09 5.777 17.656 7.343A7.975 7.975 0 0120 13a7.975 7.975 0 01-2.343 5.657z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9.879 16.121A3 3 0 1012.015 11L11 14H9c0 .768.293 1.536.879 2.121z"></path></svg>',
    "star": '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"></path></svg>',
    "users": '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"></path></svg>',
    "clock": '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
    "shield": '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"></path></svg>',
    "heart": '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z"></path></svg>',
    "check": '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>',
    "scissors": '<svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M14.121 14.121L19 19m-7-7l7-7m-7 7l-2.879 2.879M12 12L9.121 9.121m0 5.758a3 3 0 10-4.243 4.243 3 3 0 004.243-4.243zm0-5.758a3 3 0 10-4.243-4.243 3 3 0 004.243 4.243z"></path></svg>',
    "phone": '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>',
    "location": '<svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>',
    "whatsapp": '<svg class="w-6 h-6" fill="currentColor" viewBox="0 0 24 24"><path d="M17.472 14.382c-.297-.149-1.758-.867-2.03-.967-.273-.099-.471-.148-.67.15-.197.297-.767.966-.94 1.164-.173.199-.347.223-.644.075-.297-.15-1.255-.463-2.39-1.475-.883-.788-1.48-1.761-1.653-2.059-.173-.297-.018-.458.13-.606.134-.133.298-.347.446-.52.149-.174.198-.298.298-.497.099-.198.05-.371-.025-.52-.075-.149-.669-1.612-.916-2.207-.242-.579-.487-.5-.669-.51-.173-.008-.371-.01-.57-.01-.198 0-.52.074-.792.372-.272.297-1.04 1.016-1.04 2.479 0 1.462 1.065 2.875 1.213 3.074.149.198 2.096 3.2 5.077 4.487.709.306 1.262.489 1.694.625.712.227 1.36.195 1.871.118.571-.085 1.758-.719 2.006-1.413.248-.694.248-1.289.173-1.413-.074-.124-.272-.198-.57-.347m-5.421 7.403h-.004a9.87 9.87 0 01-5.031-1.378l-.361-.214-3.741.982.998-3.648-.235-.374a9.86 9.86 0 01-1.51-5.26c.001-5.45 4.436-9.884 9.888-9.884 2.64 0 5.122 1.03 6.988 2.898a9.825 9.825 0 012.893 6.994c-.003 5.45-4.437 9.884-9.885 9.884m8.413-18.297A11.815 11.815 0 0012.05 0C5.495 0 .16 5.335.157 11.892c0 2.096.547 4.142 1.588 5.945L.057 24l6.305-1.654a11.882 11.882 0 005.683 1.448h.005c6.554 0 11.89-5.335 11.893-11.893a11.821 11.821 0 00-3.48-8.413z"/></svg>',
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
    
    # Scraped data (new fields)
    reviews: list = field(default_factory=list)
    opening_hours: dict = field(default_factory=dict)
    opening_hours_json: str = ""
    payments: list = field(default_factory=list)
    accessibility: list = field(default_factory=list)
    amenities: list = field(default_factory=list)
    parking: list = field(default_factory=list)
    
    # Computed
    whatsapp_link: str = ""
    phone_link: str = ""
    maps_embed_url: str = ""
    hero_image: str = ""
    gallery_images: list = field(default_factory=list)
    theme: dict = field(default_factory=dict)
    icons: dict = field(default_factory=dict)
    
    def __post_init__(self):
        self._compute_links()
        self._select_theme()
        self._select_hero_image()
        self._prepare_gallery()
        self._generate_content()
        self._select_features()
        self.icons = SVG_ICONS
    
    def _compute_links(self):
        """Generate WhatsApp, phone, and maps links"""
        phone_clean = re.sub(r'[^\d+]', '', self.phone or '')
        if phone_clean and not phone_clean.startswith('+'):
            phone_clean = '+595' + phone_clean.lstrip('0')
        
        message = f"Hola, vi su página web y me gustaría más información sobre {self.name}"
        self.whatsapp_link = f"https://wa.me/{phone_clean}?text={quote_plus(message)}"
        self.phone_link = f"tel:{phone_clean}"
        
        if self.latitude and self.longitude:
            self.maps_embed_url = (
                f"https://www.google.com/maps/embed?pb=!1m18!1m12!1m3!1d3000!2d{self.longitude}!3d{self.latitude}"
                f"!2m3!1f0!2f0!3f0!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0x0!2z{self.latitude}!5e0!3m2!1ses!2spy!4v1"
            )
        else:
            query = quote_plus(f"{self.name} {self.city} Paraguay")
            self.maps_embed_url = f"https://www.google.com/maps?q={query}&output=embed"
    
    def _select_theme(self):
        """Select theme configuration based on category"""
        category_lower = (self.category or '').lower()
        
        for key, theme in THEME_CONFIG.items():
            if key in category_lower:
                self.theme = theme
                return
        
        self.theme = THEME_CONFIG["default"]
    
    def _select_hero_image(self):
        """Select stock hero image based on category"""
        category_lower = (self.category or '').lower()
        name_lower = (self.name or '').lower()
        
        # Check name first (more specific)
        for key, url in STOCK_IMAGES.items():
            if key in name_lower:
                self.hero_image = url
                return
        
        # Then check category
        for key, url in STOCK_IMAGES.items():
            if key in category_lower:
                self.hero_image = url
                return
        
        self.hero_image = STOCK_IMAGES["default"]
    
    def _prepare_gallery(self):
        """Prepare Google photos for gallery section"""
        if self.photo_urls:
            # Get up to 6 photos in higher resolution
            self.gallery_images = [
                url.replace('w80-', 'w600-').replace('h142-', 'h400-')
                for url in self.photo_urls[:6]
            ]
    
    def _generate_content(self):
        """Generate fallback content if not provided by CopyWriter"""
        # Use backstory as description if we have it
        if self.backstory and not self.description:
            self.description = self.backstory
        
        if not self.headline:
            self.headline = self.name
        
        if not self.tagline:
            taglines = {
                "parrilla": "El auténtico sabor del asado paraguayo",
                "dentista": "Tu sonrisa en las mejores manos",
                "odontología": "Cuidamos tu salud dental",
                "barbería": "Donde el estilo se encuentra con la tradición",
                "spa": "Tu refugio de paz y bienestar",
                "gimnasio": "Transforma tu cuerpo, transforma tu vida",
                "veterinaria": "Cuidamos a quienes más quieres",
                "restaurante": "Una experiencia gastronómica única",
                "taller": "Tu vehículo en manos expertas",
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
    
    def _select_features(self):
        """Select category-appropriate features - only if services not provided"""
        # If we have services from CopyWriter, convert them to features format
        if self.services:
            self.features = [
                {"icon": s.get("icon", "star"), "title": s["title"], "desc": s["description"][:100]}
                for s in self.services[:4]
            ]
            return
        
        category_lower = (self.category or '').lower()
        
        for key, features in CATEGORY_FEATURES.items():
            if key in category_lower:
                self.features = features
                return
        
        self.features = CATEGORY_FEATURES["default"]


# ===========================================
# FLASK APP
# ===========================================

def create_app(business: BusinessData = None) -> Flask:
    """Create Flask application"""
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
        return render_template(
            'landing/index_v2.html',
            business=biz,
            theme=biz.theme,
        )
    
    @app.route('/static/<path:filename>')
    def static_files(filename):
        return send_from_directory(str(TEMPLATES_DIR / "static"), filename)
    
    @app.route('/main.js')
    def main_js():
        return send_from_directory(str(TEMPLATES_DIR / "landing"), "main.js")
    
    return app


# ===========================================
# LEAD DATA LOADING
# ===========================================

def load_leads() -> list:
    """Load leads from JSON file"""
    if not DATA_FILE.exists():
        return []
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        return json.load(f)


# Global CopyWriter instance
_copy_writer = None

def get_copy_writer() -> CopyWriter:
    """Get or create the global CopyWriter instance"""
    global _copy_writer
    if _copy_writer is None:
        _copy_writer = CopyWriter()
    return _copy_writer


def create_business_from_lead(lead: dict) -> BusinessData:
    """Convert a lead dict to BusinessData object with rich AI-generated content"""
    address = lead.get('address') or ''
    phone = lead.get('phone') or ''
    
    # Generate rich content using CopyWriter
    writer = get_copy_writer()
    content = writer.generate_content(lead)
    
    # Parse reviews from scraped data
    reviews = []
    scraped_reviews = lead.get('reviews') or []
    if isinstance(scraped_reviews, list):
        for r in scraped_reviews[:10]:  # Limit to 10 reviews
            if isinstance(r, dict):
                reviews.append({
                    'author': r.get('author_name', r.get('author', 'Cliente')),
                    'rating': r.get('rating', 5),
                    'text': r.get('text', r.get('review_text', ''))[:500],  # Limit text length
                    'time': r.get('relative_time_description', r.get('time', ''))
                })
    
    # Parse opening hours
    opening_hours = {}
    hours_data = lead.get('opening_hours') or lead.get('current_opening_hours') or {}
    if isinstance(hours_data, dict):
        weekday_text = hours_data.get('weekday_text', [])
        if isinstance(weekday_text, list):
            day_translations = {
                'Monday': 'Lunes', 'Tuesday': 'Martes', 'Wednesday': 'Miércoles',
                'Thursday': 'Jueves', 'Friday': 'Viernes', 'Saturday': 'Sábado', 'Sunday': 'Domingo'
            }
            for day_str in weekday_text:
                if isinstance(day_str, str) and ':' in day_str:
                    parts = day_str.split(':', 1)
                    day_en = parts[0].strip()
                    hours_text = parts[1].strip() if len(parts) > 1 else ''
                    day_es = day_translations.get(day_en, day_en)
                    opening_hours[day_es] = hours_text
    
    # Parse other scraped data
    payments = lead.get('payments') or lead.get('payment_options') or []
    if isinstance(payments, dict):
        payments = [k for k, v in payments.items() if v]
    
    accessibility = lead.get('accessibility') or []
    if isinstance(accessibility, dict):
        accessibility = [k for k, v in accessibility.items() if v]
    
    amenities = lead.get('amenities') or lead.get('service_options') or []
    if isinstance(amenities, dict):
        amenities = [k for k, v in amenities.items() if v]
    
    parking = lead.get('parking') or []
    if isinstance(parking, dict):
        parking = [k for k, v in parking.items() if v]
    
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
        # Rich content from CopyWriter
        headline=content.get('headline', ''),
        tagline=content.get('tagline', ''),
        backstory=content.get('backstory', ''),
        services=content.get('services', []),
        customer_promise=content.get('customer_promise', ''),
        faqs=content.get('faqs', []),
        cta_text=content.get('cta_text', 'Contáctanos'),
        # Scraped data
        reviews=reviews,
        opening_hours=opening_hours,
        opening_hours_json=json.dumps(opening_hours) if opening_hours else '{}',
        payments=payments if isinstance(payments, list) else [],
        accessibility=accessibility if isinstance(accessibility, list) else [],
        amenities=amenities if isinstance(amenities, list) else [],
        parking=parking if isinstance(parking, list) else [],
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
            'landing/index_v2.html',
            business=business,
            theme=business.theme,
        )
    
    index_file = output_path / "index.html"
    with open(index_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    # Copy main.js to the output folder
    main_js_src = TEMPLATES_DIR / "landing" / "main.js"
    if main_js_src.exists():
        shutil.copy(main_js_src, output_path / "main.js")
    
    return output_path


def slugify(text: str) -> str:
    """Convert text to URL-friendly slug"""
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:50]


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
    
    parser = argparse.ArgumentParser(description='Generate premium landing pages')
    parser.add_argument('--preview', action='store_true', help='Launch preview server')
    parser.add_argument('--generate-all', type=int, metavar='N', help='Generate N static sites')
    parser.add_argument('--business-id', type=int, help='Preview specific business by index')
    parser.add_argument('--port', type=int, default=5001, help='Preview server port')
    
    args = parser.parse_args()
    
    if args.generate_all:
        generate_all_sites(args.generate_all)
    
    elif args.preview or args.business_id is not None:
        leads = load_leads()
        if not leads:
            print("❌ No leads found in leads.json")
            return
        
        idx = args.business_id if args.business_id is not None else 0
        if idx >= len(leads):
            print(f"❌ Business ID {idx} out of range (max: {len(leads)-1})")
            return
        
        business = create_business_from_lead(leads[idx])
        print(f"\n🚀 Starting preview server for: {business.name}")
        print(f"   Category: {business.category}")
        print(f"   Theme: {business.theme.get('mode', 'unknown')} mode")
        print(f"   URL: http://localhost:{args.port}\n")
        
        app = create_app(business)
        app.run(debug=True, port=args.port, host='0.0.0.0')
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
