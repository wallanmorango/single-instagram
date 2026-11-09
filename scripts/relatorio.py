"""Relatório: seguidores e desempenho de cada post dos últimos 30 dias, com horário de publicação.

Gera relatorios/AAAA-MM-DD.md, acrescenta uma linha em estado/seguidores.csv e grava
estado/posts.csv (uma linha por post, para análise de horário, formato e tema).
A tarefa de conteúdo de domingo lê o relatório mais recente para decidir os temas.
"""
import csv
import datetime as dt
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ig  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("America/Sao_Paulo")
METRICAS = ["reach", "views", "shares", "saved", "total_interactions", "follows", "profile_visits"]
NOMES = {"reach": "Alcance", "views": "Visualizações", "shares": "Envios", "saved": "Salvos",
         "total_interactions": "Interações", "follows": "Seguidores ganhos", "profile_visits": "Visitas ao perfil"}


def insights(media_id: str) -> dict:
    def ler(resp):
        return {m["name"]: (m.get("values") or [{}])[0].get("value", m.get("total_value", {}).get("value"))
                for m in resp.get("data", [])}
    try:
        return ler(ig.get(f"{media_id}/insights", metric=",".join(METRICAS)))
    except ig.IGError:
        resultado = {}
        for m in METRICAS:  # nem todo tipo de mídia aceita todas as métricas
            try:
                resultado.update(ler(ig.get(f"{media_id}/insights", metric=m)))
            except ig.IGError:
                pass
        return resultado


DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]


