"""Constrói o dataset de alunos por situação."""
from typing import Optional
import pandas as pd

def construir(
    df: pd.DataFrame,
    coluna_status: str,
) -> pd.DataFrame:
    """
    Constrói o dataset de alunos por situação.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.
        coluna_status (str): A coluna de status a ser usada.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    series = df[coluna_status].fillna("Não informado")
    agrupado = (
        series.groupby(series)
        .size()
        .reset_index(name="qtd")
        .sort_values("qtd", ascending=False)
        .rename(columns={coluna_status: "Situacao"})
    )
    agrupado = agrupado.rename(columns={series.name: "Situacao"})
    agrupado.columns = ["Situacao", "qtd"]
    return agrupado
