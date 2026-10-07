import socket
import json

from app.models import db, Producto
from app.schemas import validar_producto


HOST = "0.0.0.0"
PORT = 6061


def procesar_mensaje(mensaje, app):
    mensaje = mensaje.strip()

    if not mensaje.startswith("{") or not mensaje.endswith("}"):
        return {
            "statusCode": 400,
            "data": {
                "error": "Formato invalido"
            }
        }

    try:
        # ---------------------------------------------
        # INSERT
        # Formato:
        # {insert:{"nombre":"Mouse","precio":300,"categoria_id":1}}
        # ---------------------------------------------
        if mensaje.startswith("{insert:"):
            contenido = mensaje[len("{insert:"):-1]

            datos = json.loads(contenido)

            datos_validados, error_validacion = validar_producto(datos)

            if error_validacion:
                return {
                    "statusCode": 400,
                    "data": {
                        "error": error_validacion
                    }
                }

            with app.app_context():
                producto = Producto(
                    nombre=datos_validados["nombre"],
                    precio=datos_validados["precio"],
                    categoria_id=datos_validados["categoria_id"]
                )

                db.session.add(producto)
                db.session.commit()

                return {
                    "statusCode": 201,
                    "data": producto.to_dict()
                }

        # ---------------------------------------------
        # GET
        # Formato:
        # {get:1}
        # ---------------------------------------------
        if mensaje.startswith("{get:"):
            contenido = mensaje[len("{get:"):-1].strip()

            # También acepta {get:{"id":1}}
            if contenido.startswith("{"):
                datos = json.loads(contenido)
                producto_id = datos.get("id")
            else:
                producto_id = int(contenido)

            with app.app_context():
                producto = db.session.get(Producto, producto_id)

                if producto is None:
                    return {
                        "statusCode": 404,
                        "data": {
                            "error": "Producto no encontrado"
                        }
                    }

                return {
                    "statusCode": 200,
                    "data": producto.to_dict()
                }

        return {
            "statusCode": 400,
            "data": {
                "error": "Operacion no reconocida. Use {insert:<element>} o {get:<element>}"
            }
        }

    except ValueError:
        return {
            "statusCode": 400,
            "data": {
                "error": "El ID debe ser un numero entero"
            }
        }

    except json.JSONDecodeError:
        return {
            "statusCode": 400,
            "data": {
                "error": "El elemento insertado no tiene un JSON valido"
            }
        }

    except Exception as e:
        with app.app_context():
            db.session.rollback()

        return {
            "statusCode": 500,
            "data": {
                "error": str(e)
            }
        }


def iniciar_socket(app):
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    servidor.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    servidor.bind((HOST, PORT))
    servidor.listen(5)

    print(f"Socket TCP escuchando en {HOST}:{PORT}")

    while True:
        conexion, direccion = servidor.accept()

        print(f"Conexion TCP recibida desde {direccion}")

        try:
            datos = b""

            while True:
                parte = conexion.recv(4096)

                if not parte:
                    break

                datos += parte

                if b"\n" in parte:
                    break

            mensaje = datos.decode("utf-8").strip()

            print(f"Mensaje recibido: {mensaje}")

            respuesta = procesar_mensaje(mensaje, app)

            respuesta_json = json.dumps(
                respuesta,
                ensure_ascii=False
            )

            conexion.sendall(
                (respuesta_json + "\n").encode("utf-8")
            )

        except Exception as e:
            respuesta = {
                "statusCode": 500,
                "data": {
                    "error": str(e)
                }
            }

            conexion.sendall(
                (json.dumps(respuesta) + "\n").encode("utf-8")
            )

        finally:
            conexion.close()