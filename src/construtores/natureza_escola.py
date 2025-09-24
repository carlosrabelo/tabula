"""Constrói o dataset de natureza e tipo de escola."""
import pandas as pd

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset combinado de natureza de participação e tipo de escola.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    return (
        df.groupby(["natureza_participacao", "tipo_escola_origem"])
        .size()
        .reset_index(name="qtd")
    )
