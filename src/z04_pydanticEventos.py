
from pydantic import BaseModel, Field, model_validator
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
    stFoldingStatusEvento: Optional[bool] = False
    stFoldingStatusPlanejamento01: Optional[bool] = False
    stFoldingStatusPlanejamento02: Optional[bool] = False
    stFoldingStatusHistorico: Optional[bool] = False
    stFoldingStatusRelacionamentos: Optional[bool] = False

class Itens(BaseModel):  
    # --- item, atividade
    idColumn: str = Field(default_factory=lambda: str(uuid.uuid4()))
    idItem: Optional[str] = None        ## indice da grid
    tipoItem: Optional[Literal["atividade", "serviço", "material"]] = None
    grupo1: Optional[str] = None
    grupo2: Optional[str] = None
    descricaoItem: Optional[str] = None
    tituloAtividade: Optional[str] = None
    tituloAtividadeAlternativo: Optional[str] = None
    # ----- pessoas
    quem: Optional[str] = None
    responsavel: Optional[str] = None
    vendedor: Optional[str] = None
    # ----- dateTime
    dataHoraCriacao: Optional[str] = None
    dataHoraInicio: Optional[date] = None
    dataHoraFim: Optional[date] = None
    # ----- cadastro
    sku: Optional[str] = None
    # --- Orçamento
    tipoOrcamento: Optional[Literal["planejado", "forecast", "realizado"]] = None
    qtd: Optional[float] = None
    qtdList: Optional[list[float]] = None
    un: Optional[str] = None
    preco: Optional[float] = None
    precoList: Optional[list[float]] = None
    moeda: Optional[str] = None
    valorTotal: Optional[float] = None
    valorTotalList: Optional[list[float]] = None
    peso: Optional[str] = None
    volume: Optional[str] = None
    # --- notas, tags
    notas: Optional[str] = None
    tags: Optional[str] = None
    # --- filtros

    @model_validator(mode='after')
    def set_default_descricao_item(self) -> 'Itens':        ## Se descricaoItem não for fornecido na criação, define um valor padrão usando "Novo Item " e os últimos 6 caracteres de idColumn.
        if self.descricaoItem is None:
            self.descricaoItem = f"Novo Item {self.idColumn[-6:]}"
        return self

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
    nomeDocumento: Optional[str] = None
    tipoEvento: Literal["empreendimento", "os", "todo", "compra", "pesquisa", "comunicacao"] = "todo"
    tipoProjeto: Literal["Fi", "Km", "Wk", "Bs", "Fm"] = "Fi"
    tituloEvento: str
    tags: Optional[str] = None
    links: Optional[str] = None
    docsPath: Optional[str] = None
    metadados: Metadados = Field(default_factory=Metadados)
    # Plano 01
    notas: Optional[str] = Field(None, description="Notas gerais sobre o evento.", format="multi-line")
    indice: Optional[str] = None
    pessoas: Optional[str] = None
    # Plano 02
    itens: Optional[List[Itens]] = []                                        ## cronoFin => itens, 5w2h, notas, tags
    # historicoDocTree: Optional[DocTree]                                         ## historico documentos (folderFileTree), listas, propostas, contratos, midia, dwg, notas, relatorios
    historicoDocTree: Optional[str] = None
    historicoLogs: Optional[List[Logs]] = []
    historicoMsgs: Optional[List[Msgs]] = []
    # Relacionamentos
    relacionamentos_como_convidado: Optional[str] = Field(None, alias="relacionamentos como convidado")
    relacionamentos_como_anfitriao: Optional[str] = Field(None, alias="relacionamentos como anfitriao")
    
