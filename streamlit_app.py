import streamlit as st
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# Configuración

st.set_page_config(page_title="Wily Burger System", page_icon="🍔", layout="wide")

MONGO_URI = "mongodb+srv://20225041_db_user:OzIEZ7cBRp8ck7WJ@proyectobd.58lpncv.mongodb.net/?appName=ProyectoBD"

@st.cache_resource
def init_db():
    cliente = MongoClient(MONGO_URI)
    return cliente["wilyburger_db"]

db = init_db()

col_productos   = db["productos"]
col_insumos     = db["insumos"]
col_pedidos     = db["pedidos"]
col_compras     = db["compras"]
col_empleados   = db["empleados"]
col_proveedores = db["proveedores"]
col_clientes    = db["clientes"]  

def cargar_productos():
    return list(col_productos.find({}, {"_id": 0}))

def cargar_insumos():
    return list(col_insumos.find({}, {"_id": 0}))

def cargar_empleados():
    datos = list(col_empleados.find({}, {"_id": 0}))
    if not datos:
        return ["Juan Pérez (Cajero)", "María López (Admin)", "Carlos Ruiz (Cocinero)"]
    return [e.get("nombre", "") for e in datos]

def cargar_proveedores():
    datos = list(col_proveedores.find({}, {"_id": 0}))
    return [d.get("nombre","") for d in datos] if datos else ["Bimbo Perú","Makro","Coca Cola"]

PRODUCTOS   = cargar_productos()
INSUMOS     = cargar_insumos()
EMPLEADOS   = cargar_empleados()
PROVEEDORES = cargar_proveedores()

if "carrito_ventas" not in st.session_state:
    st.session_state.carrito_ventas = []
if "carrito_compras" not in st.session_state:
    st.session_state.carrito_compras = []
if "nombre_cliente" not in st.session_state:
    st.session_state.nombre_cliente = ""
if "dni_cliente" not in st.session_state:
    st.session_state.dni_cliente = ""

def buscar_cliente_por_dni():
    dni = st.session_state.get("dni_cliente","").strip()
    if not dni:
        return
    doc = col_clientes.find_one({"_id": dni})
    st.session_state.nombre_cliente = doc.get("nombre","") if doc else st.session_state.get("nombre_cliente","")


# Sidebar

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=88)
st.sidebar.title("Menú Wily Burger")

rol = st.sidebar.selectbox("Rol de sesión", ["Cajero", "Cocinero", "Administrador"])
opciones = ["🍔 Nuevo Pedido (Ventas)", "👨‍🍳 Pedidos pendientes", "📊 Historial"]
if rol == "Administrador":
    opciones.insert(1, "📦 Orden de Compra (Insumos)")

opcion = st.sidebar.radio("Ir a:", opciones)


# Ventas

if opcion == "🍔 Nuevo Pedido (Ventas)":
    st.title("🍔 Registrar Nuevo Pedido")
    st.markdown("---")

    c1, c2, c3, c4 = st.columns([1.2, 1.8, 1.2, 1.2])
    with c1:
        st.text_input("DNI/RUC Cliente", key="dni_cliente", on_change=buscar_cliente_por_dni)
    with c2:
        st.text_input("Nombre del Cliente", key="nombre_cliente")
    with c3:
        cajero = st.selectbox("Cajero", EMPLEADOS)
    with c4:
        metodo_pago = st.selectbox("Método de Pago", ["Efectivo","Tarjeta","Yape/Plin"])

    st.subheader("Agregar productos")
    nombres_prod = [p["nombre"] for p in PRODUCTOS]
    cA, cB, cC, cD = st.columns([3, 1, 1, 1])
    with cA:
        prod_sel = st.selectbox("Producto", nombres_prod)
    precio_unit = next((p["precio"] for p in PRODUCTOS if p["nombre"] == prod_sel), 0.0)
    with cB:
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
    with cC:
        st.info(f"S/ {precio_unit:.2f}")
    with cD:
        st.write(" ")
        if st.button("➕ Agregar"):
            st.session_state.carrito_ventas.append({
                "producto": prod_sel,
                "cantidad": int(cantidad),
                "precio_unit": float(precio_unit),
                "subtotal": float(cantidad) * float(precio_unit)
            })
            st.success("Producto agregado")

    if st.session_state.carrito_ventas:
        df = pd.DataFrame(st.session_state.carrito_ventas)
        st.dataframe(df, use_container_width=True)
        total = float(df["subtotal"].sum())
        st.metric("TOTAL", f"S/ {total:.2f}")

        if st.button("✅ FINALIZAR PEDIDO", type="primary", use_container_width=True):
            pedido = {
                "fecha": datetime.now(),
                "actualizado_en": datetime.now(),
                "cliente": st.session_state.get("nombre_cliente") or "Cliente General",
                "dni": st.session_state.get("dni_cliente",""),
                "empleado": cajero,
                "metodo_pago": metodo_pago,
                "detalle": st.session_state.carrito_ventas,
                "total": total,
                "estado": "EN PROCESO"
            }
            col_pedidos.insert_one(pedido)
            st.session_state.carrito_ventas = []
            st.balloons()
            st.success("Pedido creado y enviado a 👨‍🍳 Pedidos pendientes")
            st.rerun()
    else:
        st.info("Carrito vacío.")


