"""Constrói o dataset de cotas."""
import pandas as pd

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset combinado de cotas MEC e Sistec.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    if "cota_mec" not in df.columns or "cota_sistec" not in df.columns:
        return pd.DataFrame()
    mec_df = df.groupby("cota_mec").size().reset_index(name="qtd")
    mec_df["Tipo_Cota"] = "MEC"
    mec_df = mec_df.rename(columns={"cota_mec": "Categoria"})
    sistec_df = df.groupby("cota_sistec").size().reset_index(name="qtd")
    sistec_df["Tipo_Cota"] = "Sistec"
    sistec_df = sistec_df.rename(columns={"cota_sistec": "Categoria"})
    combined_df = pd.concat([mec_df, sistec_df], ignore_index=True)
    return combined_df[["Tipo_Cota", "Categoria", "qtd"]]
