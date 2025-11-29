-- ADMINISTRADOR
INSERT INTO ADMINISTRADOR (idAdministrador, nombre) VALUES (1, 'Willy Wonka');
INSERT INTO ADMINISTRADOR (idAdministrador, nombre) VALUES (2, 'Charlie Bucket');

-- CARTA (Categorías)
INSERT INTO CARTA (idCarta, nombre, descripcion) VALUES (1, 'Hamburguesas Clásicas', 'Nuestras hamburguesas tradicionales');
INSERT INTO CARTA (idCarta, nombre, descripcion) VALUES (2, 'Hamburguesas Especiales', 'Hamburguesas gourmet con ingredientes premium');
INSERT INTO CARTA (idCarta, nombre, descripcion) VALUES (3, 'Bebidas', 'Gaseosas, jugos y refrescos');
INSERT INTO CARTA (idCarta, nombre, descripcion) VALUES (4, 'Complementos', 'Papas fritas, aros de cebolla y más');
INSERT INTO CARTA (idCarta, nombre, descripcion) VALUES (5, 'Postres', 'Deliciosos postres para terminar tu comida');

-- COCINERO
INSERT INTO COCINERO (idCocinero, nombre, especialidad) VALUES (1, 'Gastón Acurio', 'Parrilla y carnes');
INSERT INTO COCINERO (idCocinero, nombre, especialidad) VALUES (2, 'Virgilio Martínez', 'Salsas y aderezos');
INSERT INTO COCINERO (idCocinero, nombre, especialidad) VALUES (3, 'Mitsuharu Tsumura', 'Hamburguesas gourmet');

-- METODOPAGO
INSERT INTO METODOPAGO (idMetodoPago, nombre) VALUES (1, 'Efectivo');
INSERT INTO METODOPAGO (idMetodoPago, nombre) VALUES (2, 'Yape');
INSERT INTO METODOPAGO (idMetodoPago, nombre) VALUES (3, 'Plin');
INSERT INTO METODOPAGO (idMetodoPago, nombre) VALUES (4, 'Tarjeta Crédito');
INSERT INTO METODOPAGO (idMetodoPago, nombre) VALUES (5, 'Tarjeta Débito');

-- INSUMO
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (1, 'Pan de Hamburguesa', 200);
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (2, 'Carne de Res (kg)', 100);
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (3, 'Queso Cheddar (lámina)', 300);
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (4, 'Papas (kg)', 150);
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (5, 'Tocino (kg)', 50);
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (6, 'Lechuga (unidad)', 80);
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (7, 'Tomate (kg)', 60);
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (8, 'Cebolla (kg)', 70);
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (9, 'Pepinillos (frasco)', 30);
INSERT INTO INSUMO (idInsumo, nombre, stock) VALUES (10, 'Salsas varias (litro)', 40);

-- PROVEEDOR
INSERT INTO PROVEEDOR (idProveedor, nombre, telefono, RUC, idAdministrador) VALUES (1, 'Panadería El Buen Gusto', '999888777', '20100010001', 1);
INSERT INTO PROVEEDOR (idProveedor, nombre, telefono, RUC, idAdministrador) VALUES (2, 'Carnes Premium del Norte', '987654321', '20200020002', 1);
INSERT INTO PROVEEDOR (idProveedor, nombre, telefono, RUC, idAdministrador) VALUES (3, 'Lácteos La Vaquita', '912345678', '20300030003', 2);
INSERT INTO PROVEEDOR (idProveedor, nombre, telefono, RUC, idAdministrador) VALUES (4, 'Verduras Frescas SAC', '998877665', '20400040004', 2);
INSERT INTO PROVEEDOR (idProveedor, nombre, telefono, RUC, idAdministrador) VALUES (5, 'Bebidas y Refrescos Perú', '976543210', '20500050005', 1);

-- PRODUCTO
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (1, 'Willy Cheese', 'Hamburguesa con doble queso cheddar', 18.50, 1, 1);
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (2, 'Willy Royal', 'Hamburguesa con huevo, queso y tocino', 22.00, 1, 1);
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (3, 'Willy Burger Especial', 'Hamburguesa con todos los ingredientes', 25.00, 2, 3);
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (4, 'Willy BBQ', 'Hamburguesa con salsa barbacoa y aros de cebolla', 23.50, 2, 3);
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (5, 'Papas Fritas Medianas', 'Papas crujientes con sal', 8.00, 4, 2);
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (6, 'Papas Fritas Grandes', 'Porción grande de papas fritas', 12.00, 4, 2);
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (7, 'Aros de Cebolla', 'Aros de cebolla empanizados', 10.00, 4, 2);
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (8, 'Inca Kola 500ml', 'La bebida del Perú', 5.00, 3, NULL);
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (9, 'Coca Cola 500ml', 'Refresco de cola', 5.00, 3, NULL);
INSERT INTO PRODUCTO (idProducto, nombre, descripcion, precio, idCarta, idCocinero) VALUES (10, 'Milkshake de Vainilla', 'Batido cremoso de vainilla', 12.00, 5, NULL);

-- RECETA
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (1, 1, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (1, 2, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (1, 3, 2);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (2, 1, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (2, 2, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (2, 3, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (2, 5, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (3, 1, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (3, 2, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (3, 3, 2);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (3, 5, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (3, 6, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (3, 7, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (5, 4, 1);
INSERT INTO RECETA (idProducto, idInsumo, cantidadInsumo) VALUES (7, 8, 1);

-- CLIENTE
INSERT INTO CLIENTE (idCliente, nombre, telefono) VALUES (1, 'Juan Pérez', '912345678');
INSERT INTO CLIENTE (idCliente, nombre, telefono) VALUES (2, 'Maria Lopez', '998877665');
INSERT INTO CLIENTE (idCliente, nombre, telefono) VALUES (3, 'Carlos Rodriguez', '976543210');
INSERT INTO CLIENTE (idCliente, nombre, telefono) VALUES (4, 'Ana García', '934567890');
INSERT INTO CLIENTE (idCliente, nombre, telefono) VALUES (5, 'Luis Torres', '945678901');

-- CAJERO
INSERT INTO CAJERO (idCajero, nombre, turno) VALUES (1, 'Luis Martínez', 'Mañana');
INSERT INTO CAJERO (idCajero, nombre, turno) VALUES (2, 'Sofia Ramirez', 'Tarde');

-- PEDIDO
INSERT INTO PEDIDO (idPedido, fecha, estado, totalPedido, idCliente, idMetodoPago, idCajero) VALUES (1, SYSDATE, 'PAGADO', 26.50, 1, 2, 1);
INSERT INTO PEDIDO (idPedido, fecha, estado, totalPedido, idCliente, idMetodoPago, idCajero) VALUES (2, SYSDATE, 'PAGADO', 35.00, 2, 1, 2);
INSERT INTO PEDIDO (idPedido, fecha, estado, totalPedido, idCliente, idMetodoPago, idCajero) VALUES (3, SYSDATE, 'PENDIENTE', 45.50, 3, 4, 1);

-- DETALLEPEDIDO
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (1, 1, 1);
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (1, 5, 1);
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (2, 3, 1);
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (2, 8, 1);
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (2, 7, 1);
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (3, 2, 2);
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (3, 9, 2);
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (3, 6, 1);

COMMIT;