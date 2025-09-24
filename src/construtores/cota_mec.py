"""Constrói o dataset de cota MEC."""
import pandas as pd
from grafico_utils import contar_categoria_simples

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói o dataset de cota MEC.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    return contar_categoria_simples(
        df,
        "cota_mec",
        nome_coluna_saida="Cota_MEC",
        incluir_percentual=True,
        nome_percentual="pct_total",
        casas_percentual=2,
    )
