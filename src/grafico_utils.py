from __future__ import annotations

"""Funções auxiliares para montar estatísticas de uma coluna."""
from typing import Optional

import pandas as pd


def _normalizar_valor_categorico(valor):
    """Limpa o valor textual, removendo espaços e tratando vazios."""
    if pd.isna(valor):
        return None
    texto = str(valor).strip()
    if not texto:
        return None
    return texto


def contar_categoria_simples(
    dados: pd.DataFrame,
    coluna: str,
    nome_coluna_saida: Optional[str] = None,
    ignorar_vazios: bool = True,
    rotulo_vazio: str = "Não informado",
    incluir_percentual: bool = False,
    nome_percentual: str = "pct_total",
    casas_percentual: int = 2,
    ordenar_por: Optional[str] = None,
    ordem_decrescente: bool = True,
    limite: Optional[int] = None,
) -> pd.DataFrame:
    """Conta a frequência de uma coluna categórica sem combinar variáveis."""
    if coluna not in dados.columns:
        col_nome = nome_coluna_saida or coluna
        colunas = [col_nome, "qtd"]
        if incluir_percentual:
            colunas.append(nome_percentual)
        return pd.DataFrame(columns=colunas)

    quadro = dados[[coluna]].copy()
    quadro[coluna] = quadro[coluna].apply(_normalizar_valor_categorico)

    if ignorar_vazios:
        quadro = quadro[quadro[coluna].notna()]
    else:
        quadro[coluna] = quadro[coluna].fillna(rotulo_vazio)
        quadro[coluna] = quadro[coluna].replace("", rotulo_vazio)

    if quadro.empty:
        col_nome = nome_coluna_saida or coluna
        colunas = [col_nome, "qtd"]
        if incluir_percentual:
            colunas.append(nome_percentual)
        return pd.DataFrame(columns=colunas)

    contagem = (
        quadro.groupby(coluna)
        .size()
        .reset_index(name="qtd")
    )

    if not ignorar_vazios:
        contagem[coluna] = contagem[coluna].fillna(rotulo_vazio).replace("", rotulo_vazio)

    if incluir_percentual:
        total = contagem["qtd"].sum()
        if total:
            contagem[nome_percentual] = contagem["qtd"].apply(
                lambda valor: round((valor / total) * 100, casas_percentual)
            )
        else:
            contagem[nome_percentual] = 0.0

    if ordenar_por and ordenar_por in contagem.columns:
        contagem = contagem.sort_values(
            by=ordenar_por,
            ascending=not ordem_decrescente,
        )

    if limite is not None and limite > 0:
        contagem = contagem.head(limite)

    if nome_coluna_saida and nome_coluna_saida != coluna:
        contagem = contagem.rename(columns={coluna: nome_coluna_saida})

    return contagem.reset_index(drop=True)


def gerar_resumo_categoria(
    dados: pd.DataFrame,
    coluna: str,
    **opcoes,
) -> dict:
    """Retorna um pacote simples com tabela e totais para análises."""
    tabela = contar_categoria_simples(dados, coluna, **opcoes)
    total = int(tabela["qtd"].sum()) if not tabela.empty else 0
    nome_coluna_saida = opcoes.get("nome_coluna_saida", coluna)
    return {
        "coluna": nome_coluna_saida,
        "total": total,
        "registros": tabela.to_dict(orient="records"),
    }
