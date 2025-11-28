import streamlit as st
import pandas as pd
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Wily Burger System",
    page_icon="🍔",
    layout="wide"
)

# ==========================================
# 2. DATOS SIMULADOS (MOCK DATA)
# Aquí es donde, en el futuro, harás SELECT a la Base de Datos
# ==========================================
PRODUCTOS_MOCK = {
    1: {"nombre": "Hamburguesa Clásica", "precio": 15.50},
    2: {"nombre": "Hamburguesa Royal", "precio": 19.00},
    3: {"nombre": "Papas Fritas Medianas", "precio": 7.00},
    4: {"nombre": "Gaseosa 500ml", "precio": 5.00},
    5: {"nombre": "Nuggets x 6", "precio": 12.00}
}

INSUMOS_MOCK = {
    101: {"nombre": "Pan Hamburguesa", "unidad": "UN"},
    102: {"nombre": "Carne Molida", "unidad": "KG"},
    103: {"nombre": "Papas Tumbay", "unidad": "KG"},
    104: {"nombre": "Aceite Vegetal", "unidad": "LT"}
}

EMPLEADOS_MOCK = ["Juan Pérez (Cajero)", "Maria Lopez (Admin)", "Carlos Ruiz (Cocinero)"]
PROVEEDORES_MOCK = ["Bimbo Perú", "Avinka", "Makro", "Coca Cola Company"]

# ==========================================
# 3. GESTIÓN DE ESTADO (SESSION STATE)
# Para guardar datos temporalmente mientras usas la app
# ==========================================
if 'carrito_ventas' not in st.session_state:
    st.session_state.carrito_ventas = []

if 'carrito_compras' not in st.session_state:
    st.session_state.carrito_compras = []

if 'historial_pedidos' not in st.session_state:
    st.session_state.historial_pedidos = []

# ==========================================
# 4. INTERFAZ GRÁFICA - SIDEBAR
# ==========================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/3075/3075977.png", width=100)
st.sidebar.title("Menú Wily Burger")
opcion = st.sidebar.radio("Ir a:", ["🍔 Nuevo Pedido (Ventas)", "📦 Orden de Compra (Insumos)", "👥 Gestión Empleados", "📊 Historial Reciente"])

# ==========================================
# 5. MÓDULO 1: NUEVO PEDIDO (VENTAS)
# ==========================================
if opcion == "🍔 Nuevo Pedido (Ventas)":
    st.title("🍔 Crear Nuevo Pedido")
    st.markdown("---")

    # --- Cabecera del Pedido ---
    col1, col2, col3 = st.columns(3)
    with col1:
        dni_cliente = st.text_input("DNI / RUC Cliente")
    with col2:
        nombre_cliente = st.text_input("Nombre del Cliente")
    with col3:
        cajero = st.selectbox("Cajero Atendiendo", EMPLEADOS_MOCK)
        metodo_pago = st.selectbox("Método de Pago", ["Efectivo", "Tarjeta", "Yape/Plin"])

    st.markdown("### 🛒 Agregar Productos")
    
    # --- Formulario de Detalle (Agregar items) ---
    c_prod1, c_prod2, c_prod3, c_prod4 = st.columns([3, 1, 1, 1])
    
    with c_prod1:
        # Creamos una lista de nombres para el selectbox
        nombres_prod = [p['nombre'] for p in PRODUCTOS_MOCK.values()]
        producto_seleccionado = st.selectbox("Seleccionar Producto", nombres_prod)
    
    # Buscar precio del producto seleccionado
    precio_unitario = 0
    id_prod_sel = 0
    for pid, data in PRODUCTOS_MOCK.items():
        if data['nombre'] == producto_seleccionado:
            precio_unitario = data['precio']
            id_prod_sel = pid
            break
            
    with c_prod2:
        cantidad = st.number_input("Cantidad", min_value=1, value=1)
    
    with c_prod3:
        st.info(f"Precio: S/ {precio_unitario:.2f}")

    with c_prod4:
        st.write("##") # Espacio vacio para alinear
        if st.button("➕ Agregar"):
            # Agregar al session state
            item = {
                "ID": id_prod_sel,
                "Producto": producto_seleccionado,
                "Cantidad": cantidad,
                "Precio Unit.": precio_unitario,
                "Subtotal": cantidad * precio_unitario
            }
            st.session_state.carrito_ventas.append(item)
            st.success("Producto agregado")

    # --- Mostrar Tabla del Carrito ---
    if len(st.session_state.carrito_ventas) > 0:
        st.markdown("### Detalle del Pedido Actual")
        df_carrito = pd.DataFrame(st.session_state.carrito_ventas)
        
        # Mostrar tabla bonita
        st.dataframe(df_carrito, use_container_width=True)
        
        # Calcular Total
        total_pedido = df_carrito["Subtotal"].sum()
        
        col_res1, col_res2 = st.columns([3, 1])
        with col_res2:
            st.metric(label="MONTO TOTAL", value=f"S/ {total_pedido:.2f}")
            
        # Botón Guardar
        if st.button("✅ FINALIZAR PEDIDO", type="primary", use_container_width=True):
            # Aquí iría el INSERT a la base de datos
            # Simulación:
            nuevo_pedido = {
                "id": len(st.session_state.historial_pedidos) + 1,
                "fecha": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "cliente": nombre_cliente if nombre_cliente else "Cliente General",
                "total": total_pedido,
                "estado": "EN PROCESO"
            }
            st.session_state.historial_pedidos.append(nuevo_pedido)
            st.session_state.carrito_ventas = [] # Limpiar carrito
            st.balloons()
            st.success(f"Pedido #{nuevo_pedido['id']} generado correctamente.")
            st.rerun() # Recargar pantalla para limpiar
            
    else:
        st.info("El carrito está vacío. Agrega productos arriba.")

