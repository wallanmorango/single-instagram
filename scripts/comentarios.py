"""Comentário vira DM: responde quem comentou a palavra-chave de um post.

Para cada post publicado que tenha "palavra_chave" no post.json:
  1. responde o comentário em público (texto curto, alternando variações);
  2. envia 1 resposta privada (DM) com o material, pelo recurso oficial de
     respostas privadas da API (uma por comentário, até 7 dias depois dele).
Os IDs já atendidos ficam em estado/comentarios.json para nunca repetir.
"""
import random
import sys
import time
import unicodedata
import datetime as dt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ig  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
ESTADO = ROOT / "estado" / "comentarios.json"
MAX_POR_EXECUCAO = 25
JANELA_DIAS = 7

RESPOSTAS_PADRAO = [
    "Te mandei no direct! Confere lá 📩",
    "Enviado no seu direct 🚀",
    "Pronto, já está no seu direct!",
]


def normalizar(texto: str) -> str:
    texto = unicodedata.normalize("NFKD", texto or "")
    return "".join(c for c in texto if not unicodedata.combining(c)).lower()


def contem_palavra(texto: str, palavra: str) -> bool:
    palavras = normalizar(texto).replace("!", " ").replace(".", " ").replace(",", " ").split()
    return normalizar(palavra) in palavras


def posts_com_palavra_chave():
    for arq in sorted((ROOT / "posts").glob("*/post.json")):
        post = ig.load_json(arq, {})
        if post.get("status") == "publicado" and post.get("media_id") and post.get("palavra_chave"):
            yield post


def main():
    estado = ig.load_json(ESTADO, {"respondidos": []})
    respondidos = set(estado["respondidos"])
    minha_conta = ig.get(ig.user_id(), fields="username").get("username", "").lower()
    agora = dt.datetime.now(dt.timezone.utc)
    enviados = 0

    for post in posts_com_palavra_chave():
        comentarios = ig.paginate(f"{post['media_id']}/comments", limit_pages=3,
                                  fields="id,text,timestamp,username", limit=50)
        for c in comentarios:
            if enviados >= MAX_POR_EXECUCAO:
                break
            cid = c["id"]
            if cid in respondidos or (c.get("username") or "").lower() == minha_conta:
                continue
            quando = dt.datetime.strptime(c["timestamp"], "%Y-%m-%dT%H:%M:%S%z")
            if (agora - quando).days >= JANELA_DIAS:
                respondidos.add(cid)
                continue
            if not contem_palavra(c.get("text", ""), post["palavra_chave"]):
                continue

            mensagem = post.get("mensagem_dm") or (
                "Oi! Aqui está o material que você pediu: {material}\n\n"
                "Se quiser conversar sobre dados e BI na sua empresa, é só responder aqui. "
                "Single Tecnologia: solicitou, entregamos."
            )
            mensagem = mensagem.format(material=post.get("material_url", "https://singletecnologia.netlify.app"))
            try:
                ig.post(f"{ig.user_id()}/messages",
                        json_body={"recipient": {"comment_id": cid}, "message": {"text": mensagem}})
                resposta = random.choice(post.get("respostas_publicas") or RESPOSTAS_PADRAO)
                ig.post(f"{cid}/replies", params={"message": f"@{c.get('username')} {resposta}"})
                print(f"Atendido: @{c.get('username')} no post {post['data']}")
                enviados += 1
            except ig.IGError as exc:
                print(f"Falha no comentário {cid}: {exc}", file=sys.stderr)
            respondidos.add(cid)
            time.sleep(random.uniform(4, 9))

    estado["respondidos"] = sorted(respondidos)[-5000:]
    ig.save_json(ESTADO, estado)
    print(f"{enviados} comentário(s) atendido(s).")


if __name__ == "__main__":
    main()
