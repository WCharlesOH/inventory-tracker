

import os
from datetime import datetime
import streamlit as st
import pandas as pd
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError

st.set_page_config(page_title="Wily Burger System", page_icon="🍔", layout="wide")

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://20225041_db_user:OzIEZ7cBRp8ck7WJ@proyectobd.58lpncv.mongodb.net/?appName=ProyectoBD")
NOMBRE_BD = os.getenv("MONGO_DBNAME", "wilyburger_db")

@st.cache_resource
def obtener_db():
    return MongoClient(MONGO_URI)[NOMBRE_BD]

db = obtener_db()

# Colecciones
col_productos   = db["productos"]
col_insumos     = db["insumos"]
col_recetas     = db["recetas"]
col_pedidos     = db["pedidos"]
col_compras     = db["compras"]
col_empleados   = db["empleados"]
col_proveedores = db["proveedores"]
col_clientes    = db["clientes"]
col_cajeros     = db["cajeros"]
col_metodos     = db["metodos_pago"]
col_ordenes     = db["ordenes"]


# Utilidades

def listar_productos():
    return list(col_productos.find({}, {"_id": 0}).sort("idProducto", 1))

def listar_insumos():
    return list(col_insumos.find({}, {"_id": 0}).sort("idInsumo", 1))

def receta_de(id_producto: int):
    return col_recetas.find_one({"idProducto": id_producto}, {"_id": 0}) or {}

def listar_empleados():
    data = list(col_empleados.find({}, {"_id": 0}))
    return [x.get("nombre", "") for x in data] or ["Juan Pérez (Cajero)", "María López (Admin)", "Carlos Ruiz (Cocinero)"]

def listar_proveedores():
    data = list(col_proveedores.find({}, {"_id": 0}))
    return [x.get("nombre", "") for x in data] or ["Makro", "Bimbo Perú", "Coca Cola"]

def listar_cajeros():
    data = list(col_cajeros.find({}, {"_id": 0}))
    return [x.get("nombre", "") for x in data] or ["Cajero 1", "Cajero 2"]

def listar_metodos():
    data = list(col_metodos.find({}, {"_id": 0}))
    return [x.get("nombre", "") for x in data] or ["Efectivo", "Tarjeta", "Yape/Plin"]

def nuevo_id(coleccion, campo_id):
    doc = coleccion.find_one(sort=[(campo_id, -1)])
    return (doc[campo_id] if doc else 0) + 1

def buscar_cliente(dni: str):
    if not dni:
        return None
    return col_clientes.find_one({"$or": [{"_id": dni}, {"idCliente": dni}]}, {"_id": 0, "idCliente": 1, "nombre": 1, "telefono": 1})

def crear_o_actualizar_cliente(dni: str, nombre: str, telefono: str | None):
    col_clientes.update_one(
        {"_id": dni},
        {"$set": {"idCliente": dni, "nombre": (nombre or "Cliente").strip(), "telefono": (telefono or None)}},
        upsert=True
    )

def es_dni_o_ruc(valor: str):
    v = (valor or "").strip()
    if v.isdigit() and len(v) == 8:  return "DNI"
    if v.isdigit() and len(v) == 11: return "RUC"
    return None

def es_celular_valido(tel: str):
    t = (tel or "").strip()
    if t == "": return True
    return t.isdigit() and len(t) == 9 and t.startswith("9")


# Estado

if "carrito_ventas" not in st.session_state:   st.session_state.carrito_ventas = []
if "carrito_compras" not in st.session_state:  st.session_state.carrito_compras = []
if "dni_cliente" not in st.session_state:      st.session_state.dni_cliente = ""
if "nombre_cliente" not in st.session_state:   st.session_state.nombre_cliente = ""
if "telefono_cliente" not in st.session_state: st.session_state.telefono_cliente = ""


