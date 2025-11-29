# app.py
import os
from datetime import datetime
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError
import streamlit as st
import pandas as pd

st.set_page_config(page_title="Willy Burger", page_icon="🍔", layout="wide")

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://20225041_db_user:OzIEZ7cBRp8ck7WJ@proyectobd.58lpncv.mongodb.net/?appName=ProyectoBD")
NOMBRE_BD = "willy_burguer_bd"
COLECCIONES = {
    "productos": "Productos",
    "insumos": "Insumos",
    "recetas": "Recetas",
    "pedidos": "Pedidos",
    "metodos_pago": "Metodos_pago",
    "empleados": "Empleados",
    "proveedores": "Proveedores",
    "cajeros": "Cajeros",
    "clientes": "Clientes",
    "ordenes": "Ordenes",
}

@st.cache_resource
def obtener_db():
    cliente = MongoClient(MONGO_URI)
    return cliente[NOMBRE_BD]

db = obtener_db()
col_productos   = db[COLECCIONES["productos"]]
col_insumos     = db[COLECCIONES["insumos"]]
col_recetas     = db[COLECCIONES["recetas"]]
col_pedidos     = db[COLECCIONES["pedidos"]]
col_metodos     = db[COLECCIONES["metodos_pago"]]
col_empleados   = db[COLECCIONES["empleados"]]
col_proveedores = db[COLECCIONES["proveedores"]]
col_cajeros     = db[COLECCIONES["cajeros"]]
col_clientes    = db[COLECCIONES["clientes"]]
col_ordenes     = db[COLECCIONES["ordenes"]]

def listar_productos():
    return list(col_productos.find({}, {"_id":0}).sort("idProducto", 1))

def listar_insumos():
    return list(col_insumos.find({}, {"_id":0}).sort("idInsumo", 1))

def listar_receta(id_producto: int):
    return col_recetas.find_one({"idProducto": id_producto}, {"_id":0})

def listar_metodos_pago():
    d = list(col_metodos.find({}, {"_id":0}))
    return [x["nombre"] for x in d] if d else ["Efectivo","Tarjeta","Yape/Plin"]

def listar_empleados():
    d = list(col_empleados.find({}, {"_id":0}))
    return [x["nombre"] for x in d] if d else ["Juan Pérez (Cajero)","María López (Admin)"]

def listar_cajeros():
    d = list(col_cajeros.find({}, {"_id":0}))
    return [x["nombre"] for x in d] if d else ["Cajero 1","Cajero 2"]

def listar_proveedores():
    d = list(col_proveedores.find({}, {"_id":0}))
    return [x["nombre"] for x in d] if d else ["Makro","Proveedor 2"]

def nuevo_id(coleccion, campo_id):
    doc = coleccion.find_one(sort=[(campo_id, -1)])
    return (doc[campo_id] if doc else 0) + 1

if "carrito_ventas" not in st.session_state:
    st.session_state.carrito_ventas = []
if "carrito_compras" not in st.session_state:
    st.session_state.carrito_compras = []

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=80)
    opcion = st.radio(
        "Navegación",
        ["🍔 Ventas", "📦 Compras", "📊 Inventario", "🧾 Historial"],
        index=0
    )

