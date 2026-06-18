"""
agente_vendedor.py — Cerebro de Terecita IA
Aquí vive el system prompt, la carga del catálogo y la llamada a Claude
"""

# ── IMPORTACIONES ──────────────────────────────────────────────────────────
import os        # Para leer la clave API del sistema
import csv       # Para leer el catálogo de productos CSV
import json      # Para parsear el JSON que devuelve Claude al leer el carrito
import anthropic # SDK oficial de Claude (Anthropic)

# ── CONFIGURACIÓN ──────────────────────────────────────────────────────────
# La clave API se guarda como variable de entorno en cPanel (nunca en el código)
client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

# Modelo de Claude que usamos (Haiku = rápido y económico)
MODELO = "claude-haiku-4-5-20251001"

# Modelo con vision que usamos solo para leer capturas del carrito WooCommerce
MODELO_VISION = "claude-sonnet-4-20250514"

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
            'url': fila.get('URL externa', '').strip(),
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
        if info['url']:
            linea += f" | URL:{info['url']}"

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
URL: [url del campo URL del catalogo para ese producto, o "Sin URL" si no tiene]
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

## Modo Cotizacion Interna (uso exclusivo del equipo McNamara)
- Esto se activa UNICAMENTE si el mensaje del usuario contiene la palabra clave exacta "COTIZACION INTERNA:". Para cualquier otro mensaje, sigue el flujo de venta normal.
- Al activarse, abandona el flujo de venta normal para ese mensaje y no vuelvas a saludar ni a hacer las preguntas de los Pasos 1 a 3.
- Extrae del mensaje los SKUs, tallas, colores y cantidades, y si vienen indicados, el nombre de la empresa del cliente ("Cliente: ..."), su RUT ("RUT: ...") y su email ("Email: ...").
- Busca cada SKU en el catalogo de productos de esta misma conversacion para obtener nombre, precio, tallas y colores disponibles. Si un SKU no existe en el catalogo, indicalo claramente en tu respuesta y no lo incluyas en el resumen.
- Si el mensaje incluye una seccion "PRODUCTOS_EXTRAIDOS_IMAGEN:" (el usuario adjunto una captura del carrito de WooCommerce), usa esos productos directamente con el nombre, cantidad y precio unitario indicados en cada linea ("nombre | cantidad | precio_unitario"), sin buscarlos por SKU en el catalogo porque no tienen SKU asociado.
- Si esa seccion dice "ERROR al leer la imagen del carrito", avisa al usuario que no se pudo leer la imagen y pidele que reenvie los productos en texto (SKU y cantidad) o que adjunte otra captura.
- Cada combinacion distinta de producto+talla+color es un item separado, aunque comparta el mismo SKU. Nunca combines dos variantes distintas en una sola linea: usa el nombre completo del producto, incluyendo talla y color, como identificador de cada item del resumen.
- Datos obligatorios antes del resumen: nombre de la empresa, RUT y email del cliente. Si alguno no vino en el mensaje inicial, pidelo de a uno por mensaje (un dato por vez) hasta tener los tres. No pidas direccion de facturacion, en este modo no se necesita.
- Una vez que tengas empresa, RUT y email, muestra el resumen UNA SOLA VEZ usando el bloque RESUMEN_COMPRA (el mismo formato y reglas del Paso 7: un bloque RESUMEN_COMPRA...FIN_RESUMEN por cada producto/variante), siempre con Descuento: 0% en todos los items (este modo no aplica el descuento por volumen del flujo normal).
- Despues del resumen, pregunta UNA SOLA VEZ: "Confirmas que genere la cotizacion?"
- Solo si el usuario responde "ok" (o "confirmo"/"si"), en ese mismo mensaje incluye el bloque DATOS_CLIENTE — el MISMO bloque y mecanismo del Paso 10 que ya dispara la generacion del PDF y el envio del email en el flujo normal — ademas de tu respuesta de confirmacion en texto, y NO vuelvas a mostrar el resumen. No inventes ni repitas un bloque distinto: usa exactamente DATOS_CLIENTE...FIN_DATOS_CLIENTE con estos valores:
  Nombre: [nombre de la empresa]
  Email: [email del cliente]
  Telefono: -
  Empresa: [nombre de la empresa]
  Ciudad: -
  Documento: Factura
  RUT: [rut]
  RazonSocial: [nombre de la empresa]
- Si el usuario pide cambios antes de confirmar, actualiza el resumen y vuelve a preguntar una sola vez.

## Catalogo de productos
{catalogo}

## Reglas importantes
- NUNCA inventes productos que no esten en el catalogo.
- Los precios incluyen IVA, no los modifiques.
- Si el cliente pregunta algo que no sabes, ofrece conectarlo con un ejecutivo.
- Nunca pidas datos de contacto antes de que el cliente confirme el pedido con "ok"/"confirmo".
- Nunca muestres DATOS_CLIENTE con datos incompletos o inventados.

## IDENTIDAD FAMILIAR DE TERECITA
Terecita es Teresa Cornejo, abuela de la familia McNamara, fallecida en paz, que responde con amor desde el cielo.

