# Pipeline CI/CD para API REST (Flask + Docker + GitHub Actions + AWS EC2)

## 1. Descripción

Este proyecto implementa una API REST desarrollada con **Python y Flask**, utilizando **SQLite** como sistema de persistencia para la gestión de productos y categorías. La aplicación incluye operaciones CRUD, consultas, respaldo de información y administración de la base de datos.

El proyecto cuenta con un pipeline **CI/CD automatizado mediante GitHub Actions**, encargado de ejecutar las pruebas y verificar la cobertura de código, construir y publicar la imagen Docker en Docker Hub y desplegar automáticamente la nueva versión de la aplicación en una instancia **AWS EC2**.

---

## 2. Arquitectura

La arquitectura del proyecto integra GitHub, GitHub Actions, Docker Hub y AWS EC2.

El flujo comienza cuando el desarrollador realiza un `git push` o genera un `pull request` hacia la rama `main`. GitHub Actions ejecuta las pruebas automatizadas y verifica que la cobertura mínima requerida sea alcanzada.

Si las pruebas son satisfactorias, se construye la imagen Docker y se publica en Docker Hub. Finalmente, el pipeline se conecta mediante SSH a la instancia EC2, descarga la nueva imagen y ejecuta el contenedor actualizado.

### Diagrama del flujo

```text
                    ┌─────────────────┐
                    │  Desarrollador  │
                    └────────┬────────┘
                             │
                         git push
                             │
                             ▼
                    ┌─────────────────┐
                    │     GitHub      │
                    │   Repository    │
                    └────────┬────────┘
                             │
                             ▼
                 ┌─────────────────────────┐
                 │     GitHub Actions      │
                 │                         │
                 │  1. Tests + Coverage    │
                 │  2. Build Docker        │
                 │  3. Push Docker Hub     │
                 │  4. Deploy EC2          │
                 └───────┬─────────┬───────┘
                         │         │
              ┌──────────┘         └────────────┐
              ▼                                  ▼
      ┌─────────────────┐              ┌─────────────────┐
      │   Docker Hub    │              │     AWS EC2     │
      │                 │              │                 │
      │ Docker Image    │─────────────►│ Docker Container│
      │ :latest         │    pull      │ Flask + Socket  │
      │ :<commit-sha>   │              │                 │
      └─────────────────┘              └────────┬────────┘
                                                │
                                                ▼
                                       ┌─────────────────┐
                                       │    API REST     │
                                       │     HTTP :80    │
                                       └─────────────────┘
```

### Flujo resumido

```text
git push
   │
   ▼
GitHub Actions
   │
   ├──► Tests + Coverage ≥ 70%
   ├──► Build Docker Image
   ├──► Push → Docker Hub
   └──► SSH → AWS EC2
                │
                ├── Pull Docker Image
                ├── Stop old container
                ├── Start new container
                └── Verificar con curl
                         │
                         ▼
                     Flask API
                       :80
```

---

## 3. Endpoints

La API REST cuenta con los siguientes 10 endpoints principales:

| # | Método | Ruta | Descripción |
|---|---|---|---|
| 1 | `GET` | `/api/productos` | Obtiene todos los productos registrados. |
| 2 | `GET` | `/api/productos/<producto_id>` | Obtiene un producto específico mediante su ID. |
| 3 | `POST` | `/api/productos` | Registra un nuevo producto. |
| 4 | `PUT` | `/api/productos/<producto_id>` | Actualiza un producto existente. |
| 5 | `DELETE` | `/api/productos/<producto_id>` | Elimina un producto mediante su ID. |
| 6 | `GET` | `/api/categorias` | Obtiene todas las categorías registradas. |
| 7 | `POST` | `/api/categorias` | Registra una nueva categoría. |
| 8 | `GET` | `/api/productos/categoria/<categoria_id>` | Obtiene los productos pertenecientes a una categoría. |
| 9 | `POST` | `/api/backup` | Genera un respaldo de la base de datos SQLite. |
| 10 | `DELETE` | `/api/base-datos` | Vacía los registros de la base de datos. |

### Formato de respuesta

Las respuestas exitosas utilizan una estructura JSON estandarizada:

```json
{
    "statusCode": 200,
    "data": []
}
```

Las respuestas de error utilizan el mismo formato general:

```json
{
    "statusCode": 400,
    "data": {
        "error": "Descripción del error"
    }
}
```

---

## 4. Ejecución local

