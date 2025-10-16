# Este é o arquivo de configuração WSGI para o PythonAnywhere.
# Ele usa a biblioteca 'a2wsgi' para servir um aplicativo ASGI (NiceGUI/FastAPI) em um servidor WSGI.

import sys
import os
from a2wsgi import ASGIMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware

# --- PASSO 1: Adicionar o diretório do seu código-fonte ao path ---
# O caminho deve apontar para a pasta que contém o seu 'main.py', ou seja, a pasta 'src'.
path = '/home/muWork01/251014niceguiV02/src'
if path not in sys.path:
    sys.path.insert(0, path)

# --- PASSO 2: Mudar o diretório de trabalho ---
# Isso força o script a ser executado a partir da pasta 'src', garantindo
# que caminhos relativos (como o do banco de dados) funcionem.
os.chdir(path)

# --- PASSO 3: Importar o app ASGI, aplicar o middleware de proxy e criar a ponte WSGI ---
# O objeto 'app' do NiceGUI contém a instância do FastAPI subjacente.
from nicegui import app

# Envolve o app NiceGUI/FastAPI com o middleware.
# Isso o instrui a confiar nos cabeçalhos X-Forwarded-* enviados pelo proxy do PythonAnywhere.
proxied_app = ProxyHeadersMiddleware(app, trusted_hosts="*")

# A variável 'application' é o que o servidor do PythonAnywhere procura.
# ASGIMiddleware "traduz" o app ASGI do NiceGUI para a "língua" WSGI.
application = ASGIMiddleware(proxied_app)