# ----------- VENTAS -----------
if opcion == "🍔 Ventas":
    st.markdown("<h2 style='margin-bottom:0'>Nueva venta</h2>", unsafe_allow_html=True)
    productos = listar_productos()
    nombres_prod = [p["nombre"] for p in productos]
    metodos_pago = listar_metodos_pago()
    cajeros = listar_cajeros()

    c1, c2, c3 = st.columns(3)
    with c1:
        dni_cliente = st.text_input("DNI/RUC del cliente", "")
        nombre_cliente = st.text_input("Nombre del cliente", "")
    with c2:
        cajero = st.selectbox("Cajero", cajeros)
        metodo = st.selectbox("Método de pago", metodos_pago)
    with c3:
        st.metric("Ítems en carrito", len(st.session_state.carrito_ventas))

    st.markdown("### Agregar productos")
    f1, f2, f3, f4 = st.columns([3,1,1,1])
    with f1:
        filtro = st.text_input("Buscar", "")
        lista_filtrada = [n for n in nombres_prod if filtro.lower() in n.lower()] or nombres_prod
        nombre_sel = st.selectbox("Producto", lista_filtrada, index=0)
        prod_sel = next((p for p in productos if p["nombre"] == nombre_sel), None)
    precio = float(prod_sel["precio"]) if prod_sel else 0.0
    with f2:
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
    with f3:
        st.info(f"S/ {precio:.2f}")
    with f4:
        st.write("")
        if st.button("➕ Agregar"):
            st.session_state.carrito_ventas.append({
                "idProducto": int(prod_sel["idProducto"]),
                "nombre": prod_sel["nombre"],
                "precio": precio,
                "cantidad": int(cantidad),
                "subtotal": round(precio*int(cantidad), 2)
            })
            st.toast("Producto agregado")

    if st.session_state.carrito_ventas:
        df = pd.DataFrame(st.session_state.carrito_ventas)
        st.dataframe(df, use_container_width=True, hide_index=True)
        total = float(df["subtotal"].sum())
        m1, m2, m3 = st.columns([2,1,1])
        with m2:
            st.metric("Total", f"S/ {total:.2f}")
        with m3:
            if st.button("🧹 Limpiar"):
                st.session_state.carrito_ventas = []
                st.rerun()

        if st.button("✅ Finalizar venta", type="primary", use_container_width=True):
            try:
                necesidades = {}
                for item in st.session_state.carrito_ventas:
                    r = listar_receta(item["idProducto"])
                    if not r: 
                        continue
                    for ins in r.get("insumos", []):
                        req = float(item["cantidad"]) * float(ins["cantidadInsumo"])
                        necesidades[ins["idInsumo"]] = necesidades.get(ins["idInsumo"], 0.0) + req

                if necesidades:
                    ids = list(necesidades.keys())
                    existentes = {d["idInsumo"]: float(d["stock"]) for d in col_insumos.find({"idInsumo":{"$in": ids}}, {"_id":0, "idInsumo":1, "stock":1})}
                    faltantes = [i for i, req in necesidades.items() if existentes.get(i, 0.0) < req]
                    if faltantes:
                        st.error(f"Stock insuficiente de insumos: {faltantes}")
                        st.stop()

                    ops = [UpdateOne({"idInsumo": i}, {"$inc": {"stock": -necesidades[i]}}) for i in necesidades]
                    col_insumos.bulk_write(ops)

                nuevo = {
                    "idPedido": nuevo_id(col_pedidos, "idPedido"),
                    "fecha": datetime.utcnow(),
                    "estado": "ENTREGADO",
                    "total": total,
                    "cliente": {"dni": dni_cliente or None, "nombre": nombre_cliente or "Cliente"},
                    "cajero": {"nombre": cajero},
                    "metodo_pago": {"nombre": metodo},
                    "detalle": st.session_state.carrito_ventas
                }
                col_pedidos.insert_one(nuevo)
                st.balloons()
                st.success(f"Venta #{nuevo['idPedido']} registrada")
                st.session_state.carrito_ventas = []
                st.rerun()
            except PyMongoError as e:
                st.error(f"Error al registrar: {e}")