### 4.1 Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DEL_REPOSITORIO>
```

### 4.2 Crear el entorno virtual

En Git Bash:

```bash
python -m venv venv
source venv/Scripts/activate
```

### 4.3 Instalar las dependencias

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 Ejecutar la aplicación

```bash
python run.py
```

La aplicación inicia la API Flask en el puerto `80` y el servidor TCP en el puerto `6061`.

Para probar la API:

```bash
curl http://127.0.0.1/api/productos
```

### 4.5 Ejecutar las pruebas

```bash
python -m pytest
```

Para obtener mayor detalle:

```bash
python -m pytest -v
```

### 4.6 Ejecutar las pruebas con cobertura

```bash
python -m pytest --cov=app --cov-report=term-missing
```

Para generar un reporte HTML:

```bash
python -m pytest --cov=app --cov-report=html
```

El reporte se genera dentro del directorio `htmlcov/`.

El pipeline requiere alcanzar un mínimo del **70% de cobertura**.

### 4.7 Construir la imagen Docker

```bash
docker build -t practica-webapp:latest .
```

### 4.8 Ejecutar el contenedor

```bash
docker run -d \
  --name webapp-container \
  -p 8080:80 \
  -p 6061:6061 \
  -v webapp-data:/app/instance \
  practica-webapp:latest
```

En local se utiliza el puerto `8080` del equipo para evitar conflictos con otros servicios que ocupen el puerto `80`. En el servidor EC2, el pipeline publica la API directamente en el puerto `80`.

La API estará disponible en:

```text
http://127.0.0.1:8080
```

Por ejemplo:

```bash
curl http://127.0.0.1:8080/api/productos
```

El servidor TCP estará disponible mediante `localhost:6061`.

### 4.9 Verificar el contenedor

```bash
docker ps
docker logs webapp-container
```

### 4.10 Detener y eliminar el contenedor

```bash
docker stop webapp-container
docker rm webapp-container
```

---

## 5. Configuración del pipeline

El pipeline se encuentra definido en:

```text
.github/workflows/main.yml
```

El workflow se ejecuta automáticamente cuando se realiza un `push` o un `pull request` sobre la rama `main`.

### Secrets requeridos

| Secret | Para qué sirve |
|---|---|
| `DOCKERHUB_USERNAME` | Usuario de Docker Hub utilizado para publicar la imagen. |
| `DOCKERHUB_TOKEN` | Personal Access Token de Docker Hub utilizado para autenticarse. |
| `EC2_HOST` | Dirección IP pública o DNS de la instancia EC2. |
| `EC2_USER` | Usuario utilizado para conectarse mediante SSH. En Ubuntu normalmente es `ubuntu`. |
| `EC2_SSH_KEY` | Contenido de la llave privada `.pem` utilizada para la conexión SSH. |

### Seguridad

Las credenciales, tokens, llaves privadas y datos sensibles no se almacenan dentro del repositorio. Se mantienen protegidos mediante **GitHub Secrets**.

### Infraestructura en AWS

El despliegue utiliza una instancia **Amazon EC2 con Ubuntu**, con Docker instalado y acceso SSH.

### Reglas del Security Group

| Tipo | Protocolo | Puerto | Uso |
|---|---|---:|---|
| SSH | TCP | 22 | Conexión administrativa y despliegue mediante GitHub Actions. |
| HTTP | TCP | 80 | Acceso público a la API REST. |

El puerto `22` está abierto a `0.0.0.0/0` porque los runners de GitHub Actions no utilizan direcciones IP fijas. El acceso queda protegido porque la instancia solo acepta autenticación mediante la llave privada `.pem`, no mediante contraseña.

El puerto `6061` corresponde al servidor TCP utilizado por la aplicación dentro del contenedor. En el despliegue automatizado en EC2 este puerto no se publica; el acceso público principal requerido para la API REST se realiza mediante HTTP en el puerto `80`.

---

## 6. Flujo del pipeline

El job de pruebas se ejecuta tanto en un `push` como en un `pull request` hacia `main`. Los jobs de construcción y publicación de la imagen y de despliegue se ejecutan únicamente en un `push` a `main`, por lo que un `pull request` solo valida las pruebas y la cobertura.

### 6.1 Pruebas y cobertura

La primera etapa ejecuta las pruebas automatizadas de la aplicación y genera el reporte de cobertura mediante `pytest-cov`.

El pipeline requiere un mínimo del **70% de cobertura**. Si las pruebas fallan o no se alcanza el porcentaje mínimo establecido, el proceso se detiene y no continúa con las siguientes etapas.

```text
Código
  │
  ▼
Tests
  │
  ├── Fallan ──► Pipeline detenido
  │
  └── Exitosos
        │
        ▼
   Coverage ≥ 70%
        │
        ├── No ──► Pipeline detenido
        │
        └── Sí ──► Siguiente etapa
```

### 6.2 Construcción y publicación de la imagen

Si las pruebas y la cobertura son satisfactorias, GitHub Actions construye la imagen Docker.

La imagen se etiqueta con:

- `latest`
- El SHA del commit correspondiente.

Posteriormente, se publica en **Docker Hub**.

Si la construcción o publicación falla, el pipeline no continúa con el despliegue.

```text
Tests + Coverage
       │
       ▼
