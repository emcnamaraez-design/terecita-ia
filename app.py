"""
app.py — Servidor principal de Terecita IA
Flask recibe los mensajes del widget y los manda al agente
"""

# ── IMPORTACIONES ──────────────────────────────────────────────────────────
import os                                        # Para leer variables del sistema
import json                                      # Para manejar datos en formato JSON
import base64                                    # Para adjuntar el PDF en el email de Resend
import unicodedata                               # Para limpiar nombres de archivo
import logging                                   # Para que los logs aparezcan en Railway
import requests                                  # Para llamar a la API de Resend
from flask import Flask, request, jsonify        # Framework web
from flask_cors import CORS                      # Permite conexión desde WordPress
from agente_vendedor import obtener_respuesta    # Importa la lógica del agente
from generar_pdf import generar_pdf_cotizacion   # Genera el PDF real de la cotización

# ── LOGGING (Railway captura stdout como logs del servicio) ───────────────
logging.basicConfig(level=logging.INFO, format='%(asctime)s [%(levelname)s] %(message)s')
logger = logging.getLogger('terecita')

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────
app = Flask(__name__)   # Crea la app web
CORS(app)               # Permite que WordPress se conecte sin error de seguridad

# Carpeta donde se guardan los archivos del agente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Email de destino donde llegan las cotizaciones
EMAIL_DESTINO = "contacto@mc-namaraspa.cl"

# Log de errores de email
LOG_EMAIL = os.path.join(BASE_DIR, "email_log.txt")

# ── CONFIGURACIÓN DE RESEND (mismo proveedor que usa McNamara AI) ──────────
RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
RESEND_API_URL = "https://api.resend.com/emails"
# "from" debe ser un dominio verificado en la cuenta de Resend. El dominio
# mc-namaraspa.cl no esta verificado, asi que -igual que en McNamara AI-
# enviamos desde el remitente por defecto de Resend y usamos reply_to para
# que las respuestas lleguen al correo real de la empresa.
RESEND_FROM = "Terecita IA · McNamara SPA <onboarding@resend.dev>"


def enviar_email_resend(to, subject, html, attachments=None, reply_to=None, cc=None):
    """Envia un email usando la API REST de Resend (sin SDK, via requests.post)."""
    if not RESEND_API_KEY:
        raise RuntimeError("RESEND_API_KEY no esta configurada en las variables de entorno")

    payload = {
        "from": RESEND_FROM,
        "to": [to] if isinstance(to, str) else to,
        "subject": subject,
        "html": html,
    }
    if reply_to:
        payload["reply_to"] = reply_to
    if cc:
        payload["cc"] = [cc] if isinstance(cc, str) else cc
    if attachments:
        payload["attachments"] = attachments

    respuesta = requests.post(
        RESEND_API_URL,
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=20,
    )
    if not respuesta.ok:
        raise RuntimeError(f"Resend {respuesta.status_code}: {respuesta.text}")
    return respuesta.json()


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


