"""Constrói o dataset de cota Sistec."""
import pandas as pd
from grafico_utils import contar_categoria_simples

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói o dataset de cota Sistec.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    return contar_categoria_simples(
        df,
        "cota_sistec",
        nome_coluna_saida="Cota_Sistec",
        incluir_percentual=True,
        nome_percentual="pct_total",
        casas_percentual=2,
    )
