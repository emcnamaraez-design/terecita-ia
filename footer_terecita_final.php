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
     WIDGET CHAT CARMEN IA — WorkCorporativo
     Reemplaza la URL del fetch con la de tu subdominio del agente
     URL actual: https://web-production-8bded.up.railway.app/chat
     ═══════════════════════════════════════════════════════════ -->

<style>
/* ── Contenedor principal ── */
#carmen-chat {
  position: fixed;
  bottom: 20px;
  right: 20px;
  z-index: 9999;
  font-family: Arial, sans-serif;
}

/* ── Ventana del chat ── */
#carmen-ventana {
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
#carmen-status-bar {
  background: #2d9e5f;
  color: white;
  font-size: 11px;
  text-align: center;
  padding: 4px 10px;
  letter-spacing: 0.5px;
  flex-shrink: 0;
}

/* ── Header del chat ── */
#carmen-header {
  background: #1a1a2e;
  color: white;
  padding: 12px 15px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-shrink: 0;
}

/* ── Área de mensajes ── */
#carmen-mensajes {
  flex: 1;
  overflow-y: auto;
  padding: 15px;
  background: #f5f5f5;
}

/* ── Burbujas de mensajes ── */
.carmen-msg-usuario {
  text-align: right;
  margin: 6px 0;
}
.carmen-msg-usuario span {
  background: #1a1a2e;
  color: white;
  padding: 8px 12px;
  border-radius: 15px 15px 0 15px;
  display: inline-block;
  max-width: 80%;
  font-size: 13px;
}
.carmen-msg-agente {
  text-align: left;
  margin: 6px 0;
}
.carmen-msg-agente span {
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
.carmen-producto-card {
  background: white;
  border: 1px solid #e0e0e0;
  border-radius: 10px;
  padding: 10px;
  margin: 5px 0;
  font-size: 12px;
}
.carmen-producto-card strong {
  color: #1a1a2e;
  display: block;
  margin-bottom: 4px;
}
.carmen-producto-card .precio {
  color: #e63946;
  font-weight: bold;
  font-size: 14px;
}
.carmen-producto-card a {
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
.carmen-typing {
  color: #999;
  font-size: 12px;
  font-style: italic;
  padding: 5px;
}

/* ── Área de input ── */
#carmen-input-area {
  display: flex;
  padding: 10px;
  background: white;
  border-top: 1px solid #e0e0e0;
  gap: 8px;
  flex-shrink: 0;
}
#carmen-input {
  flex: 1;
  border: 1px solid #ddd;
  border-radius: 20px;
  padding: 8px 14px;
  font-size: 13px;
  outline: none;
}
#carmen-enviar {
  background: #1a1a2e;
  color: white;
  border: none;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  cursor: pointer;
  font-size: 16px;
}
#carmen-adjuntar {
  background: none;
  border: 1px solid #ddd;
  border-radius: 50%;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  cursor: pointer;
  font-size: 16px;
  color: #1a1a2e;
}
#carmen-imagen-preview {
  display: none;
  align-items: center;
  gap: 6px;
  padding: 4px 12px;
  font-size: 11px;
  color: #555;
  background: #f5f5f5;
  border-top: 1px solid #e0e0e0;
  flex-shrink: 0;
}
#carmen-imagen-preview button {
  background: none;
  border: none;
  color: #e63946;
  cursor: pointer;
  font-size: 12px;
}

/* ── Footer del widget ── */
#carmen-footer-brand {
  background: #f0f0f0;
  color: #999;
  font-size: 10px;
  text-align: center;
  padding: 4px;
  flex-shrink: 0;
}
#carmen-footer-brand a {
  color: #666;
  text-decoration: none;
}

/* ── Botón flotante de apertura ── */
#carmen-btn {
  background: linear-gradient(135deg, #1a1a2e, #e63946);
  color: white;
  border: none;
  border-radius: 30px;
  padding: 14px 22px;
  font-size: 15px;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(0,0,0,0.3);
  animation: carmen-pulso 2.5s infinite;
}
@keyframes carmen-pulso {
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.04); }
}

/* ── Responsive móvil ── */
@media(max-width: 480px) {
  #carmen-ventana {
    width: calc(100vw - 30px);
    height: 72vh;
  }
  #carmen-chat {
    bottom: 15px;
    right: 15px;
  }
}
</style>

