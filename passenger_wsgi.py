"""
passenger_wsgi.py — Conector entre cPanel Passenger y Flask
Este archivo es el punto de entrada que el servidor web usa para iniciar la app.
Para REINICIAR el servidor en cPanel: edita este archivo y guarda (aunque sea un espacio).
"""

import sys
import os

# Agregar la carpeta del agente al path de Python
# Reemplaza 'terecita' con tu usuario de cPanel si es diferente
CARPETA_AGENTE = '/home/terecita/agente_terecita'
sys.path.insert(0, CARPETA_AGENTE)

# Importar la app de Flask
from app import app as application

# ── INSTRUCCIONES DE REINICIO ──────────────────────────────────────────────
# Para reiniciar el servidor cuando hagas cambios:
# 1. Abre este archivo en cPanel File Manager
# 2. Agrega o borra un espacio en cualquier línea de comentario
# 3. Guarda → El servidor Passenger se reinicia automáticamente
