<?php
/**
 * The template for displaying the footer.
 * NOTA: El widget de Terecita IA está al final de este archivo.
 *
 * @package Astra
 * @since 1.0.0
 */
if ( ! defined( 'ABSPATH' ) ) {
	exit;
}
?>
<?php astra_content_bottom(); ?>
	</div> <!-- ast-container -->
	</div><!-- #content -->
<?php
	astra_content_after();
	astra_footer_before();
	astra_footer();
	astra_footer_after();
?>
	</div><!-- #page -->
<?php
	astra_body_bottom();
	wp_footer();
?>
	</body>
</html>

<!-- ═══════════════════════════════════════════════════════════
     WIDGET CHAT TERECITA IA — McNamara SPA
     Reemplaza la URL del fetch con la de tu subdominio del agente
     URL actual: https://web-production-8bded.up.railway.app/chat
     ═══════════════════════════════════════════════════════════ -->

<style>
/* ── Contenedor principal ── */
#terecita-chat {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  font-family: Arial, sans-serif;
}

/* ── Ventana del chat ── */
#terecita-ventana {
  display: none;
  flex-direction: column;
  overflow: hidden;
  background: white;
  border-radius: 15px;
  box-shadow: 0 5px 30px rgba(0,0,0,0.3);
  width: 360px;
  height: 520px;
}

/* ── Barra de estado "En línea ahora" ── */
#terecita-status-bar {
  background: #2d9e5f;
  color: white;
  font-size: 11px;
  text-align: center;
  padding: 4px 10px;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

/* ── Header del chat ── */
#terecita-header {
  background: #1a1a2e;
  color: white;
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

/* ── Área de mensajes ── */
#terecita-mensajes {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background: #f5f5f5;
}

/* ── Burbujas de mensajes ── */
.terecita-msg-usuario {
  text-align: right;
  margin: 6px 0;
}
.terecita-msg-usuario span {
  background: #1a1a2e;
  color: white;
  padding: 8px 12px;
  border-radius: 15px 15px 0 15px;
  display: inline-block;
  max-width: 80%;
  font-size: 13px;
}
.terecita-msg-agente {
  text-align: left;
  margin: 6px 0;
}
.terecita-msg-agente span {
  background: white;
  color: #333;
  padding: 8px 12px;
  border-radius: 15px 15px 15px 0;
  display: inline-block;
  max-width: 80%;
  font-size: 13px;
  border: 1px solid #e0e0e0;
  white-space: pre-wrap;
}

/* ── Tarjeta de producto ── */
.terecita-producto-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 10px;
  margin: 5px 0;
  font-size: 12px;
}
.terecita-producto-card strong {
  color: #1a1a2e;
  display: block;
  margin-bottom: 4px;
}
.terecita-producto-card .precio {
  color: #e63946;
  font-weight: bold;
  font-size: 14px;
}
.terecita-producto-card a {
  display: inline-block;
  margin-top: 6px;
  background: #1a1a2e;
  color: white;
  padding: 5px 10px;
  border-radius: 5px;
  text-decoration: none;
  font-size: 11px;
}

/* ── Indicador de escritura ── */
.terecita-typing {
  color: #999;
  font-size: 12px;
  font-style: italic;
  padding: 5px;
}

/* ── Área de input ── */
#terecita-input-area {
  display: flex;
  padding: 10px;
  background: white;
  border-top: 1px solid #e0e0e0;
  gap: 8px;
  flex-shrink: 0;
}
#terecita-input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 8px 14px;
  font-size: 13px;
  outline: none;
}
#terecita-enviar {
  background: #1a1a2e;
  color: white;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 16px;
}

/* ── Footer del widget ── */
#terecita-footer-brand {
  background: #f0f0f0;
  color: #999;
  font-size: 10px;
  text-align: center;
  padding: 4px;
  flex-shrink: 0;
}
#terecita-footer-brand a {
  color: #666;
  text-decoration: none;
}

/* ── Botón flotante de apertura ── */
#terecita-btn {
  background: linear-gradient(135deg, #1a1a2e, #e63946);
  color: white;
  border: none;
  border-radius: 30px;
  padding: 14px 22px;
  font-size: 15px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  animation: terecita-pulso 2.5s infinite;
}
@keyframes terecita-pulso {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.04); }
}

