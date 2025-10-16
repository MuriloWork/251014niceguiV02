# Conteúdo CORRIGIDO e FINAL para o arquivo muwork01_pythonanywhere_com_wsgi.py

import requests
from flask import Flask, request, Response

# Aponta para o servidor NiceGUI que está rodando internamente no console.
# Usar 127.0.0.1 é crucial para a comunicação interna no servidor.
SERVER_URL = "http://127.0.0.1:8000"

app = Flask(__name__)

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def proxy(path):
    try:
        # Encaminha a requisição para o servidor NiceGUI
        response = requests.request(
            method=request.method,
            url=f"{SERVER_URL}/{path}",
            headers={key: value for (key, value) in request.headers if key != 'Host'},
            data=request.get_data(),
            cookies=request.cookies,
            allow_redirects=False,
            stream=True
        )

        # Retorna a resposta do servidor NiceGUI para o navegador do usuário
        return Response(
            response.iter_content(chunk_size=1024),
            status=response.status_code,
            headers=dict(response.headers)
        )
    except requests.exceptions.ConnectionError:
        # Mensagem de erro amigável se o servidor NiceGUI (no console) não estiver rodando
        return "<h1>503 Serviço Indisponível</h1><p>O servidor principal do aplicativo (NiceGUI) não parece estar em execução. Por favor, inicie-o em um console Bash no PythonAnywhere.</p>", 503

# A variável 'application' é o que o servidor do PythonAnywhere procura.
application = app
