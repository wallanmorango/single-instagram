"""Publica imagens como story (1080x1920, JPEG) no Instagram.

Uso: python scripts/story.py assets/destaques/destaque-power-bi.jpg [outro.jpg ...]
As imagens precisam estar na branch main (servidas pelo GitHub Pages).
"""
import sys
import time
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ig  # noqa: E402
from publicar import esperar_container, esperar_url, pages_base  # noqa: E402

for caminho in sys.argv[1:]:
    url = f"{pages_base()}/{quote(caminho.strip().lstrip('/'))}"
    esperar_url(url)
    cid = ig.post(f"{ig.user_id()}/media", params={"media_type": "STORIES", "image_url": url})["id"]
    esperar_container(cid)
    mid = ig.post(f"{ig.user_id()}/media_publish", params={"creation_id": cid})["id"]
    print(f"Story publicado: {caminho} (id {mid})")
    time.sleep(5)
