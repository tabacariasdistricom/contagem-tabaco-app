"""Gera artigos.json (tabaco, família 01) para a app de contagem, a partir dos artigos extraídos da API ZoneSoft.

Só lê os ficheiros `dados/artigos/artigos_loja<L>.xlsx` do projeto ZoneSoft (feitos pelo `diario.py`).
Não chama a API, não leva custos, stocks nem credenciais: só código, nome, código de barras, subfamília e PVP.

Uso: python gerar_artigos.py [--origem <pasta dos artigos_loja*.xlsx>] [--com-descontinuados]
"""
import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

import pandas as pd

ORIGEM = Path(__file__).resolve().parent.parent / "zonsoft" / "dados" / "artigos"
SAIDA = Path(__file__).with_name("artigos.json")
FAMILIA_TABACO = 1


def limpar_subfam(s):
    """'01 - Cigarros - 6.5%' -> 'Cigarros'; 'Descontinuados' fica igual."""
    s = re.sub(r"^\d+\s*-\s*", "", str(s or "").strip())
    return re.sub(r"\s*-\s*[\d.,]+\s*%$", "", s)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--origem", type=Path, default=ORIGEM)
    ap.add_argument("--com-descontinuados", action="store_true")
    a = ap.parse_args()

    lojas = {}
    for loja in range(1, 5):
        f = a.origem / f"artigos_loja{loja}.xlsx"
        if not f.exists():
            sys.exit(f"Falta {f} (correr o diario.py do projeto ZoneSoft).")
        d = pd.read_excel(f, dtype={"codbarras": str})
        d = d[(d["familia"] == FAMILIA_TABACO) & (d["ativo"] == 1)]
        if not a.com_descontinuados:
            d = d[~d["subfam_desc"].astype(str).str.contains("Descontinuados", case=False)]
        itens = []
        for r in d.sort_values(["subfam_desc", "descricao"]).itertuples():
            cb = re.sub(r"\D", "", str(r.codbarras)) if pd.notna(r.codbarras) else ""
            itens.append({"c": int(r.codigo), "d": str(r.descricao).strip(), "b": cb,
                          "s": limpar_subfam(r.subfam_desc), "p": round(float(r.precovenda), 2)})
        lojas[str(loja)] = itens
        print(f"Loja {loja}: {len(itens)} artigos ({sum(1 for i in itens if not i['b'])} sem código de barras)")

    SAIDA.write_text(json.dumps({"gerado": datetime.now().strftime("%d-%m-%Y"), "lojas": lojas},
                                ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print("Escrito", SAIDA)


if __name__ == "__main__":
    main()
