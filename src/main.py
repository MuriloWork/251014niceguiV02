
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

# --- Funções Utilitárias ---
def get_local_ip():
    """Obtém o endereço IP local da máquina na rede."""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Tenta conectar a um IP não roteável para descobrir a interface de rede principal
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1' # Fallback para localhost
    finally:
        s.close()
    return IP

# --- Constantes e Configuração Inicial ---
# Define um caminho absoluto para o banco de dados, que é a forma mais robusta para ambientes de servidor.
# Isso garante que o caminho funcione independentemente de onde o script é executado.
# ATENÇÃO: Substitua 'muWork01' pelo seu nome de usuário real no PythonAnywhere.
DB_PATH = '/home/muWork01/251014niceguiV02/dbMu/financeiro.db'
db_dir = os.path.dirname(DB_PATH)
os.makedirs(db_dir, exist_ok=True)

# Detecta o ambiente para definir o HOST corretamente.
if 'PYTHONANYWHERE_DOMAIN' in os.environ:
    HOST = '0.0.0.0'  # Necessário para o ambiente de servidor do PythonAnywhere
else:
    HOST = get_local_ip() # Usa o IP local para desenvolvimento

# --- Configuração do Banco de Dados ---
def inicializar_db():
    """Cria a tabela do banco de dados se ela não existir, usando uma coluna para o JSON."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela única para armazenar os eventos como documentos JSON
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS eventos (
            id TEXT PRIMARY KEY,            
            nomeDocumento TEXT NOT NULL,
            json_data TEXT NOT NULL,
            data_modificacao TEXT NOT NULL
        )
    ''')

    # Tabela para substituir o storage-general.json
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

# -- Funções
def to_plain_python(obj):
    """Converte recursivamente ObservableDicts e ObservableLists para dicts e lists padrão."""
    # Compara o nome do tipo em vez de importar a classe, o que é mais robusto.
    obj_type_name = type(obj).__name__
    if obj_type_name == 'ObservableDict':
        return {k: to_plain_python(v) for k, v in obj.items()}
    if obj_type_name == 'ObservableList':
        return [to_plain_python(i) for i in obj]
    return obj

# --- Funções de sistema, aplicativo                                                    ## --- Funções de sistema, aplicativo
def salvar_estado_no_db():
    """Salva o conteúdo de app.storage.general na tabela app_storage."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        for key, value in app.storage.general.items():
            # Converte de forma robusta os tipos observáveis do NiceGUI para tipos Python padrão.
            standard_value = to_plain_python(value)

            # Serializa o objeto Python padrão.
            pickled_value = pickle.dumps(standard_value)
            encoded_value = base64.b64encode(pickled_value).decode('utf-8')
            cursor.execute(
                "INSERT OR REPLACE INTO app_storage (key, value) VALUES (?, ?)",
                (key, encoded_value)
            )
        conn.commit()
        conn.close()
        # ui.notify("Estado da aplicação salvo.", type='info')
    except Exception as e:
        print(f"Erro ao salvar estado da aplicação no DB: {e}")

def inicializar_estado():
    """Carrega o estado da aplicação da tabela app_storage para app.storage.general."""
    # Primeiro, garante que as chaves essenciais existam com valores padrão.
    # Isso evita o KeyError na primeira execução ou com um DB vazio.
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

# --- Funções de documento                                                              ## --- Funções de documento
def salvar_documento_no_db():
    """Pega o documento ativo, valida e salva no banco de dados SQLite."""
    documento_ativo = app.storage.general.get('documento_ativo')
    if not documento_ativo:
        ui.notify("Nenhum documento ativo para salvar.", type='warning')
        return

    try:
        # 1. Valida os dados com Pydantic
        documento_validado = Evento.model_validate(documento_ativo)
        
        # 2. Prepara os dados para o DB
        evento_id = documento_validado.id
        nome_documento = documento_ativo.get('nomeDocumento', f"evento_{evento_id[:8]}") # Fallback
        json_data = documento_validado.model_dump_json() # Converte o modelo para uma string JSON
        data_modificacao = datetime.now().isoformat()

        # 3. Salva no banco de dados
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute('''            
            INSERT OR REPLACE INTO eventos (id, nomeDocumento, json_data, data_modificacao)
            VALUES (?, ?, ?, ?)''', (evento_id, nome_documento, json_data, data_modificacao))
        conn.commit()
        conn.close()

        ui.notify(f"Evento '{nome_documento}' salvo no banco de dados!", type='positive')
        # Após salvar o documento, salva também o estado geral da aplicação
        salvar_estado_no_db()

    except ValidationError as e:
        ui.notify(f"Erro de validação ao salvar no DB: {e}", type='negative', multi_line=True)
    except Exception as e:
        ui.notify(f"Erro ao salvar no banco de dados: {e}", type='negative')

def carregar_documento_do_db(evento_id: str) -> dict:
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

async def handle_excel_import(e: events.UploadEventArguments):                          ## doc loading
    """Processa o arquivo Excel enviado pelo usuário e atualiza a grade de itens."""
    try:
        df_importado = pd.read_excel(io.BytesIO(e.content.read()))
        colunas_modelo = set(Itens.model_fields.keys())
        if not colunas_modelo.issubset(df_importado.columns):
            colunas_faltando = colunas_modelo - set(df_importado.columns)
            ui.notify(f"Arquivo Excel inválido. Faltam colunas: {', '.join(colunas_faltando)}", type='negative')
            return

        itens_importados = normalizar_df_para_pydantic(df_importado)
        itens_validados = [Itens.model_validate(item).model_dump() for item in itens_importados]

        app.storage.general['documento_ativo']['itens'] = itens_validados
        salvar_documento_no_db()
        ui.notify(f"Itens importados de '{e.name}' e salvos com sucesso!", type='positive')
        ui.navigate.reload()  # Forma recomendada para recarregar a página
    except ValidationError as err:
        ui.notify(f"Erro de validação nos dados do Excel: {err}", type='negative', multi_line=True)
    except Exception as err:
        ui.notify(f"Erro ao processar o arquivo Excel: {err}", type='negative')

def criar_novo_documento(novo_evento_nome, novo_evento_tipo):
    """Cria um novo documento de evento e o salva diretamente no banco de dados."""
    if not novo_evento_nome.value.strip():
        ui.notify("Por favor, insira um nome para o novo evento.", type='warning')
        return
    
    # Gera o nome do documento no formato de arquivo antigo
    nome_formatado = "".join(c if c.isalnum() else '_' for c in novo_evento_nome.value.strip())
    nome_documento = f"{date.today():%Y-%m-%d}_{novo_evento_tipo.value}_{nome_formatado}"

    novo_doc = Evento(
        tituloEvento=novo_evento_nome.value.strip(),
        tipoEvento=novo_evento_tipo.value, 
        metadados=Metadados(), 
        itens=[Itens().model_dump()],
        nomeDocumento=nome_documento  # Adiciona o nome do documento na criação do objeto Pydantic
    )

    # O dicionário agora conterá 'nomeDocumento' por padrão
    app.storage.general['documento_ativo'] = novo_doc.model_dump()
    app.storage.general['evento_id_ativo'] = novo_doc.id
    salvar_documento_no_db()
    ui.navigate.to('/')

