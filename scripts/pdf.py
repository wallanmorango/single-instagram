"""Gera PDFs no formato do celular (páginas de 1080x1350).

Dois usos:
  python scripts/pdf.py html materiais/fonte/dax-financeiro.html materiais/dax-financeiro.pdf
      Cada <section class="slide"> do HTML vira uma página do PDF (texto selecionável e links clicáveis).
  python scripts/pdf.py carrossel posts/2026-11-06 [prefixo]
      Junta 01.jpg, 02.jpg, ... do post em posts/AAAA-MM-DD/linkedin.pdf (carrossel para o LinkedIn).
      Com prefixo (ex.: li-), junta li-01.jpg, li-02.jpg, ... (lâminas próprias do LinkedIn,
      geradas com: python scripts/render.py posts/AAAA-MM-DD/linkedin.html --prefixo li-).
"""
import sys
from pathlib import Path

from PIL import Image


def html_para_pdf(html: Path, saida: Path):
    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": 1080, "height": 1350})
        page.goto(html.resolve().as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.add_style_tag(content="""
            @page { size: 1080px 1350px; margin: 0; }
            html, body { background: none !important; padding: 0 !important; margin: 0 !important; display: block !important; }
            section.slide { break-after: page; break-inside: avoid; }
            section.slide:last-of-type { break-after: auto; }
            /* efeitos que viram imagem no PDF e pesam o arquivo */
            .slide::after { display: none !important; }
            .vidro { backdrop-filter: none !important; }
            .halo { display: none !important; }
        """)
        page.wait_for_timeout(300)
        saida.parent.mkdir(parents=True, exist_ok=True)
        page.pdf(path=str(saida), width="1080px", height="1350px", print_background=True,
                 margin={"top": "0", "right": "0", "bottom": "0", "left": "0"})
        browser.close()
    print(f"PDF gerado: {saida}")


def carrossel_para_pdf(pasta: Path, prefixo: str = ""):
    imagens = sorted(pasta.glob(f"{prefixo}[0-9][0-9].jpg"))
    if not imagens:
        raise SystemExit(f"Nenhuma lâmina 01.jpg, 02.jpg... em {pasta}")
    paginas = [Image.open(i).convert("RGB") for i in imagens]
    saida = pasta / "linkedin.pdf"
    paginas[0].save(saida, "PDF", save_all=True, append_images=paginas[1:], resolution=144)
    print(f"PDF do LinkedIn gerado: {saida} ({len(paginas)} páginas)")


if __name__ == "__main__":
    if len(sys.argv) >= 4 and sys.argv[1] == "html":
        html_para_pdf(Path(sys.argv[2]), Path(sys.argv[3]))
    elif len(sys.argv) >= 3 and sys.argv[1] == "carrossel":
        carrossel_para_pdf(Path(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else "")
    else:
        raise SystemExit(__doc__)
