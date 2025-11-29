# app.py
import os
from datetime import datetime
import streamlit as st
import pandas as pd
from pymongo import MongoClient, UpdateOne
from pymongo.errors import PyMongoError

st.set_page_config(page_title="Willy Burger", page_icon="🍔", layout="wide")

MONGO_URI = os.getenv("MONGO_URI", "mongodb+srv://20225041_db_user:OzIEZ7cBRp8ck7WJ@proyectobd.58lpncv.mongodb.net/?appName=ProyectoBD")
NOMBRE_BD = "willy_burguer_bd"
COL = {
    "productos": "Productos",
    "insumos": "Insumos",
    "recetas": "Recetas",
    "pedidos": "Pedidos",
    "metodos": "Metodos_pago",
    "empleados": "Empleados",
    "proveedores": "Proveedores",
    "cajeros": "Cajeros",
    "clientes": "Clientes",
    "ordenes": "Ordenes",
}

@st.cache_resource
def obtener_db():
    return MongoClient(MONGO_URI)[NOMBRE_BD]  # cachea conexión única para toda la app. :contentReference[oaicite:1]{index=1}

db = obtener_db()
c_prod = db[COL["productos"]]
c_ins = db[COL["insumos"]]
c_rec = db[COL["recetas"]]
c_ped = db[COL["pedidos"]]
c_met = db[COL["metodos"]]
c_emp = db[COL["empleados"]]
c_prov = db[COL["proveedores"]]
c_caj = db[COL["cajeros"]]
c_cli = db[COL["clientes"]]
c_ord = db[COL["ordenes"]]

def listar_productos():   return list(c_prod.find({}, {"_id":0}).sort("idProducto", 1))
def listar_insumos():     return list(c_ins.find({}, {"_id":0}).sort("idInsumo", 1))
def receta_de(pid:int):   return c_rec.find_one({"idProducto": pid}, {"_id":0})
def metodos_pago():       return [x["nombre"] for x in c_met.find({}, {"_id":0})] or ["Efectivo","Tarjeta","Yape/Plin"]
def cajeros():            return [x["nombre"] for x in c_caj.find({}, {"_id":0})] or ["Cajero 1","Cajero 2"]
def proveedores():        return [x["nombre"] for x in c_prov.find({}, {"_id":0})] or ["Makro"]
def nuevo_id(colec, campo): 
    doc = colec.find_one(sort=[(campo, -1)])
    return (doc[campo] if doc else 0) + 1

if "carrito_ventas" not in st.session_state:   st.session_state.carrito_ventas = []
if "carrito_compras" not in st.session_state:  st.session_state.carrito_compras = []
if "dni_cliente" not in st.session_state:      st.session_state.dni_cliente = ""
if "nombre_cliente" not in st.session_state:   st.session_state.nombre_cliente = ""

def cargar_cliente_por_dni():
    dni = st.session_state.dni_cliente.strip()
    if not dni: 
        return
    cli = c_cli.find_one({"idCliente": dni}, {"_id":0})
    if cli:
        st.session_state.nombre_cliente = cli.get("nombre","")

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=72)
    rol_actual = st.selectbox("Rol actual", ["CAJERO","COCINERO","ADMIN"], index=0)
    opcion = st.radio("Navegación", ["🍔 Ventas", "📦 Compras", "👨‍🍳 Cocina (Pedidos web)", "🧾 Historial"])

