"""Constrói o dataset de tipo de transporte."""
import pandas as pd
from grafico_utils import contar_categoria_simples

def construir(df: pd.DataFrame) -> pd.DataFrame:
    """
    Gera o dataset de transporte combinado.

    Args:
        df (pd.DataFrame): O DataFrame pré-processado.

    Returns:
        pd.DataFrame: O DataFrame do dataset.
    """
    df_copia = df.copy()
    # Combina as colunas, tratando valores ausentes
    df_copia["transporte_combinado"] = (
        df_copia["transporte_tipo"].fillna("Não informado")
        + " - "
        + df_copia["transporte_publico"].fillna("Não informado")
    )
    # Limpa entradas que são apenas separadores
    df_copia["transporte_combinado"] = df_copia["transporte_combinado"].replace(
        "Não informado - Não informado", "Não informado"
    )
    return contar_categoria_simples(
        df_copia,
        "transporte_combinado",
        nome_coluna_saida="Transporte_Tipo",
        incluir_percentual=True,
        nome_percentual="pct_total",
        casas_percentual=2,
    )
