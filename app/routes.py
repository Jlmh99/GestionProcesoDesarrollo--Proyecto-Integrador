
import os
import sqlite3
from datetime import datetime, timezone

from flask import Blueprint, current_app, jsonify, request
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from app.models import Categoria, Producto, db
from app.schemas import error, respuesta, validar_categoria, validar_producto

api = Blueprint("api", __name__, url_prefix="/api")


def json_response(status, data):
    return jsonify(respuesta(status, data)), status


def json_error(status, message):
    return jsonify(error(status, message)), status


def obtener_json():
    if not request.is_json:
        return None, "El Content-Type debe ser application/json."

    try:
        return request.get_json(), None
    except Exception:
        return None, "El JSON enviado no es válido."


# 1. GET /api/productos
@api.get("/productos")
def listar_productos():
    productos = db.session.execute(
        select(Producto).order_by(Producto.id)
    ).scalars().all()

    return json_response(200, [p.to_dict() for p in productos])


# 2. GET /api/productos/<id>
@api.get("/productos/<int:producto_id>")
def obtener_producto(producto_id):
    producto = db.session.get(Producto, producto_id)

    if producto is None:
        return json_error(404, "Producto no encontrado.")

    return json_response(200, producto.to_dict())


# 3. POST /api/productos
@api.post("/productos")
def crear_producto():
    payload, problema = obtener_json()

    if problema:
        return json_error(400, problema)

    datos, problema = validar_producto(payload)

    if problema:
        return json_error(400, problema)

    categoria = db.session.get(Categoria, datos["categoria_id"])

    if categoria is None:
        return json_error(400, "La categoría indicada no existe.")

    producto = Producto(**datos)
    db.session.add(producto)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return json_error(409, "No fue posible registrar el producto.")

    return json_response(201, producto.to_dict())


# 4. PUT /api/productos/<id>
@api.put("/productos/<int:producto_id>")
def actualizar_producto(producto_id):
    producto = db.session.get(Producto, producto_id)

    if producto is None:
        return json_error(404, "Producto no encontrado.")

    payload, problema = obtener_json()

    if problema:
        return json_error(400, problema)

    datos, problema = validar_producto(payload)

    if problema:
        return json_error(400, problema)

    categoria = db.session.get(Categoria, datos["categoria_id"])

    if categoria is None:
        return json_error(400, "La categoría indicada no existe.")

    producto.nombre = datos["nombre"]
    producto.precio = datos["precio"]
    producto.categoria_id = datos["categoria_id"]

    db.session.commit()

    return json_response(200, producto.to_dict())


# 5. DELETE /api/productos/<id>
@api.delete("/productos/<int:producto_id>")
def eliminar_producto(producto_id):
    producto = db.session.get(Producto, producto_id)

    if producto is None:
        return json_error(404, "Producto no encontrado.")

    db.session.delete(producto)
    db.session.commit()

    return json_response(200, {
        "mensaje": "Producto eliminado correctamente."
    })


# 6. GET /api/categorias
@api.get("/categorias")
def listar_categorias():
    categorias = db.session.execute(
        select(Categoria).order_by(Categoria.id)
    ).scalars().all()

    return json_response(200, [c.to_dict() for c in categorias])


# 7. POST /api/categorias
@api.post("/categorias")
def crear_categoria():
    payload, problema = obtener_json()

    if problema:
        return json_error(400, problema)

    datos, problema = validar_categoria(payload)

    if problema:
        return json_error(400, problema)

    categoria = Categoria(**datos)
    db.session.add(categoria)

    try:
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return json_error(409, "Ya existe una categoría con ese nombre.")

    return json_response(201, categoria.to_dict())


# 8. GET /api/productos/categoria/<id>
@api.get("/productos/categoria/<int:categoria_id>")
def productos_por_categoria(categoria_id):
    categoria = db.session.get(Categoria, categoria_id)

    if categoria is None:
        return json_error(404, "Categoría no encontrada.")

    productos = db.session.execute(
        select(Producto)
        .where(Producto.categoria_id == categoria_id)
        .order_by(Producto.id)
    ).scalars().all()

    return json_response(200, [p.to_dict() for p in productos])


# 9. POST /api/backup
@api.post("/backup")
def crear_backup():
    os.makedirs(current_app.config["BACKUP_DIR"], exist_ok=True)

    marca_tiempo = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    nombre_archivo = f"webapp_backup_{marca_tiempo}.db"
    ruta_backup = os.path.join(
        current_app.config["BACKUP_DIR"],
        nombre_archivo
    )

    origen = db.engine.raw_connection()

    try:
        destino = sqlite3.connect(ruta_backup)

        try:
            origen_backup = getattr(origen, "driver_connection", origen)
            origen_backup.backup(destino)
        finally:
            destino.close()
    except Exception:
        if os.path.exists(ruta_backup):
            os.remove(ruta_backup)
        current_app.logger.exception("Error al crear el backup")
        return json_error(500, "No se pudo crear el respaldo.")
    finally:
        origen.close()

    return json_response(201, {
        "mensaje": "Respaldo creado correctamente.",
        "archivo": nombre_archivo
    })


# 10. DELETE /api/base-datos
@api.delete("/base-datos")
def vaciar_base_datos():
    try:
        # Se eliminan primero los productos para respetar la relación.
        db.session.execute(delete(Producto))
        db.session.execute(delete(Categoria))
        db.session.commit()
    except Exception:
        db.session.rollback()
        current_app.logger.exception("Error al vaciar la base de datos")
        return json_error(500, "No se pudo vaciar la base de datos.")

    return json_response(200, {
        "mensaje": "La base de datos fue vaciada correctamente."
    })