import os
import socket
from nicegui import ui
from app_builder import create

# O objeto 'app' é criado pela função create_app() para garantir que a UI
# não seja construída durante a importação pelo Uvicorn.
app = create()

# A chamada ui.run() é usada apenas para desenvolvimento local.
# Em produção no PythonAnywhere, o Uvicorn gerencia o servidor.
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host='0.0.0.0', port=8080, title='muWorkApp')