def handle_excel_export():                                                              ## doc saving
    """Gera e baixa um arquivo Excel a partir dos itens do documento ativo."""
    itens = app.storage.general.get('documento_ativo', {}).get('itens', [])
    if not itens:
        ui.notify("Não há itens para exportar.", type='warning')
        return

    df = pd.DataFrame(itens)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Itens')
    
    filename = f"{Path(app.storage.general.get('caminho_arquivo', 'export')).stem}_itens.xlsx"
    ui.download(output.getvalue(), filename, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')

def normalizar_df_para_pydantic(df: pd.DataFrame) -> List[Dict[str, Any]]:              ## schema padronização
    """Prepara um DataFrame do pandas para validação com Pydantic."""
    def converter_valor(valor):
        if pd.isna(valor):
            return None
        if isinstance(valor, np.generic):
            return valor.item()
        if isinstance(valor, pd.Timestamp):
            return valor.date() if valor.hour == 0 and valor.minute == 0 and valor.second == 0 else valor.to_pydatetime()
        return valor

    lista_de_registros = df.to_dict(orient='records')
    return [
        {chave: converter_valor(valor) for chave, valor in registro.items()}
        for registro in lista_de_registros
    ]

# --- Funções de itens                                                                  ## --- Funções de itens
DEFAULT_ITENS = {
    "idItem": "",
    "tipoItem": None,
    "sku": "",
    "descricaoItem": "item",
    "descricaoAlternativa": "",
    "grupo1": "",
    "grupo2": "",
    "tituloAtividade": "atividade",
    "tituloAtividadeAlternativo": "",
    "dataCriacao": datetime.today().strftime("%d/%m/%Y"),
    "dataFim": None,
    "quem": "",
    "qtd": 0.0,
    "un": "",
    "preco": 0.0,
    "moeda": "",
    "valorTotal": 0.0,
    "tipoOrcamento": None,
    "notas": "",
    "tags": ""
}

def setup_ui():
    documento_ativo = app.storage.general.get('documento_ativo')

    drawer_open = True  # estado global do drawer

    with ui.header(elevated=True).classes('bg-primary text-white'):                     ## Header: Meus Eventos
        btn_menu = ui.button(icon='menu', 
                #   on_click=lambda: drawer_open.set(not drawer_open.value)
                  on_click=lambda: drawer.toggle()
                )\
                .props('flat color=white')
        ui.label("Meus Eventos").classes('text-2xl')
        ui.space()
        if documento_ativo:
            # Atualizado para mostrar o título do evento em vez do nome do arquivo
            ui.label(f"Editando: {documento_ativo.get('nomeDocumento', 'Evento sem título')}").classes('text-sm')
        ui.button("Salvar", on_click=salvar_documento_no_db, icon='save').props('outline round dense color="white"')

    with ui.left_drawer(value=drawer_open, top_corner=True, bottom_corner=True).props('width=270') as drawer:        ## --- Barra Lateral (Sidebar) ---
        ui.label("Gerenciar Arquivos").classes('font-bold p-2')

        with ui.card().tight():                                                         ## novo documento
            ui.label("Novo Documento").classes('text-md font-semibold p-2')
            with ui.card_section():
                novo_evento_nome = ui.input("Nome do Evento").props('dense').classes('w-full')
                tipo_evento_options = list(get_args(Evento.model_fields['tipoEvento'].annotation))
                novo_evento_tipo = ui.select(tipo_evento_options, value="compra", label="Tipo").props('dense').classes('w-full')

            # ui.button(f"Criar Novo  {str(nome_arquivo.value)}", on_click=lambda: criar_novo_documento(novo_evento_nome, novo_evento_tipo)).props('flat dense')
            ui.button(f"Criar Novo", on_click=lambda: criar_novo_documento(novo_evento_nome, novo_evento_tipo)).props('flat dense')

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
                documento = carregar_documento_do_db(evento_id)
                app.storage.general['documento_ativo'] = documento
                app.storage.general['evento_id_ativo'] = evento_id
                # Salva o novo estado (com o documento recém-carregado) no DB
                salvar_estado_no_db()
                ui.navigate.to('/')
        
        ui.label("Abrir Existente").classes('text-md font-semibold p-2')
        for evento_id, nome_doc in eventos_existentes: ui.button(nome_doc, on_click=lambda eid=evento_id: abrir_selecionado(eid)).props('flat dense text-left').classes('text-xs')

    btn_menu.on_click(drawer.toggle)

    # if app.storage.general.get('documento_ativo'):                                         ## --- Área Principal de Edição ---
    if documento_ativo:                                                                    ## --- Área Principal de Edição ---
        with ui.card().classes('w-full max-w-screen-xl'):                                   ## --- Formulário Principal ---
            with ui.card().classes('w-full'):                                               ## --- Seção Evento --- # O estado de expansão (aberto/fechado) é um booleano. Como 'metadados' agora é uma lista de objetos, vinculamos o estado do painel a um campo booleano dentro do *primeiro* objeto dessa lista. Isso assume que a lista 'metadados' não estará vazia.
                with ui.expansion(
                    f'Evento: {documento_ativo["tituloEvento"]}' + '             ' + f'Documento: {documento_ativo["nomeDocumento"]}',
                    value=documento_ativo["metadados"].get("stFoldingStatusEvento", False)
                    )\
                    .classes("w-full"):

                    # with expansion.add_slot('header'):
                        #     ui.icon('event', color='primary')
                        #     # O argumento 'forward' é usado para transformar o valor do modelo (tituloEvento)
                        #     # antes de exibi-lo na UI. 'backward' faria o caminho inverso.
                        #     ui.label().bind_text_from(documento_ativo, 'tituloEvento', backward=lambda x: f"Evento: {x}")

                    ui.input("Título do Evento")\
                        .bind_value(documento_ativo, 'tituloEvento')\
                        .props("dense outlined")\
                        .classes("w-full")
                            
                    with ui.row().classes("w-full no-wrap"):                                                ## tipoProjeto, tipoEvento
                        ui.select(
                            list(get_args(Evento.model_fields['tipoProjeto'].annotation)),
                            label="Tipo de Projeto")\
                            .bind_value(documento_ativo, 'tipoProjeto')\
                            .props("dense outlined")\
                            .classes("w-1/2")
                        ui.select(
                            list(get_args(Evento.model_fields['tipoEvento'].annotation)),
                            label="Tipo de Evento")\
                            .bind_value(documento_ativo, 'tipoEvento')\
                            .props("dense outlined")\
                            .classes("w-1/2")

                    with ui.row().classes("w-full no-wrap"):                                                ## tags, links
                        ui.textarea("Tags (uma por linha)")\
                            .bind_value(
                                documento_ativo, 'tags',
                                forward=lambda v: '\n'.join(v or []),
                                backward=lambda v: [s.strip() for s in v.split('\n') if s.strip()] if isinstance(v, str) else v
                            )\
                            .props("dense autogrow outlined")\
                            .classes("w-1/2")

                        ui.textarea("Links (uma por linha)")\
                            .bind_value(
                                documento_ativo, 'links',
                                forward=lambda v: '\n'.join(v or []),
                                backward=lambda v: [s.strip() for s in v.split('\n') if s.strip()] if isinstance(v, str) else v
                            )\
                            .props("dense autogrow outlined")\
                            .classes("w-1/2")

                    ui.input("Pasta de Documentos")\
                        .bind_value(documento_ativo, 'docsPath')\
                        .props("dense outlined")\
                        .classes("w-full")

                    ui.textarea("Metadados")\
                        .bind_value(documento_ativo, "metadados")\
                        .props("dense outlined")\
                        .classes("w-full")

                    # PAUSED             # # O bind_value para um dicionário em um textarea precisa de conversores
                        #             # # para transformar o objeto em string (JSON) e vice-versa.
                        #             # ui.textarea("Metadados (JSON)")\
                        #             #     .bind_value(
                        #             #         documento_ativo, 'metadados',
                        #                     # # forward: Converte o dicionário em uma string JSON formatada para exibir
                        #                     # forward=lambda v: json.dumps(v, indent=2) if v is not None else '{}',
                        #                     # # backward: Converte a string do textarea de volta para um dicionário.
                        #                     # # A verificação isinstance(v, str) é necessária para evitar um TypeError
                        #                     # # quando o binding propaga uma mudança do próprio objeto (ObservableDict).
                        #                 #     backward=lambda v: json.loads(v or '{}') if isinstance(v, str) else v
                        #                 # )\
                        #                 # .props("dense outlined autogrow")\
                        #                 # .classes("w-full")

                        #             # Área para edição dos metadados como JSON
                        #             metadados_str = ui.textarea("Metadados (JSON)").props('dense outlined autogrow').classes('w-full')

                        #             # Preenche inicialmente com o JSON formatado da lista de objetos
                        #             metadados_str.value = json.dumps(
                        #                 [m if isinstance(m, dict) else m.model_dump() for m in (documento_ativo.get('metadados') or [])],
                        #                 indent=2,
                        #                 ensure_ascii=False
                        #             )

                        #             # Atualiza a lista de objetos quando o usuário terminar de editar
                        #             def atualizar_metadados(e):
                        #                 try:
                        #                     nova_lista = json.loads(metadados_str.value or '[]')
                        #                     if isinstance(nova_lista, list):
                        #                         # valida cada item como Metadados
                        #                         lista_valida = [Metadados.model_validate(m).model_dump() for m in nova_lista]
                        #                         app.storage.general['documento_ativo']['metadados'] = lista_valida
                        #                         ui.notify("Metadados atualizados!", type='positive')
                        #                     else:
                        #                         ui.notify("O JSON de metadados deve ser uma lista ([]).", type='negative')
                        #                 except json.JSONDecodeError as err:
                        #                     ui.notify(f"JSON inválido: {err}", type='negative')

                        #             metadados_str.on('blur', atualizar_metadados)

                    # PAUSED async def on_cell_value_changed(e: events.GenericEventArguments):               ## Atualiza o item específico no estado do servidor quando uma célula é editada no grid. Esta abordagem é mais eficiente do que recarregar todos os dados.
                        #     modified_row_data = e.args['data']
                        #     row_id = modified_row_data.get('idColumn')

                        #     if not row_id:
                        #         ui.notify('Erro: Não foi possível identificar a linha modificada (sem idColumn).', type='negative')
                        #         return

                        #     # Encontra o item correspondente na lista do servidor e o atualiza
                        #     itens_list = app.storage.general['documento_ativo']['itens']
                        #     for i, item in enumerate(itens_list):
                        #         if item.get('idColumn') == row_id:
                        #             app.storage.general['documento_ativo']['itens'][i] = modified_row_data
                        #             ui.notify(f"Item '{item.get('descricaoItem', row_id)}' atualizado no estado.", type='info')
                        #             # Opcional: salvar a cada edição de célula. Pode ser removido se o salvamento for apenas pelo botão "Salvar".
                        #             salvar_documento_atual()
                        #             break

                        # grid.on('cellValueChanged', on_cell_value_changed)                          ## valor alterado na celula


                    with ui.row().classes('w-full justify-end'):
                        ui.switch('Aberto')\
                        .bind_value(documento_ativo['metadados'], 'stFoldingStatusEvento')

            with ui.card().classes('w-full'):                                               ## --- Seção Planejamento 01 ---
                with ui.expansion(
                    'Planejamento 01',
                    value=documento_ativo["metadados"].get("stFoldingStatusPlanejamento01", False)
                    )\
                    .classes("w-full"):
                    
                    # with expansion.add_slot('header'):
                    #     ui.icon('edit_note', color='primary')
                    #     ui.label("Planejamento 01")
                    with ui.tabs() as tabs:
                        ui.tab('Notas').props('no-caps')
                        ui.tab('Índice').props('no-caps')
                        ui.tab('Pessoas').props('no-caps')
                    with ui.tab_panels(tabs, value='Notas').classes('w-full'):
                        with ui.tab_panel('Notas'):
                            ui.textarea("Notas Gerais").props('autogrow').bind_value(documento_ativo, 'notas')
                        with ui.tab_panel('Índice'):
                            ui.textarea("Índice (JSON)").props('autogrow').bind_value(documento_ativo, 'indice', forward=lambda v: json.dumps(v, indent=2), backward=lambda v: json.loads(v or '{}'))
                        with ui.tab_panel('Pessoas'):
                            ui.textarea("Pessoas (JSON)").props('autogrow').bind_value(documento_ativo, 'pessoas', forward=lambda v: json.dumps(v, indent=2), backward=lambda v: json.loads(v or '{}'))
                    with ui.row().classes('w-full justify-end'):
                        ui.switch('Aberto')\
                            .bind_value(documento_ativo['metadados'], 'stFoldingStatusPlanejamento01')

            with ui.card().classes('w-full'):                                               ## --- Seção Planejamento 02 (Itens) ---
                with ui.expansion(
                    'Planejamento 02',
                    value=documento_ativo["metadados"].get("stFoldingStatusPlanejamento02", False)
                    )\
                    .classes("w-full"):

                    with ui.card_section().classes('w-full'):                               ## AGGRID
                        # Dicionário para mapear grupos a colunas e função para alternar visibilidade
                        COLUMN_GROUPS = {
                            'grupos': ['tipoItem', 'grupo1', 'grupo2'],
                            'orçamento': ['qtd', 'un', 'moeda', 'preco', 'tipoOrcamento']
                        }

                        async def toggle_column_group_visibility(group_name: str, visible: bool):
                            """Altera a visibilidade de um grupo de colunas na grade."""
                            columns_to_toggle = COLUMN_GROUPS.get(group_name, [])
                            for col_id in columns_to_toggle:
                                # Altera a visibilidade da coluna
                                await grid.run_column_method('setColumnVisible', col_id, visible)
                            
                            # Se as colunas estão sendo exibidas, ajusta o tamanho delas para caber no conteúdo.
                            if visible:
                                await grid.run_grid_method('autoSizeColumns', columns_to_toggle)
                            # ui.notify(f"Colunas do grupo '{group_name}' {'visíveis' if visible else 'ocultas'}.")

                        grid_is_selected = False

                        async def atualizar_resumo(linhas: List[Dict[str, Any]]):
                            """Atualiza o container do resumo com base nas linhas fornecidas."""
                            summary_container.clear()
                            if not linhas:
                                # Se não houver seleção, pega todos os dados do cliente
                                linhas = await grid.get_client_data()
                                titulo = 'Resumo da Grade'
                            else:
                                titulo = 'Resumo da Seleção'

                            with summary_container:
                                with ui.row().classes('w-full items-center'):
                                    ui.label(titulo).classes('text-lg font-semibold')
                                    ui.space()
                                    ui.button('Fechar', on_click=lambda: summary_container.classes('hidden'), icon='close').props('flat round dense')

                                if not linhas:
                                    ui.label("ERRO!!!!!!!!! Nenhum item para resumir.").classes('text-gray-500')
                                    return

                                total_valor = sum(float(linha.get('valorTotal', 0) or 0) for linha in linhas)
                                ui.table(
                                    columns=[{'name': 'metrica', 'label': 'Métrica', 'field': 'metrica'}, {'name': 'valor', 'label': 'Valor', 'field': 'valor'}],
                                    rows=[{'metrica': 'Itens Selecionados', 'valor': len(linhas)}, {'metrica': 'Soma de "Valor Total"', 'valor': f'R$ {total_valor:,.2f}'}],
                                    row_key='metrica'
                                ).classes('w-1/3 mt-2')

                        # Adiciona estados para a visibilidade das colunas, com False como padrão
                        if 'show_grupos' not in app.storage.general:
                            app.storage.general['show_grupos'] = False
                        if 'show_orcamento' not in app.storage.general:
                            app.storage.general['show_orcamento'] = False

                        with ui.row().classes('w-full mb-4'):                             ## AVISOS, BOTÕES, CHECKBOXES
                            with ui.column():                                               ## resumo
                                async def exibir_resumo():
                                    linhas_selecionadas = await grid.get_selected_rows()
                                    await atualizar_resumo(linhas_selecionadas)
                                    summary_container.classes(remove='hidden')
                                ui.button("Resumo", on_click=exibir_resumo, icon='view_headline')\
                                    .props('flat dense')\
                                    .classes('text-base')
                                async def paused_02():                                   ## Copia a linha selecionada, gera um novo ID, valida e insere abaixo da original.
                                    linhas_selecionadas = await grid.get_selected_rows()
                                    if not linhas_selecionadas:
                                        ui.notify('Selecione um item para copiar.', type='warning')
                                        return

                                    item_original = linhas_selecionadas[0]
                                    item_copiado_dict = item_original.copy()
                                    item_copiado_dict['idColumn'] = str(uuid.uuid4())
                                    item_copiado_dict['descricaoItem'] = f"Cópia de {item_original.get('descricaoItem', 'item')}"

                                    try:
                                        novo_item_validado = Itens.model_validate(item_copiado_dict).model_dump()
                                    except ValidationError as e:
                                        ui.notify(f"Erro de validação ao copiar: {e}", type='negative', multi_line=True)
                                        return

                                    try:
                                        index_original = next(
                                            i for i, item in enumerate(documento_ativo['itens'])
                                            if item.get('idColumn') == item_original.get('idColumn')
                                        )
                                    except StopIteration:
                                        index_original = len(documento_ativo['itens']) - 1

                                    index_insercao = index_original + 1
                                    documento_ativo['itens'].insert(index_insercao, novo_item_validado)

                                    try:
                                        grid.run_grid_method('applyTransaction', {
                                            'add': [novo_item_validado],
                                            'addIndex': index_insercao,
                                        })
                                        await asyncio.sleep(0.1)
                                        novo_id = novo_item_validado.get('idColumn')
                                        grid.run_grid_method('deselectAll')
                                        grid.run_row_method(novo_id, 'setSelected', True)
                                    except Exception as e:
                                        ui.notify(f'Falha ao atualizar a grade: {e}', type='negative')
                                        documento_ativo['itens'].pop(index_insercao)
                                        return

                                    salvar_documento_no_db()
                                    aviso_grid.clear()
                                    with aviso_grid:
                                        ui.label(f"Item copiado e inserido na posição {index_insercao}.")
                                ui.button("...", on_click=paused_02, icon='add')\
                                     .props('flat dense')\
                                    .classes('text-base')
                            with ui.column():                                               ## adicionar item, excluir item
                                async def add_row():
                                    if 'itens' not in documento_ativo:
                                        documento_ativo['itens'] = []
                                    linhas_selecionadas = await grid.get_selected_rows()
                                    novo_item = Itens().model_dump()
                                    if linhas_selecionadas:                                 ## encontra linha selecionada e cria nova linha logo abaixo
                                        item_selec = linhas_selecionadas[0]

                                        try:                                            ## encontra índice da linha selecionada
                                            index_selec = next(
                                                i for i, item in enumerate(documento_ativo['itens'])
                                                if item.get('idColumn') == item_selec.get('idColumn')
                                            )
                                            ui.notify(str(index_selec))
                                        except StopIteration:
                                            index_selec = len(documento_ativo['itens']) - 1

                                        documento_ativo['itens'].insert(index_selec + 1, novo_item)     ## insere no documento logo abaixo

                                        try:                                            ## cria a nova linha na grid
                                            grid.run_grid_method('applyTransaction', {
                                                'add': [novo_item],
                                                'addIndex': index_selec + 1,
                                            })
                                            novo_id = novo_item.get('idColumn')                 ## reidentifica linha recém criada
                                            grid.run_grid_method('deselectAll')
                                            grid.run_row_method(novo_id, 'setSelected', True)   ## seleciona nova linha
                                        except Exception as e:
                                            ui.notify(f'applyTransaction falhou: {e}', type='negative')

                                    else:                                                   ## cria nova linha ao final do grid
                                        ui.notify('não há linhas_selecionadas selecionadas')
                                        # novo_item = Itens().model_dump()
                                        grid.options['rowData'].append(novo_item)
                                        documento_ativo['itens'].append(novo_item)
                                        try:                                            ## cria a nova linha na grid
                                            grid.run_grid_method('applyTransaction', {
                                                'add': [novo_item],
                                            })
                                            novo_id = novo_item.get('idColumn')                 ## reidentifica linha recém criada
                                            grid.run_grid_method('deselectAll')
                                            grid.run_row_method(novo_id, 'setSelected', True)   ## seleciona nova linha
                                        except Exception as e:
                                            ui.notify(f'applyTransaction falhou: {e}', type='negative')

                                    aviso_grid.clear()
                                    with aviso_grid:
                                        ui.label(f'item adicionado e selecionado após posição {index_selec}')

                                    salvar_documento_no_db()                                ## não precisa mais de update!!!

                                    await grid.run_row_method(item_selec, 'setSelected', True)

                                    await asyncio.sleep(0.1)
                                    last_index = len(documento_ativo['itens']) - 1
                                    grid.run_grid_method('ensureIndexVisible', last_index)              ## scroll até a nova linha
                                ui.button("Adicionar", on_click=add_row, icon='add')\
                                    .props('flat dense')\
                                    .classes('text-base')
                                async def copy_row():                                   ## Copia a linha selecionada, gera um novo ID, valida e insere abaixo da original.
                                    linhas_selecionadas = await grid.get_selected_rows()
                                    if not linhas_selecionadas:
                                        ui.notify('Selecione um item para copiar.', type='warning')
                                        return

                                    item_original = linhas_selecionadas[0]
                                    item_copiado_dict = item_original.copy()
                                    item_copiado_dict['idColumn'] = str(uuid.uuid4())
                                    item_copiado_dict['descricaoItem'] = f"Cópia de {item_original.get('descricaoItem', 'item')}"

                                    try:
                                        novo_item_validado = Itens.model_validate(item_copiado_dict).model_dump()
                                    except ValidationError as e:
                                        ui.notify(f"Erro de validação ao copiar: {e}", type='negative', multi_line=True)
                                        return

                                    try:
                                        index_original = next(
                                            i for i, item in enumerate(documento_ativo['itens'])
                                            if item.get('idColumn') == item_original.get('idColumn')
                                        )
                                    except StopIteration:
                                        index_original = len(documento_ativo['itens']) - 1

                                    index_insercao = index_original + 1
                                    documento_ativo['itens'].insert(index_insercao, novo_item_validado)

                                    try:
                                        grid.run_grid_method('applyTransaction', {
                                            'add': [novo_item_validado],
                                            'addIndex': index_insercao,
                                        })
                                        await asyncio.sleep(0.1)
                                        novo_id = novo_item_validado.get('idColumn')
                                        grid.run_grid_method('deselectAll')
                                        grid.run_row_method(novo_id, 'setSelected', True)
                                    except Exception as e:
                                        ui.notify(f'Falha ao atualizar a grade: {e}', type='negative')
                                        documento_ativo['itens'].pop(index_insercao)
                                        return

                                    salvar_documento_no_db()
                                    aviso_grid.clear()
                                    with aviso_grid:
                                        ui.label(f"Item copiado e inserido na posição {index_insercao}.")
                                ui.button("copiar", on_click=copy_row, icon='content_copy')\
                                    .props('flat dense')\
                                    .classes('text-base')
                            with ui.column():                                               ## copiar, editar
                                async def remove_selected():
                                    linhas_selecionadas = await grid.get_selected_rows()
                                    if not linhas_selecionadas:
                                        ui.notify("Selecione as linhas para remover.")
                                        return

                                    ids_para_remover = {linha['idColumn'] for linha in linhas_selecionadas}     ## 1. Obter os IDs únicos das linhas a serem removidas.

                                    itens_atuais = app.storage.general['documento_ativo']['itens']              ## 2. Atualizar o estado do servidor removendo os itens. Usar uma list comprehension é uma forma eficiente e segura de criar a nova lista.
                                    itens_filtrados = [
                                        item for item in itens_atuais
                                        if item.get('idColumn') not in ids_para_remover
                                    ]
                                    app.storage.general['documento_ativo']['itens'] = itens_filtrados

                                    grid.run_grid_method('applyTransaction', {'remove': linhas_selecionadas})       ## 3. Informar à grade do cliente para remover as linhas. A grade usará o ID de cada linha para encontrá-la e removê-la.

                                    salvar_documento_no_db()                                                    ## 4. Salvar o documento com os itens removidos.

                                    ui.notify(f'{len(linhas_selecionadas)} item(s) removido(s).', type='positive')      ## 5. Notificar o usuário do sucesso.
                                ui.button("Excluir", on_click=remove_selected, icon='remove', color='negative')\
                                    .props('flat dense')\
                                    .classes('text-base')
                                async def update_grid():
                                    # Atualiza os dados da grade com os itens mais recentes do documento ativo
                                    item_selecionado = app.storage.general.get('item_selecionado')
                                    if item_selecionado:
                                        # ui.label(str(item_selecionado))

                                        grid_is_selected = True
                                        grid.options['rowData'] = documento_ativo.get('itens', [])
                                        new_row = grid.options['rowData'][0]
                                        # grid.run_grid_method('applyTransaction', {'add': new_row})
                                        grid.update()
                                        
                                        await asyncio.sleep(0.1)
                                        # detalhes_container.update()
                                        formulario_detalhes_aberto = grid_is_selected
                                        tipo_detalhes = '1 - uma linha'
                                        atualizar_detalhes(tipo_detalhes, item_selecionado, formulario_detalhes_aberto)
                                    else:
                                        ui.label('ips, não deu')

                                    # Limpa a seleção atual e o formulário de detalhes
                                    # app.storage.general['item_selecionado'] = None
                                    
                                    # Limpa e atualiza o container de detalhes para refletir a ausência de seleção
                                    # detalhes_container.clear()
                                    # with detalhes_container:
                                    #     formulario_detalhes()  # Isso mostrará a mensagem para selecionar um item

                                    # Garante que o painel de detalhes esteja fechado
                                    # edita_card.value = False
                                    
                                    ui.notify("Grade atualizada.", type='info')
                                ui.button("Atualizar", on_click=update_grid, icon='refresh')\
                                    .props('flat dense')\
                                    .classes('text-base')
                            with ui.column():                                               ## grupos columas
                                ui.checkbox("EXIBIR GRUPOS", value=False, on_change=lambda e: toggle_column_group_visibility('grupos', e.value))\
                                    .props('dense color="primary" keep-color')\
                                    .classes('text-primary text-base font-medium mt-1.5')
                                ui.checkbox("EXIBIR ORÇAMENTO", value=False, on_change=lambda e: toggle_column_group_visibility('orçamento', e.value))\
                                    .props('dense color="primary" keep-color')\
                                    .classes('text-primary text-base font-medium mt-2.5')
                            with ui.column():                                               ## importar, exportar
                                uploader = (
                                    ui.upload(
                                        on_upload=handle_excel_import,
                                        auto_upload=True,
                                        multiple=False,
                                    )
                                    .props('accept=.xlsx,.xls')        # opcional: restringe a planilhas
                                    .style('display:none')             # oculta o card azul
                                )
                                ui.button("Importar Excel", icon='file_upload', on_click=lambda: uploader.run_method('pickFiles'))\
                                    .props('flat dense')\
                                    .classes('text-base')
                                ui.button("Exportar Excel", on_click=handle_excel_export, icon='file_download')\
                                    .props('flat dense')\
                                    .classes('text-base')
                            with ui.column().classes('w-1/4'):                              ## quadro de avisos
                                ui.space()
                                aviso_grid = ui.row().classes('w-full')

                        summary_container = ui.card().classes('w-full hidden mt-6 mb-6')

                        column_defs = [
                            # --- Item, atividade ---
                            {'headerName': 'Sel', 'headerCheckboxSelection': True, 'checkboxSelection': True, 'showDisabledCheckboxes': True},
                            {'headerName': 'Indice', 'field': 'idItem', 'width': 200},
                            {'headerName': 'Tipo', 'field': 'tipoItem', 'width': 330, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': list(get_args(get_args(Itens.model_fields['tipoItem'].annotation)[0]))}},
                            {'headerName': 'Grupo 1', 'field': 'grupo1', 'width': 350},
                            {'headerName': 'Grupo 2', 'field': 'grupo2', 'width': 350},
                            {'headerName': 'Descrição', 'field': 'descricaoItem', 'width': 200},
                            # --- 5W3H: When ---
                            {'headerName': 'Data Fim', 'field': 'dataHoraFim', 'width': 350},
                            # --- 5W3H: How Much ---
                            {'headerName': 'Total', 'field': 'valorTotal', 'type': 'numericColumn', 'valueFormatter': "params.value == null ? '' : 'R$ ' + params.value.toFixed(3)", 'width': 330},
                            {'headerName': 'Qtd', 'field': 'qtd', 'type': 'numericColumn', 'width': 80},
                            {'headerName': 'Un', 'field': 'un', 'width': 80},
                            {'headerName': 'Moeda', 'field': 'moeda', 'width': 80},
                            {'headerName': 'Preço', 'field': 'preco', 'type': 'numericColumn', 'valueFormatter': "params.value == null ? '' : 'R$ ' + params.value.toFixed(3)", 'width': 330},
                            {'headerName': 'Tipo Orçamento', 'field': 'tipoOrcamento', 'width': 350, 'cellEditor': 'agSelectCellEditor', 'cellEditorParams': {'values': list(get_args(get_args(Itens.model_fields['tipoOrcamento'].annotation)[0]))}},
                            # --- 5W3H: Who ---
                            {'headerName': 'Quem', 'field': 'quem', 'width': 350},
                            # --- Notas e Tags ---
                            {'headerName': 'Notas', 'field': 'notas', 'width': 200, 'wrapText': True, 'autoHeight': True},
                            {'headerName': 'Tags', 'field': 'tags', 'width': 200},
                            {'headerName': 'IdColumn', 'field': 'idColumn', 'width': 200},
                            {'headerName': 'Filtros', 'field': 'filtros', 'width': 350},
                        ]                                                                   ## Definições de coluna para o AG Grid, mapeando os campos do modelo Pydantic 'Itens'.
                        
                        # Define quais colunas devem começar ocultas com base no estado inicial desejado (False)
                        initial_hidden_cols = COLUMN_GROUPS['grupos'] + COLUMN_GROUPS['orçamento']
                        for col_def in column_defs:
                            if col_def.get('field') in initial_hidden_cols:
                                col_def['hide'] = True

                        # ui.label(str(documento_ativo.get('itens', [])))

                        itens_para_grid = documento_ativo.get('itens', [])
                        try:                                                                ## Validação Pydantic Corrigida. Sua ideia de validar com Pydantic aqui é excelente para depuração. A correção é iterar pela lista, pois Itens.model_validate() espera um único item, não uma lista. Validamos cada item. Isso também irá corrigir/adicionar o idColumn se ele estiver faltando, graças ao default_factory no seu modelo Pydantic.
                            itens_validados_e_corrigidos = [Itens.model_validate(item).model_dump() for item in itens_para_grid]        ## ??? ainda não entendi como é a validação
                            app.storage.general['documento_ativo']['itens'] = itens_validados_e_corrigidos          ## Se a validação passou, usamos os dados corrigidos para a grade.
                            itens_para_grid = itens_validados_e_corrigidos
                            # ui.label(str(itens_para_grid))

                        except ValidationError as e:
                            # Se a validação falhar, imprimimos um erro detalhado no terminal.
                            ui.label("\n\n==========================================================")
                            ui.label("--- ERRO DE VALIDAÇÃO PYDANTIC ANTES DE CRIAR O AG GRID ---")
                            ui.label(f"Um ou mais itens na lista 'itens' não correspondem ao modelo 'Itens'.\nErro: {e}")
                            ui.label("==========================================================\n\n")

                        async def on_cell_value_changed(e: events.GenericEventArguments):
                            modified = e.args['data']
                            row_id = modified.get('idColumn')
                            if not row_id:
                                ui.notify('Erro: item sem idColumn.', type='negative')
                                return
                            itens_list = app.storage.general['documento_ativo']['itens']
                            for i, item in enumerate(itens_list):
                                if item.get('idColumn') == row_id:
                                    itens_list[i] = modified
                                    ui.notify(f"Item '{item.get('descricaoItem', row_id)}' atualizado.", type='info')
                                    salvar_documento_no_db()
                                    break

                        async def on_grid_selection_change():
                            nonlocal formulario_detalhes_aberto, toggle_programatico
                            linhas_selecionadas = await grid.get_selected_rows()
                            tipo_detalhes = ['0', '1 - uma linha', '2 - varias linhas']

                            if len(linhas_selecionadas) == 0:
                                app.storage.general['item_selecionado'] = None
                                formulario_detalhes_aberto = False
                                tipo_detalhes = tipo_detalhes[0]
                            elif len(linhas_selecionadas) == 1:
                                id_sel = linhas_selecionadas[0].get('idColumn')
                                item_original = next(
                                    (i for i in documento_ativo['itens'] if i.get('idColumn') == id_sel),
                                    None
                                )
                                app.storage.general['item_selecionado'] = item_original
                                formulario_detalhes_aberto = True
                                tipo_detalhes = tipo_detalhes[1]
                            elif len(linhas_selecionadas) > 1:
                                # Construir "item_original" sintético com listas de valores
                                campos = set().union(*[linha.keys() for linha in linhas_selecionadas])
                                item_sintetico = {}

                                for campo in campos:
                                    valores = [linha.get(campo) for linha in linhas_selecionadas if campo in linha]
                                    # Elimina duplicados mantendo a ordem
                                    vistos = []
                                    for v in valores:
                                        if v not in vistos:
                                            vistos.append(v)
                                    # Cria string de exibição
                                    item_sintetico[campo] = ", ".join(str(v) for v in vistos if v is not None)
                                
                                # with aviso_grid:
                                #     ui.label(str(item_sintetico))

                                app.storage.general['item_selecionado'] = item_sintetico   # não faz sentido um único selecionado
                                app.storage.general['ids_selecionados'] = [linha['idColumn'] for linha in linhas_selecionadas]

                                formulario_detalhes_aberto = True
                                tipo_detalhes = tipo_detalhes[2]

                            toggle_programatico = True                                      ## trava handler manual e alterna programaticamente
                            edita_card.value = formulario_detalhes_aberto
                            toggle_programatico = False

                            item_selecionado = app.storage.general['item_selecionado']
                            # ui.notify(str(campos))

                            aviso_grid.clear()
                            with aviso_grid:
                                ui.label(len(linhas_selecionadas))
                                ui.label(tipo_detalhes)
                                # ui.label(str(item_selecionado))

                            atualizar_detalhes(tipo_detalhes, item_selecionado, formulario_detalhes_aberto)   ## (re)monta o formulário dos detalhes

                            if 'hidden' not in summary_container._classes:
                                # ui.notify(summary_container._classes)
                                await atualizar_resumo(linhas_selecionadas)

                        grid = ui.aggrid({                                              ## aggrid
                            'columnDefs': column_defs,
                            'rowData': itens_para_grid, 
                            # ':getRowId': "params.data.idColumn",
                            ':getRowId': "function(params) { return params.data.idColumn; }",
                            'defaultColDef': {
                                'editable': True, 
                                'resizable': True, 
                                'sortable': True, 
                                'filter': True,
                                'flex': None,          # impede auto ajuste
                                'minWidth': None,
                                'maxWidth': None
                                },
                            'rowSelection': 'multiple',
                            'stopEditingWhenCellsLoseFocus': True,
                            'alwaysShowHorizontalScroll': True,
                            'suppressSizeToFit': True,
                            'suppressAutoSize': True,
                            'autoSizeStrategy': {
                                'type': 'fitCellContents',
                            },
                            'domLayout': 'normal'
                        })\
                        .on('cellValueChanged', on_cell_value_changed)\
                        .on('selectionChanged', on_grid_selection_change, throttle=0.4)\
                            .classes('h-66 w-full')\
                            .props('virtual-scroll')

                    # --- DEFINIÇÃO DOS HANDLERS E FUNÇÕES AUXILIARES ---
                    # Mover as definições para antes de sua utilização garante que elas sejam encontradas.
                    
                    formulario_detalhes_aberto = False
                    toggle_programatico = False


                    async def selecionar_primeira_linha(): 
                        await asyncio.sleep(0.1)  # espera o grid renderizar
                        itens = app.storage.general['documento_ativo']['itens']
                        if itens:
                            primeiro_id = itens[0].get('idColumn')
                            segundo_id = itens[1].get('idColumn')
                            if primeiro_id:
                                await grid.run_grid_method('deselectAll')
                                await grid.run_row_method(primeiro_id, 'setSelected', True)
                                await grid.run_row_method(segundo_id, 'setSelected', True)

                    # asyncio.create_task(selecionar_primeira_linha())                    ## dispara assim que a página carregar

                    def travar_toggle_expansion(e):
                        """Controla abertura/recolhimento da expansão 'Detalhes Planejamento 02'."""
                        nonlocal toggle_programatico

                        if toggle_programatico:
                            return

                        item_sel = app.storage.general.get('item_selecionado')
                        if not item_sel:
                            # Nenhum item selecionado → sempre força fechado
                            if e.value:   # usuário tentou abrir manualmente
                                toggle_programatico = True
                                e.sender.value = False
                                toggle_programatico = False
                        else:
                            # Um ou mais selecionados → libera abrir e recolher manual
                            pass  # não forçamos nada


                    # def atualizar_detalhes(tipo_detalhes, item_selecionado, formulario_detalhes_aberto):
                    #     tipo_detalhes = tipo_detalhes[0]
                    #     detalhes_container.clear()

                    #     if tipo_detalhes == '0':
                    #         return
                    #     elif tipo_detalhes == '1':
                    #         with detalhes_container:
                    #             if not item_selecionado:
                    #                 ui.label('Selecione um item na grade para ver os detalhes.').classes('m-4 text-center text-gray-500')
                    #                 return
                    #             try:
                    #                 itens_list = app.storage.general['documento_ativo']['itens']
                    #                 item_index = itens_list.index(item_selecionado)
                    #             except ValueError:
                    #                 ui.label(f'Item selecionado {item_selecionado.items()} não encontrado. A grade pode estar dessincronizada.', type='negative')
                    #                 return
                    #             item_no_documento = documento_ativo['itens'][item_index]
                    #             with ui.expansion('Item, atividade', value=True).classes('w-full'):
                    #                 with ui.row().classes('w-full no-wrap'):
                    #                     ui.input('Indice').bind_value(item_no_documento, 'idItem').props('dense outlined').classes('w-1/4')
                    #                     ui.select(list(get_args(get_args(Itens.model_fields['tipoItem'].annotation)[0])), label='Tipo').bind_value(item_no_documento, 'tipoItem').props('dense outlined').classes('w-1/4')
                    #                     ui.input('Grupo 1').bind_value(item_no_documento, 'grupo1').props('dense outlined').classes('w-1/4')
                    #                     ui.input('Grupo 2').bind_value(item_no_documento, 'grupo2').props('dense outlined').classes('w-1/4')
                    #                 ui.input('Descrição').bind_value(item_no_documento, 'descricaoItem').props('dense outlined').classes('w-full')
                    #                 with ui.row().classes('w-full no-wrap'):
                    #                     with ui.column().classes('w-1/3'):
                    #                         ui.input('Quem').bind_value(item_no_documento, 'quem').props('dense outlined').classes('w-full')
                    #                         ui.input('Responsável').bind_value(item_no_documento, 'responsavel').props('dense outlined').classes('w-full')
                    #                         ui.input('Vendedor').bind_value(item_no_documento, 'vendedor').props('dense outlined').classes('w-full')
                    #                     with ui.column().classes('w-1/3'):
                    #                         ui.input('Data Fim').bind_value(item_no_documento, 'dataHoraFim').props('dense outlined').classes('w-full')
                    #                         ui.input('Data Inicio').bind_value(item_no_documento, 'dataHoraInicio').props('dense outlined').classes('w-full')
                    #                         ui.input('Data Criação').bind_value(item_no_documento, 'dataHoraCriacao').props('dense outlined').classes('w-full')
                    #                     with ui.column().classes('w-1/3'):
                    #                         ui.input('SKU').bind_value(item_no_documento, 'sku').props('dense outlined').classes('w-full')
                    #                 with ui.row().classes('w-full no-wrap'):
                    #                     ui.input('Título da Atividade').bind_value(item_no_documento, 'tituloAtividade').props('dense outlined').classes('w-1/2')
                    #                     ui.input('Atividade (Alt)').bind_value(item_no_documento, 'tituloAtividadeAlternativo').props('dense outlined').classes('w-1/2')
                    #                 ui.switch('Aberto')
                    #             with ui.expansion('Orçamento', value=True).classes('w-full'):
                    #                 with ui.row().classes('w-full no-wrap'):
                    #                     ui.number('Qtd').bind_value(item_no_documento, 'qtd').props('dense outlined').classes('w-1/2')
                    #                     ui.input('Un').bind_value(item_no_documento, 'un').props('dense outlined').classes('w-1/2')
                    #                     ui.number('Preço').bind_value(item_no_documento, 'preco').props('dense outlined').classes('w-1/2')
                    #                     ui.input('Moeda').bind_value(item_no_documento, 'moeda').props('dense outlined').classes('w-1/2')
                    #                     ui.number('Total').bind_value(item_no_documento, 'valorTotal').props('dense outlined').classes('w-1/2')
                    #                 with ui.row().classes('w-full no-wrap'):
                    #                     with ui.column().classes('w-1/2'):
                    #                         ui.select(list(get_args(get_args(Itens.model_fields['tipoOrcamento'].annotation)[0])), label='Tipo Orçamento').bind_value(item_no_documento, 'tipoOrcamento').props('dense outlined').classes('w-full')
                    #                     with ui.column().classes('w-1/2'):
                    #                         ui.number('peso').bind_value(item_no_documento, 'peso').props('dense outlined').classes('w-full')
                    #                         ui.number('volume').bind_value(item_no_documento, 'volume').props('dense outlined').classes('w-full')
                    #                 ui.switch('Aberto')
                    #             with ui.expansion('Notas', value=True).classes('w-full'):
                    #                 with ui.row().classes('w-full no-wrap'):
                    #                     ui.textarea('Notas').bind_value(item_no_documento, 'notas').props('dense outlined').classes('w-1/2')
                    #                     ui.input('Tags').bind_value(item_no_documento, 'tags').props('dense outlined').classes('w-1/2')
                    #                 ui.switch('Aberto')
                    #     elif tipo_detalhes == '2':
                    #         with detalhes_container:
                    #             if not item_selecionado:
                    #                 ui.label('Selecione itens na grade para ver os detalhes.').classes('m-4 text-center text-gray-500')
                    #                 return
                    #             documento_sintetico = item_selecionado
                    #             id_string = str(documento_sintetico.get('idColumn', '')).strip()
                    #             ids_alvo = [s.strip() for s in id_string.split(',')] if id_string else []
                    #             documento = app.storage.general.get('documento_ativo', {})
                    #             itens = documento.get('itens', [])
                    #             itens_por_id = {str(it.get('idColumn')).strip(): it for it in itens}

                    #             async def aplicar_alteracao(campo: str, valor_editado):
                    #                 if isinstance(valor_editado, str) or isinstance(valor_editado, list):
                    #                     partes = [p.strip() for p in valor_editado.split(',') if p.strip()]
                    #                     try:
                    #                         partes_num = [float(p) for p in partes]
                    #                         novos = partes_num if len(partes_num) > 1 else partes_num * max(1, len(ids_alvo))
                    #                     except ValueError:
                    #                         novos = partes if len(partes) > 1 else partes * max(1, len(ids_alvo))
                    #                 elif isinstance(valor_editado, (int, float)):
                    #                     novos = [valor_editado] * max(1, len(ids_alvo))
                    #                 else:
                    #                     novos = [valor_editado] * max(1, len(ids_alvo))
                    #                 if len(novos) < len(ids_alvo) and novos:
                    #                     novos += [novos[-1]] * (len(ids_alvo) - len(novos))
                    #                 elif len(novos) > len(ids_alvo):
                    #                     novos = novos[:len(ids_alvo)]
                    #                 aplicados = 0
                    #                 itens_atualizados = []
                    #                 for idx, id_ref in enumerate(ids_alvo):
                    #                     ref = str(id_ref).strip()
                    #                     itens_no_documento_ativo = itens_por_id.get(ref)
                    #                     if itens_no_documento_ativo is not None:
                    #                         itens_no_documento_ativo[campo] = novos[idx]
                    #                         itens_atualizados.append(itens_no_documento_ativo)
                    #                         aplicados += 1
                    #                 if itens_atualizados:
                    #                     await grid.run_grid_method('applyTransaction', {'update': itens_atualizados}) #                     salvar_documento_no_db()
                    #                 ui.notify(f"Campo '{campo}' distribuído em {aplicados} itens.", type='positive')

                    #             def ligar_handler_valor(comp, campo: str):
                    #                 comp.on('keydown.enter', lambda e, _c=campo, _comp=comp: aplicar_alteracao(_c, _comp.value))

                    #             with ui.expansion('Item, atividade', value=False).classes('w-full'):
                    #                 with ui.row().classes('w-full no-wrap'):
                    #                     comp = ui.input('Indice').bind_value(documento_sintetico, 'idItem').props('dense outlined').classes('w-1/4'); ligar_handler_valor(comp, 'idItem')
                    #                     comp = ui.select(list(get_args(get_args(Itens.model_fields['tipoItem'].annotation)[0])), label='Tipo').bind_value(documento_sintetico, 'tipoItem').props('dense outlined').classes('w-1/4'); ligar_handler_valor(comp, 'tipoItem')
                    #                     comp = ui.input('Grupo 1').bind_value(documento_sintetico, 'grupo1').props('dense outlined').classes('w-1/4'); ligar_handler_valor(comp, 'grupo1')
                    #                     comp = ui.input('Grupo 2').bind_value(documento_sintetico, 'grupo2').props('dense outlined').classes('w-1/4'); ligar_handler_valor(comp, 'grupo2')
                    #                 comp = ui.input('Descrição').bind_value(documento_sintetico, 'descricaoItem').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'descricaoItem')
                    #                 with ui.row().classes('w-full no-wrap'):
                    #                     with ui.column().classes('w-1/3'):
                    #                         comp = ui.input('Quem').bind_value(documento_sintetico, 'quem').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'quem')
                    #                         comp = ui.input('Responsável').bind_value(documento_sintetico, 'responsavel').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'responsavel')
                    #                         comp = ui.input('Vendedor').bind_value(documento_sintetico, 'vendedor').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'vendedor')
                    #                     with ui.column().classes('w-1/3'):
                    #                         comp = ui.input('Data Fim').bind_value(documento_sintetico, 'dataHoraFim').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'dataHoraFim')
                    #                         comp = ui.input('Data Inicio').bind_value(documento_sintetico, 'dataHoraInicio').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'dataHoraInicio')
                    #                         comp = ui.input('Data Criação').bind_value(documento_sintetico, 'dataHoraCriacao').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'dataHoraCriacao')
                    #                     with ui.column().classes('w-1/3'):
                    #                         comp = ui.input('SKU').bind_value(documento_sintetico, 'sku').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'sku')
                    #                 with ui.row().classes('w-full no-wrap'):
                    #                     comp = ui.input('Título da Atividade').bind_value(documento_sintetico, 'tituloAtividade').props('dense outlined').classes('w-1/2'); ligar

                    with ui.expansion(
                        'Detalhes Planejamento 02',
                        value=False,
                        on_value_change=travar_toggle_expansion,
                    ).classes('w-full') as edita_card:                              ## DETALHES_CONTAINER formulário de detalhes (dentro da expansão) ---
                        detalhes_container = ui.column().classes('w-full mt-4').on('cellValueChanged')

                    def atualizar_detalhes(tipo_detalhes, item_selecionado, formulario_detalhes_aberto):                                   ## item_selecionado no local de chamada de atualizar_detalhes. Reconstrói o formulário dentro do container, limpando antes.
                        # item_selecionado = app.storage.general.get('item_selecionado')
                        tipo_detalhes = tipo_detalhes[0]        ## vamos usar apenas o primeiro caractere na logica de processamento

                        # edita_card.value = formulario_detalhes_aberto
                        detalhes_container.clear()                                              ## limpa o conteúdo anterior

                        if   tipo_detalhes == '0':
                            return
                        elif tipo_detalhes == '1':
                            with detalhes_container:                                            ## tudo que for criado a partir daqui vai dentro do container
                                if not item_selecionado:
                                    ui.label('Selecione um item na grade para ver os detalhes.')\
                                    .classes('m-4 text-center text-gray-500')
                                    return

                                try:                                                            ## vincula diretamente ao documento (mesma referência)
                                    itens_list = app.storage.general['documento_ativo']['itens']
                                    item_index = itens_list.index(item_selecionado)
                                except ValueError:
                                    # ui.notify(f'Item selecionado {item_selecionado.values()} não encontrado. A grade pode estar dessincronizada.', type='negative')
                                    ui.label(f'Item selecionado {item_selecionado.items()} não encontrado. A grade pode estar dessincronizada.', type='negative')
                                    return

                                item_no_documento = documento_ativo['itens'][item_index]

                                with ui.expansion('Item, atividade', value=True).classes('w-full'):     ## --- Item, Atividade ---
                                    with ui.row().classes('w-full no-wrap'): 
                                        ui.input('Indice').bind_value(item_no_documento, 'idItem').props('dense outlined').classes('w-1/4')
                                        ui.select(
                                            list(get_args(get_args(Itens.model_fields['tipoItem'].annotation)[0])),
                                            label='Tipo'
                                        ).bind_value(item_no_documento, 'tipoItem').props('dense outlined').classes('w-1/4')
                                        ui.input('Grupo 1').bind_value(item_no_documento, 'grupo1').props('dense outlined').classes('w-1/4')
                                        ui.input('Grupo 2').bind_value(item_no_documento, 'grupo2').props('dense outlined').classes('w-1/4')
                                    ui.input('Descrição').bind_value(item_no_documento, 'descricaoItem').props('dense outlined').classes('w-full')
                                    with ui.row().classes('w-full no-wrap'):                        ## quem, quando, cadastro
                                        with ui.column().classes('w-1/3'):                          ## quem
                                            ui.input('Quem').bind_value(item_no_documento, 'quem').props('dense outlined').classes('w-full')
                                            ui.input('Responsável').bind_value(item_no_documento, 'responsavel').props('dense outlined').classes('w-full')
                                            ui.input('Vendedor').bind_value(item_no_documento, 'vendedor').props('dense outlined').classes('w-full')
                                            # ui.space()
                                        with ui.column().classes('w-1/3'):                          ## quando
                                            ui.input('Data Fim').bind_value(item_no_documento, 'dataHoraFim').props('dense outlined').classes('w-full')
                                            ui.input('Data Inicio').bind_value(item_no_documento, 'dataHoraInicio').props('dense outlined').classes('w-full')
                                            ui.input('Data Criação').bind_value(item_no_documento, 'dataHoraCriacao').props('dense outlined').classes('w-full')
                                        with ui.column().classes('w-1/3'):                          ## cadastro
                                            ui.input('SKU').bind_value(item_no_documento, 'sku').props('dense outlined').classes('w-full')
                                    with ui.row().classes('w-full no-wrap'):                        ## tituloAtividade
                                        ui.input('Título da Atividade').bind_value(item_no_documento, 'tituloAtividade').props('dense outlined').classes('w-1/2')
                                        ui.input('Atividade (Alt)').bind_value(item_no_documento, 'tituloAtividadeAlternativo').props('dense outlined').classes('w-1/2')
                                    ui.switch('Aberto')
                                with ui.expansion('Orçamento', value=True).classes('w-full'):          ## --- Orçamento ---
                                    with ui.row().classes('w-full no-wrap'):
                                        ui.number('Qtd').bind_value(item_no_documento, 'qtd').props('dense outlined').classes('w-1/2')
                                        ui.input('Un').bind_value(item_no_documento, 'un').props('dense outlined').classes('w-1/2')
                                        ui.number('Preço').bind_value(item_no_documento, 'preco').props('dense outlined').classes('w-1/2')
                                        ui.input('Moeda').bind_value(item_no_documento, 'moeda').props('dense outlined').classes('w-1/2')
                                        ui.number('Total').bind_value(item_no_documento, 'valorTotal').props('dense outlined').classes('w-1/2')
                                    with ui.row().classes('w-full no-wrap'):                            ## tipo orçamento, peso, volume
                                        with ui.column().classes('w-1/2'):
                                            ui.select(
                                                list(get_args(get_args(Itens.model_fields['tipoOrcamento'].annotation)[0])),
                                                label='Tipo Orçamento'
                                            ).bind_value(item_no_documento, 'tipoOrcamento').props('dense outlined').classes('w-full')
                                        with ui.column().classes('w-1/2'):
                                            ui.number('peso').bind_value(item_no_documento, 'peso').props('dense outlined').classes('w-full')
                                            ui.number('volume').bind_value(item_no_documento, 'volume').props('dense outlined').classes('w-full')
                                    ui.switch('Aberto')
                                with ui.expansion('Notas', value=True).classes('w-full'):              ## --- Notas e Tags ---
                                    with ui.row().classes('w-full no-wrap'):
                                        ui.textarea('Notas').bind_value(item_no_documento, 'notas').props('dense outlined').classes('w-1/2')
                                        ui.input('Tags').bind_value(item_no_documento, 'tags').props('dense outlined').classes('w-1/2')
                                    ui.switch('Aberto')
                        elif tipo_detalhes == '2':
                            with detalhes_container:
                                if not item_selecionado:
                                    ui.label('Selecione itens na grade para ver os detalhes.')\
                                        .classes('m-4 text-center text-gray-500')
                                    return
                                # else:       ## estava perdido mais abaixo
                                #     ui.label("Crie um novo documento ou abra um existente na barra lateral para começar.").classes('m-4 text-xl')

                                documento_sintetico = item_selecionado                      ## documento_sintetico, objeto com todas as linhas selecionadas
                                id_string = str(documento_sintetico.get('idColumn', '')).strip()
                                ids_alvo = [s.strip() for s in id_string.split(',')] if id_string else []       ## ids_alvo, lista dos idColumn selecionados

                                documento = app.storage.general.get('documento_ativo', {})
                                itens = documento.get('itens', [])
                                itens_por_id = {str(it.get('idColumn')).strip(): it for it in itens}

                                # async def aplicar_alteracao(campo: str, valor_editado):
                                    #     if isinstance(valor_editado, list):
                                    #         novos = valor_editado
                                    #     # elif isinstance(valor_editado, str):
                                    #     #     partes = [p.strip() for p in valor_editado.split(',')]
                                    #     #     novos = partes if len(partes) > 1 else partes * len(ids_alvo)
                                    #     # else:
                                    #     #     novos = [valor_editado] * max(1, len(ids_alvo))

                                    #     elif isinstance(valor_editado, (int, float)):
                                    #         novos = [valor_editado] * max(1, len(ids_alvo))
                                    #     elif isinstance(valor_editado, str):
                                    #         partes = [p.strip() for p in valor_editado.split(',')]
                                    #         novos = partes if len(partes) > 1 else partes * len(ids_alvo)
                                    #     else:
                                    #         novos = [str(valor_editado)] * max(1, len(ids_alvo))


                                    #     if len(novos) < len(ids_alvo) and novos:
                                    #         novos += [novos[-1]] * (len(ids_alvo) - len(novos))
                                    #     elif len(novos) > len(ids_alvo):
                                    #         novos = novos[:len(ids_alvo)]

                                    #     aplicados = 0
                                    #     itens_atualizados = []
                                    #     for idx, id_ref in enumerate(ids_alvo):
                                    #         ref = str(id_ref).strip()
                                    #         it = itens_por_id.get(ref)
                                    #         if it is not None:
                                    #             it[campo] = novos[idx]
                                    #             itens_atualizados.append(it)
                                    #             aplicados += 1

                                    #     documento_sintetico[campo] = novos
                                    #     if itens_atualizados:
                                    #         await grid.run_grid_method('applyTransaction', {'update': itens_atualizados})
                                    #     salvar_documento_atual()
                                    #     ui.notify(f"Campo '{campo}' distribuído em {aplicados} itens.", type='positive')

                                    # async def aplicar_alteracao(campo: str, valor_editado):
                                    #     # normaliza para lista de valores
                                    #     if isinstance(valor_editado, list):
                                    #         novos = valor_editado
                                    #     elif isinstance(valor_editado, (int, float)):
                                    #         novos = [valor_editado] * max(1, len(ids_alvo))
                                    #     elif isinstance(valor_editado, str):
                                    #         partes = [p.strip() for p in valor_editado.split(',') if p.strip()]
                                    #         try:
                                    #             # tenta converter para número se campo for numérico
                                    #             partes_num = [float(p) for p in partes]
                                    #             novos = partes_num if len(partes_num) > 1 else partes_num * max(1, len(ids_alvo))
                                    #         except ValueError:
                                    #             novos = partes if len(partes) > 1 else partes * max(1, len(ids_alvo))
                                    #     else:
                                    #         novos = [valor_editado] * max(1, len(ids_alvo))

                                    #     # Ajusta tamanho da lista
                                    #     if len(novos) < len(ids_alvo) and novos:
                                    #         novos += [novos[-1]] * (len(ids_alvo) - len(novos))
                                    #     elif len(novos) > len(ids_alvo):
                                    #         novos = novos[:len(ids_alvo)]

                                    #     aplicados = 0
                                    #     itens_atualizados = []
                                    #     for idx, id_ref in enumerate(ids_alvo):
                                    #         ref = str(id_ref).strip()
                                    #         it = itens_por_id.get(ref)
                                    #         if it is not None:
                                    #             # se for campo numérico com lista, guarda em *_List
                                    #             if campo in ['qtd', 'preco', 'valorTotal']:
                                    #                 it[f"{campo}List"] = novos
                                    #             else:
                                    #                 it[campo] = novos[idx]
                                    #             itens_atualizados.append(it)
                                    #             aplicados += 1

                                    #     # Atualiza também o item sintético
                                    #     if campo in ['qtd', 'preco', 'valorTotal']:
                                    #         documento_sintetico[f"{campo}List"] = novos
                                    #     else:
                                    #         documento_sintetico[campo] = novos

                                    #     if itens_atualizados:
                                    #         await grid.run_grid_method('applyTransaction', {'update': itens_atualizados})
                                    #     salvar_documento_atual()
                                    #     ui.notify(f"Campo '{campo}' distribuído em {aplicados} itens.", type='positive')

                                async def aplicar_alteracao(campo: str, valor_editado):
                                    # normaliza para lista de valores
                                    if isinstance(valor_editado, str) or isinstance(valor_editado, list):
                                        partes = [p.strip() for p in valor_editado.split(',') if p.strip()]
                                        try:
                                            partes_num = [float(p) for p in partes]
                                            novos = partes_num if len(partes_num) > 1 else partes_num * max(1, len(ids_alvo))
                                        except ValueError:
                                            novos = partes if len(partes) > 1 else partes * max(1, len(ids_alvo))
                                    elif isinstance(valor_editado, (int, float)):
                                        novos = [valor_editado] * max(1, len(ids_alvo))
                                    # elif isinstance(valor_editado, list):
                                    #     novos = valor_editado
                                    else:
                                        novos = [valor_editado] * max(1, len(ids_alvo))

                                    # Ajusta tamanho
                                    if len(novos) < len(ids_alvo) and novos:
                                        novos += [novos[-1]] * (len(ids_alvo) - len(novos))
                                    elif len(novos) > len(ids_alvo):
                                        novos = novos[:len(ids_alvo)]

                                    aplicados = 0
                                    itens_atualizados = []
                                    for idx, id_ref in enumerate(ids_alvo):                         ## ids_alvo: lista de IDs (como strings) das linhas selecionadas (os “itens reais” que você vai afetar). enumerate(ids_alvo): dá o par (idx, id_ref); o idx é usado para pegar o valor correspondente em novos[idx].
                                        ref = str(id_ref).strip()
                                        itens_no_documento_ativo = itens_por_id.get(ref)            ## itens_por_id: é um dicionário id -> item que aponta para os mesmos dicionários que estão em documento['itens'] (não são cópias). Logo, itens_no_documento_ativo[campo] = ... altera o item dentro da lista original.
                                        if itens_no_documento_ativo is not None:                    ## sempre salva o valor único em cada item real
                                            itens_no_documento_ativo[campo] = novos[idx]            ## itens_no_documento_ativo[campo] = novos[idx]: aplica, para cada item real, o valor individual correspondente.
                                            itens_atualizados.append(itens_no_documento_ativo)      ## itens_atualizados.append(itens_no_documento_ativo): guarda a referência do item alterado para mandar ao grid (com applyTransaction).
                                            aplicados += 1                                          ## aplicados += 1: contador para feedback.


                                    # PAUSED Atualiza o item sintético (único que tem *_List)
                                        # ui.notify('vamos ao list!!!!!!')
                                        # if campo in ['qtd', 'preco', 'valorTotal']:
                                        #     documento_sintetico[f"{campo}List"] = novos
                                        # else:
                                        #     documento_sintetico[campo] = novos

                                    if itens_atualizados:
                                        await grid.run_grid_method('applyTransaction', {'update': itens_atualizados})
                                    salvar_documento_no_db()
                                    ui.notify(f"Campo '{campo}' distribuído em {aplicados} itens.", type='positive')

                                def ligar_handler_valor(comp, campo: str):
                                    comp.on('keydown.enter', lambda e, _c=campo, _comp=comp: aplicar_alteracao(_c, _comp.value))

                                with ui.expansion('Item, atividade', value=False).classes('w-full'):        ## --- Item, atividade ---
                                    with ui.row().classes('w-full no-wrap'):        ## item
                                        comp = ui.input('Indice').bind_value(documento_sintetico, 'idItem').props('dense outlined').classes('w-1/4'); ligar_handler_valor(comp, 'idItem')
                                        comp = ui.select(list(get_args(get_args(Itens.model_fields['tipoItem'].annotation)[0])), label='Tipo').bind_value(documento_sintetico, 'tipoItem').props('dense outlined').classes('w-1/4'); ligar_handler_valor(comp, 'tipoItem')
                                        comp = ui.input('Grupo 1').bind_value(documento_sintetico, 'grupo1').props('dense outlined').classes('w-1/4'); ligar_handler_valor(comp, 'grupo1')
                                        comp = ui.input('Grupo 2').bind_value(documento_sintetico, 'grupo2').props('dense outlined').classes('w-1/4'); ligar_handler_valor(comp, 'grupo2')
                                    comp = ui.input('Descrição').bind_value(documento_sintetico, 'descricaoItem').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'descricaoItem')
                                    with ui.row().classes('w-full no-wrap'):        ## quem, dateTime, cadastro
                                        with ui.column().classes('w-1/3'):
                                            comp = ui.input('Quem').bind_value(documento_sintetico, 'quem').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'quem')
                                            comp = ui.input('Responsável').bind_value(documento_sintetico, 'responsavel').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'responsavel')
                                            comp = ui.input('Vendedor').bind_value(documento_sintetico, 'vendedor').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'vendedor')
                                        with ui.column().classes('w-1/3'):
                                            comp = ui.input('Data Fim').bind_value(documento_sintetico, 'dataHoraFim').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'dataHoraFim')
                                            comp = ui.input('Data Inicio').bind_value(documento_sintetico, 'dataHoraInicio').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'dataHoraInicio')
                                            comp = ui.input('Data Criação').bind_value(documento_sintetico, 'dataHoraCriacao').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'dataHoraCriacao')
                                        with ui.column().classes('w-1/3'):
                                            comp = ui.input('SKU').bind_value(documento_sintetico, 'sku').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'sku')
                                    with ui.row().classes('w-full no-wrap'):        ## atividade??
                                        comp = ui.input('Título da Atividade').bind_value(documento_sintetico, 'tituloAtividade').props('dense outlined').classes('w-1/2'); ligar_handler_valor(comp, 'tituloAtividade')
                                        comp = ui.input('Atividade (Alt)').bind_value(documento_sintetico, 'tituloAtividadeAlternativo').props('dense outlined').classes('w-1/2'); ligar_handler_valor(comp, 'tituloAtividadeAlternativo')
                                    ui.switch('Aberto')
                                with ui.expansion('Orçamento', value=True).classes('w-full'):               ## --- Orçamento ---
                                    # ui.label(str(documento_sintetico))
                                    with ui.row().classes('w-full no-wrap'):
                                        # comp = ui.input('Qtd')\
                                            #     .bind_value(
                                            #         documento_sintetico, 'qtdList',
                                            #         # Mostra SEMPRE os valores atuais dos itens selecionados
                                            #         forward=lambda _v, _ids=ids_alvo, _map=itens_por_id: ', '.join(
                                            #             [
                                            #                 '' if _map.get(str(i).strip()) is None
                                            #                 else ('' if _map[str(i).strip()].get('qtd') in (None, '') else str(_map[str(i).strip()].get('qtd')))
                                            #                 for i in _ids
                                            #             ]
                                            #         ),
                                            #         # Converte texto digitado de volta para lista de floats (para o item sintético)
                                            #         backward=lambda s: [float(x) for x in s.split(',') if x.strip()],
                                            #     ).props('dense outlined').classes('w-1/5')

                                        comp = ui.input('Qtd')\
                                            .bind_value(
                                                documento_sintetico, 'qtd',
                                                # forward=lambda v: ', '.join(map(str, v)) if isinstance(v, list) else '',
                                                # backward=lambda v: [float(x) for x in v.split(',') if x.strip()],
                                            ).props('dense outlined').classes('w-1/5')
                                        ligar_handler_valor(comp, 'qtd')
                                        comp = ui.input('Un')\
                                            .bind_value(documento_sintetico, 'un')\
                                            .props('dense outlined').classes('w-1/5')
                                        ligar_handler_valor(comp, 'un')
                                        comp = ui.input('Preço')\
                                            .bind_value(
                                                documento_sintetico, 'preco',
                                                # forward=lambda v: ', '.join(map(str, v)) if isinstance(v, list) else '',
                                                # backward=lambda v: [float(x) for x in v.split(',') if x.strip()],
                                            ).props('dense outlined').classes('w-1/5')
                                        ligar_handler_valor(comp, 'preco')
                                        comp = ui.input('Moeda')\
                                            .bind_value(documento_sintetico, 'moeda')\
                                            .props('dense outlined').classes('w-1/5')
                                        ligar_handler_valor(comp, 'moeda')
                                        comp = ui.input('Total')\
                                            .bind_value(
                                                documento_sintetico, 'valorTotalList',
                                                # forward=lambda v: ', '.join(map(str, v)) if isinstance(v, list) else '',
                                                # backward=lambda v: [float(x) for x in v.split(',') if x.strip()],
                                            ).props('dense outlined').classes('w-1/5')
                                        ligar_handler_valor(comp, 'valorTotal')
                                    with ui.row().classes('w-full no-wrap'):                         ## tipoOrçamento, ...
                                        with ui.column().classes('w-1/2'):
                                            comp = ui.select(list(get_args(get_args(Itens.model_fields['tipoOrcamento'].annotation)[0])), label='Tipo Orçamento').bind_value(documento_sintetico, 'tipoOrcamento').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'tipoOrcamento')
                                        with ui.column().classes('w-1/2'):
                                            comp = ui.input('peso').bind_value(documento_sintetico, 'peso').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'peso')
                                            comp = ui.input('volume').bind_value(documento_sintetico, 'volume').props('dense outlined').classes('w-full'); ligar_handler_valor(comp, 'volume')
                                    ui.switch('Aberto')
                                with ui.expansion('Notas', value=True).classes('w-full'):                   ## --- Notas ---
                                    with ui.row().classes('w-full no-wrap'):
                                        comp = ui.textarea('Notas').bind_value(documento_sintetico, 'notas').props('dense outlined').classes('w-1/2'); ligar_handler_valor(comp, 'notas')
                                        comp = ui.input('Tags').bind_value(documento_sintetico, 'tags').props('dense outlined').classes('w-1/2'); ligar_handler_valor(comp, 'tags')
                                    ui.switch('Aberto')

                    # with ui.row().classes('w-full justify-end'):
                    ui.switch('Aberto')\
                        .classes('w-full justify-end')\
                        .bind_value(documento_ativo['metadados'], 'stFoldingStatusPlanejamento02')

            with ui.card().classes('w-full'):                                               ## --- Seção Histórico ---
                with ui.expansion(
                    'Histórico',
                    value=documento_ativo["metadados"].get("stFoldingStatusHistorico", False)
                    )\
                    .classes("w-full"):
                    # with expansion.add_slot('header'):
                    #     ui.icon('history', color='primary')
                    #     ui.label("Histórico")
                    with ui.tabs() as tabs:
                        ui.tab('Docs').props('no-caps')
                        ui.tab('Logs').props('no-caps')
                        ui.tab('Msgs').props('no-caps')
                    # with ui.card_section():
                    #         ui.textarea("Árvore de Documentos").props('autogrow').bind_value(documento_ativo, 'historicoDocTree')
                    with ui.tab_panels(tabs, value='Docs').classes('w-full'):
                        with ui.tab_panel('Docs'):
                            ui.textarea("arvore de documentos").props('autogrow').bind_value(documento_ativo, 'notas')
                        with ui.tab_panel('Logs'):
                            ui.textarea("Índice logs (JSON)").props('autogrow').bind_value(documento_ativo, 'indice', forward=lambda v: json.dumps(v, indent=2), backward=lambda v: json.loads(v or '{}'))
                        with ui.tab_panel('Msgs'):
                            ui.textarea("Mensagens (JSON)").props('autogrow').bind_value(documento_ativo, 'pessoas', forward=lambda v: json.dumps(v, indent=2), backward=lambda v: json.loads(v or '{}'))
                    with ui.row().classes('w-full justify-end'):
                        ui.switch('Aberto')\
                            .bind_value(documento_ativo['metadados'], 'stFoldingStatusHistorico')

            with ui.card().classes('w-full'):                                               ## --- Seção Relacionamentos ---
                with ui.expansion(
                    'Relacionamentos',
                    value=documento_ativo["metadados"].get("stFoldingStatusRelacionamentos", False)
                    )\
                    .classes("w-full"):
                    # with expansion.add_slot('header'):
                    #     ui.icon('people', color='primary')
                    #     ui.label("Relacionamentos")
                    with ui.card_section().classes('w-full'):
                        with ui.row().classes('w-full no-wrap'):

                            ui.tree([
                                {'id': 'numbers', 'children': [{'id': '1'}, {'id': '2'}]},
                                {'id': 'letters', 'children': [{'id': 'A'}, {'id': 'B'}]},
                            ], label_key='id', on_select=lambda e: ui.notify(e.value))

                            ui.textarea("Como Anfitrião")\
                                .bind_value(documento_ativo, "relacionamentos_como_anfitriao")\
                                .props("autogrow; dense outlined")\
                                .classes("w-1/2")
                            ui.textarea("Como Convidado")\
                                .bind_value(documento_ativo, "relacionamentos_como_convidado")\
                                .props("autogrow; dense outlined")\
                                .classes("w-1/2")
                        with ui.row().classes('w-full justify-end'):
                            ui.switch('Aberto')\
                                .bind_value(documento_ativo['metadados'], 'stFoldingStatusRelacionamentos')

    else:
        ui.label("Crie um novo documento ou abra um existente na barra lateral para começar.").classes('m-4 text-xl')

# --- Ponto de Entrada da UI ---
# Registra a função que constrói a interface do usuário para a rota raiz.
# Isso garante que a UI só seja construída quando um cliente se conecta.
ui.page('/')(setup_ui)

# --- Application Lifecycle Events ---
# Initialize the application state when the server starts up.
app.on_startup(inicializar_estado)

# Save the application's general state when the server shuts down.
app.on_shutdown(salvar_estado_no_db)
