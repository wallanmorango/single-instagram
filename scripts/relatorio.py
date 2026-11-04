"""Relatório semanal: seguidores e desempenho de cada post dos últimos 30 dias.

Gera relatorios/AAAA-MM-DD.md e acrescenta uma linha em estado/seguidores.csv.
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


def main():
    hoje = dt.datetime.now(TZ).date()
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
                         fields="id,caption,media_product_type,media_type,timestamp,permalink", limit=25)
    linhas = []
    for m in midias:
        quando = dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
        if quando < corte:
            continue
        dados = insights(m["id"])
        titulo = (m.get("caption") or "").strip().split("\n")[0][:60]
        formato = "Reel" if m.get("media_product_type") == "REELS" else (
            "Carrossel" if m.get("media_type") == "CAROUSEL_ALBUM" else "Imagem")
        linhas.append((quando.astimezone(TZ).date().isoformat(), formato, titulo, m.get("permalink"), dados))

    linhas.sort(key=lambda l: ((l[4].get("shares") or 0), (l[4].get("saved") or 0)), reverse=True)
    variacao = "" if anterior is None else f" ({seguidores - anterior:+d} desde o último relatório)"

    md = [f"# Relatório do Instagram — {hoje.isoformat()}", "",
          f"**@{conta.get('username')}**: {seguidores} seguidores{variacao}, "
          f"seguindo {conta.get('follows_count')}, {conta.get('media_count')} posts.", "",
          "## Posts dos últimos 30 dias (ordenados por envios e salvos)", "",
          "| Data | Formato | Post | " + " | ".join(NOMES[m] for m in METRICAS) + " |",
          "| --- | --- | --- | " + " | ".join("---" for _ in METRICAS) + " |"]
    for data, formato, titulo, link, dados in linhas:
        valores = " | ".join(str(dados.get(m, "–")) for m in METRICAS)
        md.append(f"| {data} | {formato} | [{titulo or 'post'}]({link}) | {valores} |")
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
