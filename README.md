# single-instagram

Automação gratuita do Instagram **@singletecnologia**: o Claude cria os posts, você aprova pelo GitHub e o GitHub Actions publica, responde comentários com DM e gera o relatório semanal.

## Como funciona

| Etapa | Quem faz | Quando |
| --- | --- | --- |
| Criar os 5 posts da semana e abrir um pull request | Claude (tarefa agendada) | Domingo |
| Aprovar a semana (merge do pull request) | Você | Domingo, ~10 min |
| Publicar o post do dia | `publicar.yml` | Segunda a sexta, 11:40 |
| Responder quem comentou a palavra-chave e mandar o material por DM | `comentarios.yml` | A cada 15 min |
| Relatório de seguidores e desempenho | `relatorio.yml` | Segunda, 8:10 |
| Renovar o token do Instagram | `renovar-token.yml` | Dias 1 e 15 |

## Configuração (uma única vez)

1. **GitHub Pages:** Settings → Pages → Source: *Deploy from a branch* → `main` / `(root)` → Save.
2. **Variável do repositório:** Settings → Secrets and variables → Actions → aba *Variables* → `PAGES_BASE_URL` = `https://wallanmorango.github.io/single-instagram`.
3. **App na Meta e token do Instagram:** em developers.facebook.com, criar um app, adicionar o produto *Instagram* → *API setup with Instagram login*, adicionar a conta @singletecnologia e gerar o token com as permissões `instagram_business_basic`, `instagram_business_content_publish`, `instagram_business_manage_comments`, `instagram_business_manage_messages` e `instagram_business_manage_insights`.
4. **Secrets do repositório** (aba *Secrets*):
   - `IG_ACCESS_TOKEN`: o token gerado no passo 3.
   - `IG_USER_ID`: o ID da conta do Instagram mostrado na mesma tela.
   - `GH_PAT`: token *fine-grained* do GitHub só para este repositório, com permissão *Secrets: Read and write* (usado para renovar o token sozinho).
5. Testar: Actions → *Relatório semanal* → *Run workflow*. Se gerar um arquivo em `relatorios/`, está tudo certo.

Detalhes do formato dos posts e regras de conteúdo: [CLAUDE.md](CLAUDE.md).
