from nicegui import ui, app

# O decorador @ui.page garante que o código dentro da função
# só será executado quando um usuário acessar a página.
@ui.page('/')
def index_page():
    ui.label('Hello, World! O aplicativo de teste funcionou!')

# A guarda __main__ é para execução local e não interfere no deploy.
if __name__ in {"__main__", "__mp_main__"}:
    ui.run()