/* ── Responsive móvil ── */
@media(max-width: 480px) {
  #terecita-ventana {
    width: calc(100vw - 30px);
    height: 72vh;
  }
  #terecita-chat {
    bottom: 15px;
    right: 15px;
  }
}
</style>

<div id="terecita-chat">

  <!-- Ventana del chat -->
  <div id="terecita-ventana">

    <!-- Barra verde "En línea ahora" -->
    <div id="terecita-status-bar">🟢 En línea ahora</div>

    <!-- Header -->
    <div id="terecita-header">
      <span style="font-size:14px;">🤖 Terecita - McNamara SPA</span>
      <div style="display:flex;align-items:center;gap:8px;">
        <button onclick="limpiarConversacion()"
          style="background:none;border:none;color:#aaa;cursor:pointer;font-size:11px;">
          Nueva conversación
        </button>
        <button onclick="toggleChat()"
          style="background:none;border:none;color:white;font-size:20px;cursor:pointer;line-height:1;">
          ×
        </button>
      </div>
    </div>

    <!-- Mensajes -->
    <div id="terecita-mensajes"></div>

    <!-- Input -->
    <div id="terecita-input-area">
      <input id="terecita-input" type="text" placeholder="Escribe tu mensaje..."
        onkeypress="if(event.key==='Enter') enviarMensaje()">
      <button id="terecita-enviar" onclick="enviarMensaje()">➤</button>
    </div>

    <!-- Footer de marca -->
    <div id="terecita-footer-brand">
      Agente IA desarrollado por
      <a href="https://www.estudiowebseo.cl" target="_blank">estudiowebseo.cl</a>
    </div>

  </div>

  <!-- Botón flotante -->
  <button id="terecita-btn" onclick="toggleChat()">🤖 Habla con Terecita</button>

</div>

<script>
// ── URL del agente (cambia esto si usas otro subdominio) ──────────────────
const TERECITA_URL = 'https://web-production-8bded.up.railway.app/chat';

// ── Estado del chat ───────────────────────────────────────────────────────
let historial = [];         // Historial de la conversación para la API
let chatAbierto = false;    // Si el chat está visible o no
let primerMensaje = true;   // Para saber si es el inicio de la conversación

// ── Abrir/cerrar el chat ──────────────────────────────────────────────────
function toggleChat() {
  chatAbierto = !chatAbierto;
  const ventana = document.getElementById('terecita-ventana');
  const btn = document.getElementById('terecita-btn');

  ventana.style.display = chatAbierto ? 'flex' : 'none';
  btn.style.display = chatAbierto ? 'none' : 'block';

  // Si es la primera vez que se abre, enviar saludo inicial
  if (chatAbierto && primerMensaje) {
    primerMensaje = false;
    cargarHistorialLocal();
    if (historial.length === 0) {
      enviarMensaje('INICIO');  // Dispara el saludo de Terecita
    }
  }
}

// ── Guardar/cargar historial en localStorage (persiste entre páginas) ─────
function guardarHistorialLocal() {
  localStorage.setItem('terecita_historial', JSON.stringify(historial));
}

function cargarHistorialLocal() {
  const guardado = localStorage.getItem('terecita_historial');
  if (guardado) {
    historial = JSON.parse(guardado);
    // Renderizar mensajes guardados
    historial.forEach(msg => {
      agregarBurbuja(msg.content, msg.role === 'user' ? 'usuario' : 'agente');
    });
  }
}

// ── Limpiar conversación ──────────────────────────────────────────────────
function limpiarConversacion() {
  historial = [];
  localStorage.removeItem('terecita_historial');
  document.getElementById('terecita-mensajes').innerHTML = '';
  primerMensaje = true;
  enviarMensaje('INICIO');
}

