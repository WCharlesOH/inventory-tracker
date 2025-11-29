CREATE TABLE ADMINISTRADOR (
    idAdministrador   NUMBER(6)     PRIMARY KEY,
    nombre            VARCHAR2(100) NOT NULL
);

CREATE TABLE PROVEEDOR (
    idProveedor       NUMBER(6)     PRIMARY KEY,
    nombre            VARCHAR2(100) NOT NULL,
    telefono          VARCHAR2(20),
    RUC               VARCHAR2(20),
    idAdministrador   NUMBER(6),
    CONSTRAINT fk_proveedor_admin
        FOREIGN KEY (idAdministrador)
        REFERENCES ADMINISTRADOR (idAdministrador)
);

CREATE TABLE INSUMO (
    idInsumo          NUMBER(6)     PRIMARY KEY,
    nombre            VARCHAR2(100) NOT NULL,
    stock             NUMBER(10)    DEFAULT 0
);

CREATE TABLE CARTA (
    idCarta           NUMBER(6)     PRIMARY KEY,
    nombre            VARCHAR2(100) NOT NULL,
    descripcion       VARCHAR2(255)
);

CREATE TABLE COCINERO (
    idCocinero        NUMBER(6)     PRIMARY KEY,
    nombre            VARCHAR2(100) NOT NULL,
    especialidad      VARCHAR2(100)
);

CREATE TABLE PRODUCTO (
    idProducto        NUMBER(6)     PRIMARY KEY,
    nombre            VARCHAR2(100) NOT NULL,
    descripcion       VARCHAR2(255),
    precio            NUMBER(10,2)  NOT NULL,
    idCarta           NUMBER(6),
    idCocinero        NUMBER(6),
    CONSTRAINT fk_producto_carta
        FOREIGN KEY (idCarta)
        REFERENCES CARTA (idCarta),
    CONSTRAINT fk_producto_cocinero
        FOREIGN KEY (idCocinero)
        REFERENCES COCINERO (idCocinero)
);

CREATE TABLE CLIENTE (
    idCliente         NUMBER(6)     PRIMARY KEY,
    nombre            VARCHAR2(100) NOT NULL,
    telefono          VARCHAR2(20)
);

CREATE TABLE CAJERO (
    idCajero          NUMBER(6)     PRIMARY KEY,
    nombre            VARCHAR2(100) NOT NULL,
    turno             VARCHAR2(50)
);

CREATE TABLE METODOPAGO (
    idMetodoPago      NUMBER(6)     PRIMARY KEY,
    nombre            VARCHAR2(50)  NOT NULL
);

CREATE TABLE PEDIDO (
    idPedido          NUMBER(6)     PRIMARY KEY,
    fecha             DATE          DEFAULT SYSDATE,
    estado            VARCHAR2(50),
    totalPedido       NUMBER(10,2),
    idCliente         NUMBER(6),
    idMetodoPago      NUMBER(6),
    idCajero          NUMBER(6),
    CONSTRAINT fk_pedido_cliente
        FOREIGN KEY (idCliente)
        REFERENCES CLIENTE (idCliente),
    CONSTRAINT fk_pedido_metodopago
        FOREIGN KEY (idMetodoPago)
        REFERENCES METODOPAGO (idMetodoPago),
    CONSTRAINT fk_pedido_cajero
        FOREIGN KEY (idCajero)
        REFERENCES CAJERO (idCajero)
);

CREATE TABLE DETALLEPEDIDO (
    idPedido          NUMBER(6),
    idProducto        NUMBER(6),
    cantidad          NUMBER(10)   NOT NULL,
    PRIMARY KEY (idPedido, idProducto),
    CONSTRAINT fk_detallepedido_pedido
        FOREIGN KEY (idPedido)
        REFERENCES PEDIDO (idPedido),
    CONSTRAINT fk_detallepedido_producto
        FOREIGN KEY (idProducto)
        REFERENCES PRODUCTO (idProducto)
);

CREATE TABLE ORDEN (
    idOrden           NUMBER(6)     PRIMARY KEY,
    fecha             DATE          DEFAULT SYSDATE,
    montoTotal        NUMBER(10,2),
    idProveedor       NUMBER(6),
    CONSTRAINT fk_orden_proveedor
        FOREIGN KEY (idProveedor)
        REFERENCES PROVEEDOR (idProveedor)
);

CREATE TABLE DETALLECOMPRA (
    idOrden           NUMBER(6),
    idInsumo          NUMBER(6),
    cantidadComprada  NUMBER(10)   NOT NULL,
    costoUnitario     NUMBER(10,2),
    PRIMARY KEY (idOrden, idInsumo),
    CONSTRAINT fk_detallecompra_orden
        FOREIGN KEY (idOrden)
        REFERENCES ORDEN (idOrden),
    CONSTRAINT fk_detallecompra_insumo
        FOREIGN KEY (idInsumo)
        REFERENCES INSUMO (idInsumo)
);

CREATE TABLE RECETA (
    idProducto        NUMBER(6),
    idInsumo          NUMBER(6),
    cantidadInsumo    NUMBER(10)   NOT NULL,
    PRIMARY KEY (idProducto, idInsumo),
    CONSTRAINT fk_receta_producto
        FOREIGN KEY (idProducto)
        REFERENCES PRODUCTO (idProducto),
    CONSTRAINT fk_receta_insumo
        FOREIGN KEY (idInsumo)
        REFERENCES INSUMO (idInsumo)
);