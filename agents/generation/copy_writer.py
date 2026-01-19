"""
Copy Writer Agent - AI-Powered Content Generation
Solves the 'thin content' problem by generating rich, professional copy

Features:
- Hallucinated professional backstories based on business name
- Detailed service cards with descriptions and icons
- Social proof injection based on ratings
- Category-specific FAQ generation
- Rich nested JSON output for premium templates

Usage:
    from agents.generation.copy_writer import CopyWriter
    
    writer = CopyWriter()
    content = writer.generate_content(lead_data)
"""

import json
import random
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

# Try to import OpenAI for AI-powered generation
try:
    import openai
    HAS_OPENAI = True
except ImportError:
    HAS_OPENAI = False


# ===========================================
# CATEGORY CONTENT TEMPLATES
# ===========================================

CATEGORY_TEMPLATES = {
    # ===== FOOD & DINING =====
    "parrilla": {
        "backstory_templates": [
            "Nacimos con una pasión inquebrantable por la tradición del asado paraguayo. Desde {year}, seleccionamos los mejores cortes de carne para ofrecer una experiencia gastronómica única que honra nuestras raíces guaraníes.",
            "Fundados por una familia apasionada por el arte del fuego, en {name} transformamos cada corte de carne en una obra maestra culinaria. Nuestra dedicación al asado tradicional nos ha convertido en referentes de la parrilla en Paraguay.",
            "Con más de una década de experiencia perfeccionando el arte del asado, {name} nació del sueño de compartir los sabores auténticos del Paraguay. Cada brasa cuenta nuestra historia de pasión y excelencia.",
        ],
        "services": [
            {
                "title": "Parrillada Premium",
                "description": "Nuestra selección de los mejores cortes: vacío, entraña, chorizo criollo y más. Cocinados a fuego lento sobre brasas de quebracho, cada bocado es una celebración de sabor y tradición.",
                "icon": "fire"
            },
            {
                "title": "Asado para Eventos",
                "description": "Llevamos la experiencia del auténtico asado paraguayo a tu evento especial. Servicio completo con parrillero experto, desde cumpleaños íntimos hasta grandes celebraciones corporativas.",
                "icon": "users"
            },
            {
                "title": "Cortes Especiales",
                "description": "Para los verdaderos conocedores: Tomahawk, Ojo de Bife madurado y nuestro exclusivo Costillar de 12 horas. Reserva anticipada recomendada para estos tesoros culinarios.",
                "icon": "star"
            }
        ],
        "faqs": [
            {"question": "¿Hacen delivery de parrillada?", "answer": "Sí, ofrecemos servicio de delivery para pedidos mayores. Empacamos cuidadosamente cada corte para mantener la temperatura y calidad perfecta hasta tu puerta."},
            {"question": "¿Necesito reservación?", "answer": "Para fines de semana y grupos mayores a 6 personas, recomendamos reservar con anticipación por WhatsApp para garantizar la mejor experiencia."},
            {"question": "¿Tienen opciones para vegetarianos?", "answer": "Absolutamente. Ofrecemos deliciosas verduras a la parrilla, provoletas, papas al rescoldo y ensaladas frescas que complementan perfectamente nuestra carta."}
        ],
        "promises": [
            "Únete a nuestros {review_count}+ clientes satisfechos que ya descubrieron el sabor de la excelencia",
            "Con {rating} estrellas de calificación, somos la elección preferida de los amantes del buen asado",
            "Más de {review_count} familias paraguayas confían en nosotros para sus momentos especiales"
        ]
    },
    
    "restaurante": {
        "backstory_templates": [
            "En {name}, creemos que cada comida es una oportunidad de crear memorias. Desde {year}, nuestro equipo de chefs apasionados fusiona técnicas tradicionales con toques contemporáneos para deleitar tu paladar.",
            "Nuestro restaurante nació del amor por la gastronomía y el deseo de ofrecer experiencias culinarias excepcionales. Cada plato cuenta una historia de ingredientes frescos, pasión culinaria y atención al detalle.",
            "Fundado por amantes de la buena mesa, {name} es el resultado de años de perfeccionar recetas y crear un ambiente donde cada visitante se sienta especial y bien atendido.",
        ],
        "services": [
            {
                "title": "Menú Degustación",
                "description": "Un viaje culinario de 5 tiempos que showcase lo mejor de nuestra cocina. Maridaje opcional con vinos seleccionados de nuestra bodega exclusiva.",
                "icon": "star"
            },
            {
                "title": "Eventos Privados",
                "description": "Espacios exclusivos para celebraciones especiales. Menús personalizados, decoración a medida y atención dedicada para hacer de tu evento algo memorable.",
                "icon": "users"
            },
            {
                "title": "Almuerzo Ejecutivo",
                "description": "La mejor opción para profesionales que valoran su tiempo. Menú rotativo de entrada, plato principal y postre servido con la eficiencia que tu agenda demanda.",
                "icon": "clock"
            }
        ],
        "faqs": [
            {"question": "¿Aceptan tarjetas de crédito?", "answer": "Sí, aceptamos todas las tarjetas principales, débito, y también pagos por QR. Facilitamos tu experiencia de principio a fin."},
            {"question": "¿El restaurante es apto para niños?", "answer": "Por supuesto. Contamos con menú infantil, sillas altas y un ambiente familiar. Los más pequeños de la casa siempre son bienvenidos."},
            {"question": "¿Tienen estacionamiento?", "answer": "Contamos con estacionamiento propio gratuito para nuestros clientes, además de fácil acceso en la zona."}
        ],
        "promises": [
            "Únete a nuestros {review_count}+ comensales satisfechos que nos califican con {rating} estrellas",
            "La preferencia de {review_count}+ clientes nos respalda como uno de los mejores restaurantes de la zona",
            "Con {rating} estrellas de calificación, cada visita garantiza una experiencia gastronómica memorable"
        ]
    },
    
    "cafetería": {
        "backstory_templates": [
            "En {name}, cada taza cuenta una historia. Desde {year}, nos dedicamos a seleccionar los mejores granos y perfeccionar el arte del café para ofrecer momentos de auténtico placer en cada sorbo.",
            "Nacimos de la pasión por el café de especialidad y el deseo de crear un espacio acogedor donde las conversaciones fluyen tan naturalmente como nuestro espresso perfectamente extraído.",
            "Somos más que una cafetería; somos un refugio para los amantes del buen café. Cada detalle, desde nuestros granos tostados artesanalmente hasta nuestra repostería casera, está pensado para tu disfrute.",
        ],
        "services": [
            {
                "title": "Café de Especialidad",
                "description": "Granos seleccionados de las mejores fincas, tostados semanalmente para garantizar frescura. Preparaciones en V60, Chemex, AeroPress y espresso tradicional.",
                "icon": "star"
            },
            {
                "title": "Repostería Artesanal",
                "description": "Croissants recién horneados, tortas caseras y una selección de dulces que cambia con las estaciones. El complemento perfecto para tu café favorito.",
                "icon": "heart"
            },
            {
                "title": "Desayunos & Brunch",
                "description": "Desde las 7am, ofrecemos opciones nutritivas y deliciosas para comenzar bien el día. Tostadas de aguacate, bowls energéticos y nuestro famoso brunch de fin de semana.",
                "icon": "clock"
            }
        ],
        "faqs": [
            {"question": "¿Tienen WiFi gratuito?", "answer": "Sí, ofrecemos WiFi de alta velocidad gratuito. Somos el espacio perfecto para trabajar, estudiar o simplemente disfrutar conectado."},
            {"question": "¿Hacen café para llevar?", "answer": "Absolutamente. Preparamos tu café favorito para llevar en vasos eco-friendly. También ofrecemos bolsas de café en grano para que disfrutes en casa."},
            {"question": "¿Aceptan mascotas?", "answer": "En nuestra terraza exterior, las mascotas son bienvenidas. Incluso tenemos agua fresca disponible para tus amigos de cuatro patas."}
        ],
        "promises": [
            "Únete a nuestros {review_count}+ clientes que comienzan su día con nosotros",
            "Con {rating} estrellas, somos el destino favorito de los amantes del buen café",
            "Más de {review_count} cafeinómanos felices avalan nuestra pasión por el café"
        ]
    },
    
    "panadería": {
        "backstory_templates": [
            "En {name}, horneamos con amor desde {year}. Nuestras recetas tradicionales, heredadas de generación en generación, se combinan con técnicas modernas para crear panes y pasteles que despiertan los sentidos.",
            "Cada mañana, antes del amanecer, nuestros maestros panaderos comienzan su labor artesanal. El aroma de pan recién horneado que llena nuestro local es la promesa de calidad que cumplimos día tras día.",
            "Fundada por una familia apasionada por la panadería tradicional, {name} es el resultado de décadas perfeccionando el arte del buen pan. Cada producto lleva nuestra firma de excelencia.",
        ],
        "services": [
            {
                "title": "Pan Artesanal Diario",
                "description": "Horneamos múltiples tandas al día para garantizar frescura. Pan francés, integral, de masa madre, ciabatta y especialidades que varían según la temporada.",
                "icon": "star"
            },
            {
                "title": "Repostería & Confitería",
                "description": "Tortas para ocasiones especiales, facturas tradicionales, medialunas y una variedad de dulces que hacen de cada visita un momento especial.",
                "icon": "heart"
            },
            {
                "title": "Pedidos Especiales",
                "description": "Tortas de cumpleaños, pan para eventos, canastas de regalo y productos personalizados. Hacemos realidad tus pedidos especiales con anticipación.",
                "icon": "users"
            }
        ],
        "faqs": [
            {"question": "¿A qué hora sale el pan caliente?", "answer": "Horneamos durante todo el día. Las primeras tandas salen a las 6:30am, con horneadas adicionales a las 10am, 2pm y 5pm."},
            {"question": "¿Hacen tortas por encargo?", "answer": "Sí, realizamos tortas personalizadas para cumpleaños, bodas y eventos. Recomendamos hacer el pedido con al menos 48 horas de anticipación."},
            {"question": "¿Tienen opciones sin gluten?", "answer": "Contamos con una línea de productos sin gluten elaborados con cuidado en área separada para evitar contaminación cruzada."}
        ],
        "promises": [
            "Más de {review_count} familias confían en nosotros para su pan de cada día",
            "Con {rating} estrellas de calificación, somos la panadería preferida del barrio",
            "Únete a {review_count}+ clientes que ya descubrieron el sabor del pan hecho con amor"
        ]
    },
    
    "pizzería": {
        "backstory_templates": [
            "En {name}, la pizza es nuestra pasión y nuestro arte. Desde {year}, elaboramos cada masa con paciencia, la dejamos fermentar naturalmente y la horneamos a la perfección en nuestro horno de piedra.",
            "Inspirados por las tradiciones napolitanas pero con alma paraguaya, creamos pizzas que celebran los mejores ingredientes locales sobre masas crujientes y sabrosas.",
            "Nuestra historia comenzó con un sueño simple: hacer la mejor pizza de la ciudad. Años después, seguimos perfeccionando cada receta con la misma pasión del primer día.",
        ],
        "services": [
            {
                "title": "Pizzas Clásicas",
                "description": "Nuestras recetas tradicionales: Margarita, Napolitana, Cuatro Quesos y más. Masa crujiente, salsa casera y los mejores ingredientes en cada porción.",
                "icon": "star"
            },
            {
                "title": "Pizzas Gourmet",
                "description": "Creaciones exclusivas del chef: desde pizza de burrata con jamón serrano hasta opciones con ingredientes de temporada que sorprenden y deleitan.",
                "icon": "fire"
            },
            {
                "title": "Delivery Express",
                "description": "Tu pizza favorita en la puerta de tu casa en 30-45 minutos. Empaque térmico especial que mantiene la temperatura y textura perfecta.",
                "icon": "clock"
            }
        ],
        "faqs": [
            {"question": "¿Hacen delivery?", "answer": "Sí, ofrecemos delivery propio en toda la zona. También estamos en las principales apps de delivery. ¡Tu pizza llega caliente garantizado!"},
            {"question": "¿Tienen opciones vegetarianas?", "answer": "Contamos con varias opciones vegetarianas deliciosas, incluyendo nuestra popular pizza de vegetales grillados y la de hongos portobello."},
            {"question": "¿Se puede personalizar la pizza?", "answer": "¡Absolutamente! Podés agregar o quitar ingredientes según tu preferencia. También ofrecemos masa integral y sin gluten bajo pedido."}
        ],
        "promises": [
            "Únete a {review_count}+ amantes de la pizza que nos eligieron como su favorita",
            "Con {rating} estrellas, cada pizza es una promesa de sabor cumplida",
            "Más de {review_count} clientes satisfechos avalan nuestra pasión por la pizza perfecta"
        ]
    },
    
    # ===== BEAUTY & WELLNESS =====
    "barbería": {
        "backstory_templates": [
            "En {name}, el arte del barbero se encuentra con el estilo moderno. Desde {year}, combinamos técnicas clásicas con las últimas tendencias para crear looks que definen tu personalidad.",
            "Fundada por barberos apasionados, nuestra barbería es un espacio donde la tradición del grooming masculino se vive con orgullo. Cada corte es una experiencia, cada visita una transformación.",
            "Más que una barbería, somos un santuario del estilo masculino. Nuestro equipo de expertos está comprometido con la excelencia en cada detalle, desde el corte hasta el acabado final.",
        ],
        "services": [
            {
                "title": "Corte Clásico Premium",
                "description": "Incluye consulta de estilo, corte personalizado, lavado con productos premium y styling final. La experiencia completa del caballero moderno en 45 minutos de atención exclusiva.",
                "icon": "scissors"
            },
            {
                "title": "Barba & Afeitado",
                "description": "Perfilado de barba con navaja, tratamiento con aceites esenciales y toalla caliente. El ritual del afeitado tradicional que tu barba merece.",
                "icon": "star"
            },
            {
                "title": "Paquete Completo",
                "description": "Corte + barba + tratamiento facial + masaje de cuero cabelludo. 90 minutos de atención integral para lucir y sentirte impecable.",
                "icon": "fire"
            }
        ],
        "faqs": [
            {"question": "¿Necesito cita previa?", "answer": "Recomendamos agendar cita por WhatsApp para evitar esperas, pero también atendemos por orden de llegada según disponibilidad."},
            {"question": "¿Atienden niños?", "answer": "Sí, atendemos caballeros de todas las edades. Los pequeños reciben un trato especial y paciente para que disfruten la experiencia."},
            {"question": "¿Qué productos utilizan?", "answer": "Trabajamos con marcas premium como American Crew, Reuzel y productos locales de alta calidad. También los tenemos a la venta."}
        ],
        "promises": [
            "Únete a {review_count}+ caballeros que confían su estilo en nuestras manos",
            "Con {rating} estrellas, somos la barbería de referencia para el hombre moderno",
            "Más de {review_count} clientes satisfechos respaldan nuestra excelencia en cada corte"
        ]
    },
    
    "peluquería": {
        "backstory_templates": [
            "En {name}, transformamos cabello en obras de arte. Desde {year}, nuestro equipo de estilistas profesionales combina creatividad, técnica y pasión para crear looks que realzan tu belleza natural.",
            "Nacimos con la visión de ofrecer servicios de peluquería de primer nivel en un ambiente cálido y acogedor. Cada cliente es único, y cada estilo que creamos refleja su personalidad.",
            "Somos más que una peluquería; somos tu aliado en el cuidado personal. Nuestros estilistas se mantienen a la vanguardia de las tendencias para ofrecerte siempre lo mejor.",
        ],
        "services": [
            {
                "title": "Corte & Styling",
                "description": "Consulta personalizada, corte de precisión adaptado a tu tipo de rostro y cabello, lavado con productos premium y peinado final. Sal lista para conquistar.",
                "icon": "scissors"
            },
            {
                "title": "Color & Mechas",
                "description": "Desde colores naturales hasta fantasía, balayage, mechas y técnicas de vanguardia. Usamos productos de alta gama que cuidan tu cabello mientras lo transforman.",
                "icon": "star"
            },
            {
                "title": "Tratamientos Capilares",
                "description": "Keratina, botox capilar, hidratación profunda y reconstrucción. Devolvemos la vida a tu cabello con tratamientos profesionales de resultados visibles.",
                "icon": "heart"
            }
        ],
        "faqs": [
            {"question": "¿Necesito turno?", "answer": "Recomendamos agendar cita para garantizar atención en el horario que te convenga. Reservá por WhatsApp o llamada telefónica."},
            {"question": "¿Cuánto dura un servicio de color?", "answer": "Dependiendo de la técnica, entre 2 y 4 horas. En tu consulta previa te daremos un tiempo estimado preciso para tu servicio."},
            {"question": "¿Atienden hombres y niños?", "answer": "Sí, atendemos a toda la familia. Tenemos servicios especializados para caballeros y paquetes especiales para los más pequeños."}
        ],
        "promises": [
            "Únete a {review_count}+ clientes que transformaron su look con nosotros",
            "Con {rating} estrellas de calificación, tu satisfacción está garantizada",
            "Más de {review_count} sonrisas reflejan nuestra pasión por la belleza"
        ]
    },
    
    "spa": {
        "backstory_templates": [
            "En {name}, creamos un oasis de tranquilidad en medio de la ciudad. Desde {year}, nos dedicamos a proporcionar experiencias de relajación y bienestar que renuevan cuerpo, mente y espíritu.",
            "Nuestro spa nació de la creencia de que el autocuidado es esencial. Combinamos técnicas ancestrales con tecnología moderna para ofrecer tratamientos que transforman y rejuvenecen.",
            "Somos tu refugio de paz y renovación. Cada tratamiento está diseñado para brindarte un momento de escape, donde el estrés se disuelve y emerge tu mejor versión.",
        ],
        "services": [
            {
                "title": "Masajes Terapéuticos",
                "description": "Desde relajantes hasta descontracturantes, nuestros masajistas certificados adaptan cada sesión a tus necesidades. Aromaterapia incluida para una experiencia sensorial completa.",
                "icon": "heart"
            },
            {
                "title": "Tratamientos Faciales",
                "description": "Limpieza profunda, hidratación, anti-age y tratamientos personalizados según tu tipo de piel. Tecnología de punta para resultados visibles desde la primera sesión.",
                "icon": "star"
            },
            {
                "title": "Circuito Spa",
                "description": "Experiencia completa: sauna, jacuzzi, sala de relajación y masaje de elección. 3 horas de desconexión total para recargar energías.",
                "icon": "fire"
            }
        ],
        "faqs": [
            {"question": "¿Necesito reservar con anticipación?", "answer": "Sí, recomendamos reservar al menos 24 horas antes para garantizar disponibilidad y preparar todo para tu llegada."},
            {"question": "¿Tienen paquetes para parejas?", "answer": "Ofrecemos suites especiales para parejas con tratamientos simultáneos, champagne y ambiente romántico. Ideal para ocasiones especiales."},
            {"question": "¿Qué debo llevar?", "answer": "Solo necesitas traer ropa cómoda. Proporcionamos batas, toallas, sandalias y todos los productos necesarios para tu tratamiento."}
        ],
        "promises": [
            "Únete a {review_count}+ personas que encontraron su momento de paz con nosotros",
            "Con {rating} estrellas, somos el destino preferido para el bienestar",
            "Más de {review_count} clientes renovados confirman nuestra excelencia en relajación"
        ]
    },
    
    "belleza": {
        "backstory_templates": [
            "En {name}, la belleza es nuestro lenguaje. Desde {year}, ayudamos a nuestras clientas a descubrir y realzar su belleza única con servicios de alta calidad y atención personalizada.",
            "Nuestro centro de estética nació del deseo de ofrecer un espacio donde cada mujer se sienta especial. Combinamos profesionalismo con calidez para crear experiencias memorables.",
            "Creemos que cada persona merece sentirse hermosa. Nuestro equipo de profesionales trabaja con pasión para ayudarte a lucir y sentirte increíble todos los días.",
        ],
        "services": [
            {
                "title": "Maquillaje Profesional",
                "description": "Para eventos especiales, sesiones fotográficas o el día de tu boda. Técnicas actuales, productos de primera línea y un acabado que dura todo el día.",
                "icon": "star"
            },
            {
                "title": "Cejas & Pestañas",
                "description": "Diseño de cejas, depilación con hilo, laminado y extensiones de pestañas pelo a pelo o volumen ruso. Enmarca tu mirada con resultados profesionales.",
                "icon": "heart"
            },
            {
                "title": "Uñas & Nail Art",
                "description": "Manicure, pedicure, esmaltado semipermanente, uñas acrílicas y diseños artísticos. Tus manos y pies en manos expertas.",
                "icon": "scissors"
            }
        ],
        "faqs": [
            {"question": "¿Hacen maquillaje a domicilio?", "answer": "Sí, ofrecemos servicio a domicilio para novias y eventos especiales. Consulta disponibilidad y tarifas al momento de agendar."},
            {"question": "¿Cuánto duran las extensiones de pestañas?", "answer": "Con el cuidado adecuado, duran 3-4 semanas. Recomendamos retoques cada 2-3 semanas para mantenerlas perfectas."},
            {"question": "¿Qué marcas de productos utilizan?", "answer": "Trabajamos con marcas profesionales líderes como MAC, Urban Decay, y productos dermatológicamente testeados para el cuidado de la piel."}
        ],
        "promises": [
            "Únete a {review_count}+ clientas que descubrieron su mejor versión con nosotros",
            "Con {rating} estrellas, tu belleza está en las mejores manos",
            "Más de {review_count} transformaciones exitosas avalan nuestra pasión por la belleza"
        ]
    },
    
    # ===== HEALTH & MEDICAL =====
    "dentista": {
        "backstory_templates": [
            "En {name}, tu sonrisa es nuestra prioridad. Desde {year}, nuestro equipo de odontólogos especializados combina tecnología de vanguardia con un trato humano y cálido para cuidar tu salud bucal.",
            "Fundado con la visión de ofrecer odontología de excelencia, nuestro consultorio se ha convertido en referente de confianza para familias que buscan atención dental integral y de calidad.",
            "Creemos que una sonrisa sana transforma vidas. Nuestro compromiso es brindarte tratamientos efectivos en un ambiente cómodo donde te sientas seguro y bien atendido.",
        ],
        "services": [
            {
                "title": "Odontología General",
                "description": "Limpiezas profesionales, empastes estéticos, tratamientos de conducto y extracciones. Cuidamos tu salud bucal con tecnología moderna y técnicas indoloras.",
                "icon": "shield"
            },
            {
                "title": "Estética Dental",
                "description": "Blanqueamiento profesional, carillas de porcelana, diseño de sonrisa. Transformamos tu sonrisa respetando la armonía natural de tu rostro.",
                "icon": "star"
            },
            {
                "title": "Ortodoncia",
                "description": "Brackets tradicionales, estéticos e invisalign. Plan de tratamiento personalizado para lograr la alineación perfecta a cualquier edad.",
                "icon": "check"
            }
        ],
        "faqs": [
            {"question": "¿Atienden urgencias dentales?", "answer": "Sí, reservamos espacios diarios para urgencias. Si tienes dolor intenso, contáctanos inmediatamente y te daremos atención prioritaria."},
            {"question": "¿Aceptan seguro médico?", "answer": "Trabajamos con las principales aseguradoras. Consulta si tu plan está dentro de nuestros convenios para facilitar tu atención."},
            {"question": "¿Es doloroso el tratamiento de conducto?", "answer": "Con técnicas modernas y anestesia efectiva, el tratamiento es prácticamente indoloro. Tu comodidad es nuestra prioridad."}
        ],
        "promises": [
            "Únete a {review_count}+ pacientes que confían su sonrisa en nosotros",
            "Con {rating} estrellas, tu salud bucal está en las mejores manos",
            "Más de {review_count} sonrisas transformadas respaldan nuestra excelencia"
        ]
    },
    
    "veterinaria": {
        "backstory_templates": [
            "En {name}, amamos a las mascotas tanto como tú. Desde {year}, nuestro equipo de veterinarios apasionados brinda atención médica integral con el cariño y profesionalismo que tu compañero peludo merece.",
            "Nacimos con la misión de cuidar la salud y bienestar de las mascotas de nuestra comunidad. Cada paciente es especial, y cada familia recibe nuestra dedicación completa.",
            "Somos más que una veterinaria; somos los guardianes de la salud de tu mejor amigo. Tecnología moderna, corazón grande y compromiso absoluto con el bienestar animal.",
        ],
        "services": [
            {
                "title": "Consultas & Vacunación",
                "description": "Exámenes generales completos, planes de vacunación personalizados, desparasitación y medicina preventiva. Mantenemos a tu mascota sana y feliz.",
                "icon": "shield"
            },
            {
                "title": "Cirugía & Emergencias",
                "description": "Quirófano equipado para cirugías programadas y de emergencia. Esterilizaciones, traumatología y procedimientos especializados con los más altos estándares.",
                "icon": "heart"
            },
            {
                "title": "Peluquería & Spa",
                "description": "Baño, corte, limpieza de oídos y uñas. Tu mascota no solo estará sana, también lucirá hermosa. Productos hipoalergénicos para pieles sensibles.",
                "icon": "star"
            }
        ],
        "faqs": [
            {"question": "¿Atienden emergencias 24 horas?", "answer": "Contamos con servicio de emergencias. Para urgencias fuera de horario, llama a nuestro número de WhatsApp y te indicaremos cómo proceder."},
            {"question": "¿Qué documentos necesito para la primera consulta?", "answer": "Trae el carnet de vacunación si lo tienes. Si es primera vez, crearemos un historial médico completo para tu mascota."},
            {"question": "¿Tienen servicio de internación?", "answer": "Sí, contamos con área de hospitalización con monitoreo constante para pacientes que requieren cuidados especiales."}
        ],
        "promises": [
            "Únete a {review_count}+ familias que confían el cuidado de sus mascotas en nosotros",
            "Con {rating} estrellas, somos la elección de los que más aman a sus mascotas",
            "Más de {review_count} mascotas sanas y felices avalan nuestra dedicación"
        ]
    },
    
    "farmacia": {
        "backstory_templates": [
            "En {name}, tu salud es nuestra vocación. Desde {year}, ofrecemos productos farmacéuticos de calidad, asesoramiento profesional y un servicio cercano que nos convierte en tu farmacia de confianza.",
            "Somos una farmacia comprometida con el bienestar de nuestra comunidad. Nuestro equipo de profesionales está siempre disponible para orientarte en el cuidado de tu salud.",
            "Más que una farmacia, somos tu aliado en salud. Productos de calidad, precios justos y la atención personalizada que mereces en cada visita.",
        ],
        "services": [
            {
                "title": "Medicamentos & Recetas",
                "description": "Amplio stock de medicamentos genéricos y de marca. Atención de recetas con asesoramiento farmacéutico sobre interacciones y dosificación correcta.",
                "icon": "shield"
            },
            {
                "title": "Dermocosmética",
                "description": "Línea completa de productos para el cuidado de la piel, cabello y belleza. Marcas líderes y asesoramiento personalizado para cada tipo de piel.",
                "icon": "star"
            },
            {
                "title": "Servicios de Salud",
                "description": "Control de presión arterial, glucosa, inyectables y test rápidos. Servicios de salud accesibles sin necesidad de cita previa.",
                "icon": "heart"
            }
        ],
        "faqs": [
            {"question": "¿Están abiertos las 24 horas?", "answer": "Consulta nuestros horarios actualizados. Ofrecemos horario extendido y servicio de guardia para emergencias."},
            {"question": "¿Hacen delivery de medicamentos?", "answer": "Sí, ofrecemos servicio de delivery en la zona. Envía tu pedido o receta por WhatsApp y lo llevamos a tu domicilio."},
            {"question": "¿Aceptan obras sociales?", "answer": "Trabajamos con las principales obras sociales y prepagas. Consulta la lista de convenios vigentes."}
        ],
        "promises": [
            "Únete a {review_count}+ familias que confían su salud en nosotros",
            "Con {rating} estrellas, somos la farmacia de confianza del barrio",
            "Más de {review_count} clientes satisfechos nos eligen día a día"
        ]
    },
    
    # ===== SERVICES =====
    "taller": {
        "backstory_templates": [
            "En {name}, tu vehículo está en las mejores manos. Desde {year}, nuestro equipo de mecánicos certificados combina experiencia y tecnología para mantener tu auto en perfectas condiciones.",
            "Fundado por apasionados de la mecánica automotriz, nuestro taller se ha ganado la confianza de miles de conductores que buscan servicio de calidad, honestidad y precios justos.",
            "Somos más que un taller mecánico; somos tu aliado en el cuidado de tu vehículo. Diagnóstico preciso, reparaciones garantizadas y el trato que mereces.",
        ],
        "services": [
            {
                "title": "Mantenimiento Preventivo",
                "description": "Cambio de aceite, filtros, revisión de frenos, líquidos y más. Seguimos las especificaciones del fabricante para mantener tu garantía vigente.",
                "icon": "shield"
            },
            {
                "title": "Diagnóstico Computarizado",
                "description": "Scanner de última generación para detectar fallas en todos los sistemas electrónicos. Identificamos problemas antes de que se conviertan en reparaciones costosas.",
                "icon": "check"
            },
            {
                "title": "Mecánica General",
                "description": "Reparación de motor, caja, suspensión, dirección y más. Repuestos originales y alternativos de calidad con garantía escrita.",
                "icon": "fire"
            }
        ],
        "faqs": [
            {"question": "¿Dan presupuesto sin compromiso?", "answer": "Sí, realizamos diagnóstico y presupuesto detallado sin costo. Tú decides si proceder con la reparación."},
            {"question": "¿Cuánto tiempo toma el service?", "answer": "Un service básico toma aproximadamente 1-2 horas. Para reparaciones mayores, te damos un tiempo estimado preciso."},
            {"question": "¿Tienen servicio de grúa?", "answer": "Contamos con servicio de grúa asociado. Si tu vehículo no puede llegar por sus propios medios, coordinamos el traslado."}
        ],
        "promises": [
            "Únete a {review_count}+ conductores que confían su vehículo en nosotros",
            "Con {rating} estrellas, somos el taller de confianza de la zona",
            "Más de {review_count} autos reparados avalan nuestra experiencia y honestidad"
        ]
    },
    
    "ferretería": {
        "backstory_templates": [
            "En {name}, tenemos todo lo que necesitas para construir, reparar y mejorar. Desde {year}, somos el aliado de hogares y profesionales con la mayor variedad de productos y asesoramiento experto.",
            "Nuestra ferretería nació del deseo de ofrecer un servicio completo: productos de calidad, precios competitivos y el conocimiento para ayudarte a completar cualquier proyecto.",
            "Somos más que una ferretería; somos tu socio en cada proyecto. Desde el tornillo más pequeño hasta la herramienta más especializada, aquí lo encuentras.",
        ],
        "services": [
            {
                "title": "Herramientas & Equipos",
                "description": "Amplia selección de herramientas manuales y eléctricas. Marcas reconocidas, garantía del fabricante y asesoramiento para elegir la correcta.",
                "icon": "fire"
            },
            {
                "title": "Materiales de Construcción",
                "description": "Cemento, hierro, ladrillos, pinturas, sanitarios y más. Stock permanente y entrega a domicilio para obras de cualquier tamaño.",
                "icon": "shield"
            },
            {
                "title": "Corte & Medida",
                "description": "Servicio de corte de vidrios, maderas y caños a medida exacta. Trabajos precisos para que tu proyecto quede perfecto.",
                "icon": "check"
            }
        ],
        "faqs": [
            {"question": "¿Hacen delivery?", "answer": "Sí, ofrecemos entrega a domicilio para compras mayores. Consulta zonas de cobertura y costos según el volumen del pedido."},
            {"question": "¿Tienen servicio de asesoramiento?", "answer": "Nuestro personal está capacitado para orientarte en cualquier proyecto. Traé tus dudas y te ayudamos a encontrar la solución."},
            {"question": "¿Aceptan pagos en cuotas?", "answer": "Sí, aceptamos tarjetas de crédito con opción de cuotas. También ofrecemos financiación propia para clientes frecuentes."}
        ],
        "promises": [
            "Únete a {review_count}+ clientes que encontraron todo lo que buscaban",
            "Con {rating} estrellas, somos la ferretería más completa de la zona",
            "Más de {review_count} proyectos completados con nuestros productos y asesoramiento"
        ]
    },
    
    "gimnasio": {
        "backstory_templates": [
            "En {name}, tu transformación comienza aquí. Desde {year}, ayudamos a personas de todas las edades y niveles a alcanzar sus metas de fitness con equipamiento de primer nivel y entrenadores expertos.",
            "Somos más que un gimnasio; somos una comunidad comprometida con la salud y el bienestar. Cada miembro recibe la motivación y el apoyo necesario para superar sus límites.",
            "Fundado por apasionados del fitness, nuestro gimnasio ofrece el ambiente perfecto para entrenar: equipos modernos, clases dinámicas y profesionales que te guían hacia tu mejor versión.",
        ],
        "services": [
            {
                "title": "Musculación & Cardio",
                "description": "Área completa de pesas libres, máquinas selectorizadas y equipos de cardio de última generación. Entrena a tu ritmo con todo lo que necesitas.",
                "icon": "fire"
            },
            {
                "title": "Clases Grupales",
                "description": "Spinning, funcional, zumba, yoga, pilates y más. Horarios variados para que encuentres la clase perfecta para tu rutina.",
                "icon": "users"
            },
            {
                "title": "Entrenamiento Personal",
                "description": "Planes personalizados con seguimiento de resultados. Nuestros trainers certificados diseñan rutinas específicas para tus objetivos.",
                "icon": "star"
            }
        ],
        "faqs": [
            {"question": "¿Ofrecen clase de prueba?", "answer": "Sí, tu primera visita es gratuita. Vení a conocer nuestras instalaciones, probá las máquinas y sentí el ambiente."},
            {"question": "¿Cuáles son los horarios?", "answer": "Abrimos de lunes a viernes de 6am a 10pm, sábados de 7am a 2pm. Horarios amplios para que entrenes cuando puedas."},
            {"question": "¿Tienen vestuarios y duchas?", "answer": "Contamos con vestuarios completos, duchas, lockers y área de amenities. Vení directo del trabajo y salí listo."}
        ],
        "promises": [
            "Únete a {review_count}+ personas que ya transformaron su vida con nosotros",
            "Con {rating} estrellas, somos el gym donde los resultados hablan",
            "Más de {review_count} miembros activos confían en nosotros para alcanzar sus metas"
        ]
    },
}

