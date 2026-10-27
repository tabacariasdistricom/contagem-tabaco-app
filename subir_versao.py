"""Sobe uma unidade à VERSAO do sw.js (tab-vN -> tab-vN+1) para os aparelhos irem buscar a versão nova."""
import re
from pathlib import Path

f = Path(__file__).with_name("sw.js")
t = f.read_text(encoding="utf-8")
novo, n = re.subn(r'(VERSAO = "tab-v)(\d+)(")', lambda m: f"{m[1]}{int(m[2]) + 1}{m[3]}", t, count=1)
assert n == 1, "VERSAO não encontrada em sw.js"
f.write_text(novo, encoding="utf-8")
print("sw.js:", re.search(r'VERSAO = "([^"]+)"', novo)[1])
