
import shutil
import json, jsonschema
from json_converter.json_mapper import JsonMapper
from genson import SchemaBuilder
import pymongo
from pymongo import MongoClient
import z02_funcPy02doc_handling as mu2
import z02_funcPy04trsf_json as mu4

def extract_json_schema(file):                                                                                                         ## lib genson
    """Gera um esquema JSON a partir de um conjunto de dados JSON.
        Args:
            json_data (list): Uma lista de dicionários Python representando os dados JSON.
        Returns:
            dict: O esquema JSON gerado."""

    json_data = [mu2.open_file(file)]
    # print(json_data["totalPeople"])

    builder = SchemaBuilder()
    schema = []

    for dado in json_data:
        builder.add_object(dado)
    

        def shorten_schema(long_schema):
            """ Simplifica um schema JSON longo (formato genson) para um schema curto.
                Args:
                    long_schema (dict): O schema JSON longo como um dicionário Python.

                Returns:
                    dict or list: O schema JSON curto simplificado.
                """
            schema_type = long_schema.get('type')

            if schema_type == 'object':
                short_obj = {}
                if 'properties' in long_schema:
                    for key, prop_schema in long_schema['properties'].items():
                        short_obj[key] = shorten_schema(prop_schema)
                else:                                                                                                                  ## Caso de um objeto sem propriedades definidas explicitamente,
                    return "object"                                                                                                    ## como "metadata": {"type": "object"}
                return short_obj
            elif schema_type == 'array':
                if 'items' in long_schema:
                    items_schema = long_schema['items']                                                                                ## Se 'items' for uma lista (genson pode gerar isso para tipos mistos,
                    if isinstance(items_schema, list) and items_schema:                                                                ## pegamos o primeiro para simplificação)
                        items_schema = items_schema[0]

                    if items_schema.get('type') == 'object':
                        return [shorten_schema(items_schema)]
                    else:
                        return "array"                                                                                                 ## Para arrays de tipos primitivos ou arrays sem 'items' definidos (raro para genson)
                else:
                    return "array"                                                                                                     ## Array sem especificação de items, simplifica para "array"
            elif schema_type in ['string', 'integer', 'number', 'boolean']:
                return schema_type
            elif isinstance(long_schema, dict) and not schema_type and 'properties' in long_schema:                                    ## Caso raiz onde o "type": "object" pode estar implícito no nível superior
                short_obj = {}                                                                                                         ## ou um objeto aninhado sem 'type' explícito mas com 'properties'
                for key, prop_schema in long_schema['properties'].items():
                    short_obj[key] = shorten_schema(prop_schema)
                return short_obj
            elif isinstance(long_schema, dict) and not schema_type and 'items' in long_schema:
                items_schema = long_schema['items']                                                                                    ## Caso raiz onde o "type": "array" pode estar implícito
                if isinstance(items_schema, list) and items_schema:
                    items_schema = items_schema[0]

                if items_schema.get('type') == 'object':
                    return [shorten_schema(items_schema)]
                else:
                    return "array"
            else:
                if isinstance(long_schema, str) and long_schema in ['string', 'integer', 'number', 'boolean', 'object', 'array']:      ## Fallback para tipos não reconhecidos ou estruturas inesperadas
                    return long_schema                                                                                                 ## Em um schema genson bem formado, isso não deve ser comum.
                return "unknown"                                                                                                       ## Se o long_schema for apenas um tipo (ex: "string" diretamente), retorna ele.


    schema_long_str = builder.to_json(indent=2)                                                                                        ## Renomeado para schema_long_str para consistência
    schema_long_dict = json.loads(schema_long_str)                                                                                     ## Agora usa a variável correta
    schema_short = shorten_schema(schema_long_dict)

    schema.append(schema_short)
    schema.append(schema_long_str)                                                                                                     ## Esta linha já estava correta se a de cima fosse schema_long_str

    return schema

def valida_json_collection(json_schema, json_data):
    try:
        jsonschema.validate(instance=json_data, schema=json_schema)                                                                    ## jsonschema é compatível com https://json-schema.org/draft-06/schema
        return "Dados válidos!"
    except jsonschema.exceptions.ValidationError as erro:
        return "Dados inválidos:  " + str(erro)[:300]

