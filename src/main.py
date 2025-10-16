from nicegui import ui, app, events
import os, io
import json, uuid
from typing import get_args, List, Dict, Any
from pydantic import BaseModel, ValidationError
import datetime, pickle, base64, copy
from datetime import date, datetime
import socket
import sqlite3

# Importa a função que constrói a UI e as funções de manipulação de dados
from ui_builder import build_ui, salvar_estado_no_db, inicializar_estado

# --- Funções Utilitárias ---
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
    print("Banco de dados SQLite (JSON-centric) inicializado.")

inicializar_db()

# --- Ponto de Entrada da UI ---
# Registra a função que constrói a interface do usuário para a rota raiz.
# A função `build_ui` recebe o caminho do banco de dados como argumento.
ui.page('/')(lambda: build_ui(DB_PATH))

# --- Eventos do Ciclo de Vida da Aplicação ---
# Os handlers de startup e shutdown recebem o caminho do banco de dados.
app.on_startup(lambda: inicializar_estado(DB_PATH))
app.on_shutdown(lambda: salvar_estado_no_db(DB_PATH))

# A chamada ui.run() é usada apenas para desenvolvimento local.
# Em produção no PythonAnywhere, o Uvicorn gerencia o servidor.
if __name__ in {"__main__", "__mp_main__"}:
    ui.run(host=HOST, port=8080, title='muWorkApp')
