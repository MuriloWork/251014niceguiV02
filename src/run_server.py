# Este script é para ser executado em um console Bash no PythonAnywhere.
# Ele inicia o servidor NiceGUI real em uma porta interna.

import os
from main import ui

# A porta 8000 é um exemplo, pode ser outra porta alta.
PORT = 8001

print(f"Iniciando servidor NiceGUI na porta {PORT}")
ui.run(host='127.0.0.1', port=PORT)