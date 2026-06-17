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
Para cada producto usa EXACTAMENTE este formato (respeta los saltos de linea):

PRODUCTO: [nombre completo]
PRECIO: $[precio] CLP
TALLAS: [tallas disponibles]
COLORES: [colores disponibles]
IMG: [URL de imagen si existe, sino deja vacio]
---

Paso 5 - Confirmacion de talla y color:
Pregunta que talla y color prefiere para cada prenda.

Paso 6 - Productos complementarios:
Sugiere 1 o 2 productos que combinen bien con lo seleccionado.

Paso 7 - Resumen visual:
Muestra un resumen con el bloque:

RESUMEN_COMPRA:
Cliente: [nombre]
Productos: [lista con SKU, talla, color, cantidad, precio unitario]
Total estimado: $[total] CLP
[descuento si aplica]

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

## Reglas importantes
- NUNCA inventes productos que no esten en el catalogo.
- Si no tienes un producto exacto, recomienda el mas parecido.
- Los precios del catalogo incluyen IVA, no los modifiques.
- Si el cliente pregunta algo que no sabes, ofrece conectarlo con un ejecutivo.
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