Docker Build
       │
       ├── Error ──► Pipeline detenido
       │
       ▼
Docker Image
       │
       ▼
Docker Hub
```

### 6.3 Despliegue en EC2

Cuando la imagen Docker ha sido publicada correctamente, GitHub Actions establece una conexión SSH con la instancia EC2.

El proceso:

1. Conecta con EC2 mediante SSH.
2. Descarga la nueva imagen desde Docker Hub.
3. Detiene el contenedor anterior.
4. Elimina el contenedor anterior.
5. Ejecuta el nuevo contenedor.
6. Expone la API mediante el puerto 80.
7. Espera unos segundos y verifica con `curl` que la API responde; si no responde, el job falla.

```text
Docker Hub
    │
    │ docker pull
    ▼
AWS EC2
    │
    ├── Detener contenedor anterior
    ├── Eliminar contenedor anterior
    ├── Iniciar nuevo contenedor
    └── Verificar respuesta con curl
              │
              ▼
        Flask API :80
```

Si la autenticación SSH o un paso crítico del despliegue falla, el workflow se marca como fallido.

---

## 7. Demostración

Una vez completado el despliegue, la API puede ser consultada mediante la dirección pública de la instancia EC2.

### Endpoint de demostración

```text
http://<IP_EC2>/api/productos
```

Mediante `curl`:

```bash
curl http://<IP_EC2>/api/productos
```

### Demostración del CI/CD

Para comprobar el funcionamiento del pipeline se realiza una modificación sencilla en el proyecto: cambiar el mensaje que devuelve la ruta principal `/`, definido en el archivo `app/__init__.py` (por ejemplo, el texto `"WebApp API funcionando"`).

Posteriormente:

```bash
git add .
git commit -m "Actualización de prueba CI/CD"
git push origin main
```

El flujo esperado es:

```text
git push
   │
   ▼
GitHub Actions
   │
   ├── Tests
   ├── Coverage
   ├── Docker Build
   ├── Docker Hub
   └── Deploy EC2
          │
          ▼
      API actualizada
```

Finalmente, se consulta la ruta principal:

```bash
curl http://<IP_EC2>/
```

para comprobar que el mensaje modificado se muestra en la versión actualizada de la aplicación que se encuentra funcionando en EC2.

---

## 8. Dockerfile

El proyecto utiliza un Dockerfile basado en `python:3.12-slim`.

```dockerfile
FROM python:3.12-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

COPY run.py .
COPY socket_server.py .

RUN mkdir -p /app/instance/backups

EXPOSE 80
EXPOSE 6061

CMD ["python", "run.py"]
```

---

## 9. Persistencia de datos

La aplicación utiliza SQLite como base de datos.

Para mantener los datos independientemente del ciclo de vida del contenedor, se utiliza un volumen Docker:

```bash
-v webapp-data:/app/instance
```

---

## 10. Tecnologías utilizadas

| Tecnología | Uso |
|---|---|
| Python 3.12 | Lenguaje principal |
| Flask | Desarrollo de la API REST |
| SQLite | Base de datos |
| SQLAlchemy | ORM y acceso a datos |
| Pytest | Pruebas automatizadas |
| Pytest-Cov | Medición de cobertura |
| Docker | Contenerización |
| Docker Hub | Almacenamiento de imágenes |
| Git | Control de versiones |
| GitHub | Repositorio del proyecto |
| GitHub Actions | Automatización CI/CD |
| AWS EC2 | Servidor de producción |
| Ubuntu | Sistema operativo de EC2 |
| SSH | Comunicación segura con EC2 |
| TCP Socket | Comunicación mediante el puerto 6061 |

---

## 11. Estructura principal del proyecto

```text
<repositorio>/
│
├── .github/
│   └── workflows/
│       └── main.yml
│
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   └── static/
│       └── swagger.json
│
├── test/
│   ├── test_endpoints.py
│   └── pruebas unitarias curl.txt
│
├── .dockerignore
├── .gitignore
├── Dockerfile
├── pytest.ini
├── requirements.txt
├── run.py
├── socket_server.py
└── README.md
```

---

## 12. Resultado esperado

Al finalizar el pipeline, el proceso permite pasar de una modificación realizada en el código fuente a una versión actualizada de la API desplegada en AWS EC2 de forma automatizada:

```text
Desarrollo
    │
    ▼
Git Push
    │
    ▼
GitHub
    │
    ▼
GitHub Actions
    │
    ├── Tests
    ├── Coverage ≥ 70%
    ├── Docker Build
    ├── Docker Hub Push
    └── EC2 Deploy
            │
            ▼
       API REST
            │
            ▼
        AWS EC2
```

De esta manera, el proyecto implementa un flujo de **Integración Continua (CI)** y **Despliegue Continuo (CD)**, reduciendo la intervención manual necesaria para validar, construir, publicar y desplegar nuevas versiones de la aplicación.