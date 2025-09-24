"""Constrói o dataset de natureza de participação."""
import pandas as pd
from grafico_utils import contar_categoria_simples

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói o dataset de natureza de participação.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    return contar_categoria_simples(
        df,
        "natureza_participacao",
        nome_coluna_saida="Natureza_Participacao",
        incluir_percentual=True,
        nome_percentual="pct_total",
        casas_percentual=2,
    )
