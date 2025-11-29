-- Valida stock al insertar
CREATE OR REPLACE TRIGGER trg_valida_stock_insert
BEFORE INSERT ON DETALLEPEDIDO
FOR EACH ROW
DECLARE
  v_stock_actual NUMBER;
BEGIN
  FOR rec IN (SELECT idInsumo, cantidadInsumo FROM RECETA WHERE idProducto = :NEW.idProducto) LOOP
    SELECT stock INTO v_stock_actual FROM INSUMO WHERE idInsumo = rec.idInsumo;
    
    IF v_stock_actual < (:NEW.cantidad * rec.cantidadInsumo) THEN
      RAISE_APPLICATION_ERROR(-20001, 'Stock insuficiente para insumo: ' || rec.idInsumo);
    END IF;
  END LOOP;
END;
/

-- Actualiza stock al insertar
CREATE OR REPLACE TRIGGER trg_actualiza_stock_insert
AFTER INSERT ON DETALLEPEDIDO
FOR EACH ROW
BEGIN
  FOR rec IN (SELECT idInsumo, cantidadInsumo FROM RECETA WHERE idProducto = :NEW.idProducto) LOOP
    UPDATE INSUMO 
    SET stock = stock - (:NEW.cantidad * rec.cantidadInsumo)
    WHERE idInsumo = rec.idInsumo;
  END LOOP;
END;
/

-- Valida stock al actualizar
CREATE OR REPLACE TRIGGER trg_valida_stock_update
BEFORE UPDATE ON DETALLEPEDIDO
FOR EACH ROW
DECLARE
  v_stock_actual NUMBER;
  v_diferencia NUMBER;
BEGIN
  v_diferencia := :NEW.cantidad - :OLD.cantidad;
  
  IF v_diferencia > 0 THEN
    FOR rec IN (SELECT idInsumo, cantidadInsumo FROM RECETA WHERE idProducto = :NEW.idProducto) LOOP
      SELECT stock INTO v_stock_actual FROM INSUMO WHERE idInsumo = rec.idInsumo;
      
      IF v_stock_actual < (v_diferencia * rec.cantidadInsumo) THEN
        RAISE_APPLICATION_ERROR(-20002, 'Stock insuficiente para actualizar: ' || rec.idInsumo);
      END IF;
    END LOOP;
  END IF;
END;
/

-- Ajusta stock al actualizar
CREATE OR REPLACE TRIGGER trg_ajusta_stock_update
AFTER UPDATE ON DETALLEPEDIDO
FOR EACH ROW
DECLARE
  v_diferencia NUMBER;
BEGIN
  v_diferencia := :NEW.cantidad - :OLD.cantidad;
  
  IF v_diferencia <> 0 THEN
    FOR rec IN (SELECT idInsumo, cantidadInsumo FROM RECETA WHERE idProducto = :NEW.idProducto) LOOP
      UPDATE INSUMO 
      SET stock = stock - (v_diferencia * rec.cantidadInsumo)
      WHERE idInsumo = rec.idInsumo;
    END LOOP;
  END IF;
END;
/

-- Recupera stock al eliminar
CREATE OR REPLACE TRIGGER trg_recupera_stock_delete
AFTER DELETE ON DETALLEPEDIDO
FOR EACH ROW
BEGIN
  FOR rec IN (SELECT idInsumo, cantidadInsumo FROM RECETA WHERE idProducto = :OLD.idProducto) LOOP
    UPDATE INSUMO 
    SET stock = stock + (:OLD.cantidad * rec.cantidadInsumo)
    WHERE idInsumo = rec.idInsumo;
  END LOOP;
END;
/