# Compras (solo Admin)

elif opcion == "📦 Orden de Compra (Insumos)":
    if rol != "Administrador":
        st.warning("Solo el Administrador puede registrar compras.")
    else:
        st.title("📦 Orden de Compra")
        c1, c2 = st.columns(2)
        with c1:
            proveedor = st.selectbox("Proveedor", PROVEEDORES)
        with c2:
            solicitante = st.selectbox("Solicitante", [e for e in EMPLEADOS if e] or ["Admin"])

        st.subheader("Agregar insumo")
        nombres_ins = [i["nombre"] for i in INSUMOS]
        with st.form("form_compra"):
            f1, f2, f3 = st.columns(3)
            insumo_sel = f1.selectbox("Insumo", nombres_ins)
            cant = f2.number_input("Cantidad", min_value=0.1, step=0.1)
            costo = f3.number_input("Costo Unitario", min_value=0.1, step=0.1)
            if st.form_submit_button("Agregar"):
                st.session_state.carrito_compras.append({
                    "insumo": insumo_sel,
                    "cantidad": float(cant),
                    "costo": float(costo),
                    "subtotal": float(cant) * float(costo)
                })
                st.rerun()

        if st.session_state.carrito_compras:
            dfc = pd.DataFrame(st.session_state.carrito_compras)
            st.dataframe(dfc, use_container_width=True)
            total_compra = float(dfc["subtotal"].sum())
            st.metric("Total Compra", f"S/ {total_compra:.2f}")

            if st.button("📤 Guardar Compra", type="primary", use_container_width=True):
                compra = {
                    "fecha": datetime.now(),
                    "proveedor": proveedor,
                    "solicitante": solicitante,
                    "detalle": st.session_state.carrito_compras,
                    "total": total_compra
                }
                col_compras.insert_one(compra)
                st.success("Compra guardada")
                st.session_state.carrito_compras = []
                st.rerun()
        else:
            st.info("Sin insumos en la orden.")


# Pedidos pendientes (Cocina)

elif opcion == "👨‍🍳 Pedidos pendientes":
    st.title("👨‍🍳 Pedidos pendientes")
    filtro_estados = ["EN PROCESO", "PREPARANDO"]
    pendientes = list(col_pedidos.find({"estado": {"$in": filtro_estados}}).sort("fecha", -1))

    if not pendientes:
        st.info("No hay pedidos pendientes.")
    else:
        for ped in pendientes:
            cab = f"#{str(ped.get('_id'))[-6:]} | {ped.get('cliente','')} | S/ {ped.get('total',0):.2f} | {ped.get('estado')}"
            with st.expander(cab, expanded=False):
                d1, d2 = st.columns([2,1])
                with d1:
                    df_det = pd.DataFrame(ped.get("detalle", []))
                    if not df_det.empty:
                        st.dataframe(df_det, use_container_width=True, hide_index=True)
                with d2:
                    st.write(f"Fecha: {ped.get('fecha'):%Y-%m-%d %H:%M}")
                    st.write(f"Método: {ped.get('metodo_pago','')}")
                    st.write(f"Cajero: {ped.get('empleado','')}")
                    st.write("")

                    if ped.get("estado") == "EN PROCESO":
                        if st.button("🔪 Marcar PREPARANDO", key=f"prep_{ped['_id']}"):
                            col_pedidos.update_one({"_id": ped["_id"]}, {"$set": {"estado":"PREPARANDO","actualizado_en": datetime.now()}})
                            st.success("Pedido actualizado a PREPARANDO")
                            st.rerun()

                    if st.button("✅ Marcar ENTREGADO", key=f"ok_{ped['_id']}"):
                        col_pedidos.update_one({"_id": ped["_id"]}, {"$set": {"estado":"ENTREGADO","actualizado_en": datetime.now()}})
                        st.success("Pedido actualizado a ENTREGADO")
                        st.rerun()


# Historial

elif opcion == "📊 Historial":
    st.title("📊 Historial")
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Pedidos recientes")
        pedidos = list(col_pedidos.find({}).sort("fecha", -1).limit(30))
        if pedidos:
            dfp = pd.DataFrame([
                {
                    "id": str(p.get("_id")),
                    "fecha": p.get("fecha"),
                    "cliente": p.get("cliente"),
                    "total": p.get("total"),
                    "estado": p.get("estado")
                } for p in pedidos
            ])
            st.dataframe(dfp, use_container_width=True, hide_index=True)
        else:
            st.info("Sin pedidos registrados.")

    with c2:
        st.subheader("Compras recientes")
        compras = list(col_compras.find({}).sort("fecha", -1).limit(30))
        if compras:
            dfc = pd.DataFrame([
                {
                    "id": str(c.get("_id")),
                    "fecha": c.get("fecha"),
                    "proveedor": c.get("proveedor"),
                    "total": c.get("total")
                } for c in compras
            ])
            st.dataframe(dfc, use_container_width=True, hide_index=True)
        else:
            st.info("Sin compras registradas.")

st.markdown("---")
st.caption("Sistema Wily Burger | Desarrollado por Equipo 5 - Proyecto BD 2025")
