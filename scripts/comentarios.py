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
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--plantao", type=int, default=0,
                    help="minutos de plantão: repete a checagem a cada 3 minutos até o tempo acabar")
    args = ap.parse_args()

    estado = ig.load_json(ESTADO, {"respondidos": []})
    respondidos = set(estado["respondidos"])
    minha_conta = ig.get(ig.user_id(), fields="username").get("username", "").lower()
    fim = time.time() + args.plantao * 60
    total = 0
    while True:
        if args.plantao:
            atualizar_posts()
        try:
            total += rodada(respondidos, minha_conta)
        except ig.IGError as exc:
            print(f"Rodada com erro (tento de novo na próxima): {exc}", file=sys.stderr)
        estado["respondidos"] = sorted(respondidos)[-5000:]
        ig.save_json(ESTADO, estado)
        if time.time() + INTERVALO_PLANTAO > fim:
            break
        time.sleep(INTERVALO_PLANTAO)
    print(f"{total} comentário(s) atendido(s).")


INTERVALO_PLANTAO = 180


def atualizar_posts():
    """No plantão, traz da main os post.json mais recentes (ex.: post publicado depois do início)."""
    import subprocess
    try:
        subprocess.run(["git", "fetch", "-q", "origin", "main"], cwd=ROOT, check=True, timeout=60)
        subprocess.run(["git", "checkout", "origin/main", "--", "posts"], cwd=ROOT, check=True, timeout=60)
    except Exception as exc:  # noqa: BLE001
        print(f"Aviso: não consegui atualizar os posts ({exc}).", file=sys.stderr)


def rodada(respondidos: set, minha_conta: str) -> int:
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
            # Proteção extra: se a conta já respondeu este comentário, não responde de novo
            # (vale mesmo se o estado não tiver sido salvo no repositório).
            try:
                respostas = ig.get(f"{cid}/replies", fields="username").get("data", [])
            except ig.IGError:
                respostas = []
            if any((r.get("username") or "").lower() == minha_conta for r in respostas):
                respondidos.add(cid)
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

    return enviados


if __name__ == "__main__":
    main()