# -------------------- VENTAS --------------------
if opcion == "🍔 Ventas":
    st.markdown("## Nueva venta")
    prods = listar_productos()
    nombres_prod = [p["nombre"] for p in prods]
    metodos = metodos_pago()
    cajero = st.selectbox("Cajero", cajeros())

    c1, c2, c3 = st.columns(3)
    with c1:
        st.text_input("DNI/RUC", key="dni_cliente", on_change=cargar_cliente_por_dni)  # callback al presionar Enter. :contentReference[oaicite:2]{index=2}
    with c2:
        st.text_input("Nombre del cliente", key="nombre_cliente")
    with c3:
        metodo = st.selectbox("Método de pago", metodos)

    st.markdown("### Agregar productos")
    f1, f2, f3 = st.columns([3,1,1])
    with f1:
        nombre_sel = st.selectbox("Producto", nombres_prod)
        prod_sel = next((p for p in prods if p["nombre"] == nombre_sel), None)
    with f2:
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
    with f3:
        if prod_sel: st.metric("Precio", f"S/ {float(prod_sel['precio']):.2f}")
    if st.button("➕ Agregar"):
        st.session_state.carrito_ventas.append({
            "idProducto": int(prod_sel["idProducto"]),
            "nombre": prod_sel["nombre"],
            "precio": float(prod_sel["precio"]),
            "cantidad": int(cantidad),
            "subtotal": round(float(prod_sel["precio"])*int(cantidad), 2)
        })
        st.toast("Producto agregado")

    if st.session_state.carrito_ventas:
        df = pd.DataFrame(st.session_state.carrito_ventas)
        st.dataframe(df, use_container_width=True, hide_index=True)
        total = float(df["subtotal"].sum())
        cta1, cta2 = st.columns([3,1])
        with cta2:
            st.metric("Total", f"S/ {total:.2f}")
        if st.button("✅ Finalizar venta", type="primary", use_container_width=True):
            try:
                necesidades = {}
                for item in st.session_state.carrito_ventas:
                    r = receta_de(item["idProducto"]) or {}
                    for ins in r.get("insumos", []):
                        req = float(item["cantidad"]) * float(ins["cantidadInsumo"])
                        necesidades[ins["idInsumo"]] = necesidades.get(ins["idInsumo"], 0.0) + req
                if necesidades:
                    ids = list(necesidades.keys())
                    stocks = {d["idInsumo"]: float(d["stock"]) for d in c_ins.find({"idInsumo":{"$in": ids}}, {"_id":0,"idInsumo":1,"stock":1})}
                    faltantes = [i for i, req in necesidades.items() if stocks.get(i, 0.0) < req]
                    if faltantes:
                        st.error(f"Stock insuficiente en insumos: {faltantes}")
                        st.stop()
                    ops = [UpdateOne({"idInsumo": i}, {"$inc": {"stock": -necesidades[i]}}) for i in necesidades]
                    c_ins.bulk_write(ops)  # lote eficiente. :contentReference[oaicite:3]{index=3}

                pedido = {
                    "idPedido": nuevo_id(c_ped, "idPedido"),
                    "fecha": datetime.utcnow(),
                    "estado": "EN PROCESO",
                    "canal": "LOCAL",
                    "total": total,
                    "cliente": {"idCliente": st.session_state.dni_cliente or None, "nombre": st.session_state.nombre_cliente or "Cliente"},
                    "cajero": {"nombre": cajero},
                    "metodo_pago": {"nombre": metodo},
                    "detalle": st.session_state.carrito_ventas
                }
                c_ped.insert_one(pedido)
                st.success(f"Venta #{pedido['idPedido']} registrada")
                st.session_state.carrito_ventas = []
                st.rerun()
            except PyMongoError as e:
                st.error(f"Error al registrar venta: {e}")

# -------------------- COMPRAS (solo ADMIN) --------------------
elif opcion == "📦 Compras":
    if rol_actual != "ADMIN":
        st.warning("Solo ADMIN puede registrar compras.")
        st.stop()
    st.markdown("## Nueva compra")
    ins = listar_insumos()
    nombres_ins = [i["nombre"] for i in ins]
    proveedor = st.selectbox("Proveedor", proveedores())
    solicitante = st.selectbox("Solicitante", [*cajeros(), "Admin"])

    g1, g2, g3 = st.columns([3,1,1])
    with g1:
        nombre_i = st.selectbox("Insumo", nombres_ins)
        ins_sel = next(i for i in ins if i["nombre"] == nombre_i)
    with g2:
        cantidad = st.number_input("Cantidad", min_value=0.1, step=0.1, value=1.0)
    with g3:
        costo = st.number_input("Costo unitario (S/.)", min_value=0.1, step=0.1, value=1.0)
    if st.button("➕ Añadir insumo"):
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
        st.metric("Total compra", f"S/ {total_c:.2f}")
        if st.button("📤 Registrar compra", type="primary", use_container_width=True):
            try:
                ops = [UpdateOne({"idInsumo": x["idInsumo"]}, {"$inc": {"stock": x["cantidadComprada"]}}) for x in st.session_state.carrito_compras]
                c_ins.bulk_write(ops)  # aumenta stock. :contentReference[oaicite:4]{index=4}
                orden = {
                    "idOrden": nuevo_id(c_ord, "idOrden"),
                    "fecha": datetime.utcnow(),
                    "montoTotal": total_c,
                    "proveedor": {"nombre": proveedor},
                    "solicitante": {"nombre": solicitante},
                    "detalle": st.session_state.carrito_compras
                }
                c_ord.insert_one(orden)
                st.success(f"Compra #{orden['idOrden']} registrada")
                st.session_state.carrito_compras = []
                st.rerun()
            except PyMongoError as e:
                st.error(f"Error al registrar compra: {e}")