# ----------- COMPRAS -----------
elif opcion == "📦 Compras":
    st.markdown("<h2 style='margin-bottom:0'>Nueva compra</h2>", unsafe_allow_html=True)
    insumos = listar_insumos()
    nombres_ins = [i["nombre"] for i in insumos]
    proveedores = listar_proveedores()
    solicitantes = listar_empleados()

    c1, c2 = st.columns(2)
    with c1:
        proveedor = st.selectbox("Proveedor", proveedores)
    with c2:
        solicitante = st.selectbox("Solicitante", solicitantes)

    st.markdown("### Agregar insumos")
    g1, g2, g3, g4 = st.columns([3,1,1,1])
    with g1:
        filtro_i = st.text_input("Buscar insumo", "")
        lista_filtrada = [n for n in nombres_ins if filtro_i.lower() in n.lower()] or nombres_ins
        nombre_ins = st.selectbox("Insumo", lista_filtrada)
        ins_sel = next((i for i in insumos if i["nombre"] == nombre_ins), None)
    with g2:
        cantidad = st.number_input("Cantidad", min_value=0.1, step=0.1, value=1.0)
    with g3:
        costo = st.number_input("Costo unitario (S/.)", min_value=0.1, step=0.1, value=1.0)
    with g4:
        st.write("")
        if st.button("➕ Añadir"):
            st.session_state.carrito_compras.append({
                "idInsumo": int(ins_sel["idInsumo"]),
                "nombre": ins_sel["nombre"],
                "cantidadComprada": float(cantidad),
                "costoUnitario": float(costo),
                "subtotal": round(float(cantidad)*float(costo), 2)
            })
            st.toast("Insumo agregado")

    if st.session_state.carrito_compras:
        dfc = pd.DataFrame(st.session_state.carrito_compras)
        st.dataframe(dfc, use_container_width=True, hide_index=True)
        total_c = float(dfc["subtotal"].sum())
        m1, m2, m3 = st.columns([2,1,1])
        with m2:
            st.metric("Total compra", f"S/ {total_c:.2f}")
        with m3:
            if st.button("🧹 Limpiar compra"):
                st.session_state.carrito_compras = []
                st.rerun()

        if st.button("📤 Registrar compra", type="primary", use_container_width=True):
            try:
                ops = [UpdateOne({"idInsumo": x["idInsumo"]}, {"$inc": {"stock": x["cantidadComprada"]}}) for x in st.session_state.carrito_compras]
                col_insumos.bulk_write(ops)
                orden = {
                    "idOrden": nuevo_id(col_ordenes, "idOrden"),
                    "fecha": datetime.utcnow(),
                    "montoTotal": total_c,
                    "proveedor": {"nombre": proveedor},
                    "solicitante": {"nombre": solicitante},
                    "detalle": st.session_state.carrito_compras
                }
                col_ordenes.insert_one(orden)
                st.success(f"Compra #{orden['idOrden']} registrada")
                st.session_state.carrito_compras = []
                st.balloons()
                st.rerun()
            except PyMongoError as e:
                st.error(f"Error al registrar compra: {e}")

# ----------- INVENTARIO -----------
elif opcion == "📊 Inventario":
    st.markdown("<h2 style='margin-bottom:0'>Inventario</h2>", unsafe_allow_html=True)
    insumos = listar_insumos()
    df = pd.DataFrame(insumos)
    st.dataframe(df, use_container_width=True, hide_index=True)
    st.markdown("### Ajuste rápido de stock")
    a1, a2, a3 = st.columns([3,1,1])
    with a1:
        nombre_ins = st.selectbox("Insumo", [i["nombre"] for i in insumos])
        ins_sel = next(i for i in insumos if i["nombre"] == nombre_ins)
        st.caption(f"Stock actual: {ins_sel['stock']}")
    with a2:
        delta = st.number_input("Ajuste (+/-)", step=0.1, value=0.0)
    with a3:
        st.write("")
        if st.button("💾 Aplicar ajuste"):
            try:
                col_insumos.update_one({"idInsumo": int(ins_sel["idInsumo"])}, {"$inc": {"stock": float(delta)}})
                st.success("Stock actualizado")
                st.rerun()
            except PyMongoError as e:
                st.error(f"Error al ajustar: {e}")

# ----------- HISTORIAL -----------
elif opcion == "🧾 Historial":
    st.markdown("<h2 style='margin-bottom:0'>Historial de pedidos</h2>", unsafe_allow_html=True)
    docs = list(col_pedidos.find({}, {"_id":0}).sort("idPedido", -1).limit(100))
    if not docs:
        st.info("Sin pedidos registrados.")
    else:
        for ped in docs:
            with st.expander(f"Pedido #{ped['idPedido']} • {ped['estado']} • S/ {ped['total']:.2f}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"Cliente: {ped.get('cliente',{}).get('nombre','-')}")
                c2.write(f"Pago: {ped.get('metodo_pago',{}).get('nombre','-')}")
                c3.write(f"Fecha: {ped['fecha']}")
                st.dataframe(pd.DataFrame(ped["detalle"]), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Willy Burger • Streamlit + PyMongo • 2025")