<div id="carmen-chat">

  <!-- Ventana del chat -->
  <div id="carmen-ventana">

    <!-- Barra verde "En línea ahora" -->
    <div id="carmen-status-bar">🟢 En línea ahora</div>

    <!-- Header -->
    <div id="carmen-header">
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
    <div id="carmen-mensajes"></div>

    <!-- Vista previa de imagen adjunta -->
    <div id="carmen-imagen-preview">
      <span id="carmen-imagen-nombre"></span>
      <button onclick="quitarImagenAdjunta()">✕ quitar</button>
    </div>

    <!-- Input -->
    <div id="carmen-input-area">
      <input type="file" id="carmen-imagen-input" accept="image/*" style="display:none;" onchange="seleccionarImagen(event)">
      <button id="carmen-adjuntar" onclick="document.getElementById('carmen-imagen-input').click()" title="Adjuntar imagen del carrito">📎</button>
      <input id="carmen-input" type="text" placeholder="Escribe tu mensaje..."
        onkeypress="if(event.key==='Enter') enviarMensaje()">
      <button id="carmen-enviar" onclick="enviarMensaje()">➤</button>
    </div>

    <!-- Footer de marca -->
    <div id="carmen-footer-brand">
      Agente IA desarrollado por
      <a href="https://www.estudiowebseo.cl" target="_blank">estudiowebseo.cl</a>
    </div>

  </div>

  <!-- Botón flotante -->
  <button id="carmen-btn" onclick="toggleChat()">🤖 Habla con Terecita</button>

</div>

<script>
// ── URL del agente (cambia esto si usas otro subdominio) ──────────────────
const CARMEN_URL = 'https://web-production-8bded.up.railway.app/chat';

// ── Estado del chat ───────────────────────────────────────────────────────
let historial = [];         // Historial de la conversación para la API
let chatAbierto = false;    // Si el chat está visible o no
let primerMensaje = true;   // Para saber si es el inicio de la conversación
let productosResumen = [];  // Acumula productos del RESUMEN_COMPRA para enviar en cotizacion
let imagenAdjunta = null;   // { dataUrl, nombre } de la imagen del carrito seleccionada para enviar

// ── Adjuntar/quitar imagen del carrito ─────────────────────────────────────
function seleccionarImagen(event) {
  const archivo = event.target.files[0];
  if (!archivo) return;
  const lector = new FileReader();
  lector.onload = () => {
    imagenAdjunta = { dataUrl: lector.result, nombre: archivo.name };
    document.getElementById('carmen-imagen-nombre').textContent = '📎 ' + archivo.name;
    document.getElementById('carmen-imagen-preview').style.display = 'flex';
  };
  lector.readAsDataURL(archivo);
}

function quitarImagenAdjunta() {
  imagenAdjunta = null;
  document.getElementById('carmen-imagen-input').value = '';
  document.getElementById('carmen-imagen-preview').style.display = 'none';
}

// ── Abrir/cerrar el chat ──────────────────────────────────────────────────
function toggleChat() {
  chatAbierto = !chatAbierto;
  const ventana = document.getElementById('carmen-ventana');
  const btn = document.getElementById('carmen-btn');

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
  productosResumen = [];
  localStorage.removeItem('terecita_historial');
  document.getElementById('carmen-mensajes').innerHTML = '';
  primerMensaje = true;
  enviarMensaje('INICIO');
}

