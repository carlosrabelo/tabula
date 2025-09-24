"""Constrói o dataset de forma de ingresso."""
import pandas as pd
from grafico_utils import contar_categoria_simples

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói o dataset de forma de ingresso.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    return contar_categoria_simples(
        df,
        "forma_ingresso",
        nome_coluna_saida="Forma_Ingresso",
        incluir_percentual=True,
        nome_percentual="pct_total",
        casas_percentual=2,
    )
