import os

import pytest

from app import create_app
from app.models import db, Categoria, Producto


@pytest.fixture
def app(tmp_path):
    """
    Crea una aplicación independiente para cada prueba,
    utilizando una base de datos SQLite temporal.
    """

    test_database = tmp_path / "test_webapp.db"
    backup_directory = tmp_path / "backups"

    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": f"sqlite:///{test_database}",
        "BACKUP_DIR": str(backup_directory)
    })

    with app.app_context():
        categoria = Categoria(nombre="Electronica")
        db.session.add(categoria)
        db.session.commit()

        producto = Producto(
            nombre="Producto de prueba",
            precio=100.00,
            categoria_id=categoria.id
        )

        db.session.add(producto)
        db.session.commit()

    yield app


@pytest.fixture
def client(app):
    """
    Cliente HTTP de pruebas de Flask.
    """
    return app.test_client()


# ============================================================
# 1. GET /api/productos
# ============================================================

def test_get_productos(client):
    response = client.get("/api/productos")

    assert response.status_code == 200

    data = response.get_json()

    assert data["statusCode"] == 200
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


# ============================================================
# 2. GET /api/productos/<id>
# ============================================================

def test_get_producto(client):
    response = client.get("/api/productos/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["statusCode"] == 200
    assert data["data"]["id"] == 1
    assert data["data"]["nombre"] == "Producto de prueba"


# ============================================================
# 3. GET producto inexistente
# Escenario de error del usuario
# ============================================================

def test_get_producto_inexistente(client):
    response = client.get("/api/productos/9999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["statusCode"] == 404
    assert "error" in data["data"]


# ============================================================
# 4. POST /api/productos
# ============================================================

def test_post_producto(client):
    response = client.post(
        "/api/productos",
        json={
            "nombre": "Mouse",
            "precio": 300,
            "categoria_id": 1
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["statusCode"] == 201
    assert data["data"]["nombre"] == "Mouse"
    assert data["data"]["precio"] == 300.0
    assert data["data"]["categoria_id"] == 1


# ============================================================
# 5. POST producto sin nombre
# Escenario de error
# ============================================================

def test_post_producto_sin_nombre(client):
    response = client.post(
        "/api/productos",
        json={
            "precio": 300,
            "categoria_id": 1
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["statusCode"] == 400
    assert "error" in data["data"]


# ============================================================
# 6. POST producto con precio negativo
# Escenario de error
# ============================================================

def test_post_producto_precio_negativo(client):
    response = client.post(
        "/api/productos",
        json={
            "nombre": "Producto invalido",
            "precio": -100,
            "categoria_id": 1
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["statusCode"] == 400
    assert "error" in data["data"]


# ============================================================
# 7. POST producto con categoría inexistente
# Escenario de error
# ============================================================

def test_post_producto_categoria_inexistente(client):
    response = client.post(
        "/api/productos",
        json={
            "nombre": "Mouse",
            "precio": 300,
            "categoria_id": 9999
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["statusCode"] == 400
    assert "no existe" in data["data"]["error"]


# ============================================================
# 8. PUT /api/productos/<id>
# ============================================================

def test_put_producto(client):
    response = client.put(
        "/api/productos/1",
        json={
            "nombre": "Producto actualizado",
            "precio": 250,
            "categoria_id": 1
        }
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["statusCode"] == 200
    assert data["data"]["nombre"] == "Producto actualizado"
    assert data["data"]["precio"] == 250.0


# ============================================================
# 9. PUT producto inexistente
# Escenario de error
# ============================================================

def test_put_producto_inexistente(client):
    response = client.put(
        "/api/productos/9999",
        json={
            "nombre": "Producto",
            "precio": 100,
            "categoria_id": 1
        }
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["statusCode"] == 404


# ============================================================
# 10. PUT producto con datos inválidos
# Escenario de error
# ============================================================

def test_put_producto_datos_invalidos(client):
    response = client.put(
        "/api/productos/1",
        json={
            "nombre": "",
            "precio": -50,
            "categoria_id": 1
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["statusCode"] == 400
    assert "error" in data["data"]


# ============================================================
# 11. DELETE /api/productos/<id>
# ============================================================

def test_delete_producto(client):
    response = client.delete("/api/productos/1")

    assert response.status_code == 200

    data = response.get_json()

    assert data["statusCode"] == 200
    assert "eliminado" in data["data"]["mensaje"]


# ============================================================
# 12. DELETE producto inexistente
# Escenario de error
# ============================================================

def test_delete_producto_inexistente(client):
    response = client.delete("/api/productos/9999")

    assert response.status_code == 404

    data = response.get_json()

    assert data["statusCode"] == 404


# ============================================================
# 13. GET /api/categorias
# ============================================================

def test_get_categorias(client):
    response = client.get("/api/categorias")

    assert response.status_code == 200

    data = response.get_json()

    assert data["statusCode"] == 200
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


# ============================================================
# 14. POST /api/categorias
# ============================================================

def test_post_categoria(client):
    response = client.post(
        "/api/categorias",
        json={
            "nombre": "Perifericos"
        }
    )

    assert response.status_code == 201

    data = response.get_json()

    assert data["statusCode"] == 201
    assert data["data"]["nombre"] == "Perifericos"


# ============================================================
# 15. POST categoría duplicada
# Escenario de error
# ============================================================

def test_post_categoria_duplicada(client):
    response = client.post(
        "/api/categorias",
        json={
            "nombre": "Electronica"
        }
    )

    assert response.status_code == 409

    data = response.get_json()

    assert data["statusCode"] == 409
    assert "existe" in data["data"]["error"]


# ============================================================
# 16. GET productos por categoría
# ============================================================

def test_get_productos_por_categoria(client):
    response = client.get(
        "/api/productos/categoria/1"
    )

    assert response.status_code == 200

    data = response.get_json()

    assert data["statusCode"] == 200
    assert isinstance(data["data"], list)
    assert len(data["data"]) >= 1


# ============================================================
# 17. GET productos de categoría inexistente
# Escenario de error
# ============================================================

def test_get_productos_categoria_inexistente(client):
    response = client.get(
        "/api/productos/categoria/9999"
    )

    assert response.status_code == 404

    data = response.get_json()

    assert data["statusCode"] == 404


# ============================================================
# 18. POST /api/backup
# ============================================================

def test_post_backup(client, app):
    response = client.post("/api/backup")

    assert response.status_code == 201

    data = response.get_json()

    assert data["statusCode"] == 201
    assert "archivo" in data["data"]

    archivo = data["data"]["archivo"]
    ruta = os.path.join(
        app.config["BACKUP_DIR"],
        archivo
    )

    assert os.path.exists(ruta)


# ============================================================
# 19. DELETE /api/base-datos
# ============================================================

def test_delete_base_datos(client):
    response = client.delete("/api/base-datos")

    assert response.status_code == 200

    data = response.get_json()

    assert data["statusCode"] == 200
    assert "vaciada" in data["data"]["mensaje"]


# ============================================================
# 20. POST sin Content-Type JSON
# Escenario de error del usuario
# ============================================================

def test_post_producto_sin_content_type_json(client):
    response = client.post(
        "/api/productos",
        data="nombre=Mouse&precio=300&categoria_id=1"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["statusCode"] == 400
    assert "application/json" in data["data"]["error"]


# ============================================================
# 21. POST con JSON inválido
# Escenario de error del usuario
# ============================================================

def test_post_producto_json_invalido(client):
    response = client.post(
        "/api/productos",
        data='{"nombre":"Mouse"',
        content_type="application/json"
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["statusCode"] == 400
    assert "JSON" in data["data"]["error"]


# ============================================================
# 22. POST con categoria_id incorrecto
# Escenario de error del usuario
# ============================================================

def test_post_producto_categoria_id_invalido(client):
    response = client.post(
        "/api/productos",
        json={
            "nombre": "Mouse",
            "precio": 300,
            "categoria_id": "uno"
        }
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["statusCode"] == 400
    assert "categoria_id" in data["data"]["error"]


# ============================================================
# 23. POST categoría sin nombre
# Escenario de error
# ============================================================

def test_post_categoria_sin_nombre(client):
    response = client.post(
        "/api/categorias",
        json={}
    )

    assert response.status_code == 400

    data = response.get_json()

    assert data["statusCode"] == 400
    assert "nombre" in data["data"]["error"]


# ============================================================
# 24. Método HTTP incorrecto
# Escenario de error del usuario
# ============================================================

def test_metodo_http_no_permitido(client):
    response = client.patch("/api/productos")

    assert response.status_code == 405

    data = response.get_json()

    assert data["statusCode"] == 405