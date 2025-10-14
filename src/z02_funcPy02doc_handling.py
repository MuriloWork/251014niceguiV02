
import win32api, win32con, win32file
import os, shutil, io                                                                                                       ## Importa o módulo os para interações com o sistema de arquivos, Import the io module for StringIO
import logging                                                                                                          ## Importa o módulo logging para logar informações e erros
import datetime, time                                                                                                   ## Importa o módulo time para formatação de datas
import tkinter as tk
from tkinter import filedialog
import csv, json, hashlib

logging.basicConfig(level=logging.INFO)                                                                                 ## Configura o logger
_log = logging.getLogger(__name__)


def open_file(file):                                                                                                  ## i/o functions, files, screen
    ## de  : file: [json, txt], python: [str, dict]
    ## para: [str, dict]
    json_data = json.loads(open(file, encoding='utf-8').read())
    return json_data

def out_file(mov, var_in, file_out):
    ## mov: save, copy
    ## var_in: file: [json, txt], python: [str, dict]
    ## file_out: file: [json, txt]
    file_out_type = file_out[file_out.rfind(".")+1:]

    if  isinstance(var_in, dict) or isinstance(var_in, list):
        var_in_type = 'dict'
    elif isinstance(var_in, str):
        var_in_type = var_in[var_in.rfind(".")+1:]
        if var_in_type != 'json' and var_in_type != 'txt':
            var_in_type = 'str'

    if   mov == 'save' and var_in_type == 'dict':
        with open(file_out, "w", encoding= 'utf-8') as f:
            f.write(json.dumps(var_in, ensure_ascii=False, indent=3))
    elif mov == 'save' and var_in_type == 'str':
        # var_in = var_in.encode('utf-8')
        with open(file_out, "w") as f:
            f.write(var_in)
    elif mov == 'copy' and var_in_type == 'json':
        shutil.copy(var_in, file_out)
    else:
        print('verificar arquivos solicitados')

def out_screen(screenData, dataType):
    if dataType == 'json':
        print(json.dumps(screenData, indent=3))
    elif dataType == 'str':
        print(screenData)

