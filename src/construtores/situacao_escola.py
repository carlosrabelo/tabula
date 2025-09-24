"""Constrói o dataset de situação e tipo de escola."""
import pandas as pd

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset combinado de situação e tipo de escola de origem.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    return (
        df.groupby(["status_simplificado", "tipo_escola_origem"])
        .size()
        .reset_index(name="qtd")
    )
