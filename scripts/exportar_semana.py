"""Monta a pasta da semana para o Wallan postar à mão (Instagram e LinkedIn).

Uso:
  python scripts/exportar_semana.py 2026-11-18 2026-11-22 [--saida exportar]

Cria <saida>/<DD-DD-MM>/ (ex.: 18-22-11) com duas pastas:
  Instagram/  "qua 18-11 - Tema - 01.jpg" ... (ou .mp4 + capa no Reel) e "qua 18-11 - Tema.txt" (legenda)
  LinkedIn/   "qua 18-11 - Tema - 01.jpg" ... e "qua 18-11 - Tema.txt" (texto do LinkedIn)
e um resumo.md com dia, conteúdo, arquivos e horário sugerido. A pasta é depois enviada
ao Google Drive do Wallan pela sessão do Claude (ver CLAUDE.md, "Pasta da semana").
"""
import argparse
import datetime as dt
import json
import hashlib
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DIAS = ["seg", "ter", "qua", "qui", "sex", "sáb", "dom"]
INVALIDOS = '<>:"/\\|?*'


def nome_curto(post: dict) -> str:
    nome = post.get("nome_conteudo") or post.get("linha") or post.get("tema") or "Post"
    nome = nome.split("(")[0].split(":")[0].strip()
    return "".join("-" if c in INVALIDOS else c for c in nome)[:60].strip()


def lâminas(pasta: Path, prefixo: str = "") -> list:
    return sorted(pasta.glob(f"{prefixo}[0-9][0-9].jpg"))


def exportar(inicio: dt.date, fim: dt.date, saida: Path) -> Path:
    destino = saida / f"{inicio:%d}-{fim:%d}-{fim:%m}"
    if destino.exists():
        shutil.rmtree(destino)
    ig, li = destino / "Instagram", destino / "LinkedIn"
    ig.mkdir(parents=True)
    li.mkdir(parents=True)
    linhas = []
    dia = inicio
    while dia <= fim:
        pasta = ROOT / "posts" / dia.isoformat()
        arq = pasta / "post.json"
        if arq.exists():
            post = json.loads(arq.read_text(encoding="utf-8"))
            base = f"{DIAS[dia.weekday()]} {dia:%d-%m} - {nome_curto(post)}"
            horario = post.get("horario") or "08:00"
            # Instagram
            arquivos_ig = []
            if post.get("tipo") == "reel":
                for m in post.get("midias", []):
                    shutil.copy(pasta / m, ig / f"{base}{Path(m).suffix}")
                    arquivos_ig.append(f"{base}{Path(m).suffix}")
                capa = pasta / (post.get("capa") or "quadro01.jpg")
                if capa.exists():
                    shutil.copy(capa, ig / f"{base} - capa.jpg")
                    arquivos_ig.append(f"{base} - capa.jpg")
            else:
                for i, m in enumerate(post.get("midias", []), start=1):
                    shutil.copy(pasta / m, ig / f"{base} - {i:02d}.jpg")
                arquivos_ig.append(f"{base} - 01 a {len(post.get('midias', [])):02d}.jpg")
            legenda = (pasta / post.get("legenda_arquivo", "legenda.txt")).read_text(encoding="utf-8").strip()
            (ig / f"{base}.txt").write_text(legenda + "\n", encoding="utf-8")
            palavra = post.get("palavra_chave")
            linhas.append(f"| {DIAS[dia.weekday()]} {dia:%d/%m} | Instagram | {nome_curto(post)} | "
                          f"`{base}` ({post.get('tipo')}) | {horario} | {palavra or '—'} |")
            # LinkedIn
            texto = pasta / "linkedin.txt"
            if texto.exists():
                nome_li = post.get("linkedin_nome") or nome_curto(post)
                nome_li = "".join("-" if c in INVALIDOS else c for c in nome_li)[:60].strip()
                base = f"{DIAS[dia.weekday()]} {dia:%d-%m} - {nome_li}"
                imgs = lâminas(pasta, "li-") if (pasta / "linkedin.html").exists() else []
                if (pasta / "linkedin.jpg").exists():
                    imgs = [pasta / "linkedin.jpg"]
                elif not imgs and (pasta / "linkedin.pdf").exists():
                    imgs = [pasta / m for m in post.get("midias", []) if m.endswith(".jpg")]
                for i, img in enumerate(imgs, start=1):
                    sufixo = "" if len(imgs) == 1 else f" - {i:02d}"
                    shutil.copy(img, li / f"{base}{sufixo}.jpg")
                shutil.copy(texto, li / f"{base}.txt")
                formato = "texto + 1 imagem" if len(imgs) == 1 else (f"carrossel {len(imgs)} imagens" if imgs else "só texto")
                palavra_li = (post.get("linkedin") or {}).get("palavra_chave")
                linhas.append(f"| {DIAS[dia.weekday()]} {dia:%d/%m} | LinkedIn | {nome_li} | "
                              f"`{base}` ({formato}) | 08:00 | {palavra_li or '—'} |")
        dia += dt.timedelta(days=1)
    resumo = ["# Semana " + destino.name, "",
              "| Dia | Rede | Conteúdo | Arquivos | Horário | Palavra-chave |",
              "| --- | --- | --- | --- | --- | --- |", *linhas, ""]
    (destino / "resumo.md").write_text("\n".join(resumo), encoding="utf-8")
    preparar_envio(destino)
    return destino


LIMITE_ENVIO = 3_000_000  # o conector do Google Drive aceita ~3,1 MB por arquivo
MIMES = {".jpg": "image/jpeg", ".mp4": "video/mp4", ".txt": "text/plain"}


def preparar_envio(destino: Path):
    """Cópias com nomes simples em <destino>/_envio e envio.json (título, pasta, referência)
    para a sessão do Claude subir ao Google Drive com mcp__Google_Drive__create_file."""
    envio = destino / "_envio"
    envio.mkdir()
    itens = []
    for i, arq in enumerate(sorted([*(destino / "Instagram").iterdir(), *(destino / "LinkedIn").iterdir()]), start=1):
        copia = envio / f"f{i:03d}{arq.suffix}"
        if arq.suffix == ".mp4" and arq.stat().st_size > LIMITE_ENVIO:
            subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(arq), "-c:v", "libx264",
                            "-preset", "slow", "-b:v", "850k", "-maxrate", "950k", "-bufsize", "1900k",
                            "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "96k", "-movflags", "+faststart",
                            str(copia)], check=True)
        else:
            shutil.copy(arq, copia)
        sha = hashlib.sha256(copia.read_bytes()).hexdigest()
        itens.append({"pasta": arq.parent.name, "titulo": arq.name, "mime": MIMES[arq.suffix],
                      "referencia": f"sha256:{sha}:{copia.resolve().as_posix()}"})
    (destino / "envio.json").write_text(json.dumps(itens, ensure_ascii=False, indent=1), encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("inicio")
    ap.add_argument("fim")
    ap.add_argument("--saida", default=str(ROOT / "exportar"))
    a = ap.parse_args()
    destino = exportar(dt.date.fromisoformat(a.inicio), dt.date.fromisoformat(a.fim), Path(a.saida))
    print(f"Pasta pronta: {destino}")
    print((destino / "resumo.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