def valida_json_documents(json_schema, json_data):
    for n, doc in enumerate(json_data):
        # if n in [677, 1075]:
        try:
            jsonschema.validate(instance=doc, schema=json_schema)                                                                      ## jsonschema é compatível com https://json-schema.org/draft-06/schema
            # return "doc {doc}:  Dados válidos!"
            print(f"doc {n}:  Dados válidos!")
        except jsonschema.exceptions.ValidationError as erro:
            # return "doc {doc}:  Dados inválidos:  " + str(erro)[:30]
            print(f"doc {n}:  Dados inválidos:  " + str(erro)[:40])
            print(doc)

def extract_nested_document_structure(file_path):                                                                                      ## pausado, ver extract_json_schema, mapear a estrutura de documentos aninhados e seus campos de um arquivo JSON
    """ Extrai a estrutura de documentos aninhados e seus campos de um arquivo JSON.
        Args:
            file_path (str): O caminho para o arquivo JSON.
        Returns:
            dict: Um dicionário representando a estrutura dos documentos aninhados.
        """

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
    except FileNotFoundError:
        return {"error": "Arquivo não encontrado."}
    except json.JSONDecodeError:
        return {"error": "Erro ao decodificar JSON."}

    structure = {}

    def explore_structure(data, current_path=""):
        if isinstance(data, dict):
            for key, value in data.items():
                new_path = f"{current_path}.{key}" if current_path else key
                structure[new_path] = type(value).__name__
                explore_structure(value, new_path)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                new_path = f"{current_path}[{i}]"
                structure[new_path] = type(item).__name__
                explore_structure(item, new_path)

    explore_structure(data)
    return structure

def flatten_json(y):
    out = {}
    def flatten(x, name=''):
        # If the Nested key-value pair is of dict type
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
                # out_file(file_02, name + a + '_\n')
        # If the Nested key-value pair is of list type
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i).zfill(2) + '_')
                # out_file(file_02, name + str(i).zfill(4) + '_\n')
                i += 1
        else:
            out[name[:-1]] = x
    flatten(y)
    return out

def convert_json(file_in, file_schema):
    json_in = mu4.open_file(file_in)
    json_out_schema = mu4.open_file(file_schema)
    json_out = JsonMapper(json_in).map(json_out_schema, on='connections')
    # print(json_out)
    return json_out
    
