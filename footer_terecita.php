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
var historial = JSON.parse(localStorage.getItem('terecita_historial') || '[]');
var iniciado = localStorage.getItem('terecita_iniciado') === 'true';
var esperando = false;

window.addEventListener('load', function(){
  if(historial.length > 0){
    historial.forEach(function(msg){
      if(msg.role === 'user' && msg.content !== 'INICIO'){
        agregarMensaje(msg.content, 'user');
      } else if(msg.role === 'assistant'){
        agregarMensaje(msg.content, 'carmen');
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
  agregarMensaje('...', 'carmen', 'typing');
  fetch('https://web-production-8bded.up.railway.app/chat',{
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
    agregarMensaje(respuesta, 'carmen');
  })
  .catch(e=>{
    quitarTyping();
    esperando = false;
    agregarMensaje('Error de conexion, intenta de nuevo.', 'carmen');
  });
}

function procesarTexto(texto) {

  // Detectar: 👕 Nombre - $precio CLP + 🔗 Ver prenda: URL
  texto = texto.replace(
    /👕 (.+?) - (\$[\d\.,]+ CLP)\s*\n🔗 Ver prenda: (https?:\/\/[^\s\n<]+)/g,
    '<div style="background:white;border:1px solid #e0e0e0;border-radius:12px;padding:12px;margin:6px 0;box-shadow:0 2px 8px rgba(0,0,0,0.08);">'
    + '<div style="font-weight:bold;font-size:13px;color:#1a1a2e;margin-bottom:4px;">👕 $1</div>'
    + '<div style="color:#e53935;font-weight:bold;font-size:14px;margin-bottom:8px;">$2</div>'
    + '<a href="$3" target="_blank" style="display:block;text-align:center;background:#1a1a2e;color:white;padding:7px;border-radius:20px;font-size:12px;text-decoration:none;">Ver prenda en tienda →</a>'
    + '</div>'
  );

  // Resumen de compra
  if(texto.indexOf('RESUMEN_COMPRA') !== -1 && texto.indexOf('FIN_RESUMEN') !== -1){
    var ini = texto.indexOf('RESUMEN_COMPRA');
    var fin = texto.indexOf('FIN_RESUMEN') + 'FIN_RESUMEN'.length;
    var bloque = texto.substring(ini, fin);
    var lineas = bloque.replace('RESUMEN_COMPRA','').replace('FIN_RESUMEN','').trim().split('\n');
    var cuadro = '<div style="background:#1a1a2e;color:white;border-radius:12px;padding:15px;margin:8px 0;font-size:12px;width:100%;">';
    cuadro += '<div style="font-size:14px;font-weight:bold;border-bottom:1px solid rgba(255,255,255,0.3);padding-bottom:8px;margin-bottom:10px;">📋 Resumen de tu pedido</div>';
    lineas.forEach(function(linea){
      if(linea.trim()){
        var idx = linea.indexOf(':');
        if(idx !== -1){
          var clave = linea.substring(0,idx).trim();
          var valor = linea.substring(idx+1).trim();
          var esTotal = clave.toLowerCase().indexOf('total') !== -1;
          cuadro += '<div style="display:flex;justify-content:space-between;padding:3px 0;'+(esTotal?'border-top:1px solid rgba(255,255,255,0.3);margin-top:6px;padding-top:8px;':'')+ '">';
          cuadro += '<span style="color:rgba(255,255,255,0.7);">'+clave+'</span>';
          cuadro += '<span style="font-weight:'+(esTotal?'bold':'normal')+';color:'+(esTotal?'#4CAF50':'white')+';">'+valor+'</span>';
          cuadro += '</div>';
        }
      }
    });
    cuadro += '</div>';
    texto = texto.replace(bloque, cuadro);
  }

  // Saltos de linea
  texto = texto.replace(/\n/g, '<br>');
  return texto;
}

function agregarMensaje(texto, quien, id){
  var div = document.getElementById('terecita-mensajes');
  var burbuja = document.createElement('div');
  if(id) burbuja.id = id;
  burbuja.style.cssText = 'margin:5px 0;text-align:'+(quien==='user'?'right':'left')+';';
  var contenido = texto;
  if(quien === 'carmen'){
    contenido = procesarTexto(texto);
  }
  burbuja.innerHTML = '<span style="background:'+(quien==='user'?'#1a1a2e':'white')+';color:'+(quien==='user'?'white':'#333')+';padding:8px 12px;border-radius:15px;display:inline-block;max-width:92%;font-size:13px;word-wrap:break-word;line-height:1.5;text-align:left;">'+contenido+'</span>';
  div.appendChild(burbuja);
  div.scrollTop = div.scrollHeight;
}

function quitarTyping(){
  var t = document.getElementById('typing');
  if(t) t.remove();
}
</script>