def extract_directory_metadata_to_json(directory_path):
    """ Extrai metadados de todos os arquivos e diretórios em um caminho especificado
        e retorna o resultado em formato JSON.

        Args:
            directory_path (str): O caminho do diretório a ser explorado.

        Returns:
            tuple: A first element is a JSON string containing a list of dictionaries with the metadata.
                   A second element is a CSV string containing the metadata.
        """
    all_metadata = []                                                                                                   ## Keep this for JSON output
    csv_header = [
        'GlobalFileId',
        'VolumeSerialNumber', 
        'FileId', 
        'Type', 
        'Path', 
        'Name', 
        'Size', 
        'CreationTime', 
        'LastWriteTime', 
        'LastAccessTime', 
        'Attributes',
        'FileHash'
    ]
    csv_rows = [csv_header]                                                                                             ## Initialize CSV data with header

    processed_paths = set()                                                                                             ## Use a set to track processed paths and avoid duplicates
    if not os.path.isdir(directory_path):                                                                               ## Verifica se o diretório existe
        _log.error(f"Erro: O diretório '{directory_path}' não existe ou não é um diretório válido.")
        return json.dumps([]), ""                                                                                       ## Return empty JSON and empty CSV string

    def get_file_metadata(path):
        """ Extrai metadados de um arquivo ou diretório usando pywin32.
            Args:
                path (str): O caminho completo do arquivo ou diretório.

            Returns:
                dict: Um dicionário contendo os metadados do arquivo/diretório,
                    ou None se houver um erro ao acessar o item.
            """
        try:
            handle = win32file.CreateFile(                                                                              ## Obter o handle do arquivo/diretório para acessar metadados avançados
                path,
                0,                                                                                                      ## Não precisamos de acesso para leitura/escrita, apenas para obter informações
                win32file.FILE_SHARE_READ | win32file.FILE_SHARE_WRITE | win32file.FILE_SHARE_DELETE,
                None,
                win32file.OPEN_EXISTING,
                win32file.FILE_FLAG_BACKUP_SEMANTICS,                                                                   ## FILE_FLAG_BACKUP_SEMANTICS é necessário para abrir diretórios com CreateFile e FILE_ATTRIBUTE_NORMAL para arquivos comuns.
                None
            )

            info = win32file.GetFileInformationByHandle(handle)                                                         ## Obter as informações estendidas do arquivo
            win32file.CloseHandle(handle)                                                                               ## Fechar o handle após obter as informações

            attributes_map = {                                                                                          ## Mapeamento de atributos de arquivo para nomes legíveis
                win32con.FILE_ATTRIBUTE_ARCHIVE: "Archive",
                win32con.FILE_ATTRIBUTE_COMPRESSED: "Compressed",
                win32con.FILE_ATTRIBUTE_DIRECTORY: "Directory",
                win32con.FILE_ATTRIBUTE_ENCRYPTED: "Encrypted",
                win32con.FILE_ATTRIBUTE_HIDDEN: "Hidden",
                win32con.FILE_ATTRIBUTE_NORMAL: "Normal",
                win32con.FILE_ATTRIBUTE_OFFLINE: "Offline",
                win32con.FILE_ATTRIBUTE_READONLY: "ReadOnly",
                win32con.FILE_ATTRIBUTE_REPARSE_POINT: "ReparsePoint",
                win32con.FILE_ATTRIBUTE_SPARSE_FILE: "SparseFile",
                win32con.FILE_ATTRIBUTE_SYSTEM: "System",
                win32con.FILE_ATTRIBUTE_TEMPORARY: "Temporary"
            }
            
            attributes = []                                                                                             ## Obter os atributos como uma lista de strings
            for attr_value, attr_name in attributes_map.items():
                if info[0] & attr_value:                                                                                ## dwFileAttributes is at index 0 of file_info tuple
                    attributes.append(attr_name)

            is_directory = bool(info[0] & win32con.FILE_ATTRIBUTE_DIRECTORY)                                            ## Verificar se é um diretório para o tipo. dwFileAttributes is at index 0
            item_type = "Directory" if is_directory else "File"

            creation_time = info[1]                                                                                     ## info[1] é ftCreationTime   ## Os campos de tempo da tupla 'info' já são objetos PyTime (compatíveis com datetime.datetime)
            last_access_time = info[2]                                                                                  ## info[2] é ftLastAccessTime
            last_write_time = info[3]                                                                                   ## info[3] é ftLastWriteTime

            date_format = "%Y-%m-%d %H:%M:%S"                                                                           ## Formatar as datas para um formato legível
            file_size = (info[5] << 32) | info[6]                                                                       ## nFileSizeHigh está no índice 5, nFileSizeLow no índice 6. Para arquivos, o tamanho é (nFileSizeHigh * 2**32) + nFileSizeLow. Para diretórios, é 0.
            
            volume_serial_number = info[4]                                                                              ## dwVolumeSerialNumber está no índice 4 da tupla 'info'. Isto é mais eficiente do que chamar GetVolumeInformation novamente.
            file_id_high = info[8]                                                                                      ## O File ID é composto por nFileIndexHigh e nFileIndexLow (índices 8 e 9 de 'info')
            file_id_low = info[9]                                                                                       ## Combinar as duas partes para formar o ID de 64 bits e converter para hexadecimal
            file_id_combined = hex((file_id_high << 32) | file_id_low)                                                  ## string hexadecimal
            global_file_id = f"{str(volume_serial_number)}-{file_id_combined}"
            file_hash = ""
            if not is_directory:                                                                                        ## extrai hash
                try:
                    with open(path, 'rb') as f:
                        bytes_content = f.read()
                        file_hash = hashlib.sha256(bytes_content).hexdigest()
                except (IOError, PermissionError) as e:
                    _log.warning(f"Não foi possível ler o conteúdo do arquivo para hash {path}: {e}")
                    file_hash = "Erro ao calcular hash"

            return {
                "GlobalFileId": global_file_id,                  ## Can contain None
                "VolumeSerialNumber": volume_serial_number, 
                "FileId": file_id_combined,
                "Type": item_type,
                "Path": path.replace('\\', '/'),
                "Name": os.path.basename(path),
                "Size": file_size if not is_directory else 0,                                                           ## Tamanho é 0 para diretórios
                "CreationTime": creation_time.strftime(date_format),
                "LastWriteTime": last_write_time.strftime(date_format),
                "LastAccessTime": last_access_time.strftime(date_format),
                "Attributes": attributes,
                "FileHash": file_hash
            }
        except Exception as e:
            _log.error(f"Erro ao obter metadados para {path}: {e}")
            return None

    start_time_walk = time.time()
    i = 0
    for root, dirs, files in os.walk(directory_path, topdown=True):
        items_to_process = [root] + [os.path.join(root, f) for f in files] + [os.path.join(root, d) for d in dirs]      ## Processa o diretório raiz e todos os arquivos/subdiretórios, usando um set para evitar duplicatas.
        i = i + 1
        # print( str(len(items_to_process)) + ' items')

        start_time_item = time.time()
        for item_path in items_to_process:
            abs_path = os.path.abspath(item_path)
            if abs_path not in processed_paths:
                metadata = get_file_metadata(item_path)
                if metadata:
                    csv_ready_metadata = metadata.copy()                                                                ## Prepara os dados para o CSV (converte a lista de atributos para string)
                    csv_ready_metadata['Attributes'] = ', '.join(metadata.get('Attributes', []))
                    
                    csv_row = [csv_ready_metadata.get(key, '') for key in csv_header]
                    csv_rows.append(csv_row)
                    
                    all_metadata.append(metadata)
                    processed_paths.add(abs_path)
        end_time_item = time.time()
        _log.info(f"Iteração {i} de {str(len(items_to_process))} itens: {end_time_item - start_time_item:.2f} segundos.")

    print(i)
    # print(csv_rows)
    end_time_walk = time.time()
    _log.info(f"Iteração e coleta de metadados concluída em: {end_time_walk - start_time_walk:.2f} segundos.")
    
    json_output = json.dumps(all_metadata, indent=4, ensure_ascii=False)                                                ## Convert collected data to JSON string

    csv_output_buffer = io.StringIO()                                                                                   ## Convert collected data to CSV string
    csv_writer = csv.writer(csv_output_buffer)
    csv_writer.writerows(csv_rows)
    csv_output = csv_output_buffer.getvalue()

    return csv_output, json_output                                                                                      ## Return both JSON and CSV strings