-- Calcula total pedido
CREATE OR REPLACE TRIGGER trg_calcula_total_pedido
AFTER INSERT OR UPDATE OR DELETE ON DETALLEPEDIDO
BEGIN
  FOR ped IN (SELECT DISTINCT idPedido FROM DETALLEPEDIDO) LOOP
    UPDATE PEDIDO p
    SET totalPedido = (
      SELECT NVL(SUM(dp.cantidad * pr.precio), 0)
      FROM DETALLEPEDIDO dp
      JOIN PRODUCTO pr ON dp.idProducto = pr.idProducto
      WHERE dp.idPedido = ped.idPedido
    )
    WHERE p.idPedido = ped.idPedido;
  END LOOP;
END;
/

-- Actualiza stock compras
CREATE OR REPLACE TRIGGER trg_actualiza_stock_compras
AFTER INSERT ON DETALLECOMPRA
FOR EACH ROW
BEGIN
  UPDATE INSUMO 
  SET stock = stock + :NEW.cantidadComprada
  WHERE idInsumo = :NEW.idInsumo;
END;
/

-- Valida cantidad positiva
CREATE OR REPLACE TRIGGER trg_valida_cantidad_positiva
BEFORE INSERT OR UPDATE ON DETALLEPEDIDO
FOR EACH ROW
BEGIN
  IF :NEW.cantidad <= 0 THEN
    RAISE_APPLICATION_ERROR(-20003, 'La cantidad debe ser mayor a 0');
  END IF;
END;
/

-- Registra historial pedidos
CREATE OR REPLACE TRIGGER trg_registra_historial
AFTER UPDATE OF estado ON PEDIDO
FOR EACH ROW
BEGIN
  INSERT INTO HISTORIAL_PEDIDOS (idPedido, estado_anterior, estado_nuevo, fecha_cambio)
  VALUES (:OLD.idPedido, :OLD.estado, :NEW.estado, SYSDATE);
END;
/

-- Actualiza estadísticas ventas
CREATE OR REPLACE TRIGGER trg_actualiza_estadisticas
AFTER INSERT ON DETALLEPEDIDO
FOR EACH ROW
BEGIN
  UPDATE PRODUCTO 
  SET total_vendido = NVL(total_vendido, 0) + :NEW.cantidad
  WHERE idProducto = :NEW.idProducto;
END;
/

-- Controla stock mínimo
CREATE OR REPLACE TRIGGER trg_controla_stock_minimo
AFTER UPDATE OF stock ON INSUMO
FOR EACH ROW
BEGIN
  IF :NEW.stock < 10 AND :OLD.stock >= 10 THEN
    INSERT INTO ALERTAS_STOCK (idInsumo, stock_actual, fecha_alerta)
    VALUES (:NEW.idInsumo, :NEW.stock, SYSDATE);
  END IF;
END;
/

-- Valida producto activo
CREATE OR REPLACE TRIGGER trg_valida_producto_activo
BEFORE INSERT ON DETALLEPEDIDO
FOR EACH ROW
DECLARE
  v_estado PRODUCTO.estado%TYPE;
BEGIN
  SELECT estado INTO v_estado FROM PRODUCTO WHERE idProducto = :NEW.idProducto;
  IF v_estado = 'INACTIVO' THEN
    RAISE_APPLICATION_ERROR(-20004, 'Producto no disponible');
  END IF;
END;
/

-- Actualiza fecha modificación
CREATE OR REPLACE TRIGGER trg_actualiza_fecha_modificacion
BEFORE UPDATE ON PEDIDO
FOR EACH ROW
BEGIN
  :NEW.fecha_modificacion := SYSDATE;
END;
/

-- Controla integridad recetas
CREATE OR REPLACE TRIGGER trg_controla_integridad_recetas
BEFORE DELETE ON INSUMO
FOR EACH ROW
DECLARE
  v_count NUMBER;
BEGIN
  SELECT COUNT(*) INTO v_count FROM RECETA WHERE idInsumo = :OLD.idInsumo;
  IF v_count > 0 THEN
    RAISE_APPLICATION_ERROR(-20005, 'No se puede eliminar insumo con recetas asociadas');
  END IF;
