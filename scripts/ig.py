"""Cliente mínimo da API do Instagram (Instagram API com login do Instagram).

Variáveis de ambiente:
  IG_ACCESS_TOKEN  token de longa duração da conta @singletecnologia (GitHub Secret)
  IG_USER_ID       ID da conta profissional (GitHub Secret); se vazio, usa "me"
  IG_API_VERSION   opcional, ex.: "v24.0"; vazio = versão padrão do app
"""
import json
import os
import time

import requests

CONTA_PADRAO = "17841458425967321"  # ID da conta @singletecnologia (não é segredo)


class IGError(Exception):
    pass


def base() -> str:
    """Tokens do login do Instagram (IG...) usam graph.instagram.com;
    tokens do login do Facebook/usuário do sistema (EAA...) usam graph.facebook.com."""
    forcada = os.environ.get("IG_API_BASE", "").strip()
    if forcada:
        return forcada.rstrip("/")
    return "https://graph.facebook.com" if _token().startswith("EAA") else "https://graph.instagram.com"


def _url(path: str) -> str:
    version = os.environ.get("IG_API_VERSION", "").strip()
    if not version and "graph.facebook.com" in base():
        version = "v24.0"
    prefix = f"/{version}" if version else ""
    return f"{base()}{prefix}/{path.lstrip('/')}"


def user_id() -> str:
    return os.environ.get("IG_USER_ID", "").strip() or CONTA_PADRAO


def _token() -> str:
    token = os.environ.get("IG_ACCESS_TOKEN", "").strip()
    if not token:
        raise IGError("IG_ACCESS_TOKEN não configurado (GitHub Secret).")
    return token


TRANSIENT_CODES = {1, 2, 4, 17, 341, 9007}


def call(method: str, path: str, params=None, json_body=None, retries: int = 3):
    params = dict(params or {})
    params["access_token"] = _token()
    last = None
    for attempt in range(retries):
        resp = requests.request(method, _url(path), params=params, json=json_body, timeout=90)
        if resp.status_code < 400:
            return resp.json() if resp.content else {}
        try:
            err = resp.json().get("error", {})
        except ValueError:
            err = {"message": resp.text[:300]}
        last = f"{method} {path} -> HTTP {resp.status_code}: {err.get('message')} (code {err.get('code')})"
        transient = resp.status_code >= 500 or err.get("is_transient") or err.get("code") in TRANSIENT_CODES
        if transient and attempt < retries - 1:
            time.sleep(15 * (attempt + 1))
            continue
        break
    raise IGError(last)


def get(path, **params):
    return call("GET", path, params=params)


def post(path, params=None, json_body=None):
    return call("POST", path, params=params, json_body=json_body)


def paginate(path, limit_pages: int = 5, **params):
    """Percorre uma lista paginada da API (campo data + paging.next)."""
    data = get(path, **params)
    items = list(data.get("data", []))
    pages = 1
    while data.get("paging", {}).get("next") and pages < limit_pages:
        resp = requests.get(data["paging"]["next"], timeout=90)
        if resp.status_code >= 400:
            break
        data = resp.json()
        items.extend(data.get("data", []))
        pages += 1
    return items


def load_json(path, default):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return default


def save_json(path, data):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")