# Default template for uncategorized businesses
DEFAULT_TEMPLATE = {
    "backstory_templates": [
        "En {name}, la excelencia es nuestra firma. Desde {year}, nos dedicamos a ofrecer servicios de la más alta calidad, construyendo relaciones duraderas basadas en confianza y profesionalismo.",
        "Nuestro compromiso con la calidad nos ha convertido en referentes en nuestro rubro. Cada cliente recibe atención personalizada y soluciones que superan sus expectativas.",
        "Fundados con pasión y dedicación, hemos crecido gracias a la confianza de nuestros clientes. Tu satisfacción es nuestra mayor recompensa y motivación.",
    ],
    "services": [
        {
            "title": "Servicio Premium",
            "description": "Atención de primera calidad con los más altos estándares de profesionalismo. Tu satisfacción es nuestra prioridad número uno.",
            "icon": "star"
        },
        {
            "title": "Atención Personalizada",
            "description": "Cada cliente es único y merece un trato especial. Adaptamos nuestros servicios a tus necesidades específicas.",
            "icon": "users"
        },
        {
            "title": "Calidad Garantizada",
            "description": "Trabajamos con los mejores productos y técnicas del mercado. Resultados que hablan por sí solos.",
            "icon": "shield"
        }
    ],
    "faqs": [
        {"question": "¿Cómo puedo agendar una cita?", "answer": "Podés contactarnos por WhatsApp o teléfono para coordinar el día y horario que mejor te convenga."},
        {"question": "¿Cuáles son las formas de pago?", "answer": "Aceptamos efectivo, tarjetas de débito/crédito y transferencias bancarias para tu comodidad."},
        {"question": "¿Ofrecen garantía en sus servicios?", "answer": "Sí, todos nuestros servicios cuentan con garantía de satisfacción. Tu tranquilidad es nuestra prioridad."}
    ],
    "promises": [
        "Únete a nuestros {review_count}+ clientes satisfechos que ya nos eligieron",
        "Con {rating} estrellas de calificación, tu satisfacción está garantizada",
        "Más de {review_count} clientes confían en nosotros por nuestra calidad y profesionalismo"
    ]
}


