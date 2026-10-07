import threading

from app import create_app
from socket_server import iniciar_socket


app = create_app()


if __name__ == "__main__":

    socket_thread = threading.Thread(
        target=iniciar_socket,
        args=(app,),
        daemon=True
    )

    socket_thread.start()

    print("Iniciando Flask en puerto 80...")
    print("Iniciando Socket TCP en puerto 6061...")

    app.run(
        host="0.0.0.0",
        port=80,
        debug=False
    )