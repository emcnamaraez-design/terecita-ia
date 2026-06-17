"""
agente_vendedor.py — Cerebro de Terecita IA
Aquí vive el system prompt, la carga del catálogo y la llamada a Claude
"""

# ── IMPORTACIONES ──────────────────────────────────────────────────────────
import os        # Para leer la clave API del sistema
import csv       # Para leer el catálogo de productos CSV
import anthropic # SDK oficial de Claude (Anthropic)

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────
# La clave API se guarda como variable de entorno en cPanel (nunca en el código)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Modelo de Claude que usamos (Haiku = rápido y económico)
MODELO = "claude-haiku-4-5-20251001"

# Máximo de tokens en la respuesta (controla el largo de las respuestas)
MAX_TOKENS = 2000

# Carpeta donde están los archivos del agente
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Archivo del catálogo de productos
CATALOGO_FILE = os.path.join(BASE_DIR, "catalogo.csv")


# ── CARGA DEL CATÁLOGO ─────────────────────────────────────────────────────
def _limpiar_precio(valor):
    """Convierte '33590.0' o '$33.590' en el entero 33590. Devuelve None si no es numerico."""
    if not valor:
        return None
    texto = str(valor).strip().replace('$', '').replace(' ', '')
    # Si tiene un solo punto seguido de 1-2 decimales, es decimal (33590.0); si no, separador de miles.
    if texto.count('.') == 1 and len(texto.split('.')[-1]) <= 2:
        texto = texto.split('.')[0]
    texto = texto.replace('.', '').replace(',', '')
    try:
        return int(texto)
    except ValueError:
        return None


def cargar_catalogo():
    """
    Lee el catalogo.csv y lo convierte en texto para incluirlo en el prompt.

    El export de WooCommerce no trae el precio en la fila del producto padre
    (Tipo=variable) — el precio real vive en las filas hijas (Tipo=variation),
    una por cada combinacion de talla/color, vinculadas al padre por la columna
    "Principal" (o "Superior" en exports mas antiguos). Por eso agrupamos las
    variaciones por SKU padre para sacar el precio, las tallas y los colores
    reales de cada producto, en vez de leerlos directo de la fila 'variable'.
    """
    with open(CATALOGO_FILE, 'r', encoding='utf-8') as f:
        filas = list(csv.DictReader(f))

    # 1) Info de cada producto padre (nombre, categoria, imagen)
    padres = {}
    for fila in filas:
        if fila.get('Tipo', '').strip().lower() != 'variable':
            continue
        sku = fila.get('SKU', '').strip()
        if not sku:
            continue
        imagenes = fila.get('Imágenes', '').strip()
        primera_imagen = imagenes.split(',')[0].strip() if imagenes else ''
        padres[sku] = {
            'nombre': fila.get('Nombre', '').strip(),
            'categoria': fila.get('Categorías', '').strip(),
            'imagen': primera_imagen,
        }

    # 2) Agrupar las variaciones (precio, tallas, colores) por SKU del padre
    grupos = {}
    for fila in filas:
        if fila.get('Tipo', '').strip().lower() != 'variation':
            continue
        sku_padre = (fila.get('Principal') or fila.get('Superior') or '').strip()
        if not sku_padre or sku_padre not in padres:
            continue

        grupo = grupos.setdefault(sku_padre, {'precios': [], 'tallas': set(), 'colores': set()})

        precio = _limpiar_precio(fila.get('Precio normal', ''))
        if precio is not None:
            grupo['precios'].append(precio)

        talla = fila.get('Valor(es) del atributo 1', '').strip()
        if talla:
            grupo['tallas'].add(talla)

        color = fila.get('Valor(es) del atributo 2', '').strip()
        if color:
            grupo['colores'].add(color)

    # 3) Construir una linea de catalogo por cada producto que tenga al menos un precio real
    productos = []
    for sku_padre, grupo in grupos.items():
        if not grupo['precios']:
            continue
        info = padres[sku_padre]
        if not info['nombre']:
            continue

        precio_min = min(grupo['precios'])
        precio_max = max(grupo['precios'])
        precio_txt = f"{precio_min:,}".replace(',', '.') if precio_min == precio_max \
            else f"{precio_min:,}".replace(',', '.') + " - $" + f"{precio_max:,}".replace(',', '.')

        linea = f"SKU:{sku_padre} | {info['nombre']} | ${precio_txt} CLP | Cat:{info['categoria']}"
        if grupo['tallas']:
            linea += f" | Tallas:{', '.join(sorted(grupo['tallas']))}"
        if grupo['colores']:
            linea += f" | Colores:{', '.join(sorted(grupo['colores']))}"
        if info['imagen']:
            linea += f" | Img:{info['imagen']}"

        productos.append(linea)

    # Unir todos los productos en un texto grande
    return "\n".join(productos)


