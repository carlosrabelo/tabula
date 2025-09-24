"""Constrói o dataset de tipo de escola de origem."""
import pandas as pd
from grafico_utils import contar_categoria_simples

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói o dataset de tipo de escola de origem.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    return contar_categoria_simples(
        df,
        "tipo_escola_origem",
        nome_coluna_saida="Tipo_Escola_Origem",
        incluir_percentual=True,
        nome_percentual="pct_total",
        casas_percentual=2,
    )
