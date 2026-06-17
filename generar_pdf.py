"""
generar_pdf.py — Generador de cotizaciones PDF para McNamara SPA
Usa ReportLab para crear PDFs profesionales con numeración automática
"""

# ── IMPORTACIONES ──────────────────────────────────────────────────────────
import os
import json
from datetime import datetime
from reportlab.lib.pagesizes import letter           # Tamaño carta
from reportlab.lib import colors                     # Colores para el diseño
from reportlab.lib.units import cm                   # Centímetros para medidas
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle,
    Paragraph, Spacer, HRFlowable, Image
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivo que guarda el número de cotización actual
CONTADOR_FILE = os.path.join(BASE_DIR, "contador_cotizacion.json")

# Logo de la empresa
LOGO_FILE = os.path.join(BASE_DIR, "logo.jpg")

# Carpeta donde se guardan los PDFs generados
PDF_DIR = os.path.join(BASE_DIR, "cotizaciones")
os.makedirs(PDF_DIR, exist_ok=True)   # Crea la carpeta si no existe

# Colores corporativos de McNamara SPA
COLOR_OSCURO = colors.HexColor('#1a1a2e')   # Azul oscuro del header
COLOR_ROJO   = colors.HexColor('#e63946')   # Rojo de acento
COLOR_GRIS   = colors.HexColor('#f5f5f5')   # Gris claro para filas alternadas


# ── CONTADOR AUTOMÁTICO ────────────────────────────────────────────────────
def obtener_numero_cotizacion():
    """
    Lee el número actual del contador y lo incrementa en 1.
    Guarda el nuevo número en el archivo JSON.
    Retorna: string tipo "COT-00042"
    """
    # Leer el contador actual
    if os.path.exists(CONTADOR_FILE):
        with open(CONTADOR_FILE, 'r') as f:
            data = json.load(f)
            numero = data.get('ultimo', 0) + 1
    else:
        numero = 1   # Primera cotización

    # Guardar el nuevo número
    with open(CONTADOR_FILE, 'w') as f:
        json.dump({'ultimo': numero}, f)

    # Formatear como COT-00042 (5 dígitos con ceros a la izquierda)
    return f"COT-{str(numero).zfill(5)}"


