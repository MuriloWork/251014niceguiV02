from nicegui import ui, app, events
import os, io
import asyncio
from pathlib import Path
import json, uuid
from typing import get_args, List, Dict, Any
from pydantic import BaseModel, ValidationError
import datetime, pickle, base64, copy
from datetime import date, datetime
import pandas as pd
import numpy as np
import socket
import sqlite3
from z04_pydanticEventos import Evento, Metadados, Itens

# --- Constantes e Configuração Inicial ---
# O caminho do DB é passado como argumento para evitar defini-lo globalmente aqui.

# --- Funções de documento ---
# Todas as suas funções (salvar_documento_no_db, carregar_documento_do_db, etc.)
# permanecem aqui, mas a variável DB_PATH será passada para elas.

def salvar_documento_no_db(DB_PATH):
    """Pega o documento ativo, valida e salva no banco de dados SQLite."""
    documento_ativo = app.storage.general.get('documento_ativo')
    if not documento_ativo:
        ui.notify("Nenhum documento ativo para salvar.", type='warning')
        return

    try:
        documento_validado = Evento.model_validate(documento_ativo)
        evento_id = documento_validado.id
        nome_documento = documento_ativo.get('nomeDocumento', f"evento_{evento_id[:8]}")
        json_data = documento_validado.model_dump_json()
        data_modificacao = datetime.now().isoformat()

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO eventos (id, nomeDocumento, json_data, data_modificacao)
            VALUES (?, ?, ?, ?)''', (evento_id, nome_documento, json_data, data_modificacao))
        conn.commit()
        conn.close()

        ui.notify(f"Evento '{nome_documento}' salvo no banco de dados!", type='positive')
        salvar_estado_no_db(DB_PATH)

    except ValidationError as e:
        ui.notify(f"Erro de validação ao salvar no DB: {e}", type='negative', multi_line=True)
    except Exception as e:
        ui.notify(f"Erro ao salvar no banco de dados: {e}", type='negative')

def carregar_documento_do_db(evento_id: str, DB_PATH) -> dict:
    """Carrega um evento e seus itens do banco de dados SQLite."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT json_data FROM eventos WHERE id = ?", (evento_id,))
        resultado = cursor.fetchone()

        if not resultado:
            ui.notify(f"Evento com ID '{evento_id}' não encontrado no banco de dados.", type='negative')
            return None

        json_data = resultado[0]
        documento = json.loads(json_data)

        ui.notify(f"Evento '{documento.get('tituloEvento')}' carregado do banco de dados.", type='positive')
        return documento
    except Exception as e:
        ui.notify(f"Erro ao carregar evento do banco de dados: {e}", type='negative', multi_line=True)
        return None
    finally:
        conn.close()

def criar_novo_documento(novo_evento_nome, novo_evento_tipo, DB_PATH):
    """Cria um novo documento de evento e o salva diretamente no banco de dados."""
    if not novo_evento_nome.value.strip():
        ui.notify("Por favor, insira um nome para o novo evento.", type='warning')
        return

    nome_formatado = "".join(c if c.isalnum() else '_' for c in novo_evento_nome.value.strip())
    nome_documento = f"{date.today():%Y-%m-%d}_{novo_evento_tipo.value}_{nome_formatado}"

    novo_doc = Evento(
        tituloEvento=novo_evento_nome.value.strip(),
        tipoEvento=novo_evento_tipo.value,
        metadados=Metadados(),
        itens=[Itens().model_dump()],
        nomeDocumento=nome_documento
    )

    app.storage.general['documento_ativo'] = novo_doc.model_dump()
    app.storage.general['evento_id_ativo'] = novo_doc.id
    salvar_documento_no_db(DB_PATH)
    ui.navigate.to('/')

def salvar_estado_no_db(DB_PATH):
    """Salva o conteúdo de app.storage.general na tabela app_storage."""
    def to_plain_python(obj):
        obj_type_name = type(obj).__name__
        if obj_type_name == 'ObservableDict':
            return {k: to_plain_python(v) for k, v in obj.items()}
        if obj_type_name == 'ObservableList':
            return [to_plain_python(i) for i in obj]
        return obj
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        for key, value in app.storage.general.items():
            standard_value = to_plain_python(value)
            pickled_value = pickle.dumps(standard_value)
            encoded_value = base64.b64encode(pickled_value).decode('utf-8')
            cursor.execute(
                "INSERT OR REPLACE INTO app_storage (key, value) VALUES (?, ?)",
                (key, encoded_value)
            )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"Erro ao salvar estado da aplicação no DB: {e}")

def inicializar_estado(DB_PATH):
    """Carrega o estado da aplicação da tabela app_storage para app.storage.general."""
    # Garante que as chaves essenciais existam com valores padrão.
    for key in ['documento_ativo', 'evento_id_ativo', 'item_selecionado']:
        if key not in app.storage.general:
            app.storage.general[key] = None

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT key, value FROM app_storage")
        rows = cursor.fetchall()
        conn.close()

        for key, encoded_value in rows:
            pickled_value = base64.b64decode(encoded_value)
            value = pickle.loads(pickled_value)
            app.storage.general[key] = value

    except Exception as e:
        print(f"Erro ao inicializar estado do DB: {e}")


def build_ui(DB_PATH):
    """
    Esta função contém toda a lógica de construção da interface do usuário.
    Ela é chamada pelo main.py depois que o servidor já está no ar.
    """
    documento_ativo = app.storage.general.get('documento_ativo')

    drawer_open = True

    with ui.header(elevated=True).classes('bg-primary text-white'):
        btn_menu = ui.button(icon='menu', on_click=lambda: drawer.toggle()).props('flat color=white')
        ui.label("Meus Eventos").classes('text-2xl')
        ui.space()
        if documento_ativo:
            ui.label(f"Editando: {documento_ativo.get('nomeDocumento', 'Evento sem título')}").classes('text-sm')
        ui.button("Salvar", on_click=lambda: salvar_documento_no_db(DB_PATH), icon='save').props('outline round dense color="white"')

    with ui.left_drawer(value=drawer_open, top_corner=True, bottom_corner=True).props('width=270') as drawer:
        ui.label("Gerenciar Arquivos").classes('font-bold p-2')

        with ui.card().tight():
            ui.label("Novo Documento").classes('text-md font-semibold p-2')
            with ui.card_section():
                novo_evento_nome = ui.input("Nome do Evento").props('dense').classes('w-full')
                tipo_evento_options = list(get_args(Evento.model_fields['tipoEvento'].annotation))
                novo_evento_tipo = ui.select(tipo_evento_options, value="compra", label="Tipo").props('dense').classes('w-full')
            ui.button("Criar Novo", on_click=lambda: criar_novo_documento(novo_evento_nome, novo_evento_tipo, DB_PATH)).props('flat dense')

        ui.separator().classes('my-4')

        def listar_eventos_db():
            try:
                conn = sqlite3.connect(DB_PATH)
                cursor = conn.cursor()
                cursor.execute("SELECT id, nomeDocumento FROM eventos ORDER BY data_modificacao DESC")
                eventos = cursor.fetchall()
                conn.close()
                return eventos
            except Exception as e:
                print(f"Erro ao listar eventos do DB: {e}")
                return []

        eventos_existentes = listar_eventos_db()

        def abrir_selecionado(evento_id: str):
            if evento_id:
                documento = carregar_documento_do_db(evento_id, DB_PATH)
                app.storage.general['documento_ativo'] = documento
                app.storage.general['evento_id_ativo'] = evento_id
                salvar_estado_no_db(DB_PATH)
                ui.navigate.to('/')

        ui.label("Abrir Existente").classes('text-md font-semibold p-2')
        for evento_id, nome_doc in eventos_existentes:
            ui.button(nome_doc, on_click=lambda eid=evento_id: abrir_selecionado(eid)).props('flat dense text-left').classes('text-xs')

    btn_menu.on_click(drawer.toggle)

    if documento_ativo:
        # ... cole aqui todo o resto do seu código de UI ...
        # (o conteúdo de 'with ui.card().classes('w-full max-w-screen-xl'):' em diante)
        with ui.card().classes('w-full max-w-screen-xl'):
            ui.label("A interface completa do seu aplicativo vai aqui.")
            # Por brevidade, não colei as 1000 linhas de UI, mas elas devem vir aqui.
            # Certifique-se de que qualquer chamada a uma função como salvar_documento_no_db
            # seja ajustada para passar o DB_PATH, por exemplo:
            # on_click=lambda: sua_funcao(DB_PATH)
    else:
        ui.label("Crie um novo documento ou abra um existente na barra lateral para começar.").classes('m-4 text-xl')