# Sidebar / Navegación

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=80)
    rol_actual = st.selectbox("Rol actual", ["Cajero", "Cocinero", "Administrador"], index=0)
    paginas = ["🍔 Ventas", "👨‍🍳 Pedidos pendientes", "🧾 Historial"]
    if rol_actual == "Administrador":
        paginas.insert(1, "📦 Compras")
    pagina = st.radio("Navegación", paginas, index=0)


# Ventas

if pagina == "🍔 Ventas":
    st.markdown("## Nueva venta")

    productos = listar_productos()
    mapa_prod = {p["nombre"]: p for p in productos}
    opciones_prod = list(mapa_prod.keys())
    if not opciones_prod:
        st.info("No hay productos disponibles.")
        st.stop()

    metodos = listar_metodos()
    cajeros = listar_cajeros()

    c1, c2, c3, c4, c5, c6 = st.columns([1.1, 1.6, 1.2, 1.2, 1.1, 1.3])
    with c1:
        st.text_input("DNI/RUC", key="dni_cliente")
    with c2:
        st.text_input("Nombre del cliente", key="nombre_cliente")
    with c3:
        st.text_input("Teléfono (opcional)", key="telefono_cliente")
    with c4:
        cajero = st.selectbox("Cajero", cajeros)
    with c5:
        if st.button("Buscar cliente"):
            dni = (st.session_state.dni_cliente or "").strip()
            cli = buscar_cliente(dni)
            if cli:
                st.session_state.nombre_cliente = cli.get("nombre", "")
                st.session_state.telefono_cliente = cli.get("telefono", "")
                st.success("Cliente cargado.")
            else:
                st.info("No se encontró el cliente.")
    with c6:
        if st.button("Registrar/Actualizar cliente"):
            dni = (st.session_state.dni_cliente or "").strip()
            nom = (st.session_state.nombre_cliente or "").strip()
            tel = (st.session_state.telefono_cliente or "").strip()
            if not es_dni_o_ruc(dni):
                st.error("DNI debe tener 8 dígitos o RUC 11 dígitos.")
            elif not es_celular_valido(tel):
                st.error("El teléfono debe tener 9 dígitos y empezar en 9 (o déjalo vacío).")
            else:
                crear_o_actualizar_cliente(dni, nom, tel)
                st.success("Cliente registrado/actualizado.")

    st.markdown("### Agregar productos")
    f1, f2, f3 = st.columns([3,1,1])
    with f1:
        nombre_sel = st.selectbox("Producto", opciones_prod, index=0)
        prod_sel = mapa_prod[nombre_sel]
    with f2:
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
    with f3:
        st.info(f"S/ {float(prod_sel['precio']):.2f}")

    if st.button("➕ Agregar"):
        st.session_state.carrito_ventas.append({
            "idProducto": int(prod_sel["idProducto"]),
            "nombre": prod_sel["nombre"],
            "precio": float(prod_sel["precio"]),
            "cantidad": int(cantidad),
            "subtotal": round(float(prod_sel["precio"]) * int(cantidad), 2)
        })
        st.toast("Producto agregado")

    if st.session_state.carrito_ventas:
        df = pd.DataFrame(st.session_state.carrito_ventas)
        st.dataframe(df, use_container_width=True, hide_index=True)
        total = float(df["subtotal"].sum())
        st.metric("Total", f"S/ {total:.2f}")

        if st.button("✅ Finalizar venta", type="primary", use_container_width=True):
            try:
                necesidades = {}
                for it in st.session_state.carrito_ventas:
                    r = receta_de(it["idProducto"])
                    for ins in r.get("insumos", []):
                        req = float(it["cantidad"]) * float(ins["cantidadInsumo"])
                        necesidades[ins["idInsumo"]] = necesidades.get(ins["idInsumo"], 0.0) + req

                if necesidades:
                    ids = list(necesidades.keys())
                    stocks = {d["idInsumo"]: float(d["stock"]) for d in col_insumos.find({"idInsumo": {"$in": ids}}, {"_id": 0, "idInsumo": 1, "stock": 1})}
                    faltantes = [i for i, req in necesidades.items() if stocks.get(i, 0.0) < req]
                    if faltantes:
                        st.error(f"Stock insuficiente en insumos: {faltantes}")
                        st.stop()
                    ops = [UpdateOne({"idInsumo": i}, {"$inc": {"stock": -necesidades[i]}}) for i in necesidades]
                    col_insumos.bulk_write(ops)

                dni = (st.session_state.dni_cliente or "").strip()
                nom = (st.session_state.nombre_cliente or "Cliente").strip()
                tel = (st.session_state.telefono_cliente or "").strip()
                if es_dni_o_ruc(dni) and es_celular_valido(tel):
                    crear_o_actualizar_cliente(dni, nom, tel)

                pedido = {
                    "idPedido": nuevo_id(col_pedidos, "idPedido"),
                    "fecha": datetime.utcnow(),
                    "actualizado_en": datetime.utcnow(),
                    "estado": "EN PROCESO",
                    "total": total,
                    "cliente": nom,
                    "dni": dni or None,
                    "telefono": tel or None,
                    "cajero": cajero,
                    "metodo_pago": st.selectbox("Método de pago", listar_metodos(), key="met_pago"),
                    "detalle": st.session_state.carrito_ventas
                }
                col_pedidos.insert_one(pedido)
                st.success(f"Venta #{pedido['idPedido']} registrada y enviada a Pedidos pendientes")
                st.session_state.carrito_ventas = []
                st.rerun()
            except PyMongoError as e:
                st.error(f"Error al registrar: {e}")
    else:
        st.info("Carrito vacío.")