def horas_dos_comentarios(media_id: str) -> list:
    """Hora (Brasília) de cada comentário do post, para ver quando o público interage."""
    try:
        dados = ig.paginate(f"{media_id}/comments", limit_pages=2, fields="timestamp", limit=50)
    except ig.IGError:
        return []
    horas = []
    for c in dados:
        try:
            horas.append(dt.datetime.strptime(c["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(TZ).hour)
        except (KeyError, ValueError):
            pass
    return horas


def seguidores_online() -> dict:
    """Seguidores online por hora (métrica online_followers). Nem toda conta recebe."""
    try:
        resp = ig.get(f"{ig.user_id()}/insights", metric="online_followers", period="lifetime")
        valores = (resp.get("data") or [{}])[0].get("values") or [{}]
        return {int(h): v for h, v in (valores[-1].get("value") or {}).items()}
    except (ig.IGError, ValueError, KeyError, IndexError, AttributeError):
        return {}


def taxa(dados: dict) -> str:
    alcance, inter = dados.get("reach") or 0, dados.get("total_interactions") or 0
    return f"{100 * inter / alcance:.1f}%".replace(".", ",") if alcance else "–"


def main():
    hoje = dt.datetime.now(TZ).date()
    print(f"Token do tipo {ig.tipo_token()}, API {ig.base()}, conta {ig.user_id()}")
    conta = ig.get(ig.user_id(), fields="username,followers_count,follows_count,media_count")
    seguidores = conta.get("followers_count", 0)

    historico = ROOT / "estado" / "seguidores.csv"
    anterior = None
    if historico.exists():
        linhas = list(csv.reader(historico.open(encoding="utf-8")))[1:]
        if linhas:
            anterior = int(linhas[-1][1])
    novo = not historico.exists()
    historico.parent.mkdir(parents=True, exist_ok=True)
    with historico.open("a", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        if novo:
            w.writerow(["data", "seguidores"])
        w.writerow([hoje.isoformat(), seguidores])

    corte = dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=30)
    midias = ig.paginate(f"{ig.user_id()}/media", limit_pages=3,
                         fields="id,caption,media_product_type,media_type,timestamp,permalink,like_count,comments_count", limit=25)
    linhas = []
    for m in midias:
        quando = dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
        if quando < corte:
            continue
        dados = insights(m["id"])
        titulo = (m.get("caption") or "").strip().split("\n")[0][:60]
        formato = "Reel" if m.get("media_product_type") == "REELS" else (
            "Carrossel" if m.get("media_type") == "CAROUSEL_ALBUM" else "Imagem")
        dados["likes"] = m.get("like_count")
        dados["comments"] = m.get("comments_count")
        local = quando.astimezone(TZ)
        linhas.append((local.date().isoformat(), formato, titulo, m.get("permalink"), dados,
                       local.strftime("%H:%M"), DIAS[local.weekday()], horas_dos_comentarios(m["id"])))

    linhas.sort(key=lambda l: ((l[4].get("shares") or 0), (l[4].get("saved") or 0)), reverse=True)
    variacao = "" if anterior is None else f" ({seguidores - anterior:+d} desde o último relatório)"

    md = [f"# Relatório do Instagram — {hoje.isoformat()}", "",
          f"**@{conta.get('username')}**: {seguidores} seguidores{variacao}, "
          f"seguindo {conta.get('follows_count')}, {conta.get('media_count')} posts.", "",
          "## Posts dos últimos 30 dias (ordenados por envios e salvos)", "",
          "| Data | Dia | Hora | Formato | Post | Curtidas | Comentários | Engajamento | "
          + " | ".join(NOMES[m] for m in METRICAS) + " |",
          "| --- | --- | --- | --- | --- | --- | --- | --- | " + " | ".join("---" for _ in METRICAS) + " |"]
    for data, formato, titulo, link, dados, hora, dia, _ in linhas:
        valores = " | ".join(str(dados.get(m, "–")) for m in METRICAS)
        md.append(f"| {data} | {dia} | {hora} | {formato} | [{titulo or 'post'}]({link}) | "
                  f"{dados.get('likes', '–')} | {dados.get('comments', '–')} | {taxa(dados)} | {valores} |")
    md += ["", "Engajamento = interações ÷ alcance."]

    # Médias por faixa de horário de publicação
    faixas = {}
    for l in linhas:
        faixa = f"{l[5][:2]}h"
        faixas.setdefault(faixa, []).append(l[4])
    if faixas:
        md += ["", "## Por horário de publicação (média por post)", "",
               "| Horário | Posts | Alcance | Curtidas | Comentários | Envios | Salvos | Engajamento |",
               "| --- | --- | --- | --- | --- | --- | --- | --- |"]
        for faixa in sorted(faixas):
            g = faixas[faixa]
            med = lambda k: sum((d.get(k) or 0) for d in g) / len(g)  # noqa: E731
            eng = f"{100 * med('total_interactions') / med('reach'):.1f}%".replace(".", ",") if med("reach") else "–"
            num = lambda v: f"{v:.1f}".replace(".", ",")  # noqa: E731
            md.append(f"| {faixa} | {len(g)} | {med('reach'):.0f} | {num(med('likes'))} | {num(med('comments'))} | "
                      f"{num(med('shares'))} | {num(med('saved'))} | {eng} |")

    contagem = {}
    for l in linhas:
        for h in l[7]:
            contagem[h] = contagem.get(h, 0) + 1
    if contagem:
        md += ["", "## Hora em que os comentários chegam (Brasília)", "",
               "| Hora | Comentários |", "| --- | --- |"]
        md += [f"| {h:02d}h | {contagem[h]} |" for h in sorted(contagem)]

    online = seguidores_online()
    if online:
        md += ["", "## Seguidores online por hora (como a Meta informa; o fuso da Meta pode não ser o de Brasília)", "",
               "| Hora | Seguidores online |", "| --- | --- |"]
        md += [f"| {h:02d}h | {online[h]} |" for h in sorted(online)]

    with (ROOT / "estado" / "posts.csv").open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["data", "dia", "hora", "formato", "post", "link", "curtidas", "comentarios"] + METRICAS
                   + ["horas_dos_comentarios"])
        for data, formato, titulo, link, dados, hora, dia, horas in linhas:
            w.writerow([data, dia, hora, formato, titulo, link, dados.get("likes"), dados.get("comments")]
                       + [dados.get(m) for m in METRICAS] + [" ".join(str(h) for h in horas)])
    if linhas:
        md += ["", "## Para a próxima semana", "",
               "- Repetir o tema e o formato dos 3 primeiros da tabela.",
               "- Evitar o tema dos 3 últimos, ou testar com outro gancho."]

    saida = ROOT / "relatorios" / f"{hoje.isoformat()}.md"
    saida.parent.mkdir(parents=True, exist_ok=True)
    saida.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(f"Relatório salvo em {saida.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
