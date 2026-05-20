#!/usr/bin/env python3
"""Verificação simples para evitar commitar segredos óbvios no control room."""
from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKIP_DIRS = {".git", "__pycache__", "node_modules"}
SKIP_FILES = {"check-no-secrets.py"}
PATTERNS = [
    ("telegram bot token", re.compile(r"\b\d{8,12}:[A-Za-z0-9_-]{30,}\b")),
    ("github pat", re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b")),
    ("openai-like key", re.compile(r"\bsk-[A-Za-z0-9_-]{20,}\b")),
    ("private key", re.compile(r"-----BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY-----")),
]

hits: list[str] = []
for path in ROOT.rglob("*"):
    if any(part in SKIP_DIRS for part in path.parts):
        continue
    if not path.is_file() or path.name in SKIP_FILES:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for name, pattern in PATTERNS:
        for match in pattern.finditer(text):
            line = text.count("\n", 0, match.start()) + 1
            hits.append(f"{path.relative_to(ROOT)}:{line}: possível {name}")

if hits:
    print("Possíveis segredos encontrados:")
    for hit in hits:
        print(f"- {hit}")
    raise SystemExit(1)

print("OK: nenhum segredo óbvio encontrado.")
