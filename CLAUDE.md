# single-instagram

Automação do Instagram **@singletecnologia** (Single Tecnologia). O Claude cria o conteúdo; o GitHub Actions publica, responde comentários com DM e gera o relatório. Tudo é gratuito: repositório público, GitHub Actions, GitHub Pages e a API oficial do Instagram.

## Regras que nunca mudam

- **Nada vai para a branch `main` sem aprovação do Wallan.** Conteúdo novo sempre entra por um pull request. Fazer o merge do pull request é aprovar os posts; o workflow `publicar.yml` só publica o que está na `main`.
- **Nunca** seguir, deixar de seguir, curtir ou comentar em perfis de outras pessoas, nem mandar DM para quem não comentou. Isso viola os Termos do Instagram e arrisca a conta.
- **Nunca** colocar token, senha ou chave em arquivo do repositório. Credenciais ficam só em GitHub Secrets.
- Todo conteúdo é original (regra de originalidade do Instagram). Não repostar conteúdo de outros perfis.
- No máximo **5 hashtags** por post, todas do tema.
- Português do Brasil, frases curtas, sem jargão desnecessário. Conteúdo técnico (DAX, Power Query, SQL) precisa estar correto: teste mentalmente cada fórmula antes de publicar.

## Marca (identidade "Encaixe")

- Cores: azul-marinho `#0B2A6F`, fundo escuro `#050F2B`, azul `#2563EB`, azul-claro `#60A5FA`, âmbar `#FFB400` (destaque, nunca em textos longos).
- Fonte: Red Hat Display (500, 700, 900) para tudo; JetBrains Mono só em código. Ambas em `templates/fonts`.
- Símbolo: duas peças em S que se encaixam em volta de um losango âmbar (`assets/logo-single.svg`).
- Slogans: "Solicitou, entregamos." e "Tudo conectado em um só lugar."
- Site: https://singletecnologia.netlify.app · WhatsApp: https://wa.me/5521965725125

## Sistema visual das artes (v2, "Entrega", aprovado pelo Wallan em 05/11/2026)

O público é o gerente de TI, de projetos ou de operações que responde pela empresa. A arte precisa parar a rolagem e mostrar tecnologia funcionando. Texto sobre fundo liso parece "cartilha" e foi reprovado. Referências de padrão: `posts/2026-11-05` e `posts/2026-11-06`, ambos usando `templates/base.css`.

- **Interface como imagem:** toda lâmina tem um objeto visual do mundo de dados desenhado em HTML: painel com gráfico, cartão de indicador (`.kpi`), janela de código (`.janela`), conversa (`.bolha`), chamado com status (`.status`), modelo de tabelas. Nada de foto de banco de imagens nem logo ou foto de empresa real.
- **Título grande e pesado** (`.titulo`, `.titulo.m`, `.titulo.p`) com a faixa `.mk` (âmbar) ou `.mk.az` (azul) só no trecho que precisa ser lido primeiro. No máximo uma faixa por título.
- **Profundidade:** cartões levemente inclinados (1° a 4°), sombra, `.halo` de luz atrás do objeto principal. Nunca cubra texto ou código com um cartão.
- **Ritmo:** alternar `.noite` (escuro), claro e `.ambar` (só na última lâmina, a de ação). Capa com `.arraste`; todas com `.pontos` no rodapé.
- **Números de exemplo** em painéis e cartões precisam fechar na conta (ex.: variação % calculada a partir dos valores mostrados).
- **Legibilidade no celular:** nada abaixo de 22px; conteúdo dentro das margens de 80px e acima do rodapé (até ~1210px de altura).

## Estratégia de conteúdo (aprovada pelo Wallan em 05/11/2026)

O diferencial da Single é resolver de tudo em um só lugar: BI, automação, SQL, Python, sistemas e aplicativos. O conteúdo mostra **problemas resolvidos** e essa variedade, e não fica preso em dicas de DAX. Instagram e LinkedIn **não são cópia um do outro**.

