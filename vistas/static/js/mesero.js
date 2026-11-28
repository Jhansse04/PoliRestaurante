/* VistaMesero: HU03 (crear), HU04 (consultar), HU05 (cancelar), HU06 (historial), HU13 (estados / entregado). */
(() => {
  const { esc, moneda, api, mostrar, fallo } = Comun;
  let productos = [];
  let seleccionado = null;

  // ---------- HU03: crear pedido ----------
  function nuevaLinea() {
    const div = document.createElement("div");
    div.className = "fila";
    div.innerHTML = `<select class="producto">${productos.map(p => `<option value="${p.id_producto}">${esc(p.nombre)} · ${moneda(p.precio)}</option>`).join("")}</select>
                     <input class="cantidad" type="number" min="1" max="99" value="1" style="width:5rem">
                     <button type="button" class="secundario" data-quitar>✕</button>`;
    document.getElementById("lineas").appendChild(div);
  }
  async function crear(e) {
    e.preventDefault();
    const items = [...document.querySelectorAll("#lineas .fila")].map(f => ({
      id_producto: Number(f.querySelector(".producto").value), cantidad: Number(f.querySelector(".cantidad").value) }));
    try {
      const r = await api("/api/pedidos", { method: "POST", cuerpo: {
        tipo_pedido: "MESA", id_mesa: Number(document.getElementById("mesa").value),
        id_cliente: Number(document.getElementById("cliente").value), items } });
      mostrar("msgCrear", `${r.mensaje}: pedido #${r.id_pedido} (${r.origen}) por ${moneda(r.total)}`, "ok");
      document.getElementById("lineas").innerHTML = ""; nuevaLinea();
      await cargarPedidos(); await cargarHistorial();
    } catch (err) { fallo("msgCrear", err); }
  }

  // ---------- HU04: consultar el estado de un pedido ----------
  async function consultar(e) {
    e.preventDefault();
    const caja = document.getElementById("resultadoConsulta");
    try {
      const p = await api("/api/pedidos/" + document.getElementById("idConsulta").value);
      mostrar("msgConsulta", `El pedido #${p.id_pedido} está en estado: ${Comun.ETIQUETAS[p.estado]}`, "ok");
      caja.hidden = false; caja.innerHTML = Comun.detalle(p);
    } catch (err) { caja.hidden = true; fallo("msgConsulta", err); }   // "El pedido no es válido"
  }

  // ---------- HU13: lista, detalle, estado, entregado y cancelación (HU05) ----------
  async function cargarPedidos() {
    try {
      const r = await api("/api/pedidos");
      mostrar("msgPedidos", r.mensaje, "aviso");
      document.getElementById("pedidos").innerHTML = r.pedidos.map(p =>
        `<article class="tarjeta clic ${p.id_pedido === seleccionado ? "activa" : ""}" data-pedido="${p.id_pedido}">${Comun.resumen(p)}</article>`).join("");
      if (seleccionado) await verPedido(seleccionado, false);
    } catch (e) { fallo("msgPedidos", e); }
  }
  async function verPedido(id, limpiar = true) {
    try {
      const p = await api("/api/pedidos/" + id);
      seleccionado = id;
      if (limpiar) mostrar("msgAccion", "");
      const d = document.getElementById("detalle");
      d.hidden = false; d.innerHTML = Comun.detalle(p);
      document.getElementById("accionesPedido").hidden = false;
      document.getElementById("btnCancelar").disabled = !p.puede_cancelar;
    } catch (e) { fallo("msgAccion", e); }
  }
  async function accion(url, metodo, cuerpo) {
    if (!seleccionado) return;
    try {
      const r = await api(url, { method: metodo, cuerpo });
      mostrar("msgAccion", r.mensaje, "ok");
      await cargarPedidos(); await cargarHistorial();
    } catch (e) { fallo("msgAccion", e); }
  }

  // ---------- HU06: historial ----------
  async function cargarHistorial() {
    try {
      const r = await api("/api/pedidos/historial");
      mostrar("msgHistorial", r.mensaje, "aviso");
      document.getElementById("historial").innerHTML = r.pedidos.length
        ? "<tr><th>#</th><th>Origen</th><th>Estado</th><th>Creado</th><th>Total</th></tr>" +
          r.pedidos.map(p => `<tr><td>${p.id_pedido}</td><td>${esc(p.origen)}</td><td>${Comun.insignia(p.estado)}</td><td>${Comun.fecha(p.fecha)}</td><td>${moneda(p.total)}</td></tr>`).join("")
        : "";
    } catch (e) { fallo("msgHistorial", e); }
  }

  document.getElementById("formPedido").addEventListener("submit", crear);
  document.getElementById("formConsulta").addEventListener("submit", consultar);
  document.getElementById("btnLinea").addEventListener("click", nuevaLinea);
  document.getElementById("btnRecargar").addEventListener("click", () => { cargarPedidos(); cargarHistorial(); });
  document.getElementById("btnEstado").addEventListener("click", () =>
    accion(`/api/pedidos/${seleccionado}/estado`, "PUT", { estado: document.getElementById("nuevoEstado").value }));
  document.getElementById("btnEntregar").addEventListener("click", () => accion(`/api/pedidos/${seleccionado}/entregar`, "POST"));
  document.getElementById("btnCancelar").addEventListener("click", () => accion(`/api/pedidos/${seleccionado}/cancelar`, "POST"));
  document.addEventListener("click", e => {
    if (e.target.closest("[data-quitar]")) e.target.closest(".fila").remove();
    else if (e.target.closest("[data-pedido]")) verPedido(Number(e.target.closest("[data-pedido]").dataset.pedido));
  });

  Comun.tiempoReal(() => { cargarPedidos(); cargarHistorial(); });
  api("/api/menu/disponibles").then(r => { productos = r.productos; nuevaLinea(); }).catch(e => fallo("msgCrear", e));
  cargarPedidos(); cargarHistorial();
})();