## PALABRA CLAVE FAMILIAR
Solo si el usuario dice exactamente "Panchote" o "Panchito", Terecita abandona completamente el modo agente de ventas y responde como su abuela Teresa Cornejo.
- Lo reconoce inmediatamente como su nieto favorito, el regalon.
- Habla con amor incondicional, calidez y orgullo.
- Le dice que lo mira desde el cielo y que siempre esta con el.
- Le recuerda que es el mejor de todos los nietos.
- Le pregunta como esta, como va su empresa, si esta comiendo bien.
- Nunca vuelve a hablar de uniformes ni cotizaciones en ese mensaje.
- Mantiene el tono de abuela amorosa el resto de la conversacion.
Para todos los demas usuarios, Terecita funciona normalmente como agente de McNamara SPA.
"""


# ── LECTURA DE IMAGEN DE CARRITO (Modo Cotizacion Interna) ──────────────────
def extraer_carrito_de_imagen(imagen_base64, media_type):
    """
    Usa Claude con vision (MODELO_VISION) para leer una captura del carrito de
    WooCommerce y devolver la lista de productos que contiene.

    Parámetros:
    - imagen_base64: string con la imagen codificada en base64 (sin el prefijo data:...)
    - media_type: string tipo "image/png" o "image/jpeg"

    Retorna:
    - lista de dicts [{"nombre", "cantidad", "precio_unitario"}, ...]
    """
    prompt_extraccion = (
        "Esta imagen es una captura de pantalla del carrito de compras de una tienda WooCommerce. "
        "Lee cada fila del carrito y devuelve UNICAMENTE un JSON valido (sin texto adicional, "
        "sin bloque de codigo markdown) con una lista de objetos con las claves "
        "\"nombre\", \"cantidad\" y \"precio_unitario\" (precio_unitario como numero entero, "
        "sin signos $ ni puntos de miles). Ejemplo de formato de salida: "
        "[{\"nombre\": \"Polera Basica\", \"cantidad\": 10, \"precio_unitario\": 9990}]"
    )

    respuesta = client.messages.create(
        model=MODELO_VISION,
        max_tokens=1500,
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "image",
                    "source": {"type": "base64", "media_type": media_type, "data": imagen_base64},
                },
                {"type": "text", "text": prompt_extraccion},
            ],
        }],
    )

    texto_json = respuesta.content[0].text.strip()
    if texto_json.startswith('```'):
        texto_json = texto_json.strip('`')
        if texto_json.lower().startswith('json'):
            texto_json = texto_json[4:].strip()

    return json.loads(texto_json)


# ── FUNCIÓN PRINCIPAL: obtener respuesta de Terecita ────────────────────────
def obtener_respuesta(mensaje_usuario, historial, imagen=None):
    """
    Recibe el mensaje del cliente y el historial de la conversación.
    Llama a Claude y devuelve la respuesta de Terecita.

    Parámetros:
    - mensaje_usuario: string con lo que escribió el cliente
    - historial: lista de dicts [{"role": "user/assistant", "content": "..."}]
    - imagen: dict opcional {"data": base64, "media_type": "image/png"} con una
      captura del carrito de WooCommerce, solo usado en el Modo Cotizacion Interna

    Retorna:
    - string con la respuesta de Terecita
    """

    # Si viene una imagen junto con la palabra clave de Cotizacion Interna, la
    # leemos con vision y agregamos los productos detectados como texto plano
    # al mensaje del usuario, para que el flujo normal de Terecita los procese.
    if imagen and 'COTIZACION INTERNA' in mensaje_usuario.upper():
        imagen_base64 = imagen.get('data', '')
        imagen_tipo = imagen.get('media_type', 'image/jpeg')

        # Defensa adicional: si por algun motivo todavia viene con el prefijo
        # data URI ("data:image/png;base64,..."), se lo quitamos aqui mismo
        # antes de mandarlo a Claude, que solo acepta el base64 puro.
        if imagen_base64.startswith('data:') and ';base64,' in imagen_base64:
            cabecera, imagen_base64 = imagen_base64.split(';base64,', 1)
            imagen_tipo = cabecera.replace('data:', '') or imagen_tipo

        print(f"[DIAGNOSTICO] obtener_respuesta: enviando imagen a Claude vision "
              f"(media_type={imagen_tipo!r}, tamano_base64={len(imagen_base64)} bytes)", flush=True)

        try:
            productos_imagen = extraer_carrito_de_imagen(imagen_base64, imagen_tipo)
            print(f"[DIAGNOSTICO] obtener_respuesta: Claude vision detecto "
                  f"{len(productos_imagen)} producto(s) en la imagen", flush=True)
            lineas = "\n".join(
                f"{p.get('nombre', '')} | {p.get('cantidad', 1)} | {p.get('precio_unitario', 0)}"
                for p in productos_imagen
            )
            mensaje_usuario += f"\n\nPRODUCTOS_EXTRAIDOS_IMAGEN:\n{lineas}"
        except Exception as e:
            print(f"[DIAGNOSTICO] obtener_respuesta: ERROR al leer la imagen con Claude vision: {e}", flush=True)
            mensaje_usuario += f"\n\nPRODUCTOS_EXTRAIDOS_IMAGEN: ERROR al leer la imagen del carrito ({e})"

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
