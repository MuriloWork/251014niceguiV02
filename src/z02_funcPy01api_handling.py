
from google.auth.transport.requests import Request                                                    ## global settings
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import socket

import os, json
import pymongo
import z02_funcPy04trsf_json as mu1
from json_converter.json_mapper import JsonMapper

def extr_gcontacts(credentials, token, file, bool_extract=False, bool_save_json=False):                   ## parametros = com/sem paginação, salva json
    # preparação
    ## para conexão com API google
    ## extração gcontacts, incluir todos os escopos necessários
    SCOPES = [
        'https://www.googleapis.com/auth/contacts', 
        'https://www.googleapis.com/auth/userinfo.profile'
        ] 

    creds = None
    if os.path.exists(token):
        creds = Credentials.from_authorized_user_file(token, SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                credentials, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(token, 'w') as t:
            t.write(creds.to_json())
    ## extração paginada
    ### opções
    #### bool_extract = API google
    #### bool_save_json = salva string.json
    ### inicializações
    list_contatos = []
    page_token = None
    try:
        people_service = build('people', 'v1', credentials=creds)                   ## serviço ativado
        user_profile = people_service.people().get(                                 ## perfil do usuario google logado no serviço
                    resourceName='people/me', 
                    personFields='names,emailAddresses'
                                                ).execute()
    # execução
    ## extração
        while bool_extract is True:
            dict_in_contatos = people_service.people().connections().list(        ## object API request answer
                        resourceName='people/me',
                        pageSize=1000,
                        personFields='names,emailAddresses,phoneNumbers,addresses,biographies,metadata',
                        pageToken=page_token
                                                                ).execute()
            print(dict_in_contatos)
            list_in_contatos = dict_in_contatos.get('connections', [])            ## lista de contatos da pagina, versão inicial, para uso

            if not list_in_contatos:                                                    ## trat desvio, msg 'no connection found'
                print('No connection found___')
                break

            for contato in list_in_contatos:
                list_contatos.append(contato)

            page_token = dict_in_contatos.get('nextPageToken')
            if not page_token:
                break
                # return  ## break, se fora da function
    except HttpError as err:
        print(err)
    # output, salva json
    if bool_extract is True:
        dict_in_contatos['connections'] = list_contatos
    if bool_save_json is True:
        with open(file, 'w', encoding='utf-8') as f:
            json.dump(dict_in_contatos, f, ensure_ascii=False, indent=4)
        print('json salvo')

def collection_mongo(mongo_client, database_name, collection_name):                                     ## precisa??? Conecta MongoDB, retorna collection, em desuso
    client = pymongo.MongoClient(mongo_client)               ## Cria um cliente MongoDB
    db = client[database_name]              ## Seleciona o banco de dados e a coleção
    collection = db[collection_name]
    return(collection)

def is_port_in_use(port):
    """
    Verifica se uma porta específica está em uso.
    Retorna True se a porta estiver em uso, False caso contrário.
    """
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            # Tenta se conectar à porta. Se conseguir, a porta está em uso.
            s.bind(("127.0.0.1", port))
            return False # Se conseguiu fazer o bind, a porta está livre
        except socket.error:
            return True # Se houve um erro (socket.error), a porta está em uso

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
