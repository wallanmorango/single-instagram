"""Publica no Instagram os posts aprovados (na branch main) com data de hoje.

Uso:
  python scripts/publicar.py                 # publica os posts de hoje (horário de Brasília)
  python scripts/publicar.py --data 2026-11-09
  python scripts/publicar.py --data 2026-11-09 --simular   # só valida, não publica

Cada post fica em posts/AAAA-MM-DD/ com post.json, legenda e mídias (ver CLAUDE.md).
As mídias precisam estar públicas no GitHub Pages (PAGES_BASE_URL).
"""
import argparse
import datetime as dt
import os
import sys
import time
from pathlib import Path
from urllib.parse import quote
from zoneinfo import ZoneInfo

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ig  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
TZ = ZoneInfo("America/Sao_Paulo")
LIMITE_LEGENDA = 2200
LIMITE_HASHTAGS = 5


def pages_base() -> str:
    base = os.environ.get("PAGES_BASE_URL", "").strip() or "https://wallanmorango.github.io/single-instagram"
    return base.rstrip("/")


def posts_do_dia(data: str):
    for arq in sorted((ROOT / "posts").glob("*/post.json")):
        post = ig.load_json(arq, {})
        if post.get("data", arq.parent.name) != data:
            continue
        if post.get("status") == "publicado":
            print(f"[{arq.parent.name}] já publicado, ignorando.")
            continue
        if post.get("status") != "aprovado":
            print(f"[{arq.parent.name}] status '{post.get('status')}', só publica 'aprovado'. Ignorando.")
            continue
        yield arq, post


def validar(pasta: Path, post: dict) -> str:
    tipo = post.get("tipo")
    if tipo not in {"imagem", "carrossel", "reel"}:
        raise ValueError(f"tipo inválido: {tipo}")
    midias = post.get("midias") or []
    if not midias:
        raise ValueError("lista 'midias' vazia")
    for m in midias:
        if not (pasta / m).exists():
            raise ValueError(f"mídia não encontrada: {m}")
        if tipo != "reel" and not m.lower().endswith((".jpg", ".jpeg", ".mp4")):
            raise ValueError(f"imagens precisam ser JPEG: {m}")
    if tipo == "carrossel" and not 2 <= len(midias) <= 10:
        raise ValueError("carrossel precisa ter de 2 a 10 mídias")
    if tipo == "reel" and not midias[0].lower().endswith(".mp4"):
        raise ValueError("reel precisa de um .mp4")
    legenda = (pasta / post.get("legenda_arquivo", "legenda.txt")).read_text(encoding="utf-8").strip()
    if len(legenda) > LIMITE_LEGENDA:
        raise ValueError(f"legenda com {len(legenda)} caracteres (máx. {LIMITE_LEGENDA})")
    hashtags = [p for p in legenda.split() if p.startswith("#")]
    if len(hashtags) > LIMITE_HASHTAGS:
        raise ValueError(f"{len(hashtags)} hashtags (máx. {LIMITE_HASHTAGS})")
    for s in post.get("stories") or []:
        if not (pasta / s).exists():
            raise ValueError(f"story não encontrado: {s}")
        if not s.lower().endswith((".jpg", ".jpeg")):
            raise ValueError(f"story precisa ser JPEG: {s}")
    return legenda


def publicar_stories(pasta: Path, post: dict) -> list:
    """Publica os stories do post (depois do post do feed). Falha aqui não desfaz o post."""
    ids = []
    for s in post.get("stories") or []:
        url = url_publica(pasta, s)
        esperar_url(url)
        cid = ig.post(f"{ig.user_id()}/media", params={"media_type": "STORIES", "image_url": url})["id"]
        esperar_container(cid)
        ids.append(ig.post(f"{ig.user_id()}/media_publish", params={"creation_id": cid})["id"])
        time.sleep(5)
    return ids


def url_publica(pasta: Path, arquivo: str) -> str:
    return f"{pages_base()}/posts/{quote(pasta.name)}/{quote(arquivo)}"


def esperar_url(url: str, minutos: int = 10):
    """O GitHub Pages leva alguns minutos para publicar arquivos novos."""
    fim = time.time() + minutos * 60
    while time.time() < fim:
        try:
            r = requests.head(url, timeout=30, allow_redirects=True)
            if r.status_code == 200:
                return
        except requests.RequestException:
            pass
        time.sleep(20)
    raise RuntimeError(f"URL pública não respondeu: {url}")


def esperar_container(cid: str, minutos: int = 15):
    fim = time.time() + minutos * 60
    while time.time() < fim:
        st = ig.get(cid, fields="status_code,status")
        code = st.get("status_code")
        if code == "FINISHED":
            return
        if code in {"ERROR", "EXPIRED"}:
            raise RuntimeError(f"container {cid} com erro: {st.get('status')}")
        time.sleep(10)
    raise RuntimeError(f"container {cid} não ficou pronto a tempo")


def criar_item(url: str, carrossel: bool = False) -> str:
    params = {"is_carousel_item": "true"} if carrossel else {}
    if url.lower().endswith(".mp4"):
        params.update(media_type="VIDEO", video_url=url)
    else:
        params["image_url"] = url
    return ig.post(f"{ig.user_id()}/media", params=params)["id"]