# ── GENERADOR PRINCIPAL ────────────────────────────────────────────────────
def generar_pdf_cotizacion(datos_cliente, productos):
    """
    Genera un PDF de cotización profesional.

    Parámetros:
    - datos_cliente: dict con {nombre, email, telefono, empresa, ciudad, documento, rut, razon_social}
    - productos: lista de dicts con {nombre, sku, talla, color, cantidad, precio_unitario}

    Retorna:
    - ruta_pdf: string con la ruta completa al PDF generado
    - numero_cot: string con el número de cotización (ej: "COT-00042")
    """

    # Obtener número correlativo
    numero_cot = obtener_numero_cotizacion()

    # Nombre del archivo PDF
    nombre_cliente_safe = datos_cliente.get('nombre', 'cliente').replace(' ', '_')
    nombre_pdf = f"{numero_cot}_{nombre_cliente_safe}.pdf"
    ruta_pdf = os.path.join(PDF_DIR, nombre_pdf)

    # Crear el documento PDF
    doc = SimpleDocTemplate(
        ruta_pdf,
        pagesize=letter,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    # Estilos de texto
    estilos = getSampleStyleSheet()

    estilo_titulo = ParagraphStyle(
        'titulo',
        fontSize=20, fontName='Helvetica-Bold',
        textColor=colors.white, alignment=TA_CENTER
    )
    estilo_subtitulo = ParagraphStyle(
        'subtitulo',
        fontSize=11, fontName='Helvetica-Bold',
        textColor=COLOR_OSCURO
    )
    estilo_normal = ParagraphStyle(
        'normal',
        fontSize=10, fontName='Helvetica',
        textColor=colors.black
    )
    estilo_pequeno = ParagraphStyle(
        'pequeno',
        fontSize=9, fontName='Helvetica',
        textColor=colors.grey
    )

    # Lista de elementos del PDF
    elementos = []

    # ── HEADER ────────────────────────────────────────────────────────────
    # Tabla del header: logo izquierda, datos empresa al centro, cotizacion a la derecha
    fecha_hoy = datetime.now().strftime('%d/%m/%Y')

    logo_celda = ''
    if os.path.exists(LOGO_FILE):
        try:
            logo_celda = Image(LOGO_FILE, width=1.6*cm, height=1.6*cm)
        except Exception:
            logo_celda = ''   # Si el logo esta corrupto o no se puede leer, seguimos sin el

    empresa_parrafo = Paragraph("<b>McNamara SPA</b><br/>Distribuidora Tworld", ParagraphStyle(
        'header_empresa', fontSize=14, fontName='Helvetica-Bold', textColor=colors.white
    ))
    cotizacion_parrafo = Paragraph(
        f"<b>COTIZACIÓN</b><br/>{numero_cot}<br/>Fecha: {fecha_hoy}",
        ParagraphStyle('header_cot', fontSize=11, fontName='Helvetica-Bold',
                       textColor=colors.white, alignment=TA_RIGHT)
    )

    if logo_celda:
        datos_header = [[logo_celda, empresa_parrafo, cotizacion_parrafo]]
        tabla_header = Table(datos_header, colWidths=[2.2*cm, 7.8*cm, 7*cm])
    else:
        datos_header = [[empresa_parrafo, cotizacion_parrafo]]
        tabla_header = Table(datos_header, colWidths=[10*cm, 7*cm])

    tabla_header.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), COLOR_OSCURO),
        ('PADDING', (0, 0), (-1, -1), 15),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
    ]))
    elementos.append(tabla_header)

    # Línea roja de acento
    elementos.append(HRFlowable(width="100%", thickness=3, color=COLOR_ROJO))
    elementos.append(Spacer(1, 0.5*cm))

    # ── DATOS DEL CLIENTE ─────────────────────────────────────────────────
    elementos.append(Paragraph("Datos del cliente", estilo_subtitulo))
    elementos.append(Spacer(1, 0.3*cm))

    nombre   = datos_cliente.get('nombre', '-')
    empresa  = datos_cliente.get('empresa', '-')
    email    = datos_cliente.get('email', '-')
    telefono = datos_cliente.get('telefono', '-')
    ciudad   = datos_cliente.get('ciudad', '-')
    doc_tipo = datos_cliente.get('documento', 'Boleta')
    rut      = datos_cliente.get('rut', '')
    razon    = datos_cliente.get('razon_social', '')

    datos_cliente_tabla = [
        ['Nombre:', nombre,       'Empresa:', empresa],
        ['Email:',  email,        'Teléfono:', telefono],
        ['Ciudad:', ciudad,       'Documento:', doc_tipo],
    ]
    if rut:
        datos_cliente_tabla.append(['RUT:', rut, 'Razón Social:', razon])

    tabla_cliente = Table(datos_cliente_tabla, colWidths=[2.5*cm, 6.5*cm, 2.5*cm, 6.5*cm])
    tabla_cliente.setStyle(TableStyle([
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME', (2, 0), (2, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (0, 0), (0, -1), COLOR_OSCURO),
        ('TEXTCOLOR', (2, 0), (2, -1), COLOR_OSCURO),
        ('PADDING', (0, 0), (-1, -1), 5),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1), [colors.white, COLOR_GRIS]),
    ]))
    elementos.append(tabla_cliente)
    elementos.append(Spacer(1, 0.5*cm))

    # ── TABLA DE PRODUCTOS ────────────────────────────────────────────────
    elementos.append(Paragraph("Detalle de productos", estilo_subtitulo))
    elementos.append(Spacer(1, 0.3*cm))

    # Encabezados de la tabla
    encabezados = ['SKU', 'Producto', 'Talla', 'Color', 'Cant.', 'P. Unit.', 'Total']
    filas = [encabezados]

    total_general = 0

    for p in productos:
        cantidad     = int(p.get('cantidad', 1))
        precio_unit  = int(str(p.get('precio_unitario', 0)).replace('.', '').replace('$', '').replace(',', '').strip() or 0)
        total_prod   = cantidad * precio_unit
        total_general += total_prod

        filas.append([
            p.get('sku', '-'),
            p.get('nombre', '-'),
            p.get('talla', '-'),
            p.get('color', '-'),
            str(cantidad),
            f"${precio_unit:,.0f}",
            f"${total_prod:,.0f}"
        ])

    # Calcular descuento por volumen
    cantidad_total = sum(int(p.get('cantidad', 1)) for p in productos)
    descuento_pct = 0
    if cantidad_total >= 50:
        descuento_pct = 5
    elif cantidad_total >= 10:
        descuento_pct = 3

    descuento_monto = int(total_general * descuento_pct / 100)
    total_con_descuento = total_general - descuento_monto

    # Neto e IVA (los precios ya incluyen IVA)
    neto = int(total_con_descuento / 1.19)
    iva  = total_con_descuento - neto

    # Filas de totales
    filas.append(['', '', '', '', '', 'Subtotal:', f"${total_general:,.0f}"])
    if descuento_pct > 0:
        filas.append(['', '', '', '', '', f'Descuento {descuento_pct}%:', f"-${descuento_monto:,.0f}"])
    filas.append(['', '', '', '', '', 'Neto:', f"${neto:,.0f}"])
    filas.append(['', '', '', '', '', 'IVA 19%:', f"${iva:,.0f}"])
    filas.append(['', '', '', '', '', 'TOTAL:', f"${total_con_descuento:,.0f}"])

    tabla_productos = Table(filas, colWidths=[1.5*cm, 6*cm, 1.5*cm, 2.5*cm, 1.2*cm, 2.3*cm, 3*cm])
    tabla_productos.setStyle(TableStyle([
        # Header
        ('BACKGROUND', (0, 0), (-1, 0), COLOR_OSCURO),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('ALIGN', (0, 0), (-1, 0), 'CENTER'),
        # Filas de datos
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, len(productos)), [colors.white, COLOR_GRIS]),
        ('ALIGN', (4, 1), (-1, -1), 'RIGHT'),
        # Totales en negrita
        ('FONTNAME', (-2, len(productos)+1), (-1, -1), 'Helvetica-Bold'),
        ('TEXTCOLOR', (-2, -1), (-1, -1), COLOR_ROJO),   # Total final en rojo
        ('FONTSIZE', (-2, -1), (-1, -1), 11),
        # Bordes
        ('GRID', (0, 0), (-1, len(productos)), 0.5, colors.lightgrey),
        ('LINEABOVE', (-2, len(productos)+1), (-1, len(productos)+1), 1, COLOR_OSCURO),
        ('PADDING', (0, 0), (-1, -1), 5),
    ]))
    elementos.append(tabla_productos)
    elementos.append(Spacer(1, 1*cm))

    # ── PIE DE PÁGINA ─────────────────────────────────────────────────────
    elementos.append(HRFlowable(width="100%", thickness=1, color=colors.lightgrey))
    elementos.append(Spacer(1, 0.3*cm))
    elementos.append(Paragraph(
        "McNamara SPA — mc-namaraspa.cl — contacto@mc-namaraspa.cl",
        ParagraphStyle('footer', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))
    elementos.append(Paragraph(
        "Cotización generada por Terecita IA — Válida por 10 días hábiles",
        ParagraphStyle('footer2', fontSize=8, textColor=colors.grey, alignment=TA_CENTER)
    ))

    # ── GENERAR EL PDF ────────────────────────────────────────────────────
    doc.build(elementos)

    return ruta_pdf, numero_cot
