/* VistaAdministrador: HU01 (crear producto), HU02 (modificar producto), HU12 (panel general de pedidos). */
(() => {
  const { esc, moneda, api, mostrar, fallo } = Comun;
  let productos = [];
  let editando = null;          // id del producto en edición (HU02) o null (HU01)
  let abierto = null;           // pedido expandido en el panel

  // ---------- HU12: panel general ----------
  async function cargarPanel() {
    try {
      const r = await api("/api/admin/panel");
      mostrar("msgPanel", r.mensaje, "aviso");
      const t = document.getElementById("panel");
      if (!r.pedidos.length) { t.innerHTML = ""; return; }
      t.innerHTML = "<tr><th>#</th><th>Origen</th><th>Responsable</th><th>Estado</th><th>Creado</th><th>Tiempo en el estado</th><th>Total</th></tr>" +
        r.pedidos.map(p => `
          <tr class="clic" data-pedido="${p.id_pedido}">
            <td>${p.id_pedido}</td><td>${esc(p.origen)}</td><td>${esc(p.responsable || "—")}</td><td>${Comun.insignia(p.estado)}</td>
            <td>${Comun.fecha(p.fecha)}</td><td>${Comun.duracion(p.segundos_en_estado)}</td><td>${moneda(p.total)}</td></tr>
          ${abierto === p.id_pedido ? `<tr><td colspan="7"><div class="detalle">${Comun.detalle(p)}</div></td></tr>` : ""}`).join("");
    } catch (e) { fallo("msgPanel", e); }   // "No fue posible realizar su consulta, intente nuevamente"
  }

  // ---------- HU01 / HU02: productos ----------
  async function cargarProductos() {
    try {
      productos = (await api("/api/menu")).productos;
      document.getElementById("productos").innerHTML =
        "<tr><th>Nombre</th><th>Tipo</th><th>Precio</th><th>Disp.</th><th></th></tr>" +
        productos.map(p => `<tr><td>${esc(p.nombre)}</td><td>${esc(p.tipo)}</td><td>${moneda(p.precio)}</td>
          <td>${p.disponible ? "Sí" : "No"}</td><td><button class="secundario" data-editar="${p.id_producto}">Editar</button></td></tr>`).join("");
    } catch (e) { fallo("msgProducto", e); }
  }
  function formulario(p) {
    editando = p ? p.id_producto : null;
    document.getElementById("tituloForm").textContent = p ? `Editar producto #${p.id_producto}` : "Nuevo producto";
    document.getElementById("btnGuardar").textContent = p ? "Guardar cambios" : "Crear producto";
    document.getElementById("btnNuevo").hidden = !p;
    document.getElementById("nombre").value = p ? p.nombre : "";
    document.getElementById("descripcion").value = p ? (p.descripcion || "") : "";
    document.getElementById("precio").value = p ? p.precio : "";
    document.getElementById("tipo").value = p ? p.tipo : "PLATO";
    document.getElementById("disponible").value = p ? String(p.disponible) : "true";
    document.getElementById("imagen").value = p ? (p.imagen || "") : "";
  }
  async function guardar(e) {
    e.preventDefault();
    const cuerpo = {
      nombre: document.getElementById("nombre").value, descripcion: document.getElementById("descripcion").value,
      precio: document.getElementById("precio").value, tipo: document.getElementById("tipo").value,
      disponible: document.getElementById("disponible").value === "true", imagen: document.getElementById("imagen").value };
    try {
      const r = editando
        ? await api("/api/admin/productos/" + editando, { method: "PUT", cuerpo })
        : await api("/api/admin/productos", { method: "POST", cuerpo });
      mostrar("msgProducto", r.mensaje, "ok");
      formulario(null);
      await cargarProductos();
    } catch (err) { fallo("msgProducto", err); }   // indica qué campos están mal (HU01 esc. 2 / HU02 esc. 2)
  }

  document.getElementById("formProducto").addEventListener("submit", guardar);
  document.getElementById("btnNuevo").addEventListener("click", () => { formulario(null); mostrar("msgProducto", ""); });
  document.getElementById("btnRecargar").addEventListener("click", cargarPanel);
  document.addEventListener("click", e => {
    const ed = e.target.closest("[data-editar]");
    if (ed) { formulario(productos.find(p => p.id_producto === Number(ed.dataset.editar))); mostrar("msgProducto", ""); return; }
    const fila = e.target.closest("tr[data-pedido]");
    if (fila) { const id = Number(fila.dataset.pedido); abierto = abierto === id ? null : id; cargarPanel(); }
  });

  Comun.tiempoReal(() => cargarPanel());
  cargarPanel(); cargarProductos();
})();
