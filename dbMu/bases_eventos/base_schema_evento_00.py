
from pydantic import BaseModel, Field
import uuid
from typing import List, Optional, Literal
from datetime import date, datetime

class Empreendimento(BaseModel):
    {
    "metadados": {} ,
    "tipoProjeto": [] ,
    "item": [
        "fonte", "titulo", "pc", "moeda", "classificacao", 
        "vendedor", 
        "condicoes comerciais", 
        "dataCotacao"
    ] ,
    "tags": [] ,
    "conteudos": {} ,
    "planejamento": {
        "indice": "pkm Id Tree",
        "chance = analiseProbabilidade = risco^-1": "" ,
        "cronograma": {},
        "orcamento": { "fluxoDeCaixa": "" },
        "pessoas": {}
    } 
    }   

class Pesquisa(BaseModel):
    {
    "metadados": {} ,
    "item": [
        "fonte", "titulo", "pc", "moeda", "classificacao", 
        "vendedor", 
        "condicoes comerciais", 
        "dataCotacao"
    ] ,
    "tags": [] ,
    "conteudos": {}
    }

class OrdemServico(BaseModel):
    tipo: Literal["os"]
    subTipo: Literal["programacao", "todo", "projeto", "planta", "prancha", "cenario", "vitrine", "desenho"]
    metadados: str
    item: Literal[
        "fonte", "titulo", "pc", "moeda", "classificacao", 
        "vendedor", 
        "condicoes comerciais", 
        "dataCotacao"
    ] 
    tags: List[str] 
    conteudos: str

class Compra(BaseModel):
    tipo: Literal["compra"]
    metadadosDocModelo: Optional[str]
    subTipo: Literal["compra", "cotação", "pgto", "contrato"]
    item: Literal[ "descricao", "qt", "pc", "moeda", "classificacao" ] 
    vendedor: str
    condicoesComerciais: str
    controle: str

# --- Eventos ---
class Metadados(BaseModel):             ## => metadadosEvento
    stFoldingStatusProjeto: Optional[bool] = False
    stFoldingStatusPlanejamento01: Optional[bool] = False
    stFoldingStatusPlanejamento02: Optional[bool] = False
    stFoldingStatusHistorico: Optional[bool] = False
    stFoldingStatusRelacionamentos: Optional[bool] = False

class Itens(BaseModel):  
    # --- identificação do item
    idItem: Optional[str]
    tipoItem: Optional[Literal["atividade", "orcamento"]]
    sku: Optional[str]
    descricaoItem: Optional[str]
    descricaoAlternativa: Optional[str]
    # --- 5w2h
    # ----- what
    grupo1: Optional[str]
    grupo2: Optional[str]
    tituloAtividade: Optional[str]
    tituloAtividadeAlternativo: Optional[str]
    # filtros, tipoAtiv, 
    # ----- when
    dataCriacao: Optional[date]
    dataFim: Optional[date]
    # ----- who
    quem: Optional[str]
    # resp, vendedor
    # ----- how much
    qtd: Optional[float]
    un: Optional[str]
    preco: Optional[float]
    moeda: Optional[str]
    valorTotal: Optional[float]
    tipoOrcamento: Optional[Literal["planejado", "forecast", "realizado"]]
    # --- notas, tags
    notas: Optional[str]
    tags: Optional[str]

class Pessoas(BaseModel):
    idPerson: Optional[str]
    nome: Optional[str]
    papelNoEvento: Optional[Literal["vendedor", "comprador"]]

class Logs(BaseModel):
    tipo: Literal["atualizacao", "execucao"]

class DocTree(BaseModel):
    tipo: Literal["atualizacao", "execucao"]

class Msgs(BaseModel):
    tipo: Literal["atualizacao", "execucao"]

class ControleExecucaoItem(BaseModel):
    tipo: Literal["atualizacao", "execucao"]

class Evento(BaseModel):
    # Evento
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Identificador único do evento.", readOnly=True)
    tituloProjeto: str
    tipoProjeto: Literal["Fi", "Km", "Wk", "Bs", "Fm"] = "Fi"
    tipoEvento: Literal["empreendimento", "os", "todo", "compra", "pesquisa", "comunicação"] = "todo"
    tags: Optional[List[str]]
    links: Optional[List[str]]
    docsPath: Optional[str]
    metadados: Optional[Metadados]
    # Plano 01
    notas: Optional[str] = Field(None, description="Notas gerais sobre o evento.", format="multi-line")
    indice: Optional[str]
    pessoas: Optional[dict]
    # Plano 02
    itens: Optional[List[Itens]]                                        ## cronoFin => itens, 5w2h, notas, tags
    # historicoDocTree: Optional[DocTree]                                         ## historico documentos (folderFileTree), listas, propostas, contratos, midia, dwg, notas, relatorios
    historicoDocTree: Optional[str] 
    historicoLogs: Optional[List[Logs]]
    historicoMsgs: Optional[List[Msgs]]
    # Relacionamentos
    relacionamentos_como_convidado: Optional[str] = Field(None, alias="relacionamentos como convidado")
    relacionamentos_como_anfitriao: Optional[str] = Field(None, alias="relacionamentos como anfitriao")
    
