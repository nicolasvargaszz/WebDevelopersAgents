# 🎨 Generation Agent - Generador de Sitios Web Personalizados

Este módulo contiene las herramientas para generar sitios web premium y altamente personalizados para negocios sin presencia web.

## 📁 Estructura

```
agents/generation/
├── client_intake_form.py   # Formulario interactivo de personalización
├── copy_writer.py           # Generador de contenido con IA
├── builder.py               # Constructor de sitios web
└── README.md               # Este archivo
```

---

## 🚀 Dos Formas de Generar Sitios Web

El sistema ofrece **dos modos de generación**:

| Modo | Tiempo | Personalización | Ideal para |
|------|--------|-----------------|------------|
| **Sin Intake** | ⚡ 10 segundos | Básica (datos de Google Maps) | Generación masiva, demos rápidos |
| **Con Intake** | 🎨 10-15 minutos | Completa (colores, logo, servicios, etc.) | Clientes premium, máxima calidad |

---

## ⚡ MODO 1: Generación Rápida (Sin Intake)

Este modo usa **únicamente los datos de Google Maps** para generar el sitio. Es perfecto para crear sitios rápidamente o generar en masa.

### Comando Básico

```bash
python -m agents.generation.builder --business-id "GOOGLE_PLACE_ID" --generate
```

### Ejemplos

```bash
# Generar sitio para un negocio específico
python -m agents.generation.builder --business-id "0x945da8a06a8b2473:0" --generate

# Generar sitios para múltiples negocios (primeros 10 sin website)
python -m agents.generation.builder --generate-all 10
```

### ¿De dónde sale el Google Place ID?

Lo encuentras en `discovered_businesses.json`:

```json
{
  "name": "Maison Mint",
  "google_place_id": "0x945da8a06a8b2473:0",  // ← Este es el ID
  "category": "Peluquería",
  ...
}
```

### Datos que usa (automáticos de Google Maps)

| Dato | Fuente |
|------|--------|
| Nombre del negocio | Google Maps |
| Dirección y teléfono | Google Maps |
| Rating y reseñas | Google Maps |
| Fotos de la galería | Google Maps |
| Horarios | Google Maps |
| Categoría | Google Maps |
| Ubicación GPS | Google Maps |

### Colores Automáticos por Categoría

Sin intake, el sistema asigna colores según la categoría:

- 🍽️ **Restaurantes**: Rojos y naranjas cálidos
- 💇 **Salones de belleza**: Púrpuras y rosas
- 🏥 **Médicos/Dentistas**: Azules profesionales
- 🐾 **Veterinarias**: Verdes naturales
- 🔧 **Talleres**: Grises industriales

---

## 🎨 MODO 2: Generación Personalizada (Con Intake)

Este modo combina **datos de Google Maps + información personalizada del cliente**. Produce sitios de alta calidad con identidad de marca.

### Paso 1: Ejecutar el Formulario de Intake

```bash
# Opción A: Seleccionar negocio desde la lista
python -m agents.generation.client_intake_form

# Opción B: Cargar negocio específico por Google Place ID (recomendado)
python -m agents.generation.client_intake_form --business-id "0x945da8a06a8b2473:0"
```

### Paso 2: Completar el Formulario Interactivo

El formulario pregunta sobre:

#### 🎨 Colores de Marca
- Color primario (principal de la marca)
- Color secundario (complementario)
- Color de acento (botones, CTAs)

#### 🎯 Identidad del Negocio
- **Visión**: Hacia dónde va el negocio
- **Misión**: Propósito y compromiso
- **Valores**: Principios fundamentales
- **Historia de Fundación**: Cómo y cuándo nació
- **USPs** (Unique Selling Points): Diferenciadores clave

#### 📸 Recursos Multimedia
- Logo personalizado (URL directa de imagen)
- Fotos propias del negocio
- Video promocional
- Redes sociales (Instagram, Facebook, TikTok)

> ⚠️ **Importante sobre URLs de imágenes**: Usa URLs **directas** de imagen que terminen en `.jpg`, `.png`, `.webp`. Las URLs de búsqueda de Google (`google.com/url?...`) NO funcionan.
>
> ✅ Válido: `https://i.imgur.com/abc123.jpg`  
> ✅ Válido: `https://drive.google.com/uc?export=view&id=FILE_ID`  
> ❌ Inválido: `https://www.google.com/url?sa=t&source=web...`

#### 🛠️ Servicios y Productos
- Lista de servicios/productos específicos
- Descripciones personalizadas
- Precios (opcional)

#### 🎁 Promociones y Ofertas
- Promociones activas
- Programas de fidelidad
- Ofertas estacionales

#### 📞 Contacto y Reservas
- Número de WhatsApp
- Email
- Tiempo de respuesta estimado
- Sistema de reservas online

### Paso 3: Generar el Sitio

```bash
# El builder detecta automáticamente el intake por nombre o Google Place ID
python -m agents.generation.builder --business-id "0x945da8a06a8b2473:0" --generate
```

O especificando el archivo de intake directamente:

```bash
python -m agents.generation.builder --intake-file intake_data/intake_maison-mint_20260123_153000.json
```

### Archivo de Intake Generado

El formulario crea un archivo JSON en `intake_data/`:

```json
{
  "business_name": "Maison Mint",
  "business_id": "0x945da8a06a8b2473:0",
  "category": "Peluquería",
  "brand_colors": {
    "primary": "#c084fc",
    "secondary": "#a855f7",
    "accent": "#f59e0b"
  },
  "business_identity": {
    "vision": "Ser el salón de belleza más innovador de Asunción",
    "mission": "Transformar la imagen de nuestros clientes",
    "values": ["Calidad", "Innovación", "Atención personalizada"]
  },
  "media_assets": {
    "logo_url": "https://example.com/logo.png",
    "custom_photos": ["https://example.com/photo1.jpg"],
    "instagram_handle": "@maisonmintpy"
  },
  "custom_services": [
    {"name": "Corte de cabello", "price": "₲ 80.000"}
  ],
  "special_offers": {
    "current_promotions": [
      {"title": "2x1 en manicure", "valid_until": "31/03/2026"}
    ]
  }
}
```

---

## 📊 Comparación: Sin Intake vs Con Intake

| Característica | Sin Intake | Con Intake |
|----------------|------------|------------|
| Nombre y dirección | ✅ Google Maps | ✅ Google Maps |
| Teléfono y horarios | ✅ Google Maps | ✅ Google Maps |
| Rating y reseñas | ✅ Google Maps | ✅ Google Maps |
| Fotos de galería | ✅ Google Maps | ✅ Google + Personalizadas |
| **Colores de marca** | 🔸 Automáticos por categoría | ✅ Personalizados |
| **Logo** | ❌ No | ✅ Sí |
| **Visión/Misión/Valores** | ❌ No | ✅ Sí |
| **Servicios con precios** | 🔸 Genéricos | ✅ Personalizados |
| **Promociones** | ❌ No | ✅ Sí |
| **Redes sociales** | 🔸 Si Google tiene | ✅ Configuradas |
| **Sección "Sobre Nosotros"** | 🔸 Básica | ✅ Completa |

---

## 🎯 ¿Cuál Modo Elegir?

### Usa **Sin Intake** cuando:
- Quieres generar muchos sitios rápidamente
- Es una demo o prueba
- El cliente no tiene tiempo para el formulario
- Solo necesitas una página básica funcional

### Usa **Con Intake** cuando:
- El cliente quiere algo premium y personalizado
- La marca tiene colores e identidad definidos
- Hay promociones o servicios específicos
- Quieres diferenciarte de la competencia
- El cliente tiene logo y fotos propias

---

## 📁 Estructura del Sitio Generado

```
generated_sites/0x945da8a06a8b24-maison-mint/
├── index.html              # Página principal
├── assets/
│   ├── css/
│   │   └── styles.css     # Estilos (con colores del intake si aplica)
│   ├── js/
│   │   └── main.js        # Interactividad
│   └── images/            # Imágenes optimizadas
├── data.json              # Todos los datos combinados
└── README.md              # Instrucciones de deployment
```

### Secciones del Sitio

| Sección | Sin Intake | Con Intake |
|---------|------------|------------|
| Hero (Cabecera) | ✅ | ✅ + Colores personalizados |
| About (Nosotros) | Básico | ✅ Visión, Misión, Valores |
| Services (Servicios) | Genéricos | ✅ Con precios y descripciones |
| Gallery (Galería) | Google Photos | ✅ + Fotos personalizadas primero |
| Testimonials | ✅ Reseñas de Google | ✅ |
| Promotions | ❌ | ✅ Ofertas actuales |
| Contact | ✅ | ✅ + WhatsApp configurado |
| Footer | Básico | ✅ + Redes sociales |

---

## 🔄 Actualizar un Sitio Existente

```bash
# 1. Edita el archivo de intake
vim intake_data/intake_maison-mint_*.json

# 2. Regenera el sitio (--force sobrescribe)
python -m agents.generation.builder --business-id "0x945da8a06a8b2473:0" --generate --force
```

---

## 📝 Tips para Mejores Resultados

1. **Colores**: Usa herramientas como [coolors.co](https://coolors.co) para elegir paletas profesionales
2. **Fotos**: Usa imágenes de alta calidad (mínimo 1920x1080)
3. **Logo**: PNG con fondo transparente funciona mejor
4. **Servicios**: Sé específico con precios y descripciones
5. **Historia**: Una buena historia conecta emocionalmente con clientes

---

## 📞 Solución de Problemas

| Problema | Solución |
|----------|----------|
| No encuentra el negocio | Verifica el Google Place ID en `discovered_businesses.json` |
| Colores no se aplican | Asegúrate de usar formato hexadecimal `#RRGGBB` |
| Fotos no cargan | Usa URLs directas de imagen, no URLs de búsqueda de Google |
| Intake no se detecta | El `business_id` del intake debe coincidir con el Google Place ID |

---

**¡Listo para crear sitios web increíbles! 🚀**