// ── Enviar mensaje ────────────────────────────────────────────────────────
async function enviarMensaje(textoForzado) {
  const input = document.getElementById('terecita-input');
  const texto = textoForzado || input.value.trim();
  if (!texto) return;

  // Limpiar el input
  if (!textoForzado) {
    input.value = '';
    agregarBurbuja(texto, 'usuario');  // Mostrar el mensaje del usuario
  }

  // Mostrar indicador de escritura
  mostrarTyping();

  try {
    // Llamar al agente
    const respuesta = await fetch(TERECITA_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        mensaje: texto,
        historial: historial
      })
    });

    const datos = await respuesta.json();
    const textoRespuesta = datos.respuesta || 'Error al obtener respuesta';

    // Quitar el indicador de escritura
    quitarTyping();

    // Mostrar la respuesta de Terecita
    procesarRespuesta(textoRespuesta);

    // Actualizar el historial
    if (!textoForzado) {
      historial.push({ role: 'user', content: texto });
    }
    historial.push({ role: 'assistant', content: textoRespuesta });
    guardarHistorialLocal();

  } catch (error) {
    quitarTyping();
    agregarBurbuja('Error de conexión. Por favor intenta de nuevo.', 'agente');
  }
}

// ── Procesar la respuesta (detectar tarjetas de producto) ─────────────────
function procesarRespuesta(texto) {
  const mensajes = document.getElementById('terecita-mensajes');

  // Detectar bloques de producto con el formato:
  // PRODUCTO: ... \n PRECIO: ... \n TALLAS: ... \n COLORES: ... \n IMG: ... \n ---
  const bloques = texto.split('---');

  bloques.forEach(bloque => {
    bloque = bloque.trim();
    if (!bloque) return;

    const tieneProducto = bloque.includes('PRODUCTO:') && bloque.includes('PRECIO:');

    if (tieneProducto) {
      // Extraer datos del producto
      const nombre  = (bloque.match(/PRODUCTO:\s*(.+)/)  || ['',''])[1].trim();
      const precio  = (bloque.match(/PRECIO:\s*(.+)/)    || ['',''])[1].trim();
      const tallas  = (bloque.match(/TALLAS:\s*(.+)/)    || ['',''])[1].trim();
      const colores = (bloque.match(/COLORES:\s*(.+)/)   || ['',''])[1].trim();
      const img     = (bloque.match(/IMG:\s*(.+)/)       || ['',''])[1].trim();

      // Generar URL del producto desde el nombre (slug)
      const slug = nombre.toLowerCase()
        .normalize('NFD').replace(/[̀-ͯ]/g, '')  // quitar tildes
        .replace(/[^a-z0-9\s-]/g, '')                      // quitar caracteres especiales
        .replace(/\s+/g, '-');                              // espacios a guiones

      const url = `https://mc-namaraspa.cl/producto/${slug}`;

      // Crear tarjeta de producto
      const card = document.createElement('div');
      card.className = 'terecita-producto-card';
      card.innerHTML = `
        <strong>👕 ${nombre}</strong>
        <span class="precio">${precio}</span><br>
        ${tallas ? `<small>📏 Tallas: ${tallas}</small><br>` : ''}
        ${colores ? `<small>🎨 Colores: ${colores}</small><br>` : ''}
        <a href="${url}" target="_blank">🔗 Ver prenda</a>
      `;
      mensajes.appendChild(card);

    } else if (bloque.length > 0) {
      // Texto normal (no es tarjeta de producto)
      agregarBurbuja(bloque, 'agente');
    }
  });

  // Hacer scroll al final
  mensajes.scrollTop = mensajes.scrollHeight;
}

// ── Agregar burbuja de mensaje ────────────────────────────────────────────
function agregarBurbuja(texto, tipo) {
  const mensajes = document.getElementById('terecita-mensajes');
  const div = document.createElement('div');
  div.className = `terecita-msg-${tipo}`;
  div.innerHTML = `<span>${texto.replace(/\n/g, '<br>')}</span>`;
  mensajes.appendChild(div);
  mensajes.scrollTop = mensajes.scrollHeight;
}

// ── Indicador de escritura ────────────────────────────────────────────────
function mostrarTyping() {
  const mensajes = document.getElementById('terecita-mensajes');
  const div = document.createElement('div');
  div.id = 'terecita-typing';
  div.className = 'terecita-typing';
  div.textContent = 'Terecita está escribiendo...';
  mensajes.appendChild(div);
  mensajes.scrollTop = mensajes.scrollHeight;
}

function quitarTyping() {
  const t = document.getElementById('terecita-typing');
  if (t) t.remove();
}
</script>