# -------------------- COCINA (PEDIDOS WEB) --------------------
elif opcion == "👨‍🍳 Cocina (Pedidos web)":
    if rol_actual not in ("COCINERO","ADMIN"):
        st.warning("Solo COCINERO o ADMIN puede gestionar pedidos web.")
        st.stop()
    st.markdown("## Pedidos web")
    estados = ["EN PROCESO","PREPARANDO","LISTO","ENTREGADO"]
    en_cocina = list(c_ped.find({"canal":"WEB", "estado":{"$ne":"ENTREGADO"}}, {"_id":0}).sort("fecha", 1))
    if not en_cocina:
        st.info("No hay pedidos web pendientes.")
    else:
        for ped in en_cocina:
            with st.expander(f"Pedido #{ped['idPedido']} • {ped['estado']} • S/ {ped['total']:.2f}"):
                st.write(f"Cliente: {ped.get('cliente',{}).get('nombre','-')}")
                st.dataframe(pd.DataFrame(ped["detalle"]), use_container_width=True, hide_index=True)
                nuevo_estado = st.selectbox("Actualizar estado", estados, index=estados.index(ped["estado"]) if ped["estado"] in estados else 0, key=f"est_{ped['idPedido']}")
                if st.button("Guardar estado", key=f"btn_{ped['idPedido']}"):
                    c_ped.update_one({"idPedido": ped["idPedido"]}, {"$set": {"estado": nuevo_estado}})
                    st.success("Estado actualizado")
                    st.rerun()

# -------------------- HISTORIAL (ventas y compras) --------------------
elif opcion == "🧾 Historial":
    st.markdown("## Historial")
    tab1, tab2 = st.tabs(["Pedidos", "Compras"])
    with tab1:
        ult = list(c_ped.find({}, {"_id":0}).sort("fecha", -1).limit(100))
        if not ult: st.info("Sin pedidos registrados.")
        for ped in ult:
            with st.expander(f"#{ped['idPedido']} • {ped.get('canal','LOCAL')} • {ped['estado']} • S/ {ped['total']:.2f}"):
                c1, c2, c3 = st.columns(3)
                c1.write(f"Cliente: {ped.get('cliente',{}).get('nombre','-')}")
                c2.write(f"Pago: {ped.get('metodo_pago',{}).get('nombre','-')}")
                c3.write(f"Fecha: {ped['fecha']}")
                st.dataframe(pd.DataFrame(ped["detalle"]), use_container_width=True, hide_index=True)
    with tab2:
        ultc = list(c_ord.find({}, {"_id":0}).sort("fecha", -1).limit(100))
        if not ultc: st.info("Sin compras registradas.")
        for od in ultc:
            with st.expander(f"#{od['idOrden']} • S/ {od['montoTotal']:.2f}"):
                c1, c2 = st.columns(2)
                c1.write(f"Proveedor: {od.get('proveedor',{}).get('nombre','-')}")
                c2.write(f"Fecha: {od['fecha']}")
                st.dataframe(pd.DataFrame(od["detalle"]), use_container_width=True, hide_index=True)

st.markdown("---")
st.caption("Willy Burger • Streamlit + PyMongo • 2025")
