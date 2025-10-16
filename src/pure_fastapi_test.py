from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI()

@app.get("/")
async def root():
    html_content = """
    <html>
        <head>
            <title>Teste FastAPI Puro com Elementos</title>
            <style>
                body { font-family: sans-serif; padding: 2em; background-color: #f4f4f9; }
                h1 { color: #1e3a8a; }
                .card { background-color: white; border: 1px solid #ddd; border-radius: 8px; padding: 16px; margin-top: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                button { padding: 10px 15px; background-color: #3b82f6; color: white; border: none; border-radius: 4px; cursor: pointer; }
            </style>
        </head>
        <body>
            <h1>Página de Teste - FastAPI Puro</h1>
            <p>Se esta página for exibida, o deploy ASGI básico para servir HTML está funcionando.</p>
            <div class="card">
                <h2>Um Card Simples (similar a ui.card)</h2>
                <button onclick="alert('Botão clicado!')">Clique Aqui (similar a ui.button)</button>
            </div>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)