**Regras de variedade:** nenhuma tecnologia se repete na mesma semana; DAX no máximo 1 vez por semana; a dica técnica reveza DAX → SQL → Python → Power Automate → Power Query (nunca a mesma em 2 semanas seguidas). Antes de criar, leia os posts das 3 últimas semanas em `posts/` para não repetir tema nem gancho.

### Linhas

1. **Bastidores de entrega** (carro-chefe): problema real → solução → resultado, contando como foi construído. Fonte principal: o **Projeto da quinzena** (abaixo) e projetos próprios do Wallan (automação deste Instagram com IA e GitHub Actions a custo zero, leitor de XML de notas para contadores, app de reembolso de despesas com código aberto, simulador CLT x PJ, extrato do cartão que chega sozinho no Power BI, Raio-X da Reforma). Nunca use dado real de cliente. Cases do emprego do Wallan só quando ele mesmo trouxer, sem mencionar nada sobre a empresa (nome, área, produto, pessoas ou sistemas internos) e sem nenhum print de tabela ou banco de dados: código e telas sempre com nomes e dados fictícios (ex.: `Pedidos`, `Clientes`), sinalizados como exemplo fictício. No Instagram, são apresentados como case do fundador, nunca como cliente da Single.
2. **Um problema, 4 ferramentas:** o mesmo desafio resolvido em Excel, Power Query, SQL e Python (ex.: juntar 50 planilhas de uma pasta). Termina perguntando "qual é o seu jeito?".
3. **Opinião:** uma posição clara que gera conversa, com respeito e sem política (ex.: "Ninguém pediu um dashboard. Pediram uma decisão."). Pode ser enquete.
4. **Quanto custa o manual:** a conta de horas e dinheiro de uma tarefa repetitiva e a automação que acaba com ela. Fala com o gestor que paga.
5. **Dados que contam história:** um dado público e neutro (ANP, Banco Central, IBGE, vagas de tecnologia) num painel com um insight. Sempre com fonte e data; números conferidos.
6. **Reforma Tributária: assunto da semana** (toda semana, ver abaixo).
7. **Dica técnica da semana** (1 por semana, revezando a tecnologia).

### Instagram (@singletecnologia): 5 por semana, voz da empresa, para o gestor

| Dia | Linha |
| --- | --- |
| Segunda | Bastidores de entrega |
| Terça | Dica técnica da semana |
| Quarta | Quanto custa o manual **ou** Um problema, 4 ferramentas |
| Quinta | Reforma Tributária: assunto da semana |
| Sexta | Dados que contam história **ou** Opinião |

Pelo menos 1 Reel por semana (de preferência o Bastidores, com gravação de tela do projeto). Todo post: gancho forte na 1ª lâmina (ou nos 2 primeiros segundos do Reel) e última lâmina com chamada para **salvar**, **enviar a um colega** ou **comentar uma palavra-chave** para receber um material.

### LinkedIn pessoal do Wallan: 3 por semana (terça, quarta e quinta, 12:15), primeira pessoa

Escrito como o Wallan fala: história, aprendizado, opinião. Pode partir do mesmo tema do Instagram da semana, mas é reescrito para o LinkedIn (não é a legenda colada). Linhas preferidas: Bastidores (sempre que houver Projeto da quinzena), Opinião, Um problema e 4 ferramentas, Carreira (lições de 7 anos com dados). Formatos: carrossel em PDF, texto puro ou texto com 1 imagem. Quando houver material, termina com "Comente PALAVRA que eu te mando o link" (as respostas são preparadas pela tarefa de respostas do LinkedIn e aprovadas pelo Wallan). Até 3 hashtags. Nunca política.

### Projeto da quinzena

A cada 2 semanas, o Wallan desenvolve uma solução nova (aplicação, automação ou dashboard) e manda: o que é e que problema resolve (2 ou 3 frases), de 3 a 5 prints ou uma gravação de tela, as tecnologias e se o código ou modelo pode ser aberto. Ficam em `assets/projetos/AAAA-MM-DD-nome/` (notas.md + imagens/vídeo). Ciclo: **semana 1, bastidores** ("estou construindo X para resolver Y": post no LinkedIn + Reel com a tela); **semana 2, entrega** ("como fiz" no LinkedIn + carrossel antes e depois + Reel da demonstração; se o código ou modelo puder ser aberto, vira material com palavra-chave). Depois, o projeto vira exemplo nas outras linhas. Use só dados fictícios ou anonimizados nas artes. Se na quinzena não chegar projeto, siga com as outras linhas e lembre o Wallan no pull request.

