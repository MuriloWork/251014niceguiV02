from fastapi.responses import HTMLResponse

# Importamos o objeto 'app' diretamente do nicegui.
# Este objeto 'app' é, na verdade, uma instância do FastAPI.
from nicegui import app

@app.get("/")
def read_root():
    # Usamos um decorador e uma resposta padrão do FastAPI.
    return HTMLResponse("<h1>Olá do FastAPI que vive dentro do NiceGUI!</h1>")