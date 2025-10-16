# Este script é para ser executado em um console Bash no PythonAnywhere.
# Ele inicia o servidor NiceGUI real em uma porta interna.

from nicegui import ui # Importa o ui diretamente para o teste

# A porta 8000 é um exemplo, pode ser outra porta alta.
PORT = 8001

ui.label("Teste de Conexão Bem-Sucedido!") # Adiciona um elemento simples

print(f"Iniciando servidor NiceGUI na porta {PORT}")
ui.run(host='127.0.0.1', port=PORT)
