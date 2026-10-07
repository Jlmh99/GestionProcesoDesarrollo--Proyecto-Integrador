
import math


def respuesta(status_code, data):
    return {
        "statusCode": status_code,
        "data": data
    }


def error(status_code, mensaje):
    return {
        "statusCode": status_code,
        "data": {
            "error": mensaje
        }
    }


def validar_categoria(payload):
    if not isinstance(payload, dict):
        return None, "El cuerpo debe ser un objeto JSON."

    nombre = payload.get("nombre")

    if not isinstance(nombre, str) or not nombre.strip():
        return None, "El campo nombre es obligatorio y debe ser texto."

    nombre = nombre.strip()

    if len(nombre) > 100:
        return None, "El nombre no puede superar 100 caracteres."

    return {"nombre": nombre}, None


def validar_producto(payload):
    if not isinstance(payload, dict):
        return None, "El cuerpo debe ser un objeto JSON."

    nombre = payload.get("nombre")
    precio = payload.get("precio")
    categoria_id = payload.get("categoria_id")

    if not isinstance(nombre, str) or not nombre.strip():
        return None, "El campo nombre es obligatorio y debe ser texto."

    nombre = nombre.strip()

    if len(nombre) > 120:
        return None, "El nombre no puede superar 120 caracteres."

    if isinstance(precio, bool) or not isinstance(precio, (int, float)):
        return None, "El precio debe ser un número."

    if not math.isfinite(precio) or precio < 0:
        return None, "El precio debe ser finito y no negativo."

    if isinstance(categoria_id, bool) or not isinstance(categoria_id, int):
        return None, "categoria_id debe ser un número entero."

    if categoria_id <= 0:
        return None, "categoria_id debe ser mayor que cero."

    return {
        "nombre": nombre,
        "precio": float(precio),
        "categoria_id": categoria_id
    }, None