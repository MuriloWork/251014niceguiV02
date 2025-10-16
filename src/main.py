import os
import socket
from nicegui import ui
from app_builder import create_app

# O objeto 'app' é criado pela função create_app() para garantir que a UI
# não seja construída durante a importação pelo Uvicorn.
app = create_app()

# A chamada ui.run() é usada apenas para desenvolvimento local.
# Em produção no PythonAnywhere, o Uvicorn gerencia o servidor.
if __name__ in {"__main__", "__mp_main__"}:
    # Para desenvolvimento local, podemos definir o host e a porta.
    # A função get_local_ip() foi movida para o app_builder,
    # mas para o ui.run local, podemos usar '0.0.0.0' que é mais simples.
    ui.run(host='0.0.0.0', port=8080, title='muWorkApp')
