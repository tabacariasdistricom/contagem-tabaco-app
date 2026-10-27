"""Gera funcionarias.json (lista para escolher na app) a partir de Funcionarias.xlsx (um nome por linha, sem cabeçalho).

Uso: python gerar_funcionarias.py [Funcionarias.xlsx]
O repositório é público: só vai o primeiro nome (com a inicial do apelido se houver dois iguais).
O Funcionarias.xlsx, com os nomes completos, fica fora do git.
"""
import json
import sys
from pathlib import Path

import pandas as pd

ORIGEM = Path(__file__).with_name("Funcionarias.xlsx")
SAIDA = Path(__file__).with_name("funcionarias.json")


def main():
    f = Path(sys.argv[1]) if len(sys.argv) > 1 else ORIGEM
    d = pd.read_excel(f, header=None, usecols=[0])
    completos = sorted({" ".join(str(n).split()).upper() for n in d[0].dropna() if str(n).strip()})
    primeiros = [n.split()[0] for n in completos]
    nomes = sorted(p if primeiros.count(p) == 1 or len(n.split()) < 2 else f"{p} {n.split()[-1][0]}." for n, p in zip(completos, primeiros))
    SAIDA.write_text(json.dumps(nomes, ensure_ascii=False), encoding="utf-8")
    print(len(nomes), "nomes ->", SAIDA)


if __name__ == "__main__":
    main()