# Compras (solo Administrador)

elif pagina == "📦 Compras":
    if rol_actual != "Administrador":
        st.warning("Solo Administrador puede registrar compras.")
        st.stop()

    st.markdown("## Nueva compra")

    insumos = listar_insumos()
    mapa_ins = {i["nombre"]: i for i in insumos}
    opciones_ins = list(mapa_ins.keys())
    if not opciones_ins:
        st.info("No hay insumos disponibles.")
        st.stop()

    proveedor = st.selectbox("Proveedor", listar_proveedores())
    solicitante = st.selectbox("Solicitante", listar_empleados())

    g1, g2, g3 = st.columns([3,1,1])
    with g1:
        nombre_i = st.selectbox("Insumo", opciones_ins, index=0)
        ins_sel = mapa_ins[nombre_i]
    with g2:
        cantidad = st.number_input("Cantidad", min_value=0.1, step=0.1, value=1.0)
    with g3:
        costo = st.number_input("Costo unitario (S/.)", min_value=0.1, step=0.1, value=1.0)

    if st.button("➕ Añadir"):
        st.session_state.carrito_compras.append({
            "idInsumo": int(ins_sel["idInsumo"]),
            "nombre": ins_sel["nombre"],
            "cantidadComprada": float(cantidad),
            "costoUnitario": float(costo),
            "subtotal": round(float(cantidad) * float(costo), 2)
        })
        st.toast("Insumo agregado")

    if st.session_state.carrito_compras:
        dfc = pd.DataFrame(st.session_state.carrito_compras)
        st.dataframe(dfc, use_container_width=True, hide_index=True)
        total_c = float(dfc["subtotal"].sum())
        st.metric("Total compra", f"S/ {total_c:.2f}")

        if st.button("📤 Registrar compra", type="primary", use_container_width=True):
            try:
                ops = [UpdateOne({"idInsumo": x["idInsumo"]}, {"$inc": {"stock": x["cantidadComprada"]}}) for x in st.session_state.carrito_compras]
                col_insumos.bulk_write(ops)
                compra = {
                    "idOrden": nuevo_id(col_ordenes, "idOrden"),
                    "fecha": datetime.utcnow(),
                    "montoTotal": total_c,
                    "proveedor": proveedor,
                    "solicitante": solicitante,
                    "detalle": st.session_state.carrito_compras
                }
                col_compras.insert_one(compra)
                st.success(f"Compra #{compra['idOrden']} registrada")
                st.session_state.carrito_compras = []
                st.balloons()
                st.rerun()
            except PyMongoError as e:
                st.error(f"Error al registrar compra: {e}")
    else:
        st.info("Sin insumos en la orden.")