def convert_schema_mongodb(mongo_collection, file_in):
    try:
        # conecta MongoDB
        mongo_client    = mongo_collection[0]
        database_name   = mongo_collection[1]
        collection_name = mongo_collection[2]
                
        client = pymongo.MongoClient(mongo_client)
        db = client[database_name]
        collection = db[collection_name]
        print("connected")
        # atualiza file_in na collection
        collection.drop()
        json_in = mu4.open_file(file_in)
        docs = json_in['connections']
        collection.insert_many(docs)
        print("updated")
        # // tarnsforma base json pelo tipo 2025-04-01, javascript???, python???
            # /// array, list
            # ///// level_object_id, concatena (campos metadata, p. ex.) com um objeto selecionado da lista
            # ///// string = string
            # ///// concat fields
            # ///// select field => list

            # /// object
            # ///// level_object_id
            # ///// hoist_every subField
        # Pipeline de agregação
        pipeline = [
            # paused {
                # {
                #     "$unwind": {"path": "$names", "preserveNullAndEmptyArrays": True, "includeArrayIndex": "names_index"}
                # },
                #     "$unwind": {"path": "$phoneNumbers"}
                #     "$unwind": {"path": "$phoneNumbers", "preserveNullAndEmptyArrays": True, "includeArrayIndex": "phoneNumbers_index"}
                # },
                # {
                #     "$unwind": "$emailAddresses"
                # },
                # {
                #     "$unwind": "$biographies"
                # },
                # {
                #     "$unwind": "$addresses"
                # },

                # {
                #     "$match": {"resourceName": "people/c6164171676504989072"}
                # },
            # filtros
            {
                "$set": {
                    "metadata_sources_filter": {"$filter": {"input": "$metadata.sources", "as": "source", "cond": {"$eq": ["$$source.type", "CONTACT" ]}}},
                    "names_filter": {"$filter": {"input": "$names", "as": "names", "cond": {"$eq": ["$$names.metadata.source.type", "CONTACT" ]}}},
                }
            },
            {
                "$set": {
                    "names_filter_00": {"$arrayElemAt": ["$names_filter", 0]}
                }
            },
            # $set
            {                                                                                                                          ## $set "resource", "names"
                "$set": {
                    "resourceId":                       {"$concat":      ["$resourceName", "-", 
                                               {"$arrayElemAt": ["$metadata_sources_filter.type", 0]}, "-", 
                                               {"$arrayElemAt": ["$metadata_sources_filter.id", 0]}, "-", 
                                               {"$arrayElemAt": ["$metadata_sources_filter.etag", 0]}
                                               ]
                                },
                    "namesId":                          {"$concat":      ["$names_filter_00.metadata.source.type", "-", 
                                            "$names_filter_00.metadata.source.id", "-sourcePrimary:", 
                                            {"$toString": "$names_filter_00.metadata.sourcePrimary"}
                                            ]
                                },
                    "resource_updateTime":              {"$arrayElemAt": ["$metadata_sources_filter.updateTime" , 0]},
                    "names_displayName":                {"$arrayElemAt": ["$names.displayName", 0]},                    
                    "names_unstructuredName":           {"$arrayElemAt": ["$names.unstructuredName" , 0]},
                    "names_familyName":                 {"$arrayElemAt": ["$names.familyName" , 0]},
                    "names_givenName":                  {"$arrayElemAt": ["$names.givenName" , 0]},
                    "names_middleName":                 {"$arrayElemAt": ["$names.middleName" , 0]},
                    "names_displayNameLastFirst":       {"$arrayElemAt": ["$names.displayNameLastFirst" , 0]},
                    "names_honorificPrefix":            {"$arrayElemAt": ["$names.honorificPrefix" , 0]},
                    "names_honorificSuffix":            {"$arrayElemAt": ["$names.honorificSuffix" , 0]},
                }
            },
            {                                                                                                                          ## $set "phoneNumbers_tree"
                "$set": {
                    "tree_00": "$names_displayName",
                    "tree_01": "$names_unstructuredName",
                    "phoneNumbers_tree": {
                        "$map": {
                            "input": "$phoneNumbers",
                            "as": "this",
                            "in": {"$setField": {
                                    "field": "tree_00",
                                    "input": "$$this",
                                    "value": {"$concat": ["phone: ", "$$this.type"]}
                                    },
                                    }
                                }
                            },
                        },
            },
            {                                                                                                                          ## $set "phoneNumbers_tree", "tree_01"
                "$set": {
                    "phoneNumbers_tree": {
                        "$map": {
                            "input": "$phoneNumbers_tree",
                            "as": "this",
                            "in": {"$setField": {
                                    "field": "tree_01",
                                    "input": "$$this",
                                    "value": "$$this.value"
                                    },
                                    }
                                }
                            },
                        },
            },
            {                                                                                                                          ## $set "emailAddresses_tree"
                "$set": {
                    "emailAddresses_tree": {
                        "$map": {
                            "input": "$emailAddresses",
                            "as": "this",
                            "in": {"$setField": {
                                    "field": "tree_00",
                                    "input": "$$this",
                                    "value": "email: "
                                    },
                                    }
                                }
                            },
                        },
            },
            {                                                                                                                          ## $set "emailAddresses_tree", "tree_01"
                "$set": {
                    "emailAddresses_tree": {
                        "$map": {
                            "input": "$emailAddresses_tree",
                            "as": "this",
                            "in": {"$setField": {
                                    "field": "tree_01",
                                    "input": "$$this",
                                    "value": "$$this.value"
                                    },
                                    }
                                }
                            },
                        },
            },
            {                                                                                                                          ## $set "addresses_tree"
                "$set": {
                    "addresses_tree": {
                        "$map": {
                            "input": "$addresses",
                            "as": "this",
                            "in": {"$setField": {
                                    "field": "tree_00",
                                    "input": "$$this",
                                    "value": {"$concat": ["address: ", "$$this.type"]}
                                    },
                                    }
                                }
                            },
                        },
            },
            {                                                                                                                          ## $set "addresses_tree", "tree_01"
                "$set": {
                    "addresses_tree": {
                        "$map": {
                            "input": "$addresses_tree",
                            "as": "this",
                            "in": {"$setField": {
                                    "field": "tree_01",
                                    "input": "$$this",
                                    "value": "$$this.streetAddress"
                                    },
                                    }
                                }
                            },
                        },
            },
            {                                                                                                                          ## $set "biographies_tree"
                "$set": {
                    "biographies_tree": {
                        "$map": {
                            "input": "$biographies",
                            "as": "this",
                            "in": {"$setField": {
                                    "field": "tree_00",
                                    "input": "$$this",
                                    "value": "nota: "
                                    },
                                    }
                                }
                            },
                        },
            },
            {                                                                                                                          ## $set "biographies_tree", "tree_01"
                "$set": {
                    "biographies_tree": {
                        "$map": {
                            "input": "$biographies_tree",
                            "as": "this",
                            "in": {"$setField": {
                                    "field": "tree_01",
                                    "input": "$$this",
                                    "value": "$$this.value"
                                    },
                                    }
                                }
                            },
                        },
            },
            {                                                                                                                          ## $set "_children"
                "$set": {
                    "_children": {
                            "$concatArrays": [
                                {"$ifNull": ["$phoneNumbers_tree", []]},
                                {"$ifNull": ["$emailAddresses_tree", []]},
                                {"$ifNull": ["$addresses_tree", []]},
                                {"$ifNull": ["$biographies_tree", []]},
                            ]
                            },
                        },
            },
            {
                "$unset": [
                    "_id", "resourceName", "etag", "metadata", "names", "phoneNumbers", "emailAddresses", "addresses", "biographies",
                    "metadata_sources_filter", "names_filter", "names_filter_00", 
                    "phoneNumbers_tree", "emailAddresses_tree", "addresses_tree", "biographies_tree", "_children.metadata",
                ]
            }
        ]

        # Executa pipeline, converte resultado para JSON
        results = collection.aggregate(pipeline)
        results_list = list(results)

        json_data = json.loads(json.dumps(results_list, default=str, indent=3))

        client.close()                                                                                                                 ## fecha a conexão
        return json_data
    
    except pymongo.errors.ConnectionFailure as e:
        print(f"Erro de conexão com o MongoDB: {e}")
    except pymongo.errors.PyMongoError as e:
        print(f"Erro no MongoDB: {e}")

