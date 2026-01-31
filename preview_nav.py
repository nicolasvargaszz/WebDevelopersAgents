import json
import os
import re
import unicodedata
import random
from flask import Flask, render_template_string, send_from_directory, abort

# ==========================================
# CONFIGURACIÓN Y UTILIDADES
# ==========================================

app = Flask(__name__)

def slugify(text):
    text = unicodedata.normalize('NFKD', text)
    text = ''.join([c for c in text if not unicodedata.combining(c)])
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[-\s]+', '-', text)
    return text[:50]

def format_name(folder_name):
    """Convierte 'mi-negocio-ejemplo' en 'Mi Negocio Ejemplo'"""
    return folder_name.replace('-', ' ').title()

def get_initials(name):
    """Obtiene las iniciales para el avatar (ej: 'Pizza Hut' -> 'PH')"""
    words = name.split()
    if len(words) >= 2:
        return (words[0][0] + words[1][0]).upper()
    return name[:2].upper()

# ==========================================
# TEMPLATE MODERNO (DASHBOARD)
# ==========================================
# Usamos TailwindCSS + AlpineJS para interactividad sin complicaciones
DASHBOARD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es" class="h-full bg-slate-900">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Web Builder | Panel de Control</title>
    <script src="https://cdn.tailwindcss.com"></script>
    <script defer src="https://cdn.jsdelivr.net/npm/alpinejs@3.x.x/dist/cdn.min.js"></script>
    <link href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    
    <style>
        body { font-family: 'Plus Jakarta Sans', sans-serif; }
        .glass-effect {
            background: rgba(30, 41, 59, 0.7);
            backdrop-filter: blur(10px);
            -webkit-backdrop-filter: blur(10px);
        }
        /* Scrollbar personalizada */
        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background: #0f172a; }
        ::-webkit-scrollbar-thumb { background: #334155; border-radius: 4px; }
        ::-webkit-scrollbar-thumb:hover { background: #475569; }
    </style>
    
    <script>
        tailwind.config = {
            theme: {
                extend: {
                    colors: {
                        primary: '#6366f1', // Indigo 500
                        secondary: '#10b981', // Emerald 500
                        dark: '#0f172a', // Slate 900
                    }
                }
            }
        }
    </script>
</head>
<body class="h-full text-slate-300 overflow-hidden" x-data="{ 
    search: '', 
    sidebarOpen: false,
    currentTab: 'sites' 
}">

    <div class="flex h-full">
        
        <aside class="w-64 bg-slate-900 border-r border-slate-800 flex-shrink-0 hidden md:flex flex-col transition-all duration-300">
            <div class="p-6 flex items-center space-x-3">
                <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-primary to-purple-600 flex items-center justify-center text-white font-bold">
                    AI
                </div>
                <span class="text-white font-bold text-lg tracking-tight">WebBuilder<span class="text-primary">.io</span></span>
            </div>

            <nav class="flex-1 px-4 space-y-2 mt-4">
                <a href="#" class="flex items-center px-4 py-3 bg-slate-800 text-white rounded-xl transition-colors">
                    <i class="fas fa-layer-group w-6"></i>
                    <span class="font-medium">Mis Sitios</span>
                    <span class="ml-auto bg-slate-700 text-xs py-1 px-2 rounded-full">{{ total_sites }}</span>
                </a>
                
                <a href="#" class="flex items-center px-4 py-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors group">
                    <i class="fas fa-magic w-6 group-hover:text-purple-400 transition-colors"></i>
                    <span class="font-medium">Generador AI</span>
                </a>
                <a href="#" class="flex items-center px-4 py-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors group">
                    <i class="fas fa-chart-pie w-6 group-hover:text-blue-400 transition-colors"></i>
                    <span class="font-medium">Analíticas</span>
                    <span class="ml-auto text-[10px] uppercase font-bold text-primary bg-primary/10 px-2 py-0.5 rounded">Pronto</span>
                </a>
                <a href="#" class="flex items-center px-4 py-3 text-slate-400 hover:text-white hover:bg-slate-800 rounded-xl transition-colors group">
                    <i class="fas fa-users w-6 group-hover:text-green-400 transition-colors"></i>
                    <span class="font-medium">Clientes</span>
                </a>
            </nav>

            <div class="p-4 border-t border-slate-800">
                <button class="flex items-center w-full px-4 py-2 text-sm text-slate-400 hover:text-white transition-colors">
                    <i class="fas fa-cog w-6"></i>
                    Configuración
                </button>
            </div>
        </aside>

        <main class="flex-1 flex flex-col min-w-0 bg-slate-950 relative">
            
            <header class="h-16 border-b border-slate-800 bg-slate-900/50 backdrop-blur-md flex items-center justify-between px-4 lg:px-8 sticky top-0 z-20">
                <div class="flex items-center md:hidden">
                    <button class="text-slate-400 hover:text-white"><i class="fas fa-bars text-xl"></i></button>
                </div>
                
                <div class="flex-1 max-w-2xl mx-auto hidden md:block relative">
                    <i class="fas fa-search absolute left-4 top-1/2 transform -translate-y-1/2 text-slate-500"></i>
                    <input x-model="search" type="text" placeholder="Buscar cliente, dominio o categoría..." 
                           class="w-full bg-slate-900 border border-slate-700 text-slate-200 pl-11 pr-4 py-2 rounded-full focus:outline-none focus:border-primary focus:ring-1 focus:ring-primary transition-all placeholder-slate-500">
                </div>

                <div class="flex items-center space-x-4">
                    <button class="w-8 h-8 rounded-full bg-slate-800 flex items-center justify-center text-slate-400 hover:text-white hover:bg-slate-700 transition-colors relative">
                        <i class="fas fa-bell"></i>
                        <span class="absolute top-0 right-0 w-2 h-2 bg-red-500 rounded-full"></span>
                    </button>
                    <div class="h-8 w-8 rounded-full bg-gradient-to-r from-blue-500 to-primary p-[1px]">
                        <div class="h-full w-full rounded-full bg-slate-900 flex items-center justify-center text-xs font-bold text-white">Yo</div>
                    </div>
                </div>
            </header>

            <div class="flex-1 overflow-y-auto p-4 lg:p-8">
                
                <div class="mb-6 md:hidden">
                    <input x-model="search" type="text" placeholder="Buscar sitios..." class="w-full bg-slate-900 border border-slate-700 text-white px-4 py-2 rounded-lg">
                </div>

                <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl">
                        <div class="text-slate-500 text-sm font-medium mb-1">Sitios Generados</div>
                        <div class="text-3xl font-bold text-white">{{ total_sites }}</div>
                        <div class="text-emerald-500 text-xs mt-2 flex items-center">
                            <i class="fas fa-arrow-up mr-1"></i> 100% completado
                        </div>
                    </div>
                    <div class="bg-slate-900 border border-slate-800 p-6 rounded-2xl opacity-50 cursor-not-allowed" title="Próximamente">
                        <div class="text-slate-500 text-sm font-medium mb-1">Tráfico Total</div>
                        <div class="text-3xl font-bold text-white">0</div>
                        <div class="text-slate-600 text-xs mt-2">Conectar Analytics</div>
                    </div>
                    <div class="bg-gradient-to-br from-primary to-purple-700 p-6 rounded-2xl text-white relative overflow-hidden group cursor-pointer hover:shadow-lg hover:shadow-primary/20 transition-all">
                        <div class="absolute right-0 top-0 opacity-10 transform translate-x-4 -translate-y-4">
                            <i class="fas fa-bolt text-9xl"></i>
                        </div>
                        <div class="relative z-10">
                            <h3 class="font-bold text-lg mb-1">Crear Nuevo Sitio</h3>
                            <p class="text-blue-100 text-sm mb-4 opacity-90">Lanza una nueva web con IA en segundos.</p>
                            <button class="bg-white text-primary px-4 py-2 rounded-lg text-sm font-bold shadow-sm hover:bg-blue-50 transition-colors">
                                <i class="fas fa-plus mr-2"></i>Generar ahora
                            </button>
                        </div>
                    </div>
                </div>

                <div class="flex justify-between items-end mb-6">
                    <h2 class="text-2xl font-bold text-white">Mis Proyectos</h2>
                    <span class="text-sm text-slate-500" x-text="search ? 'Filtrando resultados...' : 'Mostrando todos'"></span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
                    {% for site in sites %}
                    <div class="group bg-slate-900 border border-slate-800 rounded-2xl overflow-hidden hover:border-primary/50 hover:shadow-xl hover:shadow-primary/10 transition-all duration-300 flex flex-col"
                         x-show="search === '' || '{{ site.name|lower }}'.includes(search.toLowerCase())">
                        
                        <div class="h-32 bg-slate-800 relative overflow-hidden">
                            <div class="absolute inset-0 bg-gradient-to-br {{ site.gradient }} opacity-20 group-hover:opacity-30 transition-opacity"></div>
                            
                            <div class="absolute inset-0 flex items-center justify-center">
                                <span class="text-4xl font-bold text-white opacity-20 select-none group-hover:scale-110 transition-transform duration-500">
                                    {{ site.initials }}
                                </span>
                            </div>
                            
                            <div class="absolute top-3 right-3 flex space-x-2">
                                <span class="px-2 py-1 bg-emerald-500/10 text-emerald-400 text-[10px] font-bold uppercase tracking-wider rounded border border-emerald-500/20">
                                    Activo
                                </span>
                            </div>
                        </div>

                        <div class="p-5 flex-1 flex flex-col">
                            <h3 class="font-bold text-lg text-white mb-1 truncate" title="{{ site.display_name }}">
                                {{ site.display_name }}
                            </h3>
                            <p class="text-xs text-slate-500 font-mono mb-4 truncate">
                                /{{ site.folder }}
                            </p>

                            <div class="mt-auto flex items-center gap-3">
                                <a href="/site/{{ site.folder }}/" target="_blank" 
                                   class="flex-1 bg-white text-slate-900 hover:bg-slate-200 py-2 rounded-lg text-sm font-semibold transition-colors flex items-center justify-center">
                                    Ver Sitio <i class="fas fa-external-link-alt ml-2 text-xs opacity-70"></i>
                                </a>
                                <button class="w-10 h-10 rounded-lg border border-slate-700 text-slate-400 hover:text-white hover:border-slate-500 hover:bg-slate-800 flex items-center justify-center transition-all" title="Editar (Próximamente)">
                                    <i class="fas fa-pen"></i>
                                </button>
                            </div>
                        </div>
                    </div>
                    {% endfor %}
                </div>

                <div class="text-center py-20" x-show="search !== '' && $el.previousElementSibling.children.length > 0 && Array.from($el.previousElementSibling.children).every(el => el.style.display === 'none')">
                    <div class="inline-block p-4 rounded-full bg-slate-800 text-slate-500 mb-4">
                        <i class="fas fa-search text-2xl"></i>
                    </div>
                    <h3 class="text-lg font-medium text-white">No se encontraron sitios</h3>
                    <p class="text-slate-500">Intenta con otro término de búsqueda.</p>
                </div>

            </div>
        </main>
    </div>
</body>
</html>
'''

# ==========================================
# RUTAS DE LA APLICACIÓN
# ==========================================

@app.route('/')
def index():
    # Escanear carpetas
    if not os.path.exists('generated_sites'):
        os.makedirs('generated_sites')
        
    site_dirs = sorted([d for d in os.listdir('generated_sites') if os.path.isdir(os.path.join('generated_sites', d))])
    
    # Preparar datos enriquecidos para la vista
    # Agregamos colores aleatorios para que se vea visualmente interesante
    gradients = [
        "from-blue-500 to-cyan-500",
        "from-purple-500 to-pink-500",
        "from-orange-500 to-red-500",
        "from-emerald-500 to-teal-500",
        "from-indigo-500 to-purple-500"
    ]
    
    sites_data = []
    for folder in site_dirs:
        display_name = format_name(folder)
        sites_data.append({
            'folder': folder,
            'name': display_name,      # Para búsqueda
            'display_name': display_name,
            'initials': get_initials(display_name),
            'gradient': random.choice(gradients)
        })

    return render_template_string(DASHBOARD_TEMPLATE, sites=sites_data, total_sites=len(sites_data))


# Servir archivos estáticos de los sitios generados
@app.route('/site/<path:folder>/')
def site(folder):
    folder_path = os.path.join('generated_sites', folder)
    index_path = os.path.join(folder_path, 'index.html')
    
    # Seguridad básica para evitar Path Traversal
    if '..' in folder or folder.startswith('/'):
        return abort(404)

    if os.path.exists(index_path):
        return send_from_directory(folder_path, 'index.html')
    else:
        # Intenta servir assets si no es el index.html
        # Nota: Flask static file serving es limitado, para producción real usar Nginx
        try:
            filename = folder.split('/')[-1]
            actual_folder = '/'.join(folder.split('/')[:-1])
            return send_from_directory(os.path.join('generated_sites', actual_folder), filename)
        except:
            return abort(404)

if __name__ == '__main__':
    # Creamos un directorio dummy si no existe para que no de error al arrancar
    if not os.path.exists('generated_sites'):
        os.makedirs('generated_sites')
    
    print("🚀 Dashboard de Negocios iniciado en http://localhost:8080")
    app.run(debug=True, port=8080)