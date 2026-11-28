/* VistaCliente: HU14 (menú y carrito), HU10 (pedido a domicilio), HU11 (estado de mis pedidos), HU15 (cancelar). */
(() => {
  const { esc, moneda, api, mostrar, fallo } = Comun;
  let menu = [];
  const carrito = new Map();   // id_producto -> cantidad (el carrito vive en la vista)
  let pedidoSeleccionado = null;
  let productoAbierto = null;

  // ---------- Menú (HU14) ----------
  async function cargarMenu() {
    try {
      menu = (await api("/api/menu")).productos;
      document.getElementById("menu").innerHTML = menu.map(p => `
        <article class="tarjeta">
          <div><strong>${esc(p.nombre)}</strong> <span class="suave">${esc(p.tipo)}</span></div>
          <div class="precio">${moneda(p.precio)}</div>
          ${p.disponible ? "" : '<span class="insignia no-disp">No disponible</span>'}
          <div class="fila">
            <button class="secundario" data-ver="${p.id_producto}">Ver detalle</button>
            <button data-agregar="${p.id_producto}" ${p.disponible ? "" : "disabled"}>Agregar</button>
          </div>
        </article>`).join("") || "<p>No hay productos en el menú.</p>";
    } catch (e) { fallo("msgMenu", e); }
  }

  async function verProducto(id) {
    try {
      const p = await api("/api/productos/" + id);
      productoAbierto = p;
      document.getElementById("contenidoProducto").innerHTML = `
        <h2>${esc(p.nombre)}</h2>
        ${p.imagen ? `<img class="producto" src="${esc(p.imagen)}" alt="${esc(p.nombre)}" onerror="this.remove()">` : ""}
        <div class="precio">${moneda(p.precio)}</div>
        <p>${esc(p.descripcion || "Sin descripción")}</p>
        ${p.disponible ? "" : '<span class="insignia no-disp">No disponible</span>'}`;
      document.getElementById("btnAgregarDetalle").disabled = !p.disponible;
      document.getElementById("dlgProducto").showModal();
    } catch (e) { fallo("msgMenu", e); }
  }

  // ---------- Carrito ----------
  function agregar(id) {
    const p = menu.find(x => x.id_producto === id);
    if (!p || !p.disponible) return;            // HU14 esc. 5: no se agrega un producto no disponible
    carrito.set(id, (carrito.get(id) || 0) + 1);
    pintarCarrito();
    mostrar("msgPedido", `"${p.nombre}" agregado al carrito`, "ok");
  }
  function pintarCarrito() {
    const cont = document.getElementById("carrito");
    if (!carrito.size) { cont.innerHTML = '<p class="suave">El carrito está vacío.</p>'; return; }
    let total = 0;
    cont.innerHTML = "<table>" + [...carrito].map(([id, cant]) => {
      const p = menu.find(x => x.id_producto === id); if (!p) return "";
      total += Number(p.precio) * cant;
      return `<tr><td>${esc(p.nombre)}</td><td>${cant}</td><td>${moneda(p.precio * cant)}</td>
              <td><button class="secundario" data-menos="${id}">−</button> <button class="secundario" data-mas="${id}">+</button></td></tr>`;
    }).join("") + `</table><div class="precio">Total: ${moneda(total)}</div>`;
  }
  function cambiarCantidad(id, delta) {
    const nueva = (carrito.get(id) || 0) + delta;
    nueva <= 0 ? carrito.delete(id) : carrito.set(id, nueva);
    pintarCarrito();
  }
  async function confirmarPedido() {
    if (!carrito.size) { mostrar("msgPedido", "Agregue al menos un producto al carrito", "aviso"); return; }
    try {
      const r = await api("/api/pedidos", { method: "POST", cuerpo: {
        tipo_pedido: "DOMICILIO", direccion: document.getElementById("direccion").value,
        items: [...carrito].map(([id_producto, cantidad]) => ({ id_producto, cantidad })) } });
      carrito.clear(); pintarCarrito(); document.getElementById("direccion").value = "";
      mostrar("msgPedido", `${r.mensaje}: pedido #${r.id_pedido} por ${moneda(r.total)}`, "ok");
      await cargarPedidos();
    } catch (e) { fallo("msgPedido", e); }
  }

  // ---------- Mis pedidos (HU11) y cancelación (HU15) ----------
  async function cargarPedidos() {
    try {
      const r = await api("/api/pedidos/historial");
      mostrar("msgPedidos", r.mensaje, "aviso");
      document.getElementById("pedidos").innerHTML = r.pedidos.map(p =>
        `<article class="tarjeta clic ${p.id_pedido === pedidoSeleccionado ? "activa" : ""}" data-pedido="${p.id_pedido}">${Comun.resumen(p)}</article>`).join("");
      if (pedidoSeleccionado) await verPedido(pedidoSeleccionado, false);
    } catch (e) { fallo("msgPedidos", e); }
  }
  async function verPedido(id, limpiar = true) {
    try {
      const p = await api("/api/pedidos/" + id);
      pedidoSeleccionado = id;
      if (limpiar) mostrar("msgCancelar", "");
      const cont = document.getElementById("detallePedido");
      cont.hidden = false;
      cont.innerHTML = Comun.detalle(p) +
        (p.puede_cancelar ? `<button data-cancelar="${p.id_pedido}">Cancelar pedido</button>` : "");
    } catch (e) { fallo("msgCancelar", e); }
  }
  async function cancelar(id) {
    try {
      let r = await api(`/api/pedidos/${id}/cancelar`, { method: "POST" });
      if (r.requiere_confirmacion) {
        if (!window.confirm(r.mensaje)) return;
        r = await api(`/api/pedidos/${id}/cancelar`, { method: "POST", cuerpo: { confirmar: true } });
      }
      mostrar("msgCancelar", r.mensaje, "ok");
      await cargarPedidos();
    } catch (e) { fallo("msgCancelar", e); }
  }

  // ---------- eventos ----------
  document.addEventListener("click", e => {
    const t = e.target;
    if (t.closest("[data-ver]")) verProducto(Number(t.closest("[data-ver]").dataset.ver));
    else if (t.closest("[data-agregar]")) agregar(Number(t.closest("[data-agregar]").dataset.agregar));
    else if (t.closest("[data-mas]")) cambiarCantidad(Number(t.closest("[data-mas]").dataset.mas), 1);
    else if (t.closest("[data-menos]")) cambiarCantidad(Number(t.closest("[data-menos]").dataset.menos), -1);
    else if (t.closest("[data-cancelar]")) cancelar(Number(t.closest("[data-cancelar]").dataset.cancelar));
    else if (t.closest("[data-pedido]")) verPedido(Number(t.closest("[data-pedido]").dataset.pedido));
  });
  document.getElementById("btnConfirmar").addEventListener("click", confirmarPedido);
  document.getElementById("btnRecargar").addEventListener("click", cargarPedidos);
  document.getElementById("btnCerrarDetalle").addEventListener("click", () => document.getElementById("dlgProducto").close());
  document.getElementById("btnAgregarDetalle").addEventListener("click", () => {
    if (productoAbierto) agregar(productoAbierto.id_producto);
    document.getElementById("dlgProducto").close();
  });

  Comun.tiempoReal(() => cargarPedidos());   // el servidor solo envía eventos de MIS pedidos
  cargarMenu().then(pintarCarrito);
  cargarPedidos();
})();
