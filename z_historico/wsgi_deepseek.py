# Este é o arquivo de configuração WSGI para o PythonAnywhere.
# Ele serve como uma "ponte" entre o servidor web (que fala WSGI) e seu aplicativo NiceGUI (que fala ASGI).

import sys
import os

# --- PASSO 1: Adicionar o diretório do seu código-fonte ao path ---
# ATENÇÃO: Substitua 'muWork01' pelo seu nome de usuário real no PythonAnywhere.
# O caminho deve apontar para a pasta que contém o seu 'main.py', ou seja, a pasta 'src'.
path = '/home/muWork01/251014niceguiV02/src'
if path not in sys.path:
    sys.path.insert(0, path)

# --- PASSO 2: Mudar o diretório de trabalho ---
# Isso força o script a ser executado a partir da pasta 'src'.
# É crucial para que caminhos relativos no seu código (como o do banco de dados) funcionem corretamente.
os.chdir(path)

# --- PASSO 3: Importar o app e expor o servidor WSGI ---
# Agora que o path está correto, o Python pode encontrar e importar o objeto 'ui' de 'main.py'.
from main import ui
application = ui.server