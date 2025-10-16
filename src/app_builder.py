from nicegui import ui, app
import os
import sqlite3
import socket

# Importe suas funções de UI e de dados do ui_builder
from ui_builder import build_ui, salvar_estado_no_db, inicializar_estado

def get_local_ip():
    """Obtém o endereço IP local da máquina na rede."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1' # Fallback para localhost
    finally:
        s.close()
    return IP

def create_app():
    """
    Esta função é a "fábrica" da sua aplicação.
    Ela configura tudo e retorna o objeto 'app' do NiceGUI.
    """
    # --- Configuração do Ambiente e Constantes ---
    DB_PATH = '/home/muWork01/251014niceguiV02/dbMu/financeiro.db'
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)

    if 'PYTHONANYWHERE_DOMAIN' in os.environ:
        HOST = '0.0.0.0'
    else:
        HOST = get_local_ip()

    # --- Inicialização do Banco de Dados ---
    def inicializar_db():
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS eventos (
                id TEXT PRIMARY KEY,
                nomeDocumento TEXT NOT NULL,
                json_data TEXT NOT NULL,
                data_modificacao TEXT NOT NULL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS app_storage (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        ''')
        conn.commit()
        conn.close()

    inicializar_db()

    # --- Definição da Página Principal ---
    # O decorador é aplicado aqui, dentro da fábrica,
    # o que adia sua execução para o momento certo.
    @ui.page('/')
    def main_page():
        build_ui(DB_PATH)

    # --- Eventos do Ciclo de Vida da Aplicação ---
    app.on_startup(lambda: inicializar_estado(DB_PATH))
    app.on_shutdown(lambda: salvar_estado_no_db(DB_PATH))

    # Retorna o objeto 'app' configurado
    return app