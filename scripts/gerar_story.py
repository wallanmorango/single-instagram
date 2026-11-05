"""Cria o story (1080x1920) que avisa do post novo, a partir da capa do post.

Uso: python scripts/gerar_story.py posts/2026-11-06

Lê post.json e usa 01.jpg (ou "capa") como imagem. Se o post tiver palavra_chave,
o story chama para comentar a palavra e receber o material ("material_nome").
Gera story.html e story-01.jpg na pasta do post e registra "stories" no post.json.
A API do Instagram não aceita figurinhas (link, enquete), então o story é só imagem.
"""
import html
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ig  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent

MODELO = """<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><title>Story</title>
<link rel="stylesheet" href="../../templates/base.css">
<style>
.slide.reel {{ padding: 250px 80px 0; }}
.toque {{ align-self: center; display: inline-flex; align-items: center; gap: 12px; font-weight: 700; font-size: 30px; padding: 16px 28px; border-radius: 99px; background: rgba(255,255,255,.12); border: 1.5px solid rgba(255,255,255,.25); color: #fff; }}
.toque svg {{ width: 30px; height: 30px; }}
.capa {{ position: relative; align-self: center; margin-top: 60px; width: 720px; }}
.capa img {{ width: 720px; height: 900px; display: block; border-radius: 34px; transform: rotate(-3deg); box-shadow: 0 60px 120px -30px rgba(0,0,0,.8), 0 0 0 2px rgba(255,255,255,.12); }}
.capa .novo {{ position: absolute; right: -40px; top: -34px; transform: rotate(4deg); background: var(--ambar); color: var(--noite); font-weight: 900; font-size: 34px; padding: 16px 28px; border-radius: 18px; box-shadow: 0 20px 40px -14px rgba(0,0,0,.6); }}
.chamada {{ margin-top: 70px; display: flex; flex-direction: column; gap: 18px; align-items: center; text-align: center; }}
.chamada .titulo {{ font-size: 92px; }}
.chamada .apoio {{ font-size: 38px; max-width: 820px; }}
</style></head><body>
<svg width="0" height="0" style="position:absolute" aria-hidden="true">
  <symbol id="cima" viewBox="0 0 24 24"><path d="M12 19V6M6 11l6-6 6 6" fill="none" stroke="currentColor" stroke-width="2.6" stroke-linecap="round" stroke-linejoin="round"/></symbol>
</svg>
<section class="slide reel noite">
  <span class="toque"><svg><use href="#cima"/></svg>Toque em @singletecnologia para ver</span>
  <div class="capa"><div class="halo" style="width:600px;height:600px;left:60px;top:150px;background:rgba(37,99,235,.6)"></div><img src="{capa}" alt=""><span class="novo">Post novo</span></div>
  <div class="chamada">{chamada}</div>
</section>
</body></html>
"""


def gerar(pasta: Path):
    arq = pasta / "post.json"
    post = ig.load_json(arq, {})
    if not post:
        raise SystemExit(f"post.json não encontrado em {pasta}")
    capa = post.get("capa") or (post.get("midias") or ["01.jpg"])[0]
    if capa.lower().endswith(".mp4"):
        raise SystemExit("Para Reel, defina 'capa' (JPEG) no post.json antes de gerar o story.")
    palavra = (post.get("palavra_chave") or "").strip()
    if palavra:
        material = html.escape(post.get("material_nome") or "o material")
        chamada = (f'<h2 class="titulo">Comente <span class="mk">{html.escape(palavra.upper())}</span></h2>'
                   f'<p class="apoio">no post e receba {material} no seu direct.</p>')
    else:
        chamada = ('<h2 class="titulo">Arraste e <span class="mk">salve</span></h2>'
                   '<p class="apoio">para usar no seu próximo projeto.</p>')
    (pasta / "story.html").write_text(MODELO.format(capa=html.escape(capa), chamada=chamada), encoding="utf-8")
    subprocess.run([sys.executable, str(ROOT / "scripts" / "render.py"), str(pasta / "story.html"),
                    "--reel", "--prefixo", "story-"], check=True)
    post["stories"] = ["story-01.jpg"]
    ig.save_json(arq, post)
    print(f"Story pronto: {pasta / 'story-01.jpg'}")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    for p in sys.argv[1:]:
        gerar(Path(p))
