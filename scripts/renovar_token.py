"""Renova o token de longa duração do Instagram (válido por 60 dias).

Grava o novo token no arquivo indicado em NOVO_TOKEN_ARQUIVO para o workflow
atualizar o GitHub Secret. Nunca imprime o token.
"""
import os
import sys

import requests

token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
destino = os.environ.get("NOVO_TOKEN_ARQUIVO", "").strip()
if not token or not destino:
    sys.exit("IG_ACCESS_TOKEN e NOVO_TOKEN_ARQUIVO são obrigatórios.")
if token.startswith("EAA"):
    # Token do login do Facebook / usuário do sistema: não usa esta renovação.
    print("Token do tipo Facebook (EAA...): renovação pelo Instagram não se aplica.")
    print("::notice::Confira a validade no Depurador de Token da Meta (developers.facebook.com/tools/debug/accesstoken).")
    sys.exit(0)

resp = requests.get("https://graph.instagram.com/refresh_access_token",
                    params={"grant_type": "ig_refresh_token", "access_token": token}, timeout=60)
if resp.status_code >= 400:
    sys.exit(f"Falha ao renovar o token: HTTP {resp.status_code} {resp.text[:300]}")

dados = resp.json()
novo = dados["access_token"]
print(f"::add-mask::{novo}")
fd = os.open(destino, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
with os.fdopen(fd, "w") as f:
    f.write(novo)
print(f"Token renovado. Válido por mais {int(dados.get('expires_in', 0)) // 86400} dias.")