# ===========================================
# COPY WRITER CLASS
# ===========================================

class CopyWriter:
    """
    AI-powered copy writer that generates rich, professional content
    for business landing pages based on minimal input data.
    """
    
    def __init__(self, use_ai: bool = False, api_key: str = None):
        """
        Initialize the copy writer.
        
        Args:
            use_ai: Whether to use OpenAI for content generation (requires API key)
            api_key: OpenAI API key (optional, will use env var if not provided)
        """
        self.use_ai = use_ai and HAS_OPENAI
        if self.use_ai:
            openai.api_key = api_key or os.environ.get('OPENAI_API_KEY')
    
    def _get_template(self, category: str) -> Dict:
        """Get the appropriate template for a business category."""
        category_lower = (category or "").lower()
        
        # Try exact match first
        if category_lower in CATEGORY_TEMPLATES:
            return CATEGORY_TEMPLATES[category_lower]
        
        # Try partial match
        for key, template in CATEGORY_TEMPLATES.items():
            if key in category_lower or category_lower in key:
                return template
        
        # Check for common category keywords
        category_keywords = {
            "parrilla": ["asado", "carne", "parrillada", "churrasquería", "grill"],
            "restaurante": ["comida", "restaurant", "cocina", "gastro", "resto"],
            "cafetería": ["café", "coffee", "cafeteria"],
            "panadería": ["pan", "panaderia", "confitería", "bakery"],
            "pizzería": ["pizza", "pizzeria"],
            "barbería": ["barber", "barbero", "barbershop"],
            "peluquería": ["pelo", "hair", "coiffure", "salón", "salon", "estilista"],
            "spa": ["spa", "wellness", "relax", "masaje"],
            "belleza": ["beauty", "estética", "estetica", "belleza", "makeup", "uñas"],
            "dentista": ["dental", "odonto", "diente", "sonrisa"],
            "veterinaria": ["vet", "mascota", "animal", "pet", "clínica veterinaria"],
            "farmacia": ["farma", "botica", "medicamento", "droguería"],
            "taller": ["mecánic", "auto", "car", "motor", "service"],
            "ferretería": ["ferret", "construc", "herramienta", "material"],
            "gimnasio": ["gym", "fitness", "training", "muscul", "ejercicio"],
        }
        
        for template_key, keywords in category_keywords.items():
            if any(kw in category_lower for kw in keywords):
                return CATEGORY_TEMPLATES[template_key]
        
        return DEFAULT_TEMPLATE
    
    def _generate_year(self) -> int:
        """Generate a realistic founding year."""
        import random
        current_year = 2026
        # Most businesses are 3-15 years old
        return random.randint(current_year - 15, current_year - 3)
    
    def _generate_backstory(self, name: str, category: str, template: Dict) -> str:
        """Generate a professional backstory for the business."""
        backstory = random.choice(template["backstory_templates"])
        year = self._generate_year()
        return backstory.format(name=name, year=year)
    
    def _generate_services(self, template: Dict) -> List[Dict]:
        """Generate service cards from template."""
        return template["services"]
    
    def _generate_promise(self, template: Dict, rating: float, review_count: int) -> str:
        """Generate a social proof promise based on rating."""
        promise = random.choice(template["promises"])
        return promise.format(
            rating=f"{rating:.1f}",
            review_count=review_count if review_count > 0 else random.randint(15, 50)
        )
    
    def _generate_faqs(self, template: Dict) -> List[Dict]:
        """Generate FAQs from template."""
        return template["faqs"]
    
    def _generate_headline(self, name: str, category: str) -> str:
        """Generate a compelling headline."""
        headlines = {
            "parrilla": [
                "El Arte del Fuego",
                "Pasión por el Asado",
                "Donde el Sabor es Tradición",
                "Fuego, Carne y Alma"
            ],
            "restaurante": [
                "Sabores que Inspiran",
                "Una Experiencia Culinaria",
                "Donde Cada Plato Cuenta",
                "El Arte de la Buena Mesa"
            ],
            "cafetería": [
                "Tu Momento, Tu Café",
                "Donde el Café es Pasión",
                "El Ritual del Buen Café",
                "Despierta tus Sentidos"
            ],
            "barbería": [
                "El Arte del Estilo Masculino",
                "Donde el Caballero Moderno se Define",
                "Estilo, Tradición, Excelencia",
                "Tu Mejor Versión Comienza Aquí"
            ],
            "peluquería": [
                "Transforma tu Imagen",
                "Donde la Belleza Cobra Vida",
                "Tu Estilo, Nuestra Pasión",
                "El Arte de Realzar tu Belleza"
            ],
            "dentista": [
                "Sonrisas que Transforman Vidas",
                "Tu Sonrisa en las Mejores Manos",
                "Cuidamos lo que Más Importa",
                "Excelencia en Salud Bucal"
            ],
            "veterinaria": [
                "Amor y Cuidado para tu Mascota",
                "Donde las Mascotas son Familia",
                "Salud y Bienestar Animal",
                "Cuidamos a Quien Más Amas"
            ],
            "gimnasio": [
                "Transforma tu Vida",
                "Tu Mejor Versión te Espera",
                "Fuerza, Disciplina, Resultados",
                "Donde los Límites se Rompen"
            ],
            "taller": [
                "Tu Vehículo en las Mejores Manos",
                "Confianza Sobre Ruedas",
                "Servicio de Excelencia Automotriz",
                "Donde la Calidad es Garantía"
            ],
            "default": [
                "Excelencia en Cada Detalle",
                "Tu Satisfacción es Nuestra Misión",
                "Calidad que Habla por Sí Sola",
                "Donde la Confianza se Construye"
            ]
        }
        
        category_lower = (category or "").lower()
        for key in headlines:
            if key in category_lower:
                return random.choice(headlines[key])
        
        return random.choice(headlines["default"])
    
    def _generate_tagline(self, name: str, category: str) -> str:
        """Generate a tagline/subtitle."""
        taglines = {
            "parrilla": [
                "Los mejores cortes de carne preparados con la tradición y pasión que nos define",
                "Carnes premium, brasas de quebracho y el sabor auténtico del asado paraguayo",
                "Experiencia gastronómica única donde cada corte cuenta una historia de excelencia"
            ],
            "restaurante": [
                "Gastronomía de autor en un ambiente acogedor que despierta todos tus sentidos",
                "Sabores memorables, atención impecable y momentos que perduran",
                "Donde cada plato es una celebración del buen comer"
            ],
            "cafetería": [
                "Café de especialidad, repostería artesanal y el mejor ambiente para tu día",
                "El lugar perfecto para comenzar el día o disfrutar una pausa especial",
                "Donde cada taza cuenta una historia de pasión y dedicación"
            ],
            "barbería": [
                "Cortes de precisión, afeitados tradicionales y el estilo que te define",
                "El santuario del caballero moderno donde tradición y tendencia se encuentran",
                "Más que un corte, una experiencia de estilo y cuidado masculino"
            ],
            "peluquería": [
                "Estilistas profesionales, productos premium y la transformación que mereces",
                "Tu cabello en manos expertas que entienden tu estilo y personalidad",
                "Donde cada visita es una oportunidad de reinventarte"
            ],
            "dentista": [
                "Tecnología de vanguardia y atención humana para tu salud bucal integral",
                "Tratamientos personalizados que transforman sonrisas y cambian vidas",
                "Tu sonrisa perfecta comienza con profesionales que realmente se preocupan"
            ],
            "veterinaria": [
                "Atención veterinaria integral con el amor y profesionalismo que tu mascota merece",
                "Cuidamos la salud de tu compañero peludo como si fuera de nuestra familia",
                "Medicina veterinaria de excelencia con corazón y compromiso"
            ],
            "gimnasio": [
                "Equipamiento de primer nivel, trainers expertos y el ambiente que te impulsa",
                "Tu transformación comienza aquí, con el apoyo que necesitas para lograrlo",
                "Más que un gimnasio, una comunidad comprometida con tu bienestar"
            ],
            "taller": [
                "Mecánicos especializados, diagnóstico preciso y reparaciones garantizadas",
                "Tu vehículo en manos de expertos que trabajan con honestidad y calidad",
                "Servicio automotriz integral donde la confianza se construye"
            ],
            "default": [
                "Profesionales dedicados a brindarte la mejor experiencia y resultados",
                "Calidad, compromiso y atención personalizada en cada servicio",
                "Tu satisfacción es nuestra prioridad y nuestro mayor orgullo"
            ]
        }
        
        category_lower = (category or "").lower()
        for key in taglines:
            if key in category_lower:
                return random.choice(taglines[key])
        
        return random.choice(taglines["default"])
    
    def _generate_cta_text(self, category: str) -> str:
        """Generate call-to-action text."""
        ctas = {
            "parrilla": "Reservar Mesa",
            "restaurante": "Hacer Reservación",
            "cafetería": "Visítanos Hoy",
            "pizzería": "Pedir Ahora",
            "barbería": "Agendar Cita",
            "peluquería": "Reservar Turno",
            "spa": "Reservar Tratamiento",
            "belleza": "Agendar Cita",
            "dentista": "Agendar Consulta",
            "veterinaria": "Agendar Cita",
            "farmacia": "Consultar Stock",
            "taller": "Pedir Presupuesto",
            "ferretería": "Consultar",
            "gimnasio": "Clase de Prueba Gratis",
            "default": "Contáctanos Ahora"
        }
        
        category_lower = (category or "").lower()
        for key, cta in ctas.items():
            if key in category_lower:
                return cta
        
        return ctas["default"]
    
    def generate_content(self, lead_data: Dict) -> Dict:
        """
        Generate rich content for a business landing page.
        
        Args:
            lead_data: Dictionary with business info from leads.json
        
        Returns:
            Dictionary with rich, nested content structure
        """
        name = lead_data.get('name', 'Negocio')
        category = lead_data.get('category', '')
        rating = lead_data.get('rating', 0) or 0
        review_count = lead_data.get('user_ratings_total', 0) or 0
        address = lead_data.get('address', '')
        phone = lead_data.get('phone', '')
        
        # Get appropriate template
        template = self._get_template(category)
        
        # Generate all content pieces
        content = {
            # Business info
            "name": name,
            "category": category,
            "address": address,
            "phone": phone,
            "rating": rating,
            "review_count": review_count,
            
            # Generated copy
            "headline": self._generate_headline(name, category),
            "tagline": self._generate_tagline(name, category),
            "backstory": self._generate_backstory(name, category, template),
            "cta_text": self._generate_cta_text(category),
            
            # Rich content sections
            "services": self._generate_services(template),
            "customer_promise": self._generate_promise(template, rating, review_count),
            "faqs": self._generate_faqs(template),
            
            # Meta content
            "seo_description": f"{name} - {self._generate_tagline(name, category)[:120]}",
        }
        
        return content
    
    def generate_all_content(self, leads: List[Dict]) -> List[Dict]:
        """
        Generate content for multiple leads.
        
        Args:
            leads: List of lead dictionaries
        
        Returns:
            List of content dictionaries
        """
        return [self.generate_content(lead) for lead in leads]


