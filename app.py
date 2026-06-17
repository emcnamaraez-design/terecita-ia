"""
app.py — Servidor principal de Terecita IA
Flask recibe los mensajes del widget y los manda al agente
"""

# ── IMPORTACIONES ──────────────────────────────────────────────────────────
import os                                        # Para leer variables del sistema
import json                                      # Para manejar datos en formato JSON
from flask import Flask, request, jsonify        # Framework web
from flask_cors import CORS                      # Permite conexión desde WordPress
from agente_vendedor import obtener_respuesta    # Importa la lógica del agente
import smtplib                                   # Para enviar emails
from email.mime.multipart import MIMEMultipart   # Para armar emails con adjuntos
from email.mime.text import MIMEText             # Para el texto del email
from email.mime.application import MIMEApplication  # Para adjuntar el PDF
import unicodedata                               # Para limpiar nombres de archivo

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────
app = Flask(__name__)   # Crea la app web
CORS(app)               # Permite que WordPress se conecte sin error de seguridad

# Carpeta donde se guardan los archivos del agente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Email de destino donde llegan las cotizaciones
EMAIL_DESTINO = "contacto@mc-namaraspa.cl"

# Log de errores de email
LOG_EMAIL = os.path.join(BASE_DIR, "email_log.txt")

# ── FUNCIÓN PARA LIMPIAR NOMBRES DE ARCHIVO (evita errores con ñ, tildes) ──
def nombre_seguro(texto):
    """Convierte texto con tildes/ñ a texto plano ASCII para usar en nombres de archivo"""
    texto = unicodedata.normalize('NFKD', texto)              # Descompone caracteres especiales
    texto = texto.encode('ascii', 'ignore').decode('ascii')   # Elimina lo que no es ASCII
    texto = texto.replace(' ', '_')                           # Reemplaza espacios con guión bajo
    return texto

# ── RUTA PRINCIPAL: recibe mensajes del widget ─────────────────────────────
@app.route('/chat', methods=['POST'])
def chat():
    """
    Acepta dos formatos de body (compatibilidad con distintos widgets):
    1. { "mensaje": "texto del cliente", "historial": [...] }
    2. { "messages": [{"role": "user"|"assistant", "content": "..."}, ...] }
    Devuelve: { "respuesta": "texto de Terecita", "reply": "texto de Terecita" }
    """
    try:
        datos = request.get_json() or {}

        if 'messages' in datos:
            mensajes_completos = datos.get('messages') or []
            if not mensajes_completos:
                return jsonify({'respuesta': 'Error: messages vacío', 'reply': 'Error: messages vacío'}), 400
            ultimo = mensajes_completos[-1]
            mensaje = ultimo.get('content', '')
            historial = mensajes_completos[:-1]
        else:
            mensaje = datos.get('mensaje', '')          # Extrae el mensaje del cliente
            historial = datos.get('historial', [])      # Extrae el historial de conversación

        if not mensaje:
            return jsonify({'respuesta': 'Error: mensaje vacío', 'reply': 'Error: mensaje vacío'}), 400

        # Llama al cerebro del agente para obtener la respuesta
        respuesta = obtener_respuesta(mensaje, historial)

        return jsonify({'respuesta': respuesta, 'reply': respuesta})    # Devuelve la respuesta al widget

    except Exception as e:
        return jsonify({'respuesta': f'Error: {str(e)}', 'reply': f'Error: {str(e)}'}), 500


# ── RUTA DE EMAIL: envía cotización con PDF ────────────────────────────────
@app.route('/enviar-cotizacion', methods=['POST'])
def enviar_cotizacion():
    """
    Recibe los datos de la cotización y el PDF en base64
    Envía email a contacto@mc-namaraspa.cl con el PDF adjunto
    """
    try:
        datos = request.get_json()
        nombre_cliente = datos.get('nombre', 'Cliente')
        email_cliente = datos.get('email', '')
        resumen = datos.get('resumen', '')
        pdf_bytes = datos.get('pdf_base64', None)

        # Armar el email
        msg = MIMEMultipart()
        msg['Subject'] = f"Cotizacion Terecita IA - McNamara SPA - {nombre_cliente}"
        msg['From'] = EMAIL_DESTINO
        msg['To'] = EMAIL_DESTINO

        # Cuerpo del email
        cuerpo = f"""
Nueva cotización generada por Terecita IA

Cliente: {nombre_cliente}
Email: {email_cliente}

Resumen de la conversación:
{resumen}
        """
        msg.attach(MIMEText(cuerpo, 'plain', 'utf-8'))

        # Adjuntar PDF si viene
        if pdf_bytes:
            import base64
            pdf_data = base64.b64decode(pdf_bytes)
            nombre_archivo = nombre_seguro(f"Cotizacion_{nombre_cliente}.pdf")
            adjunto = MIMEApplication(pdf_data, _subtype='pdf')
            adjunto.add_header('Content-Disposition', 'attachment', filename=nombre_archivo)
            msg.attach(adjunto)

        # Enviar usando el servidor local (localhost:25, sin contraseña)
        with smtplib.SMTP('localhost', 25) as servidor:
            servidor.sendmail(EMAIL_DESTINO, [EMAIL_DESTINO], msg.as_string())

        # Registrar en log
        with open(LOG_EMAIL, 'a', encoding='utf-8') as log:
            log.write(f"OK | {nombre_cliente} | {email_cliente}\n")

        return jsonify({'ok': True})

    except Exception as e:
        with open(LOG_EMAIL, 'a', encoding='utf-8') as log:
            log.write(f"ERROR | {str(e)}\n")
        return jsonify({'ok': False, 'error': str(e)}), 500


# ── RUTA DE SALUD: para verificar que el servidor está vivo ───────────────
@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'ok', 'agente': 'Terecita IA - McNamara SPA'})


# ── RUTA DE PRUEBA DE EMAIL ────────────────────────────────────────────────
@app.route('/test-email', methods=['GET'])
def test_email():
    """Envía un email de prueba para verificar que el SMTP funciona"""
    try:
        msg = MIMEMultipart()
        msg['Subject'] = "Test Terecita IA - Email funcionando"
        msg['From'] = EMAIL_DESTINO
        msg['To'] = EMAIL_DESTINO
        msg.attach(MIMEText("Este es un email de prueba de Terecita IA ✅", 'plain', 'utf-8'))

        with smtplib.SMTP('localhost', 25) as s:
            s.sendmail(EMAIL_DESTINO, [EMAIL_DESTINO], msg.as_string())

        return jsonify({'ok': True, 'mensaje': 'Email de prueba enviado correctamente'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


# ── ARRANCAR EL SERVIDOR ───────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)   # Solo para pruebas locales
