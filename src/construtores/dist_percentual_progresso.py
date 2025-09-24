"""Constrói o dataset de distribuição de percentual de progresso."""
import pandas as pd

ORDEM_BUCKET = ["0-25%", "25-50%", "50-75%", "75-100%"]

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Constrói o dataset de distribuição de percentual de progresso.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    filtrado = df[df["bucket_progresso"].notna()]
    agrupado = (
        filtrado.groupby("bucket_progresso")
        .size()
        .reset_index(name="qtd")
        .rename(columns={"bucket_progresso": "Bucket_Progresso"})
    )
    if agrupado.empty:
        return agrupado
    agrupado["Bucket_Progresso"] = pd.Categorical(
        agrupado["Bucket_Progresso"], categories=ORDEM_BUCKET, ordered=True
    )
    agrupado = agrupado.sort_values("Bucket_Progresso").reset_index(drop=True)
    return agrupado
