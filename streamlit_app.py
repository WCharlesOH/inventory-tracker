import streamlit as st
import pandas as pd
from datetime import datetime
from pymongo import MongoClient

# =============================================================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# =============================================================================
st.set_page_config(
    page_title="Wily Burger System",
    page_icon="🍔",
    layout="wide"
)

# =============================================================================
# 2. CONEXIÓN A MONGODB
# =============================================================================
# IMPORTANTE: Reemplaza TU_URI con tu cadena real de Mongo Atlas o local
MONGO_URI = "mongodb+srv://20225041_db_user:OzIEZ7cBRp8ck7WJ@proyectobd.58lpncv.mongodb.net/?appName=ProyectoBD"

@st.cache_resource
def init_connection():
    try:
        client = MongoClient(MONGO_URI)
        return client["wilyburger_db"]  # nombre de base de datos
    except Exception as e:
        st.error(f"❌ Error conectando a MongoDB: {e}")
        return None

db = init_connection()

# Colecciones
col_productos = db["productos"]
col_insumos = db["insumos"]
col_pedidos = db["pedidos"]
col_compras = db["compras"]
col_empleados = db["empleados"]
col_proveedores = db["proveedores"]

# =============================================================================
# 3. CARGA PREVIA DE DATOS DESDE MONGODB
# =============================================================================
def cargar_productos():
    data = list(col_productos.find({}, {"_id": 0}))
    return data if data else []

def cargar_insumos():
    data = list(col_insumos.find({}, {"_id": 0}))
    return data if data else []

def cargar_empleados():
    data = list(col_empleados.find({}, {"_id": 0}))
    return data if data else ["Juan Pérez (Cajero)", "Maria Lopez (Admin)"]

def cargar_proveedores():
    data = list(col_proveedores.find({}, {"_id": 0}))
    return data if data else ["Bimbo", "Makro", "Coca Cola"]

# REEMPLAZAMOS MOCKS POR DATOS DESDE MONGODB
PRODUCTOS = cargar_productos()
INSUMOS = cargar_insumos()
EMPLEADOS = cargar_empleados()
PROVEEDORES = cargar_proveedores()

# =============================================================================
# 4. SESSION STATE
# =============================================================================
if 'carrito_ventas' not in st.session_state:
    st.session_state.carrito_ventas = []

if 'carrito_compras' not in st.session_state:
    st.session_state.carrito_compras = []

# =============================================================================
# 5. SIDEBAR
# =============================================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=100)
st.sidebar.title("Menú Wily Burger")

opcion = st.sidebar.radio("Ir a:", [
    "🍔 Nuevo Pedido (Ventas)",
    "📦 Orden de Compra (Insumos)",
    "📊 Historial de Pedidos"
])

# =============================================================================
# 6. NUEVO PEDIDO (VENTAS)
# =============================================================================
if opcion == "🍔 Nuevo Pedido (Ventas)":
    st.title("🍔 Registrar Nuevo Pedido")
    st.markdown("---")

    col1, col2, col3 = st.columns(3)
    with col1:
        dni_cliente = st.text_input("DNI Cliente")
    with col2:
        nombre_cliente = st.text_input("Nombre del Cliente")
    with col3:
        empleado = st.selectbox("Cajero", EMPLEADOS)
        metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Tarjeta", "Yape/Plin"])

    st.subheader("Agregar Productos")

    # Select de productos
    nombres_prod = [p["nombre"] for p in PRODUCTOS]
    colA, colB, colC, colD = st.columns([3, 1, 1, 1])

    with colA:
        prod_sel = st.selectbox("Producto", nombres_prod)

    precio_unit = next((p["precio"] for p in PRODUCTOS if p["nombre"] == prod_sel), 0)

    with colB:
        cantidad = st.number_input("Cantidad", min_value=1, value=1)

    with colC:
        st.info(f"S/ {precio_unit:.2f}")

    with colD:
        st.write("##")
        if st.button("➕ Agregar"):
            st.session_state.carrito_ventas.append({
                "producto": prod_sel,
                "cantidad": cantidad,
                "precio_unit": precio_unit,
                "subtotal": cantidad * precio_unit
            })
            st.success("Producto agregado")

    # TABLA CARRITO
    if st.session_state.carrito_ventas:
        df = pd.DataFrame(st.session_state.carrito_ventas)
        st.dataframe(df, use_container_width=True)

        total = df["subtotal"].sum()
        st.metric("TOTAL", f"S/ {total:.2f}")

        if st.button("✅ FINALIZAR PEDIDO"):
            pedido = {
                "fecha": datetime.now(),
                "cliente": nombre_cliente,
                "dni": dni_cliente,
                "empleado": empleado,
                "metodo_pago": metodo_pago,
                "detalle": st.session_state.carrito_ventas,
                "total": total,
                "estado": "ENTREGADO"
            }

            col_pedidos.insert_one(pedido)
            st.balloons()
            st.success("Pedido guardado en MongoDB ✔")

            st.session_state.carrito_ventas = []
            st.rerun()

# =============================================================================
# 7. ORDEN DE COMPRA
# =============================================================================
elif opcion == "📦 Orden de Compra (Insumos)":
    st.title("📦 Orden de Compra")

    proveedor = st.selectbox("Proveedor", PROVEEDORES)
    solicitante = st.selectbox("Solicitante", EMPLEADOS)

    st.subheader("Agregar Insumo")

    nombres_ins = [i["nombre"] for i in INSUMOS]
    with st.form("form_compra"):
        c1, c2, c3 = st.columns(3)
        insumo_sel = c1.selectbox("Insumo", nombres_ins)
        cant = c2.number_input("Cantidad", min_value=0.1, step=0.1)
        costo = c3.number_input("Costo Unitario", min_value=0.1)

        if st.form_submit_button("Agregar"):
            st.session_state.carrito_compras.append({
                "insumo": insumo_sel,
                "cantidad": cant,
                "costo": costo,
                "subtotal": cant * costo
            })
            st.rerun()

    if st.session_state.carrito_compras:
        dfc = pd.DataFrame(st.session_state.carrito_compras)
        st.dataframe(dfc, use_container_width=True)

        total_compra = dfc["subtotal"].sum()
        st.metric("Costo Total", f"S/ {total_compra:.2f}")

        if st.button("📤 Guardar Compra"):
            compra = {
                "fecha": datetime.now(),
                "proveedor": proveedor,
                "solicitante": solicitante,
                "detalle": st.session_state.carrito_compras,
                "total": total_compra
            }
            col_compras.insert_one(compra)
            st.success("Compra guardada correctamente ✔")
            st.session_state.carrito_compras = []
            st.rerun()

# =============================================================================
# 8. HISTORIAL DE PEDIDOS
# =============================================================================
elif opcion == "📊 Historial de Pedidos":
    st.title("📊 Historial de Pedidos")

    pedidos = list(col_pedidos.find({}, {"_id": 0}))
    if pedidos:
        dfp = pd.DataFrame(pedidos)
        st.dataframe(dfp, use_container_width=True)
    else:
        st.info("No hay pedidos registrados.")

# =============================================================================
# FOOTER
# =============================================================================
st.markdown("---")
st.caption("Wily Burger System | MongoDB + Streamlit | 2025")