def publicar(pasta: Path, post: dict, legenda: str) -> dict:
    urls = [url_publica(pasta, m) for m in post["midias"]]
    for u in urls:
        esperar_url(u)

    uid = ig.user_id()
    tipo = post["tipo"]
    if tipo == "imagem":
        cid = ig.post(f"{uid}/media", params={"image_url": urls[0], "caption": legenda})["id"]
    elif tipo == "carrossel":
        filhos = []
        for u in urls:
            filho = criar_item(u, carrossel=True)
            esperar_container(filho)
            filhos.append(filho)
        cid = ig.post(f"{uid}/media", params={
            "media_type": "CAROUSEL", "children": ",".join(filhos), "caption": legenda,
        })["id"]
    else:
        params = {"media_type": "REELS", "video_url": urls[0], "caption": legenda}
        if post.get("capa"):
            capa = url_publica(pasta, post["capa"])
            esperar_url(capa)
            params["cover_url"] = capa
        if post.get("trial_reel"):
            params["trial_params"] = '{"graduation_strategy":"SS_PERFORMANCE"}'
        else:
            params["share_to_feed"] = "true"
        cid = ig.post(f"{uid}/media", params=params)["id"]

    esperar_container(cid)
    media_id = ig.post(f"{uid}/media_publish", params={"creation_id": cid})["id"]
    info = ig.get(media_id, fields="permalink")
    return {"media_id": media_id, "permalink": info.get("permalink")}


def ja_no_instagram(legenda: str, data: str):
    """Trava contra post duplicado: procura nas últimas mídias da conta um post do mesmo dia
    com a mesma primeira linha de legenda. Protege quando o agendamento e a segunda tentativa
    rodam perto um do outro, ou quando o estado não foi salvo no repositório."""
    try:
        recentes = ig.get(f"{ig.user_id()}/media", fields="id,caption,timestamp,permalink", limit=10).get("data", [])
    except Exception as exc:  # noqa: BLE001 (se a consulta falhar, segue o fluxo normal)
        print(f"Aviso: não consegui conferir posts recentes ({exc}).", file=sys.stderr)
        return None
    primeira = legenda.strip().split("\n")[0].strip()[:80]
    for m in recentes:
        try:
            quando = dt.datetime.strptime(m["timestamp"], "%Y-%m-%dT%H:%M:%S%z").astimezone(TZ).date().isoformat()
        except (KeyError, ValueError):
            continue
        if quando == data and (m.get("caption") or "").strip().startswith(primeira):
            return m
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=dt.datetime.now(TZ).date().isoformat())
    ap.add_argument("--simular", action="store_true")
    args = ap.parse_args()

    erros = 0
    encontrados = 0
    for arq, post in posts_do_dia(args.data):
        encontrados += 1
        pasta = arq.parent
        try:
            legenda = validar(pasta, post)
            if args.simular:
                print(f"[{pasta.name}] OK (simulação): {post['tipo']} com {len(post['midias'])} mídia(s)"
                      f" e {len(post.get('stories') or [])} story(s).")
                continue
            horario = (post.get("horario") or "").strip()
            if horario:
                h, m = (int(x) for x in horario.split(":"))
                liberado = dt.datetime.now(TZ).replace(hour=h, minute=m, second=0, microsecond=0) - dt.timedelta(minutes=15)
                if args.data == dt.datetime.now(TZ).date().isoformat() and dt.datetime.now(TZ) < liberado:
                    print(f"[{pasta.name}] horário marcado para {horario}: ainda não é hora, não publiquei.")
                    continue
            existente = ja_no_instagram(legenda, args.data)
            if existente:
                post.update(media_id=existente["id"], permalink=existente.get("permalink"), status="publicado")
                post.pop("erro", None)
                ig.save_json(arq, post)
                print(f"[{pasta.name}] já estava no Instagram, não publiquei de novo: {existente.get('permalink')}")
                continue
            resultado = publicar(pasta, post, legenda)
            post.update(resultado, status="publicado",
                        publicado_em=dt.datetime.now(TZ).isoformat(timespec="seconds"))
            post.pop("erro", None)
            ig.save_json(arq, post)
            print(f"[{pasta.name}] publicado: {resultado['permalink']}")
            if post.get("stories"):
                try:
                    post["story_ids"] = publicar_stories(pasta, post)
                    print(f"[{pasta.name}] {len(post['story_ids'])} story(s) publicado(s).")
                except Exception as exc:  # noqa: BLE001
                    post["story_erro"] = str(exc)[:500]
                    print(f"[{pasta.name}] story falhou (o post está no ar): {exc}", file=sys.stderr)
                ig.save_json(arq, post)
        except Exception as exc:  # noqa: BLE001
            erros += 1
            post["erro"] = str(exc)[:500]
            ig.save_json(arq, post)
            print(f"[{pasta.name}] ERRO: {exc}", file=sys.stderr)
    if not encontrados:
        print(f"Nenhum post pendente para {args.data}.")
    sys.exit(1 if erros else 0)


if __name__ == "__main__":
    main()
