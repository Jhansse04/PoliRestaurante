/* VistaCocina: HU07 (recibir pedidos), HU08 (actualizar estado), HU09 (ver detalle). */
(() => {
  const { api, mostrar, fallo } = Comun;
  let seleccionado = null;

  function tarjeta(p) {
    const siguiente = p.estado === "PENDIENTE" ? ["EN PREPARACION", "Iniciar preparación"]
                    : p.estado === "EN PREPARACION" ? ["LISTO", "Marcar como listo"] : null;
    return `<article class="tarjeta clic ${p.id_pedido === seleccionado ? "activa" : ""}" data-pedido="${p.id_pedido}">${Comun.resumen(p)}
            ${siguiente ? `<div><button data-avanzar="${p.id_pedido}" data-estado="${siguiente[0]}">${siguiente[1]}</button></div>` : ""}</article>`;
  }

  async function cargar() {
    try {
      const r = await api("/api/pedidos");
      mostrar("msgPedidos", r.mensaje, "aviso");
      const por = estado => r.pedidos.filter(p => p.estado === estado).map(tarjeta).join("") || '<p class="suave">—</p>';
      document.getElementById("colPendientes").innerHTML = por("PENDIENTE");
      document.getElementById("colPreparacion").innerHTML = por("EN PREPARACION");
      document.getElementById("colListos").innerHTML = por("LISTO");
      if (seleccionado) await ver(seleccionado, false);
    } catch (e) { fallo("msgPedidos", e); }
  }

  // HU09: estado, cantidades por plato, mesa y mesero asignado
  async function ver(id, limpiar = true) {
    try {
      const p = await api("/api/pedidos/" + id);
      seleccionado = id;
      if (limpiar) mostrar("msgAccion", "");
      const d = document.getElementById("detalle");
      d.hidden = false; d.innerHTML = Comun.detalle(p);
      document.getElementById("sinDetalle").hidden = true;
      document.getElementById("accionesPedido").hidden = false;
    } catch (e) { fallo("msgAccion", e); }
  }

  // HU08: el servidor rechaza los retrocesos con "El estado del pedido no se puede retroceder"
  async function cambiar(id, estado) {
    try {
      const r = await api(`/api/pedidos/${id}/estado`, { method: "PUT", cuerpo: { estado } });
      seleccionado = id;
      mostrar("msgAccion", `Pedido #${id}: ${r.mensaje}`, "ok");
      await cargar();
    } catch (e) { fallo("msgAccion", e); }
  }

  document.addEventListener("click", e => {
    const avanzar = e.target.closest("[data-avanzar]");
    if (avanzar) { cambiar(Number(avanzar.dataset.avanzar), avanzar.dataset.estado); return; }
    const tarjetaEl = e.target.closest("[data-pedido]");
    if (tarjetaEl) ver(Number(tarjetaEl.dataset.pedido));
  });
  document.getElementById("btnEstado").addEventListener("click", () => {
    if (seleccionado) cambiar(seleccionado, document.getElementById("nuevoEstado").value);
  });
  document.getElementById("btnRecargar").addEventListener("click", cargar);

  Comun.tiempoReal(() => cargar());   // HU07: los pedidos nuevos llegan sin recargar
  cargar();
})();
