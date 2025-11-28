import streamlit as st
import oracledb
import datetime

# 1. CONEXIÓN A LA BASE DE DATOS
# Si usas Oracle Cloud, necesitas la Wallet. Si es local, solo host/port.
def get_connection():
    return oracledb.connect(
        user="ADMIN", # Tu usuario
        password="TuPassword123", # Tu pass
        dsn="db2022_high" # Tu DSN de la Wallet o "localhost/xepdb1"
    )

st.title("🍔 Gestión Wily Burger")

# 2. SECCIÓN DE CREAR PEDIDO
st.header("Nuevo Pedido")

# --- PASO A: Cabecera del Pedido ---
col1, col2 = st.columns(2)
with col1:
    dni_cliente = st.text_input("DNI Cliente")
with col2:
    # Aquí deberías hacer una query para traer los empleados reales
    id_cajero = st.selectbox("ID Cajero (Simulado)", [1, 2, 3]) 
    metodo_pago = st.selectbox("Método Pago", ["Efectivo", "Tarjeta", "Yape"])

# --- PASO B: Agregar Productos (El Detalle) ---
st.subheader("Agregar Productos")

# Inicializar lista temporal en memoria (Session State)
if 'carrito' not in st.session_state:
    st.session_state.carrito = []

# Formulario para agregar item al carrito
with st.form("add_product_form"):
    # Aquí podrías cargar productos desde la BD con una query
    prod_id = st.number_input("ID Producto", min_value=1, step=1)
    cantidad = st.number_input("Cantidad", min_value=1, step=1)
    precio = st.number_input("Precio Unitario (S/.)", min_value=0.0)
    
    submitted = st.form_submit_button("Agregar al Pedido")
    if submitted:
        st.session_state.carrito.append({
            "id_producto": prod_id,
            "cantidad": cantidad,
            "precio": precio,
            "subtotal": cantidad * precio
        })
        st.success("Producto agregado")

# Mostrar lo que llevamos en el pedido
if st.session_state.carrito:
    st.write("### Resumen del Pedido")
    st.dataframe(st.session_state.carrito)
    
    # --- PASO C: Guardar Todo en Oracle ---
    if st.button("CONFIRMAR Y GUARDAR PEDIDO"):
        try:
            conn = get_connection()
            cursor = conn.cursor()
            
            # 1. Insertar Cabecera (PEDIDO)
            # Nota: Necesitamos obtener el ID del cliente basado en el DNI primero
            # Para simplificar, asumo que envías IDs directos o usas lógica extra.
            
            # Insertar Pedido y retornar el ID generado
            out_id = cursor.var(int)
            sql_pedido = """
                INSERT INTO PEDIDO (ID_CLIENTE, ID_EMPLEADO_CAJERO, ID_METODO_PAGO, ESTADO)
                VALUES ((SELECT ID_CLIENTE FROM CLIENTE WHERE NUMERO_DOCUMENTO = :dni), :cajero, 1, 'EN PROCESO')
                RETURNING ID_PEDIDO INTO :id_ped
            """
            cursor.execute(sql_pedido, dni=dni_cliente, cajero=id_cajero, id_ped=out_id)
            new_pedido_id = out_id.getvalue()[0]
            
            # 2. Insertar Detalles (Loop en Python)
            sql_detalle = """
                INSERT INTO DETALLE_PEDIDO (ID_PEDIDO, ID_PRODUCTO, CANTIDAD, PRECIO_UNITARIO)
                VALUES (:id_ped, :id_prod, :cant, :precio)
            """
            
            data_detalles = []
            for item in st.session_state.carrito:
                data_detalles.append((new_pedido_id, item['id_producto'], item['cantidad'], item['precio']))
            
            cursor.executemany(sql_detalle, data_detalles)
            
            conn.commit()
            st.success(f"✅ Pedido #{new_pedido_id} creado exitosamente!")
            
            # Limpiar carrito
            st.session_state.carrito = []
            
        except Exception as e:
            st.error(f"Error en BD: {e}")
        finally:
            if conn: conn.close()
