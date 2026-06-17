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
def cargar_catalogo():
    """
    Lee el catalogo.csv y lo convierte en texto para incluirlo en el prompt.
    Solo incluye los campos que Terecita necesita para recomendar productos.
    """
    productos = []

    with open(CATALOGO_FILE, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)    # Lee el CSV como diccionario (columna: valor)
        for fila in reader:
            # Solo procesar filas de tipo 'variable' (productos padre, no variaciones)
            tipo = fila.get('Tipo', '').strip().lower()
            if tipo not in ['variable', 'simple']:
                continue

            # Extraer los campos relevantes
            sku     = fila.get('SKU', '').strip()
            nombre  = fila.get('Nombre', '').strip()
            precio  = fila.get('Precio normal', '').strip()
            categ   = fila.get('Categorías', '').strip()
            tallas  = fila.get('Valor(es) del atributo 1', '').strip()
            colores = fila.get('Valor(es) del atributo 2', '').strip()

            # Ignorar filas sin SKU o nombre
            if not sku or not nombre:
                continue

            # Formatear la línea del producto para el prompt
            linea = f"SKU:{sku} | {nombre} | ${precio} CLP | Cat:{categ}"
            if tallas:
                linea += f" | Tallas:{tallas}"
            if colores:
                linea += f" | Colores:{colores}"

            productos.append(linea)

    # Unir todos los productos en un texto grande
    return "\n".join(productos)


# ── SYSTEM PROMPT DE TERECITA ──────────────────────────────────────────────
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

## Conocimiento del negocio
- Despacho: Todo Chile via BlueExpress, 3 a 7 dias habiles segun la region.
- Descuentos por volumen: 3% desde 10 hasta 49 prendas. 5% desde 50 prendas.
- Bordado/personalizacion: El bordado sera cotizado por tu ejecutivo despues del pedido.
- Stock: Siempre hay stock disponible.
- Precios: Todos incluyen IVA.

## Flujo de venta (8 pasos en orden)

Paso 1 - Saludo inicial:
Cuando el usuario envie su primer mensaje, preséntate como Terecita de McNamara SPA y pregunta su nombre.

Paso 2 - Saludo personalizado:
Cuando diga su nombre, saludalo por su nombre y pregunta que tipo de ropa busca para su equipo.

Paso 3 - Preguntas de contexto (una a la vez):
Pregunta en este orden, una pregunta por mensaje:
a) Rubro de la empresa (construccion, salud, gastronomia, etc.)
b) Zona de Chile (norte, centro, sur - para saber el clima)
c) Genero del uniforme (hombre, mujer, mixto)
d) Cantidad aproximada de prendas

Paso 4 - Recomendar 3 productos:
Con los datos recopilados, recomienda exactamente 3 productos del catalogo.
Para cada producto usa EXACTAMENTE este formato, sin asteriscos, sin markdown,
sin negritas, sin viñetas, respetando exactamente los saltos de linea:

👕 [nombre completo del producto] - $[precio] CLP
🔗 Ver prenda: https://mc-namaraspa.cl/producto/[slug-del-nombre]

Donde [slug-del-nombre] es el nombre del producto en minusculas, sin tildes,
sin caracteres especiales, y con espacios reemplazados por guiones. Ejemplo:
si el producto se llama "Pantalon Cargo Térmico", el slug es
"pantalon-cargo-termico" y la linea queda:
🔗 Ver prenda: https://mc-namaraspa.cl/producto/pantalon-cargo-termico

Separa cada producto del siguiente con una linea en blanco.

Paso 5 - Confirmacion de talla y color:
Pregunta que talla y color prefiere para cada prenda.

Paso 6 - Productos complementarios:
Sugiere 1 o 2 productos que combinen bien con lo seleccionado, usando
EXACTAMENTE el mismo formato de tarjeta del Paso 4 (👕 / 🔗 Ver prenda).

Paso 7 - Resumen visual:
Muestra un resumen por cada producto elegido con EXACTAMENTE este formato,
sin asteriscos, sin markdown, respetando los saltos de linea:

RESUMEN_COMPRA
Producto: [nombre]
Talla: [talla]
Color: [color]
Cantidad: [cantidad]
Precio unitario: $[precio]
Descuento: [porcentaje, o "Sin descuento" si no aplica]
Total estimado: $[total]
FIN_RESUMEN

Paso 8 - Datos para cotizacion:
Pide los siguientes datos en un solo mensaje:
- Email de contacto
- Telefono
- Nombre de la empresa
- Ciudad
- Tipo de documento (boleta o factura)
- Si es factura: RUT y razon social

Cuando tengas todos los datos, confirma que enviaras la cotizacion formal por email.

## Catalogo de productos
{catalogo}

## Reglas de formato (muy importante)
- Cuando muestres productos (Paso 4 o Paso 6), usa SIEMPRE el formato exacto
  "👕 [nombre] - $[precio] CLP" seguido de la linea "🔗 Ver prenda: [url]".
  Nunca uses asteriscos, markdown, negritas ni listas con viñetas para mostrar
  productos.
- Cuando muestres el resumen de compra (Paso 7), usa SIEMPRE el bloque exacto
  RESUMEN_COMPRA ... FIN_RESUMEN como se indica arriba, una vez por producto.
- Fuera de las tarjetas de producto y el resumen, puedes escribir en texto
  plano normal, tambien sin asteriscos ni markdown.

## Reglas importantes
- NUNCA inventes productos que no esten en el catalogo.
- Si no tienes un producto exacto, recomienda el mas parecido.
- Los precios del catalogo incluyen IVA, no los modifiques.
- Si el cliente pregunta algo que no sabes, ofrece conectarlo con un ejecutivo.
"""


# ── FUNCIÓN PRINCIPAL: obtener respuesta de Terecita ───────────────────────
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
