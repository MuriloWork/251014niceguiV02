# 1. Regras de desenvolvimento 

- papeis
    - o meu papel é de **desenvolvedor** com as seguintes regras:
        1. planejar com a melhor clareza, detalhamento e consistencia possíveis;
        2. validar o plano com o agente em conversas prévias;
        3. dividir o desenvolvimento em etapas para permitir que o agente possa ser mais efetivo
        4. interromper o desenvolvimento após 3 tentativas de solucionar um problema e conduzir análise em busca da causa;
        5. corrigir o plano quando necessario e atualizar o agente.
    - o seu papel é de **"agente"** com as seguintes regras:
        - seguir as instruções planejadas, sempre conforme A versão Mais atualizada do plano;
        - adotar soluções usando ao máximo a tecnologia, linguagem, padrão;
        - alertar Quando for seguir Uma direção diferente da planejada Informando o motivo;
        - Junto com as alterações de código propostas Informar Como podem ser verificadas pelo desenvolvedor, através de logs, mensagens e Funções que possam ser verificadas Na interface de usuário;
        - diante de erros, identificar as possíveis causas e resumir o que pode ser feito para corrigir, antes de sair criando ou revisando codigos e alertar se identificar um possível problema no paradigma de programação que está no plano.
        - modo de solução de problema
            - quero
                - Identificação de possíveis causas
                - Explicação Dos trechos de código correspondentes
                - Sugestão de possíveis soluções
                - que alerte quando a possivel solução Representar uma mudança de paradigma
            - não quero
                - sugestão de alteração de nada que não esteja relacionado estritamente a causa do problema
                - Alteração de nada que não tenha sido explicitamente autorizado
- retorno
    - ESTRUTURA PADRÃO DAS RESPOSTAS do agente
        - PAPEL: Agente - Seguindo plano [versão/etapa]
        - AÇÃO: [o que vou fazer]
        - ALERTA: [se houver desvio]
        - VERIFICAÇÃO: [como você pode testar]
    - formatos
        - para chats web
            - paragrafos em listas markdown não numeradas
                - marcador "-" traço
                - tabulação de 4 espaços
                - sem linhas em branco, sem titulos em negrito
        - especifico para markdown
        - especifico para scripts
            - não incluir icones
- persistência dos papeis durante as conversas
    - PARA O DESENVOLVEDOR
        - **Início de cada sessão:** Relembrar os papéis estabelecidos
        - **A cada 5-10 mensagens:** Reconfirmar papéis
        - **Antes de cada etapa:** Confirmar se estou seguindo o plano atualizado
        - **Quando houver desvio:** Alertar imediatamente e corrigir a direção
        - **Após 3 tentativas:** Interromper e conduzir análise da causa
        - a cada requisição
            - modo de desenvolvimento: ao final, sugerir o que fazer a seguir e pedir autorização para executar
            - modo de solução de problema
                - quero
                    - Identificação de possíveis causas
                    - Explicação Dos trechos de código correspondentes
                    - Sugestão de possíveis soluções
                    - que alerte quando a possivel solução Representar uma mudança de paradigma
                - não quero
                    - sugestão de alteração de nada que não esteja relacionado estritamente a causa do problema
                    - Alteração de nada que não tenha sido explicitamente autorizado
        - PALAVRAS-CHAVE DE ATIVAÇÃO:**
            - **"Relembrar papéis"** - Para reativar a estrutura
            - **"Verificar plano"** - Para confirmar alinhamento
            - **"Pausar para análise"** - Para interromper e analisar
    - PARA O AGENTE
        - **Sempre começar** cada resposta com confirmação do papel
        - **Antes de cada ação:** Verificar se está alinhada com o plano
        - **Ao desviar:** Alertar explicitamente o motivo
        - **Incluir sempre:** Como verificar as alterações propostas
        - **Em erros:** Identificar causas antes de criar códigos
- modo de desenvolvimento: ao final, sugerir o que fazer a seguir e pedir autorização para executar
- modo de solução de problema
    - quero
        - Identificação de possíveis causas
        - Explicação Dos trechos de código correspondentes
        - Sugestão de possíveis soluções
        - que alerte quando a possivel solução Representar uma mudança de paradigma
    - não quero
        - sugestão de alteração de nada que não esteja relacionado estritamente a causa do problema
        - Alteração de nada que não tenha sido explicitamente autorizado