### Reforma Tributária (toda semana)

Pegar um fato atual da semana (prazo que vence, mudança nas notas, regra nova do Simples, CBS e IBS) e mostrar o que muda na prática para a empresa ou o escritório de contabilidade. Pesquisar em fontes oficiais (Receita Federal, CGIBS, Portal da NF-e) e em imprensa econômica; citar a fonte e a data na lâmina de dados. Nunca afirmar prazo ou alíquota sem conferir na semana. A última lâmina leva ao **Raio-X da Reforma Tributária** (painel que lê os XMLs das notas e compara os impostos de hoje com CBS e IBS; página https://singletecnologia.netlify.app/reforma), com a palavra-chave `RAIOX`. Tom informativo, sem alarmismo e sem opinião política.

### Materiais (o que a pessoa recebe ao comentar)

Todo post com palavra-chave entrega um material de verdade, nunca só o link do site.

- **Biblioteca Single** (`biblioteca/`, publicada em https://singletecnologia.netlify.app/biblioteca): hoje com 60 medidas DAX por área, em `biblioteca/medidas.js`. Palavra-chave `DAX` sempre entrega a Biblioteca. Quando um post ensinar uma medida nova e útil, acrescente-a à Biblioteca (conferindo a fórmula). Depois virão as seções SQL (`SQL`), Python (`PYTHON`) e Automação: crie a seção quando houver pelo menos 20 itens bons.
- **PDFs** em `materiais/` (fonte HTML em `materiais/fonte/`, no visual v2), gerados com `python scripts/pdf.py html materiais/fonte/NOME.html materiais/NOME.pdf`. Prontos: `caminho-dados.pdf` (checklist com 10 perguntas, palavra `SINGLE`), `dax-financeiro.pdf` (10 medidas DAX, substituído pela Biblioteca) e `python-planilhas.pdf` (10 receitas de Python para planilhas, palavra `PYTHON`; base para a futura seção Python da Biblioteca).
- Reaproveite um material existente quando o tema for o mesmo.
- **Links sempre pelo site da Single:** `https://singletecnologia.netlify.app/biblioteca` e `https://singletecnologia.netlify.app/materiais/NOME.pdf`. O site no Netlify repassa esses endereços para o GitHub Pages (arquivo `_redirects` do site), então tudo que entra em `biblioteca/` e `materiais/` aparece lá sozinho.

## Formato de cada post

Pasta `posts/AAAA-MM-DD/` (a data é o dia da publicação, de segunda a sexta):

- `slides.html` — lâminas em `<section class="slide">`, usando `../../templates/base.css`.
- `01.jpg`, `02.jpg`, ... — geradas com `python scripts/render.py posts/AAAA-MM-DD/slides.html` (1080x1350, JPEG).
- Reel: quadros com `render.py --reel --prefixo quadro` e vídeo com `scripts/reel.py` → `video.mp4` (1080x1920). Música só livre de direitos.
- `legenda.txt` — legenda final, até 5 hashtags no fim.
- `story-01.jpg` — story que avisa do post novo, gerado com `python scripts/gerar_story.py posts/AAAA-MM-DD` (usa a capa; se houver palavra-chave, chama para comentar). É publicado automaticamente logo depois do post.
- LinkedIn (só nos dias com post no LinkedIn: terça, quarta e quinta): `linkedin.txt` (texto na voz do Wallan, gancho na 1ª linha, até 3 hashtags) e, se for carrossel, `linkedin.pdf`. O PDF pode ser o carrossel do Instagram (`python scripts/pdf.py carrossel posts/AAAA-MM-DD`) ou lâminas próprias em `linkedin.html` (`render.py posts/AAAA-MM-DD/linkedin.html --prefixo li-` e depois `pdf.py carrossel posts/AAAA-MM-DD li-`). Se o post do LinkedIn tiver palavra-chave, registre em `post.json` como `"linkedin": {"palavra_chave": "DAX", "material_url": "..."}`. Aprovar o pull request aprova também o LinkedIn: a tarefa agendada "LinkedIn — agendar o post aprovado do dia" (dias úteis, 8:43) agenda o `linkedin.txt` do dia para as 12:15, e a tarefa "LinkedIn — respostas à palavra-chave" prepara as respostas aos comentários para o Wallan aprovar.
- `post.json`:

```json
{
  "data": "2026-11-09",
  "tipo": "carrossel",
  "midias": ["01.jpg", "02.jpg", "03.jpg"],
  "legenda_arquivo": "legenda.txt",
  "palavra_chave": "DAX",
  "material_url": "https://singletecnologia.netlify.app/materiais/dax-financeiro.pdf",
  "material_nome": "o PDF com 10 medidas DAX",
  "mensagem_dm": "Oi! Aqui está o material: {material}\n\nSe quiser conversar sobre dados na sua empresa, é só responder.",
  "stories": ["story-01.jpg"],
  "trial_reel": false,
  "status": "aprovado"
}
```

`tipo`: `imagem`, `carrossel` (2 a 10 mídias) ou `reel` (`midias: ["video.mp4"]`, `capa` opcional). `palavra_chave`, `material_url`, `material_nome` e `stories` são opcionais. Só é publicado o que estiver com `status: aprovado` (use `pausado` para segurar um post). Os scripts preenchem `media_id`, `permalink`, `story_ids` e `status: publicado` depois de publicar.

## Rotina semanal de conteúdo (tarefa agendada de domingo)

1. Ler o relatório mais recente em `relatorios/` e ver quais temas e formatos tiveram mais envios, salvos e seguidores ganhos.
2. Pesquisar dúvidas reais de Power BI e DAX da semana (comunidade Microsoft Fabric, Reddit r/PowerBI) e os comentários recebidos.
3. Pesquisar as notícias da semana sobre a Reforma Tributária para o post da linha "assunto da semana", e ver se há Projeto da quinzena novo em `assets/projetos/`.
4. Criar os 5 posts do Instagram e os 3 do LinkedIn (terça, quarta e quinta) seguindo a estratégia de conteúdo e o sistema visual v2, com pelo menos 1 Reel e respeitando as regras de variedade. Cada post com palavra-chave entrega o seu material (Biblioteca ou PDF, novo ou reaproveitado).
5. Gerar as imagens com `render.py`, o story com `gerar_story.py` e o PDF do LinkedIn quando houver, e **olhar cada imagem** antes de seguir: texto cortado, sobreposição, cartão cobrindo texto ou contraste ruim devem ser corrigidos. Conferir a conta de todo número de exemplo e cada fórmula.
6. Validar com `python scripts/publicar.py --data AAAA-MM-DD --simular` para cada dia.
7. Criar a branch `semana-AAAA-MM-DD` (data da segunda-feira), fazer commit e abrir um pull request com o título "Semana de AAAA-MM-DD", listando cada dia com linha editorial, tema, formato, legenda, texto do LinkedIn e links das imagens.
8. Enquanto as fotos do Wallan não chegarem, lembrar no pull request: "Fotos pendentes: mande 5 a 10 fotos suas para usar nas capas e Reels." Quando chegarem (pasta `assets/fotos/`), usar em pelo menos 1 capa ou Reel por semana.

**Atenção:** esta sessão não consegue enviar arquivos dentro de `.github/workflows/` (o GitHub recusa). Mudanças de agendamento precisam ser feitas pelo Wallan no site do GitHub.

**Confiabilidade:** os horários agendados do GitHub atrasam ou são pulados com frequência. Por isso a tarefa agendada "Instagram — segunda tentativa de publicação" (dias úteis, 11:56) dispara `publicar.yml` se o post do dia ainda não saiu e depois dispara `comentarios.yml` uma vez, que no disparo manual fica de plantão (`--plantao 340`, conferindo a cada 3 minutos). O `publicar.py` confere no Instagram antes de publicar, então disparos repetidos não duplicam o post.