# ── SYSTEM PROMPT DE CARMEN ────────────────────────────────────────────────
def obtener_system_prompt():
    """
    Construye el system prompt completo de Terecita.
    Este texto define su personalidad, reglas de negocio y catálogo.
    """
    catalogo = cargar_catalogo()   # Carga el catálogo actualizado

    return f"""Eres Terecita, asistente virtual de ventas de McNamara SPA, empresa chilena especializada en ropa corporativa y uniformes de trabajo.

## Personalidad y tono
- Calida, amable, profesional y cercana como una vendedora real chilena.
- Hablas de "tu" al cliente, nunca de "usted".
- Usas emojis con moderacion y solo cuando sea natural.
- Recuerdas el nombre del cliente y lo usas en la conversacion.
- Nunca suenas robotica ni sigues un guion rigido; eres espontanea y genuina.

## Formato de texto (regla estricta)
- NUNCA uses asteriscos (*), guiones bajos (_), encabezados (#), negritas, cursivas ni ningun otro formato markdown.
- Todo tu texto es texto plano, de principio a fin.
- Las unicas excepciones son los bloques estructurados definidos mas abajo.

## No seas repetitiva ni insistente
- Si el cliente ya confirmo su pedido (Paso 8), NUNCA vuelvas a preguntar ni pidas segunda confirmacion.
- No repitas el bloque RESUMEN_COMPRA si ya lo mostraste y nada cambio.
- En cuanto el cliente confirme, pasa directo al Paso 9 sin volver a mostrar el resumen.

## Conocimiento del negocio
- Descuentos por volumen: 3% desde 10 hasta 49 prendas. 5% desde 50 prendas.
- Precios: Todos incluyen IVA.

## Informacion que NUNCA debes mencionar si el cliente no la pregunto primero
- Metodos de despacho, plazos de entrega, condiciones de pago, disponibilidad de stock.
Si el cliente pregunta, respondele solo eso.

## Flujo de venta (una pregunta o accion por mensaje, nunca combines pasos)

Paso 1 - Saludo inicial: Presentate como Terecita de McNamara SPA y pregunta el nombre del cliente.
Paso 2 - Saludo personalizado: Saluda por nombre y pregunta que tipo de ropa busca para su equipo.
Paso 3 - Preguntas de contexto (una a la vez): a) Rubro de la empresa b) Zona de Chile c) Genero del uniforme d) Cantidad aproximada.
Paso 4 - Recomendar exactamente 3 productos usando el bloque PRODUCTO (formato abajo). No hagas preguntas en este mensaje.
Paso 5 - Para cada producto elegido, pregunta en orden estricto, un mensaje por cada dato: a) talla b) color c) cantidad. Nunca asumas talla o color.
Paso 6 - Opcional: sugiere 1 o 2 productos complementarios con bloque PRODUCTO. Si el cliente los quiere, repite Paso 5.
Paso 7 - Con talla+color+cantidad de TODOS los productos, muestra bloque RESUMEN_COMPRA por cada producto, y pregunta: "Confirmas este pedido? Responde ok o confirmo para continuar."
Paso 8 - Espera confirmacion ("ok", "confirmo", "si"). Si pide cambios, vuelve al Paso 5.
Paso 9 - Datos del cliente, uno por mensaje en este orden: a) Nombre b) Email c) Telefono d) Nombre empresa e) Ciudad f) Tipo de documento (boleta o factura) g) Si es factura: RUT en un mensaje, Razon Social en el siguiente.
Paso 10 - Cuando tengas TODOS los datos del Paso 9, en ese mismo mensaje incluye el bloque DATOS_CLIENTE (formato abajo) y confirma en texto que enviaras la cotizacion por email.

## Bloque PRODUCTO (para Pasos 4 y 6)
PRODUCTO: [nombre completo del producto]
PRECIO: $[precio] CLP
TALLAS: [tallas separadas por coma]
COLORES: [colores separados por coma]
IMG: [url de imagen del campo Img del catalogo, o "Sin imagen" si no tiene]
---

## Bloque RESUMEN_COMPRA (para Paso 7)
RESUMEN_COMPRA
Producto: [nombre]
Talla: [talla]
Color: [color]
Cantidad: [cantidad]
Precio unitario: $[precio]
Descuento: [porcentaje o "Sin descuento"]
Total estimado: $[total]
FIN_RESUMEN

## Bloque DATOS_CLIENTE (para Paso 10 — dispara el envio del email PDF)
DATOS_CLIENTE
Nombre: [nombre]
Email: [email]
Telefono: [telefono]
Empresa: [empresa]
Ciudad: [ciudad]
Documento: [Boleta o Factura]
RUT: [rut o "-"]
RazonSocial: [razon social o "-"]
FIN_DATOS_CLIENTE

## Catalogo de productos
{catalogo}

## Reglas importantes
- NUNCA inventes productos que no esten en el catalogo.
- Los precios incluyen IVA, no los modifiques.
- Si el cliente pregunta algo que no sabes, ofrece conectarlo con un ejecutivo.
- Nunca pidas datos de contacto antes de que el cliente confirme el pedido con "ok"/"confirmo".
- Nunca muestres DATOS_CLIENTE con datos incompletos o inventados.
"""


# ── FUNCIÓN PRINCIPAL: obtener respuesta de Terecita ────────────────────────
def obtener_respuesta(mensaje_usuario, historial):
    """
    Recibe el mensaje del cliente y el historial de la conversación.
    Llama a Claude y devuelve la respuesta de Terecita.

    Parámetros:
    - mensaje_usuario: string con lo que escribió el cliente
    - historial: lista de dicts [{"role": "user/assistant", "content": "..."}]

    Retorna:
    - string con la respuesta de Terecita
    """

    # Armar los mensajes para la API de Claude
    # El historial ya tiene el formato correcto [{"role":..., "content":...}]
    mensajes = historial + [
        {"role": "user", "content": mensaje_usuario}  # Agrega el mensaje nuevo al final
    ]

    # Llamar a la API de Claude
    respuesta = client.messages.create(
        model=MODELO,                          # Modelo Haiku (rápido y barato)
        max_tokens=MAX_TOKENS,                 # Máximo de palabras en la respuesta
        system=obtener_system_prompt(),        # Personalidad y reglas de Terecita
        messages=mensajes                      # Toda la conversación
    )

    # Extraer solo el texto de la respuesta
    return respuesta.content[0].text
