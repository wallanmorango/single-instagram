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

## Linhas editoriais (por semana)

| Linha | Formato | Por semana | Para quem |
| --- | --- | --- | --- |
| Dica rápida de Power BI/DAX | Carrossel de 5 a 8 lâminas | 2 | Analistas |
| Antes e depois | Reel 15–30 s ou carrossel | 1 | Analistas e gestores |
| Erro comum | Carrossel | 1 | Analistas |
| Negócio e resultado / Reforma Tributária (alternar) | Carrossel | 1 | Donos, gestores, contadores |

Todo post: gancho forte na 1ª lâmina (ou nos 2 primeiros segundos do Reel) e última lâmina com chamada para **salvar**, **enviar a um colega** ou **comentar uma palavra-chave** para receber um material.

## Formato de cada post

Pasta `posts/AAAA-MM-DD/` (a data é o dia da publicação, de segunda a sexta):

- `slides.html` — lâminas em `<section class="slide">`, usando `../../templates/base.css`.
- `01.jpg`, `02.jpg`, ... — geradas com `python scripts/render.py posts/AAAA-MM-DD/slides.html` (1080x1350, JPEG).
- Reel: quadros com `render.py --reel --prefixo quadro` e vídeo com `scripts/reel.py` → `video.mp4` (1080x1920). Música só livre de direitos.
- `legenda.txt` — legenda final, até 5 hashtags no fim.
- `post.json`:

```json
{
  "data": "2026-11-09",
  "tipo": "carrossel",
  "midias": ["01.jpg", "02.jpg", "03.jpg"],
  "legenda_arquivo": "legenda.txt",
  "palavra_chave": "DAX",
  "material_url": "https://wallanmorango.github.io/single-instagram/materiais/dax-financeiro.pdf",
  "mensagem_dm": "Oi! Aqui está o material: {material}\n\nSe quiser conversar sobre dados na sua empresa, é só responder.",
  "trial_reel": false,
  "status": "aprovado"
}
```

`tipo`: `imagem`, `carrossel` (2 a 10 mídias) ou `reel` (`midias: ["video.mp4"]`, `capa` opcional). `palavra_chave` e `material_url` são opcionais. Os scripts preenchem `media_id`, `permalink` e `status: publicado` depois de publicar.

## Rotina semanal de conteúdo (tarefa agendada de domingo)

1. Ler o relatório mais recente em `relatorios/` e ver quais temas e formatos tiveram mais envios, salvos e seguidores ganhos.
2. Pesquisar dúvidas reais de Power BI e DAX da semana (comunidade Microsoft Fabric, Reddit r/PowerBI) e os comentários recebidos.
3. Criar 5 posts (segunda a sexta) seguindo as linhas editoriais, com pelo menos 1 Reel.
4. Gerar as imagens com `render.py` e **olhar cada imagem** antes de seguir: texto cortado, sobreposição ou contraste ruim devem ser corrigidos.
5. Validar com `python scripts/publicar.py --data AAAA-MM-DD --simular` para cada dia.
6. Criar a branch `semana-AAAA-MM-DD` (data da segunda-feira), fazer commit e abrir um pull request com o título "Semana de AAAA-MM-DD", listando cada dia com tema, formato, legenda e links das imagens.