# ==========================================
# 6. MÓDULO 2: ORDEN DE COMPRA (INSUMOS)
# ==========================================
elif opcion == "📦 Orden de Compra (Insumos)":
    st.title("📦 Reposición de Inventario")
    st.markdown("---")

    # --- Cabecera Compra ---
    col1, col2 = st.columns(2)
    with col1:
        proveedor = st.selectbox("Seleccionar Proveedor", PROVEEDORES_MOCK)
    with col2:
        solicitante = st.selectbox("Solicitado por (Admin)", [e for e in EMPLEADOS_MOCK if "Admin" in e])

    st.markdown("### 📝 Lista de Insumos a Pedir")
    
    # --- Formulario Detalle Compra ---
    with st.form("form_compras"):
        c1, c2, c3 = st.columns(3)
        with c1:
            nombres_insumos = [i['nombre'] for i in INSUMOS_MOCK.values()]
            insumo_sel = st.selectbox("Insumo", nombres_insumos)
        with c2:
            cant_compra = st.number_input("Cantidad a comprar", min_value=1.0, step=0.5)
        with c3:
            costo_estimado = st.number_input("Costo Unitario (S/.)", min_value=0.0, step=0.1)
        
        btn_add_insumo = st.form_submit_button("Agregar Línea")
        
        if btn_add_insumo:
            st.session_state.carrito_compras.append({
                "Insumo": insumo_sel,
                "Cantidad": cant_compra,
                "Costo Unit.": costo_estimado,
                "Subtotal": cant_compra * costo_estimado
            })
            st.success("Línea agregada")
            st.rerun()

    # --- Tabla Compras ---
    if st.session_state.carrito_compras:
        df_compras = pd.DataFrame(st.session_state.carrito_compras)
        st.dataframe(df_compras, use_container_width=True)
        
        total_compra = df_compras["Subtotal"].sum()
        st.metric("Total Estimado", f"S/ {total_compra:.2f}")
        
        if st.button("📤 EMITIR ORDEN DE COMPRA"):
            st.session_state.carrito_compras = []
            st.success("Orden de Compra enviada al proveedor correctamente.")
            st.rerun()

# ==========================================
# 7. MÓDULO 3: GESTIÓN EMPLEADOS
# ==========================================
elif opcion == "👥 Gestión Empleados":
    st.title("👥 Gestión de Personal")
    
    tab1, tab2 = st.tabs(["Nuevo Empleado", "Lista de Personal"])
    
    with tab1:
        with st.form("nuevo_empleado"):
            col1, col2 = st.columns(2)
            with col1:
                st.text_input("DNI")
                st.text_input("Nombres Completos")
                st.text_input("Teléfono")
            with col2:
                st.selectbox("Rol", ["ADMIN", "CAJERO", "COCINERO"])
                st.selectbox("Turno", ["MAÑANA", "TARDE", "NOCHE"])
                st.text_input("Especialidad (Solo Cocineros)")
            
            if st.form_submit_button("Registrar Empleado"):
                st.success("Empleado registrado en el sistema (Simulado)")
                
    with tab2:
        # Simulamos una tabla de DB
        data_empleados = [
            {"DNI": "77554433", "Nombre": "Juan Pérez", "Rol": "CAJERO", "Turno": "MAÑANA"},
            {"DNI": "12345678", "Nombre": "Maria Lopez", "Rol": "ADMIN", "Turno": "MAÑANA"},
            {"DNI": "87654321", "Nombre": "Carlos Ruiz", "Rol": "COCINERO", "Turno": "TARDE"},
        ]
        st.table(data_empleados)

# ==========================================
# 8. MÓDULO 4: HISTORIAL (Solo visualización)
# ==========================================
elif opcion == "📊 Historial Reciente":
    st.title("📊 Monitor de Pedidos del Día")
    
    if len(st.session_state.historial_pedidos) > 0:
        df_hist = pd.DataFrame(st.session_state.historial_pedidos)
        st.dataframe(df_hist, use_container_width=True)
    else:
        st.info("No hay pedidos registrados en esta sesión.")

# Footer simple
st.markdown("---")
st.caption("Sistema Wily Burger v1.0 | Desarrollado con Streamlit & Python")