def json_convert(file_path):                                                                                                           ## mongodb
    mongo_client = 'str???'
    client = MongoClient(mongo_client)                                                                                                 ## enchendo linguiça

def format_structure_for_mindmap(structure):
    """
    Formata a estrutura extraída para melhor visualização em um mapa mental.
    Args:
        structure (dict): A estrutura dos documentos aninhados.
    Returns:
        str: Uma string formatada para representar a estrutura em um mapa mental.
    """

    formatted_output = ""
    for key, value in structure.items():
        formatted_output += f"{key} ({value})\n"
    return formatted_output


# exec
file_path = "gcontatos copy.txt"                                                                                                       ## Caminho para o arquivo JSON
file_02 = file_path
file_03 = file_path
## Extrair a estrutura do documento
document_structure = extract_nested_document_structure(file_path)
## Formatar a estrutura para o mapa mental
formatted_mindmap = format_structure_for_mindmap(document_structure)
data = file_path

flat_json_dict = flatten_json(data)
fieldNames = ""
list_fieldNames = []

for fieldName in list(flat_json_dict):
    # print(fieldName)
    fieldNames += fieldName + '\n'
    list_fieldNames.append(fieldName)
# out_file(file_02, fieldNames)
# out_file(file_03, str(list_fieldNames)[1:-1])