- regras para criação das etapas de implantação
    - seguir recomendaçoes da API principal
    - dividir em etapas que:
        - tenham contexto limitado de forma que o agente possa manter foco na qualidade e eficiencia do codigo
        - sejam funcionais do ponto de vista do usuário
        - possam ser testadas por funcionalidades acessadas pelo usuário e por mensagens no console

# 2. Objetivos e contextos do projeto

- objetivos
    - Migrar estrutura de documentos para SQLite
    - Manter todas as funcionalidades existentes no aplicativo para a nova estrutura de documentos
    - Exclusões
- contextos
    - `./z_contexto/`
    - [SQLite MCP](https://github.com/modelcontextprotocol/servers-archived/tree/main/src/sqlite)

# 3. Estrutura do projeto e configurações

Árvore de arquivos, suas principais características e responsabilidades.

- arquivos
    - `README.md`
        - Explica como funciona o aplicativo
    - `src/`
        - `2025-10-14 nicegui_eventos.py`
            - script principal
            - logicas (detalhadas mais abaixo)
                - será mapeada pelo agente
        - `2025-10-14 pydanticEventos.py`
            - schemas pydantic
            - Lógicas
                - será mapeada pelo agente
    - `./dbMu/`
        - `bases_eventos/`
            - Estrutura atual de documentos json
        - `financeiro.db`
            - Alvo do projeto para reconfiguração
    - Desconsiderar Arquivos das pastas
        - `./z_historico/`
        - `./dbMu/bases_cadastros/`
- configurações, dependências
    - linguagens: python
    - bibliotecas principais: nicegui, pydantic
    - servidores MCP: SQLite

# 4. Lógicas e requisitos

- fluxo do plugin, logicas
    - será mapeada pelo agente
- requisitos gerais

# 5. Etapas de implantação

- Etapa 1 — agente entender as lógicas existentes e detalhar o planejamento 
- Etapa 2 — reendereçar base de documentos
    - contexto especifico
        - Endereço atual dos documentos: pasta fora do contexto do projeto
        - Endereço alvo dos documentos `./dbMu/bases_eventos/`
    - logicas
        - Versão atual do aplicativo edita os documentos em endereço fora do contexto do projeto
        - Nova versão deve editar os documentos no endereço alvo
    - requisitos especificos
- Etapa 3 — refatorar a logica de atualização dos documentos
    - contexto especifico
        - Banco de dados desatualizado `./dbMu/financeiro.db`
    - logicas
        - Migrar a estrutura de documentos unitários para documentos em banco de dados SQLite
        - Funções de atualização dos documentos voltadas para SQLite
    - requisitos especificos
        - Incluir servidor MCP SQLite no fluxo de desenvolvimento
    - Ação
        - Integração do Servidor MCP: Adicionar as dependências e a configuração inicial para o servidor MCP SQLite.
        - Mapeamento de Tabelas: Definir as tabelas no banco de dados SQLite que corresponderão aos modelos Pydantic Evento e Itens. Proponho uma estrutura relacional:
            - Uma tabela eventos para armazenar os campos do modelo Evento (exceto a lista de itens).
            - Uma tabela itens para armazenar os campos do modelo Itens, com uma chave estrangeira (evento_id) para relacioná-la à tabela eventos.
        - Refatoração das Funções CRUD:
            - carregar_documento será substituída por uma função que consulta o banco de dados pelo ID do evento e reconstrói o dicionário documento_ativo.
            - salvar_documento_atual será modificada para executar operações de UPDATE ou INSERT nas tabelas eventos e itens.
            - As funções de manipulação de itens (add_row, copy_row, remove_selected, on_cell_value_changed) serão ajustadas para interagir diretamente com o banco de dados, garantindo a persistência imediata das alterações.
- Etapa 4 — refatorar a logica das demais funcionalidades
    - contexto especifico
    - logicas
    - requisitos especificos
    - Ação
        - Após a migração do CRUD principal, revisaremos todas as outras funcionalidades (importação/exportação de Excel, gerenciamento de arquivos na barra lateral) para garantir que continuem funcionando corretamente com a nova fonte de dados SQLite.
        - A lista de "Arquivos Existentes" na barra lateral, por exemplo, precisará ser populada com uma consulta SELECT na tabela eventos, em vez de listar arquivos .json do diretório.

