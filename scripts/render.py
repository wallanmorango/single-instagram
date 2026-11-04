"""Transforma as lâminas de um arquivo HTML em imagens JPEG para o Instagram.

Cada elemento <section class="slide"> vira um arquivo 01.jpg, 02.jpg, ...
Tamanhos: carrossel/feed 1080x1350 (padrão) ou --reel 1080x1920.

Uso:
  python scripts/render.py posts/2026-11-09/slides.html
  python scripts/render.py posts/2026-11-10/quadros.html --reel --prefixo quadro
"""
import argparse
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("html")
    ap.add_argument("--reel", action="store_true", help="1080x1920 em vez de 1080x1350")
    ap.add_argument("--prefixo", default="")
    args = ap.parse_args()

    html = Path(args.html).resolve()
    largura, altura = (1080, 1920) if args.reel else (1080, 1350)
    saidas = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": largura, "height": altura}, device_scale_factor=1)
        page.goto(html.as_uri(), wait_until="networkidle")
        page.evaluate("document.fonts.ready")
        page.wait_for_timeout(300)
        slides = page.query_selector_all("section.slide")
        if not slides:
            raise SystemExit("Nenhum <section class=\"slide\"> encontrado.")
        for i, slide in enumerate(slides, start=1):
            png = html.parent / f"{args.prefixo}{i:02d}.png"
            slide.screenshot(path=str(png))
            jpg = png.with_suffix(".jpg")
            img = Image.open(png).convert("RGB")
            if img.size != (largura, altura):
                img = img.resize((largura, altura))
            img.save(jpg, "JPEG", quality=92, optimize=True)
            png.unlink()
            saidas.append(jpg.name)
        browser.close()
    print("Geradas:", ", ".join(saidas))


if __name__ == "__main__":
    main()