# Pedidos pendientes (Cocina)

elif pagina == "👨‍🍳 Pedidos pendientes":
    st.markdown("## Pedidos pendientes")
    estados_en_cocina = ["EN PROCESO", "PREPARANDO"]
    pendientes = list(col_pedidos.find({"estado": {"$in": estados_en_cocina}}).sort("fecha", 1))

    if not pendientes:
        st.info("No hay pedidos pendientes.")
    else:
        for ped in pendientes:
            titulo = f"#{ped.get('idPedido','?')} • {ped.get('cliente','-')} • S/ {ped.get('total',0):.2f} • {ped.get('estado')}"
            with st.expander(titulo, expanded=False):
                c1, c2 = st.columns([2,1])
                with c1:
                    det = pd.DataFrame(ped.get("detalle", []))
                    if not det.empty:
                        st.dataframe(det, use_container_width=True, hide_index=True)
                with c2:
                    st.write(f"Fecha: {ped.get('fecha')}")
                    st.write(f"Cajero: {ped.get('cajero')}")
                    st.write(f"Pago: {ped.get('metodo_pago')}")
                    nuevo_estado = st.selectbox(
                        "Actualizar estado",
                        ["EN PROCESO", "PREPARANDO", "ENTREGADO"],
                        index=["EN PROCESO", "PREPARANDO", "ENTREGADO"].index(ped.get("estado", "EN PROCESO")),
                        key=f"estado_{ped.get('idPedido')}"
                    )
                    if st.button("Guardar", key=f"guardar_{ped.get('idPedido')}"):
                        col_pedidos.update_one(
                            {"idPedido": ped["idPedido"]},
                            {"$set": {"estado": nuevo_estado, "actualizado_en": datetime.utcnow()}}
                        )
                        st.success("Estado actualizado")
                        st.rerun()


# Historial

elif pagina == "🧾 Historial":
    st.markdown("## Historial")
    t1, t2 = st.tabs(["Pedidos", "Compras"])

    with t1:
        pedidos = list(col_pedidos.find({}, {"_id": 0}).sort("fecha", -1).limit(100))
        if not pedidos:
            st.info("Sin pedidos registrados.")
        else:
            for ped in pedidos:
                with st.expander(f"#{ped.get('idPedido','?')} • {ped.get('estado','-')} • S/ {ped.get('total',0):.2f}"):
                    c1, c2, c3 = st.columns(3)
                    c1.write(f"Cliente: {ped.get('cliente','-')}")
                    c2.write(f"Pago: {ped.get('metodo_pago','-')}")
                    c3.write(f"Fecha: {ped.get('fecha')}")
                    det = pd.DataFrame(ped.get("detalle", []))
                    if not det.empty:
                        st.dataframe(det, use_container_width=True, hide_index=True)

    with t2:
        compras = list(col_compras.find({}, {"_id": 0}).sort("fecha", -1).limit(100))
        if not compras:
            st.info("Sin compras registradas.")
        else:
            for comp in compras:
                with st.expander(f"#{comp.get('idOrden','?')} • S/ {comp.get('montoTotal',0):.2f}"):
                    c1, c2 = st.columns(2)
                    c1.write(f"Proveedor: {comp.get('proveedor','-')}")
                    c2.write(f"Fecha: {comp.get('fecha')}")
                    det = pd.DataFrame(comp.get("detalle", []))
                    if not det.empty:
                        st.dataframe(det, use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Sistema Wily Burger | Desarrollado por Equipo 5 - Proyecto BD 2025")