// ── Enviar mensaje ────────────────────────────────────────────────────────
async function enviarMensaje(textoForzado) {
  const input = document.getElementById('carmen-input');
  const texto = textoForzado || input.value.trim();
  if (!texto) return;

  const imagenParaEnviar = imagenAdjunta;

  // Limpiar el input
  if (!textoForzado) {
    input.value = '';
    agregarBurbuja(texto, 'usuario');  // Mostrar el mensaje del usuario
  }
  if (imagenParaEnviar) quitarImagenAdjunta();

  // Mostrar indicador de escritura
  mostrarTyping();

  try {
    const cuerpo = { mensaje: texto, historial: historial };
    if (imagenParaEnviar) cuerpo.imagen = imagenParaEnviar.dataUrl;

    // Llamar al agente
    const respuesta = await fetch(CARMEN_URL, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(cuerpo)
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
  const mensajes = document.getElementById('carmen-mensajes');

  // 1. Detectar DATOS_CLIENTE (dispara envio de cotizacion)
  const matchDatos = texto.match(/DATOS_CLIENTE\n([\s\S]*?)FIN_DATOS_CLIENTE/);
  if (matchDatos) {
    const bloqueDatos = matchDatos[1];
    const extraer = (campo) => {
      const m = bloqueDatos.match(new RegExp(campo + ':\\s*(.+)'));
      return m ? m[1].trim() : '';
    };
    const datosCliente = {
      nombre:       extraer('Nombre'),
      email:        extraer('Email'),
      telefono:     extraer('Telefono'),
      empresa:      extraer('Empresa'),
      ciudad:       extraer('Ciudad'),
      documento:    extraer('Documento'),
      rut:          extraer('RUT'),
      razon_social: extraer('RazonSocial'),
      productos:    productosResumen,
    };
    texto = texto.replace(/DATOS_CLIENTE[\s\S]*?FIN_DATOS_CLIENTE/, '').trim();
    fetch(CARMEN_URL.replace('/chat', '/enviar-cotizacion'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datosCliente)
    }).then(r => r.json()).then(res => {
      if (res.ok) {
        const div = document.createElement('div');
        div.className = 'carmen-msg-agente';
        div.innerHTML = '<span>✅ Cotización enviada. Revisa tu correo en unos minutos.</span>';
        mensajes.appendChild(div);
      }
    }).catch(() => {});
    productosResumen = [];
  }

  // 1b. Detectar COTIZACION_INTERNA (dispara envio de cotizacion interna por SKU)
  const matchCotInterna = texto.match(/COTIZACION_INTERNA\n([\s\S]*?)FIN_COTIZACION_INTERNA/);
  if (matchCotInterna) {
    const bloqueCot = matchCotInterna[1];
    const extraerCot = (campo) => {
      const m = bloqueCot.match(new RegExp(campo + ':\\s*(.+)'));
      return m ? m[1].trim() : '';
    };
    const productosCot = [];
    const regexProductoCot = /PRODUCTO:\s*(.+)/g;
    let matchProductoCot;
    while ((matchProductoCot = regexProductoCot.exec(bloqueCot)) !== null) {
      const partes = matchProductoCot[1].split('|').map(p => p.trim());
      productosCot.push({
        sku:             partes[0] || '',
        nombre:          partes[1] || '',
        cantidad:        partes[2] || '1',
        precio_unitario: (partes[3] || '0').replace(/[$\.]/g, '').replace('CLP', '').trim(),
      });
    }
    const datosCotInterna = {
      nombre:    extraerCot('Cliente'),
      email:     extraerCot('Email'),
      productos: productosCot,
    };
    texto = texto.replace(/COTIZACION_INTERNA[\s\S]*?FIN_COTIZACION_INTERNA/, '').trim();
    fetch(CARMEN_URL.replace('/chat', '/enviar-cotizacion'), {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(datosCotInterna)
    }).then(r => r.json()).then(res => {
      if (res.ok) {
        const div = document.createElement('div');
        div.className = 'carmen-msg-agente';
        div.innerHTML = '<span>✅ Cotización interna enviada. Revisa tu correo en unos minutos.</span>';
        mensajes.appendChild(div);
      }
    }).catch(() => {});
  }

  // 2. Detectar bloques RESUMEN_COMPRA (fondo oscuro)
  const regexResumen = /RESUMEN_COMPRA\n([\s\S]*?)FIN_RESUMEN/g;
  let matchResumen;
  const partesResumen = [];
  while ((matchResumen = regexResumen.exec(texto)) !== null) {
    const bloqueR = matchResumen[1];
    const exR = (campo) => {
      const m = bloqueR.match(new RegExp(campo + ':\\s*(.+)'));
      return m ? m[1].trim() : '';
    };
    productosResumen.push({
      nombre:          exR('Producto'),
      talla:           exR('Talla'),
      color:           exR('Color'),
      cantidad:        exR('Cantidad'),
      precio_unitario: exR('Precio unitario').replace(/[$\.]/g,'').replace('CLP','').trim(),
    });
    partesResumen.push({
      inicio: matchResumen.index,
      fin: matchResumen.index + matchResumen[0].length,
      precioU: exR('Precio unitario'),
      totalE: exR('Total estimado'),
      nombre: exR('Producto'),
      talla: exR('Talla'),
      color: exR('Color'),
      cantidad: exR('Cantidad'),
      descuento: exR('Descuento'),
    });
  }
  if (partesResumen.length > 0) {
    const textoPre = texto.substring(0, partesResumen[0].inicio).trim();
    if (textoPre) agregarBurbuja(textoPre, 'agente');
    partesResumen.forEach(p => {
      const card = document.createElement('div');
      card.innerHTML = `
        <div style="background:#1a1a2e;color:#e0e0e0;border-radius:10px;padding:12px 14px;margin:6px 0;font-size:13px;line-height:1.8;border:1px solid #2563eb;">
          <div style="font-weight:bold;color:#60a5fa;margin-bottom:6px;">🛍️ ${p.nombre}</div>
          <div>📏 Talla: ${p.talla}</div>
          <div>🎨 Color: ${p.color}</div>
          <div>📦 Cantidad: ${p.cantidad}</div>
          <div>💰 Precio unitario: ${p.precioU}</div>
          <div>🏷️ Descuento: ${p.descuento}</div>
          <div style="font-weight:bold;color:#34d399;">💵 Total estimado: ${p.totalE}</div>
        </div>`;
      mensajes.appendChild(card);
    });
    const textoPost = texto.substring(partesResumen[partesResumen.length-1].fin).trim();
    if (textoPost) agregarBurbuja(textoPost, 'agente');
    mensajes.scrollTop = mensajes.scrollHeight;
    return;
  }

  // 3. Detectar bloques PRODUCTO formato Carmen (separados por ---)
  const bloques = texto.split('---');
  bloques.forEach(bloque => {
    bloque = bloque.trim();
    if (!bloque) return;
    const tieneProducto = bloque.includes('PRODUCTO:') && bloque.includes('PRECIO:');
    if (tieneProducto) {
      const nombre  = (bloque.match(/PRODUCTO:\s*(.+)/)  || ['',''])[1].trim();
      const precio  = (bloque.match(/PRECIO:\s*(.+)/)    || ['',''])[1].trim();
      const tallas  = (bloque.match(/TALLAS:\s*(.+)/)    || ['',''])[1].trim();
      const colores = (bloque.match(/COLORES:\s*(.+)/)   || ['',''])[1].trim();
      const img     = (bloque.match(/IMG:\s*(.+)/)       || ['',''])[1].trim();
      const url     = (bloque.match(/URL:\s*(.+)/)       || ['',''])[1].trim();
      let urlValida = '';
      if (url && url !== 'Sin URL') {
        try {
          const u = new URL(url);
          if (u.protocol === 'http:' || u.protocol === 'https:') urlValida = url;
        } catch (e) { /* URL invalida, no se muestra el boton */ }
      }
      const card = document.createElement('div');
      card.className = 'carmen-producto-card';
      card.innerHTML = `
        ${(img && img !== 'Sin imagen') ? `<img src="${img}" alt="${nombre}" style="width:100%;border-radius:8px;margin-bottom:8px;object-fit:cover;max-height:160px;">` : ''}
        <strong>👕 ${nombre}</strong>
        <span class="precio">${precio}</span><br>
        ${tallas ? `<small>📏 Tallas: ${tallas}</small><br>` : ''}
        ${colores ? `<small>🎨 Colores: ${colores}</small><br>` : ''}
        ${urlValida ? `<a href="${urlValida}" target="_blank">🔗 Ver producto completo</a>` : ''}
      `;
      mensajes.appendChild(card);
    } else if (bloque.length > 0) {
      agregarBurbuja(bloque, 'agente');
    }
  });
  mensajes.scrollTop = mensajes.scrollHeight;
}

// ── Agregar burbuja de mensaje ────────────────────────────────────────────
function agregarBurbuja(texto, tipo) {
  const mensajes = document.getElementById('carmen-mensajes');
  const div = document.createElement('div');
  div.className = `carmen-msg-${tipo}`;
  div.innerHTML = `<span>${texto.replace(/\n/g, '<br>')}</span>`;
  mensajes.appendChild(div);
  mensajes.scrollTop = mensajes.scrollHeight;
}

// ── Indicador de escritura ────────────────────────────────────────────────
function mostrarTyping() {
  const mensajes = document.getElementById('carmen-mensajes');
  const div = document.createElement('div');
  div.id = 'carmen-typing';
  div.className = 'carmen-typing';
  div.textContent = 'Terecita está escribiendo...';
  mensajes.appendChild(div);
  mensajes.scrollTop = mensajes.scrollHeight;
}

function quitarTyping() {
  const t = document.getElementById('carmen-typing');
  if (t) t.remove();
}
</script>
