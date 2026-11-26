/* Utilidades compartidas por todas las vistas. */
const Comun = (() => {
  const ETIQUETAS = { "PENDIENTE": "Pendiente", "EN PREPARACION": "En preparación", "LISTO": "Listo",
                      "ENTREGADO": "Entregado", "CANCELADO": "Cancelado" };

  // Todo texto que viene del servidor (nombres, direcciones, descripciones) se escapa antes de ir al HTML.
  function esc(texto) {
    return String(texto ?? "").replace(/[&<>"']/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  }
  const moneda = n => new Intl.NumberFormat("es-CO", { style: "currency", currency: "COP", maximumFractionDigits: 0 }).format(Number(n) || 0);
  const fecha = iso => iso ? new Date(iso).toLocaleString("es-CO") : "—";
  function duracion(seg) {
    seg = Math.max(0, Math.floor(seg || 0));
    const h = Math.floor(seg / 3600), m = Math.floor((seg % 3600) / 60);
    return h ? `${h} h ${m} min` : m ? `${m} min` : `${seg} s`;
  }

  async function api(url, { method = "GET", cuerpo } = {}) {
    const cfg = { method, headers: {}, credentials: "same-origin" };
    if (cuerpo !== undefined) { cfg.headers["Content-Type"] = "application/json"; cfg.body = JSON.stringify(cuerpo); }
    let resp;
    try { resp = await fetch(url, cfg); }
    catch (e) { throw new Error("No fue posible realizar su consulta, intente nuevamente"); }
    let datos = null;
    try { datos = await resp.json(); } catch (e) { /* sin cuerpo JSON */ }
    if (resp.status === 401 && !url.startsWith("/api/sesion")) { window.location.href = "/login"; throw new Error("Debe iniciar sesión"); }
    if (!resp.ok) {
      const error = new Error((datos && datos.error) || "Ocurrió un error en el proceso. Intente nuevamente");
      error.campos = datos && datos.campos;
      throw error;
    }
    return datos;
  }

  // Muestra un mensaje en un contenedor (tipo: ok | error | aviso). Los errores de campos se listan.
  function mostrar(idContenedor, texto, tipo = "ok") {
    const el = document.getElementById(idContenedor);
    if (!el) return;
    el.className = "msg " + tipo;
    el.textContent = texto || "";
  }
  function textoError(error) {
    let texto = error.message;
    if (error.campos) texto += " — " + Object.entries(error.campos).map(([c, m]) => `${c}: ${m}`).join(" | ");
    return texto;
  }
  const fallo = (idContenedor, error) => mostrar(idContenedor, textoError(error), "error");

  const insignia = estado => `<span class="insignia e-${esc(String(estado).replace(/ /g, "-"))}">${esc(ETIQUETAS[estado] || estado)}</span>`;

  function lineas(p) {
    return `<ul>${(p.detalles || []).map(d => `<li>${d.cantidad} × ${esc(d.producto)} <span class="suave">(${moneda(d.subtotal)})</span></li>`).join("")}</ul>`;
  }
  function resumen(p) {
    return `<div><strong>#${p.id_pedido}</strong> ${insignia(p.estado)} <span class="suave">${esc(p.origen)}</span></div>
            <div class="suave">Creado: ${fecha(p.fecha)} · En este estado hace ${duracion(p.segundos_en_estado)}</div>
            ${lineas(p)}<div class="precio">${moneda(p.total)}</div>`;
  }
  function detalle(p) {
    const partes = [`<h3>Pedido #${p.id_pedido} ${insignia(p.estado)}</h3>`,
      `<div>${esc(p.origen)}${p.direccion ? " · " + esc(p.direccion) : ""}</div>`,
      p.mesero ? `<div>Mesero: ${esc(p.mesero.nombre)}</div>` : "",
      p.cliente ? `<div>Cliente: ${esc(p.cliente.nombre)}</div>` : "",
      `<div class="suave">Realizado: ${fecha(p.fecha)}<br>Último cambio de estado: ${fecha(p.fecha_estado)} (hace ${duracion(p.segundos_en_estado)})</div>`,
      lineas(p), `<div class="precio">Total: ${moneda(p.total)}</div>`];
    if (p.mensaje) partes.push(`<div class="msg aviso">${esc(p.mensaje)}</div>`);
    return partes.join("");
  }

  // Tiempo real: la vista se suscribe a su sala (el servidor decide cuál según la sesión).
  function tiempoReal(alEvento, idIndicador = "tiempoReal") {
    const indicador = document.getElementById(idIndicador);
    if (typeof io === "undefined") { if (indicador) indicador.textContent = "Sin tiempo real (use Actualizar)"; return null; }
    const socket = io();
    socket.on("connect", () => { if (indicador) indicador.textContent = "● En vivo"; });
    socket.on("disconnect", () => { if (indicador) indicador.textContent = "○ Reconectando…"; });
    socket.on("pedido", alEvento);
    return socket;
  }

  async function cerrarSesion() {
    try { await api("/api/sesion", { method: "DELETE" }); } finally { window.location.href = "/login"; }
  }
  document.addEventListener("click", e => { if (e.target.closest("[data-salir]")) cerrarSesion(); });

  return { ETIQUETAS, esc, moneda, fecha, duracion, api, mostrar, fallo, textoError, insignia, resumen, detalle, lineas, tiempoReal };
})();