# ===========================================
# CLI & MAIN
# ===========================================

def main():
    """CLI for testing the copy writer."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Generate rich copy for business landing pages')
    parser.add_argument('--test', action='store_true', help='Test with sample data')
    parser.add_argument('--lead-index', type=int, help='Generate content for specific lead index')
    parser.add_argument('--output', type=str, help='Output JSON file path')
    
    args = parser.parse_args()
    
    writer = CopyWriter()
    
    if args.test:
        # Test with sample data
        test_lead = {
            "name": "Carnes de mi Tierra Paraguay",
            "category": "Parrilla",
            "rating": 4.8,
            "user_ratings_total": 36,
            "address": "Av. España 1234, Asunción",
            "phone": "+595 21 123 456"
        }
        
        content = writer.generate_content(test_lead)
        print(json.dumps(content, indent=2, ensure_ascii=False))
    
    elif args.lead_index is not None:
        # Load leads and generate content for specific one
        base_dir = Path(__file__).parent.parent.parent
        leads_file = base_dir / "leads.json"
        
        with open(leads_file, 'r', encoding='utf-8') as f:
            leads = json.load(f)
        
        if args.lead_index >= len(leads):
            print(f"Error: Lead index {args.lead_index} out of range (max: {len(leads)-1})")
            return
        
        content = writer.generate_content(leads[args.lead_index])
        
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(content, f, indent=2, ensure_ascii=False)
            print(f"Content saved to {args.output}")
        else:
            print(json.dumps(content, indent=2, ensure_ascii=False))
    
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