def open_file_dialog(initial_dir: str = None, title: str = "Selecione um arquivo", file_types=(("Todos os arquivos", "*.*"),)):
    """
    Abre uma caixa de diálogo nativa para selecionar um arquivo.
    Retorna o caminho do arquivo selecionado ou None se cancelado.
    """
    root = tk.Tk()
    root.withdraw()  # Esconde a janela raiz do Tkinter
    root.attributes('-topmost', True)  # Garante que o diálogo apareça na frente

    if not initial_dir or not os.path.isdir(initial_dir):
        initial_dir = os.path.expanduser("~")

    filepath = filedialog.askopenfilename(
        initialdir=initial_dir,
        title=title,
        filetypes=file_types
    )
    root.destroy()
    return filepath if filepath else None

def listar_documentos_md(diretorio_base, recursive=False):
    """
        Lista todos os arquivos .md em um diretório e seus subdiretórios,
        ou apenas no diretório raiz (se recursive=False).
        Inclui metadados básicos.
    """
    documentos_md_selecionados = []
    try:
        if not os.path.isdir(diretorio_base):
            _log.error(f"Erro: O diretório base '{diretorio_base}' não foi encontrado ou não é um diretório.")
            return documentos_md_selecionados

        if recursive:
            for root, _, files in os.walk(diretorio_base):
                for filename in files:
                    if filename.lower().endswith('.md'):
                        filepath = os.path.join(diretorio_base, filename)
                        try:
                            stat_info = os.stat(filepath)
                            metadados = {
                                'tamanho_bytes': stat_info.st_size,
                                'data_modificacao': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_mtime)),
                                'data_criacao': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_ctime))
                            }
                            documentos_md_selecionados.append({
                                'path': filepath,
                                'nome_arquivo': filename,
                                'metadados': metadados
                            })
                        except Exception as e:
                            _log.error(f"Erro ao obter metadados para {filepath}: {e}")
        else:
            for filename in os.listdir(diretorio_base):
                if filename.lower().endswith('.md'):
                    filepath = os.path.join(diretorio_base, filename)
                    try:
                        stat_info = os.stat(filepath)
                        metadados = {
                            'tamanho_bytes': stat_info.st_size,
                            'data_modificacao': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_mtime)),
                            'data_criacao': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(stat_info.st_ctime))
                        }
                        documentos_md_selecionados.append({
                            'path': filepath,
                            'nome_arquivo': filename,
                            'metadados': metadados
                        })
                    except Exception as e:
                        _log.error(f"Erro ao obter metadados para {filepath}: {e}")
        _log.info(f"Encontrados {len(documentos_md_selecionados)} arquivos .md em '{diretorio_base}'.")
    except Exception as e:
        _log.error(f"Ocorreu um erro ao listar arquivos: {e}")
    return documentos_md_selecionados

def exibe_grid(base):
    ""
