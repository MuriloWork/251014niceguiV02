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
    - criar joplin plugin para meu uso pessoal
        - criar painel de visualização adicional personalizado sem perdas de funcionalidades nativas
            - o painel será ativável por comando (local a ser definido, se menu ou botão)
            - o painel personalizado será também será utilizado na versão mobile
        - Funcionalidades principais
            - renderizações adicionais
                - com alteração do conteúdo da nota
                    - incluir TOC table of contents
                - sem alteração do conteúdo da nota
                    - aplicar `<details><summary>` nos headers e aninhar por níveis, por exemplo, todos os `<h2>` abaixo de um `<h1>` são filhos deste último
                    - aplicar `<details><summary>` nas listas e aninhar
                    - inibir a exibição de frontmatter
            - persistir o estado de abertura de `<details>` entre sessões 
    - Exclusões
        - não alterar os editores de texto nativos
        - painel adicional não será utilizado para edição de conteúdo 
- contextos
    - `./z_contexto/`
        - `plano plugin webview.md`
        - `doc_joplin/`
    - API joplin links
        - [site joplin](https://joplinapp.org/api/references/plugin_api/classes/joplin.html)
        - [github api](https://github.com/laurent22/joplin/tree/dev/readme/api/references)
        - [github dev](https://github.com/laurent22/joplin/tree/dev/readme/dev)
    - API joplin documentos locais

# 3. Estrutura do projeto e configurações

Árvore de arquivos, suas principais características e responsabilidades.

- arquivos
    - `README.md`
        - Explica o propósito do plugin, como usar os comandos para gerar/atualizar o sumário e as opções de configuração.
    - `package.json`
        - Dependências (markdown-it), scripts de build, e metadados do plugin.
    - `manifest.json`
        - Arquivo de manifesto do plugin Joplin, definindo ID, versão, nome, etc.
    - `src/`
        - `index.ts`
            - Ponto de entrada principal (`joplin.plugins.register`).
            - logicas
                - Orquestra a lógica principal: recebe dados dos content scripts e outras funções.
                - Registra
                    - `Content Scripts` (MarkdownIt plugins) para analisar a nota.
                    - comandos do usuário
                    - comandos do joplin
        - `sectionHandler.js`
            - Características: um `MarkdownItPlugin` para a lógica de renderização. seções recolhíveis (`<details>`).
            - Lógicas (detalhadas mais abaixo)
                - Renderização do conteudo da nota
- configurações, dependências
    - API principal: joplin plugin
    - linguagens:
        - typescript apenas para `index.ts`
        - javascript e nodejs para todos os demais scripts
    - bibliotecas: markdown-it, codeMirror

# 4. Lógicas e requisitos

- fluxo do plugin, logicas
    - Eliminação de Dependências: Ao adotar as tags nativas `<details>` e `<summary>` do HTML, eliminamos a necessidade de:
        - section-styles.css: O estilo básico de expandir/recolher é fornecido pelo navegador.
        - toggle-handler.js: A funcionalidade de clique é nativa das tags `<details>`/`<summary>`, dispensando JavaScript customizado no lado do cliente.
    - Ativação do plugin (Por Nota)
        - Como funciona: Usamos uma regra de "core" do markdown-it chamada frontmatter_remover.
        - O que faz:
            - Ela é executada no início de cada renderização de nota.
            - Procura por um bloco de metadados (YAML frontmatter) no topo da nota.
            - Verifica se a propriedade pluginWebview: true está presente.
            - Se estiver, ela ativa a funcionalidade do plugin para aquela renderização específica, definindo uma flag env.mdPanelEnabled = true.
            - Por fim, remove os tokens do frontmatter para que eles não apareçam no painel renderizado.
        - Resultado: O plugin só modifica as notas que explicitamente o ativam, tornando-o não intrusivo.
    - Renderização do conteudo `sectionHandler.js`
        A lógica pode ser dividida em três partes principais: Ativação, Renderização Principal e Tratamento de Casos Especiais.
        - Lógica de Renderização Principal (Seções e Listas)
            - Tecnologia Base: Usamos as tags `<details>` (o contêiner que expande/recolhe) e `<summary>` (o título clicável).
            - Para Títulos (heading_open / heading_close):
            - A regra heading_open é o principal motor. Ela usa uma stack (pilha) para rastrear os níveis dos títulos (h1, h2, etc.).
                - Ao encontrar um novo título, ela fecha as seções (`</details>`) de níveis iguais ou inferiores que estavam abertas.
                - Em seguida, ela injeta as tags `<details><summary>` antes do título.
                - A regra heading_close simplesmente fecha a tag `</summary>`.
                - A palavra-chave open no final de um título adiciona o atributo open à tag `<details>`, fazendo com que a seção já comece expandida.
            - Para Listas com Sub-listas (list_item_open, etc.):
                - A lógica aqui é mais complexa e lida com o caso de um item de lista que contém uma sub-lista aninhada.
                - A regra list_item_open detecta se um item de lista tem filhos. Se tiver, ela o transforma em uma seção recolhível, injetando `<li><details><summary>`.
                - Ela usa uma variável de estado (listDetailsToClose) para "lembrar" que precisa fechar o `<summary>` e o `<details>` nos momentos certos, que são, respectivamente, quando a sub-lista abre (bullet_list_open) e quando ela fecha (bullet_list_close).
        - Tratamento de Casos Especiais (As Correções Finais)
            - Espaçamento com `<br>` (br_section_fixer):
                - Problema: Um `<br>` usado para criar espaço vertical entre duas seções estava sendo renderizado dentro da seção anterior.
                - Solução: Criamos uma regra de "core" que é executada antes da renderização. Ela procura pelo padrão de um token `<br>` seguido por um token de título. Ao encontrar, ela insere um novo token de </html_block> contendo `</details>` antes do `<br>`. Isso força o fechamento da seção anterior no local exato, garantindo que o `<br>` seja renderizado entre as seções.
            - Fechamento no Final do Documento (section_closer):
                - Problema: Se a nota terminasse com seções abertas, as tags `</details>` não seriam fechadas.
                - Solução: Uma regra de "core" final, section_closer, verifica a stack e adiciona todas as tags `</details>` de fechamento necessárias no final do documento.
    - comandos joplin
        - editorView, botão: Habilita/desabilita `lineWrapping`
- requisitos gerais
    - Faça o front-end simples inicialmente (HTML estático + vanilla JS) e depois evolua para bundlers/frameworks se quiser.

# 5. Etapas de implantação

- concluidas
    - Etapa 1 — Configuração e Limpeza
        - objetivo: Limpar a arquitetura de painel antiga e configurar a base para a nova abordagem de `Content Script`.
        - tarefas:
            - Remover os diretórios `src/ui/` e `web/`.
            - Reescrever `index.ts` para registrar um `Content Script` básico do tipo `MarkdownItPlugin`.
            - Criar o arquivo `src/content_scripts/sectionHandler.ts` como um placeholder.
            - Limpar `webpack.config.js` e `commands.js` de referências à arquitetura antiga.
        - verificação:
            - O plugin compila e carrega no Joplin sem erros.
            - O console de desenvolvimento do Joplin exibe uma mensagem confirmando que o `MarkdownItPlugin` foi carregado.
    - Etapa 2 — Renderização Simples e Estilo
        - objetivo: Provar que conseguimos interceptar a renderização de um elemento e aplicar um estilo customizado.
        - tarefas:
            - Implementar a lógica em `sectionHandler.ts` para interceptar a renderização de títulos `H1` e envolvê-los em uma tag `<details>`.
            - Criar um arquivo `src/assets/section-styles.css` e registrá-lo no `Content Script` para estilizar os novos elementos.
        - verificação:
            - Na visualização de nota do Joplin, todos os títulos `H1` aparecem como seções `<details>` recolhíveis e com o estilo customizado aplicado.
    - Etapa 3 — Depuração da Renderização HTML
        - objetivo: Criar uma ferramenta de depuração para extrair o HTML renderizado pelo nosso plugin e salvá-lo em um arquivo para inspeção.
        - tarefas:
            - Criar um novo comando (ex: `debug.renderNoteToHtml`) em `commands.js`.
            - A lógica do comando irá:
                - Obter o corpo da nota selecionada.
                - Instanciar o `markdown-it` localmente, carregar nosso plugin `sectionHandler` e renderizar o corpo da nota para uma string HTML.
                - Salvar a string HTML em um arquivo (ex: `debug_render.html`) na raiz do projeto.
        - verificação:
            - Executar o novo comando pela paleta de comandos do Joplin.
            - Um arquivo `debug_render.html` é criado na raiz do projeto, permitindo inspecionar o HTML gerado em um navegador.
    - Etapa 4 — Comunicação e Persistência (Teste com Botão)
        - objetivo: Validar o ciclo completo de comunicação (da visualização para o plugin) e a persistência da alteração na nota.
        - tarefas:
            - Modificar o `sectionHandler.ts` para adicionar um botão de teste ao lado de cada `H1` renderizado.
            - Criar e registrar um arquivo `src/assets/toggle-handler.js` que, ao clicar no botão, envia uma mensagem para o plugin via `webviewApi.postMessage`.
            - Em `index.ts`, ouvir a mensagem com `joplin.contentScripts.onMessage` e, ao recebê-la, usar a API do Joplin para adicionar um texto de confirmação ao final da nota.
        - verificação:
            - Clicar no botão de teste na visualização da nota faz com que um texto (ex: "Teste OK!") seja adicionado ao corpo do markdown da nota.
    - Etapa 5 — Implementação Completa das Seções (Headings)
        - objetivo: Expandir a lógica para todos os níveis de título e usar o clique nativo do `<summary>`.
        - tarefas:
            - Substituir o botão de teste pela lógica de clique nativa do `<summary>` no `toggle-handler.js`.
            - Expandir a lógica do `sectionHandler.ts` para funcionar com todos os níveis de título (H1-H6), utilizando a lógica do `sectioner.js` para garantir o aninhamento correto.
            - Implementar a lógica de persistência que adiciona/remove a palavra-chave ` open` no markdown.
        - verificação:
            - Todos os títulos na visualização são seções `<details>` aninhadas corretamente.
            - Clicar em um título para abrir/fechar a seção adiciona/remove a palavra ` open` da linha correspondente no editor de markdown.
    - Etapa 6 — Implementação das Seções (Listas)
        - objetivo: Adicionar a funcionalidade de transformar listas em seções recolhíveis, similar aos cabeçalhos.
        - tarefas:
            - Modificar o `sectionHandler.ts` para interceptar a renderização das listas (`bullet_list_open`, `ordered_list_open`) existentes no documento.
            - Envolver todos os itens da listas que tenham filhos em tags `<details>``<summary>`.
            - Implementar a lógica de persistência para listas, usando a palavra-chave ` open` no final do conteudo de todos os itens com filhos.
            - Atualizar o `toggle-handler.js` para gerenciar o clique em `summary` de listas.
        - verificação:
            - Todas as listas na visualização aparecem completamente recolhíveis.
            - Clicar no `summary` da lista adiciona/remove ` open` no texto do item da lista no markdown.
    - Etapa 7 — Leitura do Estado `open`
        - objetivo: Fazer com que as seções já apareçam abertas se a palavra `open` estiver no título do markdown.
        - tarefas:
            - No `MarkdownItPlugin`, ao encontrar um título, verificar se o texto original no markdown contém a palavra-chave ` open`.
            - Se contiver, adicionar o atributo `open` à tag `<details>` (`<details open>`).
        - verificação:
            - Títulos no markdown que terminam com ` open` fazem com que a seção correspondente já apareça expandida na visualização.
    - etapa 8 - melhorias na renderização
        - objetivo: incluir novas condições (a) Renderização da TOC existente; (b) Como tratar a tag `<br>`
        - contexto
            - TOC
                - as notas são editadas tanto no joplin quanto no vscode
                - quando editadas no vscode é utilizada uma extensão que aplica e atualiza toc (table of contents) automaticamente
                - a toc vinda do vscode é uma lista markdown e cada linha é um link markdown atualizado automaticamente pelos títulos dos headings
                - neste caso a palavra open estará no fim do título do link (entre colchetes) e não no fim da linha
                - A seção TOC tem heading sempre com titulo "TOC"
            - tag `<br>`
                - quando existir a tag `<br>` imedatamente acima de um heading o `</details>` deve ser colocado na linha anterior a essa tag `<br>`
                    - exemplo da condição encontrada
                        ```markdown
                        ## heading 1
                        
                        texto

                        <br>

                        ## heading 2

                        texto
                        ```
                    - como fica após a renderização
                        ```markdown
                        <details>
                        <summary><h2 style="display: inline">heading 2<h2></summary>
                        
                        texto
                        </details>
                        <br>

                        <details>
                        <summary><h2 style="display: inline">heading 2<h2></summary>

                        texto
                        </details>
                        ```
                - sempre existe 1 linha em branco entre `<br>` e o heading
        - Tarefas:
            - Para o TOC:
                - Modificar a regra list_item_open em src/sectionHandler.js.
                - Adicionar uma lógica que detecte se o item de lista atual está dentro de uma seção cujo título é "TOC".
                - Se estiver, a verificação da palavra-chave open deve ser feita dentro do texto do link Markdown (o conteúdo entre []), em vez de no final da linha.
            - Para a tag `<br>`:
                - Modificar a regra heading_open em src/sectionHandler.js.
                - Antes de gerar as tags `<details>` de abertura, a lógica deve inspecionar os tokens imediatamente anteriores.
                - Se um token do tipo html_block contendo `<br>` for encontrado antes do cabeçalho, a tag de fechamento `</details>` da seção anterior deve ser inserida antes da tag `<br>`.'
        - Verificação:
            - Para o TOC:
                - Crie uma nota com um cabeçalho # TOC seguido por uma lista de links Markdown.
                - Adicione a palavra open dentro do texto de um dos links (ex: - Título da Seção open).
                - Verifique se este item da lista é renderizado como uma seção `<details>` já expandida, enquanto os outros itens da lista TOC não são afetados.
            - Para a tag `<br>`:
                - Crie uma nota com a estrutura: ## Seção 1, conteúdo, `<br>`, ## Seção 2.
                - Inspecione o HTML renderizado (usando o comando de debug ou as ferramentas do desenvolvedor).
                - Confirme que o HTML gerado é `</details><br><details...>`, garantindo que a tag `<br>` fique fora da seção recolhível da "Seção 1".
    - Etapa 9 — ocultar frontmatter
    - Etapa 10 — habilitação do plugin via frontmatter
    - etapa 11 — Organização, implantação
        - Limpar códigos e comentários
        - identificar e eliminar arquivos descartáveis
        - Organização final de arquivos
        - Implantar em produção
- etapa 12 — Planejar possíveis melhorias 
    - Nova condição para listas, "openAll"
    - webview própria 
        - resumo chatGpt
            A renderização da *webview* no Joplin envolve alguns passos distintos (e um componente chamado *renderer*). Vou explicar de forma direta, passo a passo, e indicar onde isso acontece no código/documentação.
            - Visão geral rápida
                1. O Joplin guarda a nota em Markdown.
                2. Um *renderer* converte esse Markdown para HTML (usa **markdown-it** + plugins e transformações específicas do Joplin). ([GitHub][1])
                3. O HTML gerado passa por adaptadores: conversão de links/recursos internos (imagens, anexos), sanitização/segurança e injeção de CSS do tema. ([GitHub][1])
                4. O HTML final é exibido dentro de uma WebView / BrowserWindow (processo de render do Electron ou componente WebView no mobile). A comunicação entre a UI nativa e a webview é feita via mensagens/IPC (postMessage/bridge). ([electronjs.org][2])
            - Componentes importantes (onde olhar)
                - **joplin-renderer / @joplin/renderer**: biblioteca que implementa a conversão Markdown → HTML usada pelo Joplin. Antigamente estava num repo separado; hoje faz parte do código do Joplin e também existe como pacote. É aqui que ficam as regras, plugins e transformações específicas (fenced code, mermaid, math, etc.). ([GitHub][1])
                - **WebView (Electron / Mobile)**: no desktop Joplin usa a arquitetura do Electron — o HTML final roda no processo de render (Chromium). No mobile usa o componente WebView da plataforma. Comunicação e atualização do conteúdo são feitas via mensagens entre processos. ([electronjs.org][2])
            - Detalhes úteis para desenvolvedores de plugin / webview
                - Se você abre uma *webview panel* a partir de um plugin, a *webview* não — por si só — fornece uma instância do Markdown renderer dentro do contexto da página. Ou seja, se você quer converter Markdown dentro da sua própria página webview, normalmente precisa incluir/instalar `markdown-it` no seu código de plugin ou pedir ao backend do Joplin que gere o HTML e te envie. (Isso é mencionado nas discussões da comunidade). ([Joplin Forum][3])
                - Plugins e o renderer trocam assets/CSS: o renderer injeta CSS do tema e adapta caminhos de recursos (anexos/images) para que a webview consiga carregar os arquivos locais corretamente. Há também preocupações de segurança (conteúdo local pode ficar bloqueado conforme configurações). ([GitHub][1])
            - Fluxo técnico simplificado
                - Usuário salva/edita nota (Markdown).
                - App pede ao renderer: “converte essa nota” (renderer aplica markdown-it, plugins e transformações Joplin). ([GitHub][1])
                - Renderer retorna HTML já sanitizado + referências a assets e CSS.
                - HTML é entregue à webview; o Chromium (ou WebView nativa) renderiza o HTML/CSS/JS, exibindo a nota renderizada. ([electronjs.org][2])
            - Onde encontrar o código / referência
                - Repositório/documentação do renderer (laurent22/joplin-renderer e a versão integrada no repositório principal). ([GitHub][1])
                - Discussões da comunidade (fórum) sobre parsing no webview e comunicação postMessage (úteis se for desenvolver plugin). ([Joplin Forum][3])
            - Referências
                [1]: https://github.com/laurent22/joplin-renderer?utm_source=chatgpt.com "laurent22/joplin-renderer: Markdown and HTML ..."
                [2]: https://electronjs.org/docs/latest/tutorial/process-model?utm_source=chatgpt.com "Process Model"
                [3]: https://discourse.joplinapp.org/t/parse-md-from-within-webview/15320?utm_source=chatgpt.com "Parse MD from within webview - Plugins"
    - versão mobile
    - Estilização dos marcadores de lista
        - substittuição do marcador markdown pelo triangulo do `<details>`
        - inversão dos marcadores, Como poderia ser feito?
            Sua dúvida sobre o estilo dos marcadores de lista é muito pertinente. O comportamento que você descreve é o padrão do navegador: o marcador do `<li>` (o bullet) é renderizado, e depois o conteúdo do `<li>`, que no nosso caso é a tag `<details>` com seu próprio marcador (o triângulo).

            Para inverter essa ordem e alcançar o resultado desejado (triângulo -> marcador original), precisaremos fazer uma alteração tanto na estrutura HTML que geramos quanto no CSS para controlar a aparência.

            Seguindo as regras do nosso modo de solução de problema, aqui está a análise de como isso pode ser feito.

            Análise da Causa e Solução Proposta
            Identificação da Causa Raiz:

            O problema é que estamos colocando a tag `<details>` dentro da tag `<li>`. O navegador aplica o estilo de lista (o marcador) ao `<li>` e, separadamente, aplica o marcador padrão (o triângulo) ao `<summary>` dentro do `<details>`. Não temos controle direto sobre a ordem desses dois marcadores gerados pelo navegador.
            Explicação dos Trechos de Código Correspondentes:

            A lógica atual em src/sectionHandler.js na regra list_item_open gera o seguinte HTML:
            ```javascript
            // Lógica atual
            return `<li><details ...><summary>`; 
            ```
            Isso resulta em uma estrutura ``<li><details><summary>...</summary></details></li>``, que causa a ordem de marcadores que você observou.
            Sugestão de Possíveis Soluções:

            A solução é mudar a abordagem: em vez de o `<li>` conter o `<details>`, faremos o `<details>` conter o `<li>`. Além disso, vamos remover o marcador padrão do `<li>` via CSS e "simular" o marcador original dentro do `<summary>`.

            Passo 1: Alterar a Estrutura HTML (em sectionHandler.js)

            Vamos modificar a regra list_item_open para gerar uma estrutura onde o `<details>` envolve o `<li>`.
            O summary conteria o texto do item, e o `<li>` conteria a sub-lista.
            A estrutura HTML alvo seria:

            ```html
                Show full code block 
                <details>
                    <summary>
                        <span class="list-marker-content">...texto do item...</span>
                    </summary>
                    <li> <!-- Este li não terá marcador, apenas conterá a sub-lista -->
                        <ul>...sub-lista...</ul>
                    </li>
                </details>
            ```
            
            Passo 2: Alterar o Estilo (com um novo arquivo CSS)

            Criaríamos um arquivo CSS (src/assets/section-styles.css).
            Nesse CSS, usaríamos a propriedade list-style: none; para remover o marcador padrão do <li> que está dentro do `<details>`.
            Usaríamos o pseudo-elemento ::before no nosso `<span class="list-marker-content">` para recriar o marcador de lista (o bullet • ou o número) ao lado do texto, mas depois do triângulo do `<summary>`.
            Alerta de Paradigma:

            Isso representa uma mudança significativa na forma como renderizamos as listas. Em vez de usar o `<li>` como o contêiner principal, estamos usando o `<details>` e tratando o `<li>` como um mero invólucro para a sub-lista. É uma abordagem mais complexa, mas necessária para obter o controle visual que você deseja.
            Essa combinação de mudanças no HTML e no CSS nos daria controle total sobre a posição dos elementos, permitindo alcançar a ordem triângulo -> marcador -> texto.
    - toggle lineWrapping
	- navegação: gotoLine, gotoEnd
- etapa 13 — Atualizar documentação 
- etapa 14 (atual) — implantar toggle lineWrapping
    - contexto especifico open 
        - classes html: `cm-scroller`, `cm-content`, `cm-lineWrapping`
		- pasta `docs_joplin`
		- Instruções De como usar CodeMirror no joplin `2025-10-09 codeMirror no joplin.md`
    - logicas
		- recursos adotados, em ordem de prioridade:
            - api Joplin
            - api CodeMirror
            - css
		- botão na barra de ferramentas do editorViewer
		- ponto de atenção existe um conflito de causa não identificada entre `white-space: pre` e `overflow`
    - requisitos especificos open 
        - Exibir barra de rolagem horizontal do conteúdo 
        - Navegação via tecla `End` deve atingir o final da linha (que já não tem quebra)
        - Deve funcionar no joplin mobile
