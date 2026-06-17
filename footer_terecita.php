<?php
/**
 * The template for displaying the footer.
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

<!-- Widget Chat Terecita -->
<style>
#terecita-chat{position:fixed;bottom:20px;right:20px;z-index:9999;font-family:Arial,sans-serif;}
#terecita-ventana{display:none;flex-direction:column;overflow:hidden;background:white;border-radius:15px;box-shadow:0 5px 30px rgba(0,0,0,0.3);width:350px;height:500px;}
#terecita-mensajes{flex:1;overflow-y:auto;padding:15px;background:#f5f5f5;}
@media(max-width:480px){
  #terecita-ventana{width:calc(100vw - 30px);height:72vh;}
  #terecita-chat{bottom:15px;right:15px;}
}
</style>

<div id="terecita-chat">
  <div id="terecita-ventana">

    <!-- BARRA EN LÍNEA AHORA -->
    <div style="background:#16a34a;padding:5px 14px;display:flex;align-items:center;gap:7px;flex-shrink:0;">
      <div style="width:8px;height:8px;border-radius:50%;background:#bbf7d0;"></div>
      <span style="font-size:12px;color:#f0fdf4;font-weight:500;">En línea ahora</span>
    </div>

    <!-- HEADER ORIGINAL -->
    <div style="background:#1a1a2e;color:white;padding:12px 15px;display:flex;justify-content:space-between;align-items:center;flex-shrink:0;">
      <span style="font-size:14px;">🤖 Terecita - McNamara SPA</span>
      <div style="display:flex;align-items:center;gap:8px;">
        <button onclick="limpiarTerecita()" style="background:none;border:none;color:rgba(255,255,255,0.6);font-size:11px;cursor:pointer;">🗑️ Nueva conversación</button>
        <button onclick="cerrarTerecita()" style="background:none;border:none;color:white;font-size:22px;cursor:pointer;line-height:1;">×</button>
      </div>
    </div>

    <div id="terecita-mensajes"></div>

    <div style="padding:10px;background:white;display:flex;gap:5px;flex-shrink:0;">
      <input id="terecita-input" type="text" placeholder="Escribe tu mensaje..." style="flex:1;padding:8px;border:1px solid #ddd;border-radius:20px;outline:none;font-size:14px;" onkeypress="if(event.key==='Enter')enviarMensajeTerecita()">
      <button onclick="enviarMensajeTerecita()" style="background:#1a1a2e;color:white;border:none;border-radius:50%;width:38px;height:38px;font-size:18px;cursor:pointer;flex-shrink:0;">➤</button>
    </div>

    <!-- FOOTER ESTUDIOWEBSEO -->
    <div style="background:#f8fafc;padding:7px 12px;border-top:1px solid #e2e8f0;text-align:center;flex-shrink:0;">
      <span style="font-size:11px;color:#94a3b8;">Agente creado por </span>
      <a href="https://www.estudiowebseo.cl" target="_blank" style="font-size:11px;color:#1a2744;text-decoration:none;font-weight:600;">www.estudiowebseo.cl</a>
    </div>

  </div>
  <button onclick="toggleTerecita()" id="terecita-btn-abrir" style="background:linear-gradient(135deg,#1a1a2e 60%,#c0392b);color:white;border:none;border-radius:50px;padding:10px 16px;cursor:pointer;box-shadow:0 4px 15px rgba(0,0,0,0.4);display:flex;align-items:center;gap:8px;font-size:13px;font-weight:bold;animation:pulso 2s infinite;"><svg width="22" height="22" viewBox="0 0 24 24" fill="white"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm-2 10H6V10h12v2zm0-3H6V7h12v2z"/></svg> Habla con Terecita</button>
  <style>@keyframes pulso{0%{box-shadow:0 4px 15px rgba(192,57,43,0.4);}50%{box-shadow:0 4px 25px rgba(192,57,43,0.8);}100%{box-shadow:0 4px 15px rgba(192,57,43,0.4);}}</style>
</div>

<script>
var TERECITA_URL = 'https://web-production-8bded.up.railway.app/chat';
var TERECITA_API_BASE = TERECITA_URL.replace(/\/chat$/, '');

var historial = JSON.parse(localStorage.getItem('terecita_historial') || '[]');
var iniciado = localStorage.getItem('terecita_iniciado') === 'true';
var esperando = false;
var productosPendientes = [];   // Productos capturados de los bloques RESUMEN_COMPRA

window.addEventListener('load', function(){
  if(historial.length > 0){
    historial.forEach(function(msg){
      if(msg.role === 'user' && msg.content !== 'INICIO'){
        agregarMensaje(msg.content, 'user');
      } else if(msg.role === 'assistant'){
        agregarMensaje(msg.content, 'terecita');
      }
    });
  }
});

function cerrarTerecita(){
  document.getElementById('terecita-ventana').style.display='none';
}

function toggleTerecita(){
  var v = document.getElementById('terecita-ventana');
  var abierto = v.style.display === 'flex';
  v.style.display = abierto ? 'none' : 'flex';
  if(!iniciado && !abierto){
    iniciado = true;
    llamarTerecita('INICIO');
  }
}

function limpiarTerecita(){
  historial = [];
  iniciado = false;
  localStorage.removeItem('terecita_historial');
  localStorage.removeItem('terecita_iniciado');
  document.getElementById('terecita-mensajes').innerHTML = '';
  llamarTerecita('INICIO');
}

function enviarMensajeTerecita(){
  if(esperando) return;
  var input = document.getElementById('terecita-input');
  var msg = input.value.trim();
  if(!msg) return;
  input.value = '';
  agregarMensaje(msg, 'user');
  historial.push({role:'user', content: msg});
  llamarTerecita(null);
}

function llamarTerecita(mensajeInicial){
  esperando = true;
  var mensajes = historial.slice();
  if(mensajeInicial){
    mensajes = [{role:'user', content: mensajeInicial}];
  }
  agregarMensaje('...', 'terecita', 'typing');
  fetch(TERECITA_URL,{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({messages: mensajes})
  })
  .then(r=>r.json())
  .then(d=>{
    quitarTyping();
    esperando = false;
    var respuesta = d.reply || d.error || 'Sin respuesta';
    if(mensajeInicial){
      historial.push({role:'user', content: mensajeInicial});
    }
    historial.push({role:'assistant', content: respuesta});
    localStorage.setItem('terecita_historial', JSON.stringify(historial));
    localStorage.setItem('terecita_iniciado', 'true');
    agregarMensaje(respuesta, 'terecita');
  })
  .catch(e=>{
    quitarTyping();
    esperando = false;
    agregarMensaje('Error de conexion, intenta de nuevo.', 'terecita');
  });
}

function procesarTexto(texto) {

  // Tarjeta visual de producto: bloque PRODUCTO_VISUAL...FIN_PRODUCTO_VISUAL
  // con Nombre/Precio/Imagen/Link. Se muestra como miniatura clicable +
  // boton "Ver producto completo ->" — la URL nunca se ve como texto plano.
  texto = texto.replace(/PRODUCTO_VISUAL([\s\S]*?)FIN_PRODUCTO_VISUAL/g, function(match, contenido){
    var lineas = contenido.trim().split('\n');
    var datos = {};
    lineas.forEach(function(linea){
      linea = linea.trim();
      if(!linea) return;
      var idx = linea.indexOf(':');
      if(idx === -1) return;
      var clave = linea.substring(0,idx).trim().toLowerCase();
      var valor = linea.substring(idx+1).trim();
      datos[clave] = valor;
    });

    var nombre = datos['nombre'] || '';
    var precio = datos['precio'] || '';
    var imagen = datos['imagen'] || '';
    var link = datos['link'] || '#';
    var tieneImagen = imagen && imagen.toLowerCase() !== 'sin imagen';

    var html = '<div style="background:white;border:1px solid #e0e0e0;border-radius:12px;overflow:hidden;margin:6px 0;box-shadow:0 2px 8px rgba(0,0,0,0.08);">';
    if(tieneImagen){
      html += '<a href="'+link+'" target="_blank">'
        + '<img src="'+imagen+'" alt="" style="width:100%;max-height:160px;object-fit:cover;display:block;cursor:pointer;">'
        + '</a>';
    }
    html += '<div style="padding:10px 12px;">';
    html += '<div style="font-weight:bold;font-size:13px;color:#1a1a2e;margin-bottom:4px;">👕 '+nombre+'</div>';
    html += '<div style="color:#e53935;font-weight:bold;font-size:14px;margin-bottom:8px;">'+precio+'</div>';
    html += '<a href="'+link+'" target="_blank" style="display:block;text-align:center;background:#1a1a2e;color:white;padding:7px;border-radius:20px;font-size:12px;text-decoration:none;">Ver producto completo →</a>';
    html += '</div></div>';
    return html;
  });

  // Resumen de compra: Terecita puede mandar uno o varios bloques
  // RESUMEN_COMPRA...FIN_RESUMEN (uno por producto). Cada bloque se
  // convierte en su tarjeta visual Y se guarda en productosPendientes
  // para poder llamar a /enviar-cotizacion mas adelante.
  texto = texto.replace(/RESUMEN_COMPRA([\s\S]*?)FIN_RESUMEN/g, function(match, contenido){
    var lineas = contenido.trim().split('\n');
    var item = {};
    var cuadro = '<div style="background:#1a1a2e;color:white;border-radius:12px;padding:15px;margin:8px 0;font-size:12px;width:100%;">';
    cuadro += '<div style="font-size:14px;font-weight:bold;border-bottom:1px solid rgba(255,255,255,0.3);padding-bottom:8px;margin-bottom:10px;">📋 Resumen de tu pedido</div>';
    lineas.forEach(function(linea){
      linea = linea.trim();
      if(!linea) return;
      var idx = linea.indexOf(':');
      if(idx === -1) return;
      var clave = linea.substring(0,idx).trim();
      var valor = linea.substring(idx+1).trim();
      var esTotal = clave.toLowerCase().indexOf('total') !== -1;
      cuadro += '<div style="display:flex;justify-content:space-between;padding:3px 0;'+(esTotal?'border-top:1px solid rgba(255,255,255,0.3);margin-top:6px;padding-top:8px;':'')+ '">';
      cuadro += '<span style="color:rgba(255,255,255,0.7);">'+clave+'</span>';
      cuadro += '<span style="font-weight:'+(esTotal?'bold':'normal')+';color:'+(esTotal?'#4CAF50':'white')+';">'+valor+'</span>';
      cuadro += '</div>';

      var claveNorm = clave.toLowerCase();
      if(claveNorm === 'producto') item.nombre = valor;
      else if(claveNorm === 'talla') item.talla = valor;
      else if(claveNorm === 'color') item.color = valor;
      else if(claveNorm === 'cantidad') item.cantidad = parseInt(valor, 10) || 1;
      else if(claveNorm === 'precio unitario') item.precio_unitario = parseInt(valor.replace(/[^\d]/g, ''), 10) || 0;
      else if(claveNorm === 'descuento') item.descuento = valor;
      else if(claveNorm === 'total estimado') item.total = valor;
    });
    cuadro += '</div>';
    if(item.nombre) productosPendientes.push(item);
    return cuadro;
  });

  // Saltos de linea
  texto = texto.replace(/\n/g, '<br>');
  return texto;
}

// ── Formulario de datos del cliente para enviar la cotizacion ─────────────
function mostrarFormularioCotizacion(){
  if(document.getElementById('terecita-form-cotizacion')) return;
  var div = document.getElementById('terecita-mensajes');
  var form = document.createElement('div');
  form.id = 'terecita-form-cotizacion';
  form.style.cssText = 'background:white;border:1px solid #e0e0e0;border-radius:10px;padding:12px;margin:6px 0;font-size:12px;';
  form.innerHTML =
    '<div style="font-weight:bold;margin-bottom:8px;color:#1a1a2e;">📩 Completa tus datos para recibir la cotización</div>' +
    '<input id="tc-nombre" placeholder="Nombre" style="width:100%;margin-bottom:6px;padding:7px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">' +
    '<input id="tc-email" placeholder="Email" style="width:100%;margin-bottom:6px;padding:7px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">' +
    '<input id="tc-telefono" placeholder="Teléfono" style="width:100%;margin-bottom:6px;padding:7px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">' +
    '<input id="tc-empresa" placeholder="Empresa" style="width:100%;margin-bottom:6px;padding:7px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">' +
    '<input id="tc-ciudad" placeholder="Ciudad" style="width:100%;margin-bottom:6px;padding:7px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">' +
    '<select id="tc-documento" style="width:100%;margin-bottom:8px;padding:7px;border:1px solid #ddd;border-radius:6px;box-sizing:border-box;">' +
      '<option value="Boleta">Boleta</option>' +
      '<option value="Factura">Factura</option>' +
    '</select>' +
    '<button id="tc-enviar-btn" style="width:100%;background:#1a1a2e;color:white;border:none;border-radius:20px;padding:9px;cursor:pointer;font-size:13px;">Enviar cotización por correo</button>' +
    '<div id="tc-status" style="margin-top:6px;font-size:11px;color:#888;"></div>';
  div.appendChild(form);
  div.scrollTop = div.scrollHeight;

  document.getElementById('tc-enviar-btn').onclick = enviarCotizacionApi;
}

function enviarCotizacionApi(){
  var btn = document.getElementById('tc-enviar-btn');
  var status = document.getElementById('tc-status');
  var nombre = document.getElementById('tc-nombre').value.trim();
  var email = document.getElementById('tc-email').value.trim();

  if(!nombre || !email){
    status.textContent = 'Por favor completa al menos nombre y email.';
    status.style.color = '#e63946';
    return;
  }

  btn.disabled = true;
  btn.textContent = 'Enviando...';
  status.textContent = '';

  fetch(TERECITA_API_BASE + '/enviar-cotizacion', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
      nombre: nombre,
      email: email,
      telefono: document.getElementById('tc-telefono').value.trim(),
      empresa: document.getElementById('tc-empresa').value.trim(),
      ciudad: document.getElementById('tc-ciudad').value.trim(),
      documento: document.getElementById('tc-documento').value,
      productos: productosPendientes,
      resumen: JSON.stringify(productosPendientes)
    })
  })
  .then(function(r){ return r.json(); })
  .then(function(d){
    if(d.ok){
      status.textContent = '✅ Cotización ' + (d.numero || '') + ' enviada a tu correo.';
      status.style.color = '#16a34a';
      btn.textContent = 'Enviada ✓';
      productosPendientes = [];
    } else {
      status.textContent = 'Error: ' + (d.error || 'no se pudo enviar');
      status.style.color = '#e63946';
      btn.disabled = false;
      btn.textContent = 'Reintentar';
    }
  })
  .catch(function(){
    status.textContent = 'Error de conexión, intenta de nuevo.';
    status.style.color = '#e63946';
    btn.disabled = false;
    btn.textContent = 'Reintentar';
  });
}

function agregarMensaje(texto, quien, id){
  var div = document.getElementById('terecita-mensajes');
  var burbuja = document.createElement('div');
  if(id) burbuja.id = id;
  burbuja.style.cssText = 'margin:5px 0;text-align:'+(quien==='user'?'right':'left')+';';
  var contenido = texto;
  if(quien === 'terecita'){
    contenido = procesarTexto(texto);
  }
  burbuja.innerHTML = '<span style="background:'+(quien==='user'?'#1a1a2e':'white')+';color:'+(quien==='user'?'white':'#333')+';padding:8px 12px;border-radius:15px;display:inline-block;max-width:92%;font-size:13px;word-wrap:break-word;line-height:1.5;text-align:left;">'+contenido+'</span>';
  div.appendChild(burbuja);
  div.scrollTop = div.scrollHeight;

  if(quien === 'terecita' && productosPendientes.length > 0){
    mostrarFormularioCotizacion();
  }
}

function quitarTyping(){
  var t = document.getElementById('typing');
  if(t) t.remove();
}
</script>