# ── RUTA DE COTIZACIÓN: genera el PDF real y lo envía por Resend ──────────
@app.route('/enviar-cotizacion', methods=['POST'])
def enviar_cotizacion():
    """
    Recibe los datos del cliente y la lista de productos (la captura el widget
    cuando Terecita muestra el bloque RESUMEN_COMPRA...FIN_RESUMEN), genera el
    PDF real con generar_pdf_cotizacion() y lo envia por email via Resend.

    Body esperado:
    {
      "nombre": "...", "email": "...", "telefono": "...", "empresa": "...",
      "ciudad": "...", "documento": "Boleta"|"Factura", "rut": "...", "razon_social": "...",
      "productos": [{"nombre", "sku", "talla", "color", "cantidad", "precio_unitario"}, ...],
      "resumen": "texto libre opcional para el cuerpo del email"
    }
    """
    try:
        datos = request.get_json() or {}
        nombre_cliente = datos.get('nombre', 'Cliente')
        email_cliente = datos.get('email', '')
        telefono = datos.get('telefono', '')
        empresa = datos.get('empresa', '')
        ciudad = datos.get('ciudad', '')
        documento = datos.get('documento', 'Boleta')
        rut = datos.get('rut', '')
        razon_social = datos.get('razon_social', '')
        productos = datos.get('productos') or []
        resumen = datos.get('resumen', '')

        logger.info(
            "enviar-cotizacion: recibido nombre=%r email=%r telefono=%r empresa=%r "
            "ciudad=%r documento=%r productos=%d",
            nombre_cliente, email_cliente, telefono, empresa, ciudad, documento, len(productos)
        )

        if not email_cliente:
            logger.warning("enviar-cotizacion: email_cliente vacio, el envio puede fallar mas adelante")

        if not productos:
            logger.warning("enviar-cotizacion: sin productos, se rechaza con 400")
            return jsonify({'ok': False, 'error': 'No se recibieron productos para cotizar'}), 400

        datos_cliente = {
            'nombre': nombre_cliente,
            'email': email_cliente,
            'telefono': telefono,
            'empresa': empresa,
            'ciudad': ciudad,
            'documento': documento,
            'rut': rut,
            'razon_social': razon_social,
        }

        # Genera el PDF real con numeración correlativa (COT-00001, COT-00002, ...)
        ruta_pdf, numero_cot = generar_pdf_cotizacion(datos_cliente, productos)
        logger.info("enviar-cotizacion: PDF generado %s (%s)", numero_cot, ruta_pdf)

        with open(ruta_pdf, 'rb') as f:
            pdf_base64 = base64.b64encode(f.read()).decode('utf-8')
        nombre_archivo = nombre_seguro(f"{numero_cot}_{nombre_cliente}.pdf")

        cuerpo_html = f"""
        <h2>Nueva cotización {numero_cot} generada por Terecita IA</h2>
        <p><b>Cliente:</b> {nombre_cliente}</p>
        <p><b>Email:</b> {email_cliente}</p>
        <p><b>Teléfono:</b> {telefono}</p>
        <p><b>Empresa:</b> {empresa}</p>
        <p><b>Ciudad:</b> {ciudad}</p>
        <p><b>Documento:</b> {documento}</p>
        {f'<p><b>RUT:</b> {rut}</p><p><b>Razón Social:</b> {razon_social}</p>' if documento.lower() == 'factura' else ''}
        <p>Revisa el PDF adjunto para el detalle de productos y totales.</p>
        {f'<pre style="white-space:pre-wrap;font-family:inherit;">{resumen}</pre>' if resumen else ''}
        """

        # El cliente es el destinatario principal de su cotizacion. Mientras
        # la cuenta de Resend no tenga un dominio verificado (modo sandbox),
        # Resend exige que TODOS los destinatarios (to y cc) sean el correo
        # del propio dueño de la cuenta — por eso no se puede usar "cc" para
        # avisar a la empresa todavia. Una vez verificado un dominio en
        # resend.com/domains, se puede volver a agregar cc=EMAIL_DESTINO.
        destinatario = email_cliente or EMAIL_DESTINO
        logger.info("enviar-cotizacion: enviando email a %r via Resend", destinatario)

        enviar_email_resend(
            to=destinatario,
            subject=f"Cotización {numero_cot} - Terecita IA - McNamara SPA - {nombre_cliente}",
            html=cuerpo_html,
            attachments=[{'filename': nombre_archivo, 'content': pdf_base64}],
            reply_to=EMAIL_DESTINO,
        )

        logger.info("enviar-cotizacion: email %s enviado correctamente a %r", numero_cot, destinatario)

        # Registrar en log
        with open(LOG_EMAIL, 'a', encoding='utf-8') as log:
            log.write(f"OK | {numero_cot} | {nombre_cliente} | {email_cliente}\n")

        return jsonify({'ok': True, 'numero': numero_cot})

    except Exception as e:
        logger.exception("enviar-cotizacion: fallo al generar/enviar la cotizacion")
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
    """Envía un email de prueba para verificar que Resend funciona"""
    try:
        enviar_email_resend(
            to=EMAIL_DESTINO,
            subject="Test Terecita IA - Email funcionando",
            html="<p>Este es un email de prueba de Terecita IA enviado via Resend ✅</p>",
            reply_to=EMAIL_DESTINO,
        )
        return jsonify({'ok': True, 'mensaje': 'Email de prueba enviado correctamente via Resend'})
    except Exception as e:
        return jsonify({'ok': False, 'error': str(e)})


# ── ARRANCAR EL SERVIDOR ───────────────────────────────────────────────────
if __name__ == '__main__':
    app.run(debug=True, port=5000)   # Solo para pruebas locales