END;
/

-- Limpiar datos de prueba
DELETE FROM DETALLEPEDIDO WHERE idPedido = 3 AND idProducto = 5;
COMMIT;

-- Probar validación stock insuficiente
BEGIN
  INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (1, 1, 500);
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

-- Probar validación cantidad positiva
BEGIN
  INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (1, 1, 0);
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

-- Probar inserción exitosa
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (3, 5, 3);

-- Verificar cambios
SELECT idInsumo, nombre, stock FROM INSUMO WHERE idInsumo = 4;
SELECT idPedido, totalPedido FROM PEDIDO WHERE idPedido = 3;

-- Probar actualización con validación
BEGIN
  UPDATE DETALLEPEDIDO SET cantidad = 100 WHERE idPedido = 3 AND idProducto = 5;
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

-- Probar actualización exitosa
UPDATE DETALLEPEDIDO SET cantidad = 5 WHERE idPedido = 3 AND idProducto = 5;

-- Verificar cambios
SELECT idInsumo, nombre, stock FROM INSUMO WHERE idInsumo = 4;
SELECT idPedido, totalPedido FROM PEDIDO WHERE idPedido = 3;

-- Probar eliminación
DELETE FROM DETALLEPEDIDO WHERE idPedido = 3 AND idProducto = 5;

-- Verificar stock recuperado
SELECT idInsumo, nombre, stock FROM INSUMO WHERE idInsumo = 4;
SELECT idPedido, totalPedido FROM PEDIDO WHERE idPedido = 3;

-- Probar alerta stock mínimo
UPDATE INSUMO SET stock = 5 WHERE idInsumo = 9;

-- Resumen final
SELECT idInsumo, nombre, stock FROM INSUMO WHERE idInsumo IN (1,2,3,4,9);

--======VERIFICACION DE TRIGGERS========--

-- Limpiar datos de prueba
DELETE FROM DETALLEPEDIDO WHERE idPedido = 3 AND idProducto = 5;
COMMIT;

-- Probar validación stock insuficiente
BEGIN
  INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (1, 1, 500);
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

-- Probar validación cantidad positiva
BEGIN
  INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (1, 1, 0);
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

-- Probar inserción exitosa
INSERT INTO DETALLEPEDIDO (idPedido, idProducto, cantidad) VALUES (3, 5, 3);

-- Verificar cambios
SELECT idInsumo, nombre, stock FROM INSUMO WHERE idInsumo = 4;
SELECT idPedido, totalPedido FROM PEDIDO WHERE idPedido = 3;

-- Probar actualización con validación
BEGIN
  UPDATE DETALLEPEDIDO SET cantidad = 100 WHERE idPedido = 3 AND idProducto = 5;
EXCEPTION
  WHEN OTHERS THEN NULL;
END;
/

-- Probar actualización exitosa
UPDATE DETALLEPEDIDO SET cantidad = 5 WHERE idPedido = 3 AND idProducto = 5;

-- Verificar cambios
SELECT idInsumo, nombre, stock FROM INSUMO WHERE idInsumo = 4;
SELECT idPedido, totalPedido FROM PEDIDO WHERE idPedido = 3;

-- Probar eliminación
DELETE FROM DETALLEPEDIDO WHERE idPedido = 3 AND idProducto = 5;

-- Verificar stock recuperado
SELECT idInsumo, nombre, stock FROM INSUMO WHERE idInsumo = 4;
SELECT idPedido, totalPedido FROM PEDIDO WHERE idPedido = 3;

-- Probar alerta stock mínimo
UPDATE INSUMO SET stock = 5 WHERE idInsumo = 9;

-- Resumen final
SELECT idInsumo, nombre, stock FROM INSUMO WHERE idInsumo IN (1,2,3,4,9);
SELECT idPedido, estado, totalPedido FROM PEDIDO ORDER BY idPedido;