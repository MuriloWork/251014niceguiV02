print("--- main.py: Top of file ---")

from nicegui import ui, app, events
import os, io
import json, uuid
from typing import get_args, List, Dict, Any
from pydantic import BaseModel, ValidationError
import datetime, pickle, base64, copy
from datetime import date, datetime
import socket
import sqlite3

print("--- main.py: Standard imports complete ---")

# Importa a função que constrói a UI e as funções de manipulação de dados
from ui_builder import build_ui, salvar_estado_no_db, inicializar_estado

print("--- main.py: ui_builder imported ---")

# --- Funções Utilitárias ---
def get_local_ip():
    # print("--- main.py: get_local_ip() called ---")
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
print(f"--- main.py: DB_PATH set to {DB_PATH} ---")

if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    HOST = '0.0.0.0'
else:
    HOST = get_local_ip()
print(f"--- main.py: HOST set to {HOST} ---")

# --- Inicialização do Banco de Dados ---
def inicializar_db():
    print("--- main.py: inicializar_db() called ---")
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
    print("--- main.py: inicializar_db() finished ---")

inicializar_db()

print("--- main.py: Before @ui.page decorator ---")
# --- Definição da Página Principal ---
# Usamos o decorador @ui.page para registrar a função.
# Isso garante que a função `build_ui` só será executada quando um cliente se conectar.
@ui.page('/')
def main_page():
    print("--- main.py: main_page() function is executing ---")
    build_ui(DB_PATH)

print("--- main.py: After @ui.page decorator ---")

# --- Eventos do Ciclo de Vida da Aplicação ---
# Os handlers de startup e shutdown recebem o caminho do banco de dados.
app.on_startup(lambda: (print("--- main.py: app.on_startup executing ---"), inicializar_estado(DB_PATH)))
app.on_shutdown(lambda: (print("--- main.py: app.on_shutdown executing ---"), salvar_estado_no_db(DB_PATH)))

print("--- main.py: Lifecycle events registered ---")

# A chamada ui.run() é usada apenas para desenvolvimento local.
# Em produção no PythonAnywhere, o Uvicorn gerencia o servidor.
if __name__ in {"__main__", "__mp_main__"}:
    print("--- main.py: Running for local development via ui.run() ---")
    ui.run(host=HOST, port=8080, title='muWorkApp')
