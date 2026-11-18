"""Gera posts/AAAA-MM-DD/linkedin.html (carrossel do LinkedIn pessoal do Wallan) a partir do slides.html
do Instagram: troca o cabeçalho da Single pelo do Wallan, aplica templates/linkedin.css, tira o site
da Single do rodapé e troca a última lâmina (a de ação da Single) por uma chamada pessoal.

Uso:
  python scripts/linkedin_html.py posts/2026-11-19 \
      --etiqueta "PDF gratuito" --titulo 'Comente <span class="palavra">FLUXO</span>' \
      --apoio "que eu te mando o PDF com <b>10 fluxos</b> de Power Automate." --botao "Salve para usar depois"
Depois: python scripts/render.py posts/AAAA-MM-DD/linkedin.html --prefixo li-
        python scripts/pdf.py carrossel posts/AAAA-MM-DD li-
"""
import argparse
import re
from pathlib import Path

CABECALHO = ('<div class="topo"><div class="autor"><span class="avatar">WJ</span><div><b>Wallan Jorge</b>'
             '<small>Dados, BI e automação</small></div></div><span class="perfil">in/wallanjorge</span></div>')


def chamada(n_pontos: int, etiqueta: str, titulo: str, apoio: str, botao: str) -> str:
    pontos = "".join("<i></i>" for _ in range(n_pontos - 1)) + '<i class="at"></i>'
    return f'''<section class="slide destaque">
  {CABECALHO}
  <div class="conteudo" style="margin-top:auto;margin-bottom:auto;padding-bottom:90px;gap:32px">
    <span class="etiqueta">{etiqueta}</span>
    <h2 class="titulo m">{titulo}</h2>
    <p class="apoio">{apoio}</p>
    <span class="botao-li"><svg viewBox="0 0 24 24"><path d="M6 3h12v18l-6-4-6 4z" fill="currentColor"/></svg>{botao}</span>
  </div>
  <div class="rodape"><div class="pontos">{pontos}</div><span class="perfil" style="opacity:.8">Wallan Jorge</span></div>
</section>'''


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pasta")
    ap.add_argument("--etiqueta", required=True)
    ap.add_argument("--titulo", required=True)
    ap.add_argument("--apoio", required=True)
    ap.add_argument("--botao", required=True)
    a = ap.parse_args()
    pasta = Path(a.pasta)
    s = (pasta / "slides.html").read_text(encoding="utf-8")
    s = s.replace('<link rel="stylesheet" href="../../templates/base.css">',
                  '<link rel="stylesheet" href="../../templates/base.css">\n'
                  '<link rel="stylesheet" href="../../templates/linkedin.css">', 1)
    s = re.sub(r"<title>.*?</title>", "<title>LinkedIn — Wallan Jorge</title>", s, count=1)
    s = re.sub(r'<div class="topo">.*?@singletecnologia</span></div>', CABECALHO, s)
    s = re.sub(r'<span style="font-weight:900;font-size:\d+px">singletecnologia\.netlify\.app[^<]*</span>', "", s)
    secoes = list(re.finditer(r'<section class="slide[^"]*">.*?</section>', s, flags=re.S))
    ultima = secoes[-1]
    s = s[:ultima.start()] + chamada(len(secoes), a.etiqueta, a.titulo, a.apoio, a.botao) + s[ultima.end():]
    for proibido in ("SINGLE", "singletecnologia", "Single Tecnologia"):
        if proibido in re.sub(r"<symbol.*?</symbol>", "", s, flags=re.S).replace("<title>", ""):
            print(f"Atenção: ainda aparece '{proibido}' em linkedin.html")
    (pasta / "linkedin.html").write_text(s, encoding="utf-8")
    print(f"Gerado: {pasta / 'linkedin.html'} ({len(secoes)} lâminas)")


if __name__ == "__main__":
    main()
