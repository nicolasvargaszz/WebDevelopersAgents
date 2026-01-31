
import json
import os
import re
import unicodedata
from flask import Flask, render_template_string, send_from_directory, abort

# Utilidad para normalizar y slugificar nombres (igual que builder.py)
def slugify(text):
  text = unicodedata.normalize('NFKD', text)
  text = ''.join([c for c in text if not unicodedata.combining(c)])
  text = text.lower().strip()
  text = re.sub(r'[^\w\s-]', '', text)
  text = re.sub(r'[-\s]+', '-', text)
  return text[:50]

# Cargar los datos filtrados
with open('datos_definitivos_limpio.json', 'r', encoding='utf-8') as f:
  negocios = json.load(f)


# Mostrar todos los folders generados, usando el nombre del folder como display
site_dirs = sorted([d for d in os.listdir('generated_sites') if os.path.isdir(os.path.join('generated_sites', d))])
site_map = {folder: folder for folder in site_dirs}

# Flask app
app = Flask(__name__)

# Flask app
app = Flask(__name__)

NAV_TEMPLATE = '''
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>Negocios sin repetidos</title>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css">
</head>
<body>
<nav class="navbar navbar-expand-lg navbar-dark bg-dark mb-4">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">Negocios únicos</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
      <ul class="navbar-nav">
        {% for name, folder in site_map.items() %}
        <li class="nav-item">
          <a class="nav-link" href="/site/{{ folder }}/" target="_blank">{{ name }}</a>
        </li>
        {% endfor %}
      </ul>
    </div>
  </div>
</nav>
<div class="container">
  <h2>Negocios únicos: {{ site_map|length }}</h2>
  <ul>
    {% for name, folder in site_map.items() %}
      <li><a href="/site/{{ folder }}/" target="_blank">{{ name }}</a></li>
    {% endfor %}
  </ul>
</div>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(NAV_TEMPLATE, site_map=site_map)


# Servir archivos estáticos de los sitios generados
@app.route('/site/<path:folder>/')
def site(folder):
  folder_path = os.path.join('generated_sites', folder)
  index_path = os.path.join(folder_path, 'index.html')
  if os.path.exists(index_path):
    return send_from_directory(folder_path, 'index.html')
  else:
    return abort(404)

if __name__ == '__main__':
    app.run(debug=True, port=8080)
