"""Mostra o que o token configurado consegue acessar (sem imprimir o token)."""
import json
import sys
from pathlib import Path

import requests

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ig  # noqa: E402

tok = ig._token()
print("Tipo do token:", ig.tipo_token(), "| API:", ig.base())


def tentar(nome, fn):
    try:
        print(f"\n== {nome}\n" + json.dumps(fn(), ensure_ascii=False, indent=2)[:3000])
    except Exception as exc:  # noqa: BLE001
        print(f"\n== {nome}\nERRO: {exc}")


tentar("me", lambda: ig.get("me", fields="id,name"))
tentar("debug_token (escopos e contas liberadas)",
       lambda: {k: v for k, v in ig.get("debug_token", input_token=tok).get("data", {}).items()
                if k in ("type", "app_id", "is_valid", "expires_at", "scopes", "granular_scopes", "profile_id")})
tentar("me/accounts (páginas e Instagram ligados)",
       lambda: ig.get("me/accounts", fields="name,instagram_business_account{id,username}"))
tentar("conta padrão", lambda: ig.get(ig.CONTA_PADRAO, fields="id,username,followers_count"))
tentar("graph.instagram.com/me com o mesmo token",
       lambda: requests.get("https://graph.instagram.com/me",
                            params={"fields": "id,user_id,username", "access_token": tok}, timeout=60).json())
