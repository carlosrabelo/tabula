#!/usr/bin/env -S ./.venv/bin/python
"""Build aggregated CSV datasets from SUAP master export."""
import argparse
import math
import re
import sys
from datetime import datetime, timedelta
from pathlib import Path
import unicodedata
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

import pandas as pd

from grafico_utils import contar_categoria_simples

# Mapping of canonical column names to synonyms (accent-insensitive, case-insensitive)
COLUMN_SYNONYMS = {
    "curso": [
        "Curso",
        "Curso Nome",
        "Nome do Curso",
        "Descrição do Curso",
        "Descricao do Curso",
    ],
    "situacao_curso": [
        "Situação no Curso",
        "Situacao no Curso",
        "Status no Curso",
    ],
    "situacao_sistema": [
        "Situação no Sistema",
        "Situacao no Sistema",
    ],
    "data_matricula": [
        "Data de Matrícula",
        "Data da Matrícula",
        "Data Matricula",
        "Matricula Data",
    ],
    "data_conclusao": [
        "Data de Conclusão de Curso",
        "Data de Conclusão",
        "Conclusão Data",
    ],
    "data_integralizacao": [
        "Data de Integralização",
        "Data de Integralizacao",
    ],
    "modalidade": ["Modalidade"],
    "turno": ["Turno", "Período", "Periodo"],
    "forma_ingresso": ["Forma de Ingresso", "Forma Ingresso"],
    "campus": ["Campus"],
    "cota_mec": ["Cota MEC", "Cota_MEC"],
    "cota_sistec": ["Cota Sistec", "Cota_Sistec"],
    "etnia_raca": [
        "Etnia/Raça",
        "Etnia - Raça",
        "Raca/Cor",
        "Raça/Cor",
    ],
    "necessidades_especiais": [
        "Deficiências/Transtornos/Superdotação",
        "Necessidades Especiais",
    ],
    "frequencia_periodo": [
        "Frequência no Período",
        "Frequencia no Periodo",
    ],
    "media_final_periodo": [
        "Média Final no Período",
        "Media Final no Periodo",
    ],
    "pendencias_conclusao": [
        "Pendências de Requisitos de Conclusão",
        "Pendencias Conclusao",
    ],
    "estado": ["Estado", "UF"],
    "cidade": ["Cidade", "Município", "Municipio"],
    "polo": ["Polo", "Pólo"],
    "transporte_publico": [
        "Transporte Escolar: Poder Público",
        "Transporte Escolar - Poder Publico",
    ],
    "transporte_tipo": [
        "Transporte Escolar: Tipo de Veículo",
        "Transporte Escolar - Tipo de Veiculo",
    ],
    "percentual_progresso": [
        "Percentual de Progresso",
        "Progresso (%)",
        "% Progresso",
    ],
    "ano_ingresso": ["Ano de Ingresso", "Ano_Ingresso"],
    "tipo_escola_origem": ["Tipo de Escola de Origem"],
    "natureza_participacao": ["Natureza de Participação", "Natureza de Participacao"],
}

DATE_COLUMNS = ["data_matricula", "data_conclusao", "data_integralizacao"]

OUTPUT_SPECS = {
    "alunos_por_situacao.csv": {
        "requires": ["status_simplificado"],
        "sources_any": [["situacao_curso", "situacao_sistema"]],
    },
    "modalidade.csv": {
        "requires": ["modalidade"],
        "sources_all": ["modalidade"],
    },
    "dist_percentual_progresso.csv": {
        "requires": ["bucket_progresso"],
        "sources_all": ["percentual_progresso"],
    },
    "turno.csv": {
        "requires": ["turno"],
        "sources_all": ["turno"],
    },
    "forma_ingresso.csv": {
        "requires": ["forma_ingresso"],
        "sources_all": ["forma_ingresso"],
    },
    "cota_mec.csv": {
        "requires": ["cota_mec"],
        "sources_all": ["cota_mec"],
    },
    "cota_sistec.csv": {
        "requires": ["cota_sistec"],
        "sources_all": ["cota_sistec"],
    },
    "cotas.csv": {
        "requires": ["cota_mec", "cota_sistec"],
        "sources_all": ["cota_mec", "cota_sistec"],
    },
    "etnia_raca.csv": {
        "requires": ["etnia_raca"],
        "sources_all": ["etnia_raca"],
    },
    "necessidades_especiais.csv": {
        "requires": ["tem_ne"],
        "sources_all": ["necessidades_especiais"],
    },
    "tipo_escola_origem.csv": {
        "requires": ["tipo_escola_origem"],
        "sources_all": ["tipo_escola_origem"],
    },
    "natureza_participacao.csv": {
        "requires": ["natureza_participacao"],
        "sources_all": ["natureza_participacao"],
    },
    "transporte_tipo.csv": {
        "requires": ["transporte_publico", "transporte_tipo"],
        "sources_all": ["transporte_publico", "transporte_tipo"],
    },
    "natureza_escola.csv": {
        "requires": ["natureza_participacao", "tipo_escola_origem"],
        "sources_all": ["natureza_participacao", "tipo_escola_origem"],
    },
    "situacao_escola.csv": {
        "requires": ["status_simplificado", "tipo_escola_origem"],
        "sources_any": [["situacao_curso", "situacao_sistema"]],
        "sources_all": ["tipo_escola_origem"],
    },
}

BUCKET_ORDER = ["0-25%", "25-50%", "50-75%", "75-100%"]


def normalize_text(value: Optional[str]) -> str:
    if value is None:
        return ""
    text = str(value).strip()
    if not text:
        return ""
    text_nfkd = unicodedata.normalize("NFKD", text)
    return "".join(ch for ch in text_nfkd if not unicodedata.combining(ch)).lower()


def resolve_columns(columns: Sequence[str]) -> Dict[str, str]:
    normalized_map = {normalize_text(col): col for col in columns}
    resolved = {}
    for canonical, candidates in COLUMN_SYNONYMS.items():
        for candidate in candidates + [canonical]:
            key = normalize_text(candidate)
            if key in normalized_map:
                resolved[canonical] = normalized_map[key]
                break
    return resolved


def parse_excel_datetime(value):
    if pd.isna(value):
        return pd.NaT
    if isinstance(value, pd.Timestamp):
        return value
    if isinstance(value, datetime):
        return pd.Timestamp(value)
    if isinstance(value, str):
        text = value.strip()
        if not text:
            return pd.NaT
        parsed = pd.to_datetime(text, errors="coerce", dayfirst=True)
        if pd.isna(parsed):
            parsed = pd.to_datetime(text, errors="coerce")
        return parsed
    if isinstance(value, (int, float)):
        if math.isnan(value):
            return pd.NaT
        base_date = datetime(1899, 12, 30)
        return pd.Timestamp(base_date + timedelta(days=float(value)))
    return pd.NaT


def ensure_datetime(series: pd.Series) -> pd.Series:
    if series is None:
        return pd.Series(dtype="datetime64[ns]")
    converted = series.apply(parse_excel_datetime)
    return pd.to_datetime(converted, errors="coerce")


def parse_percentage(value) -> float:
    if pd.isna(value):
        return math.nan
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return math.nan
    text = text.replace("%", "")
    text = text.replace(" ", "")
    text = text.replace(".", "", text.count(".") - 1)
    text = text.replace(",", ".")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    if not match:
        return math.nan
    try:
        return float(match.group())
    except ValueError:
        return math.nan


def bucketize_progress(value: float) -> Optional[str]:
    if value is None or pd.isna(value):
        return None
    value = max(0.0, min(100.0, float(value)))
    if value < 25:
        return "0-25%"
    if value < 50:
        return "25-50%"
    if value < 75:
        return "50-75%"
    return "75-100%"


def simplify_status(text: Optional[str]) -> str:
    normalized = normalize_text(text)
    if not normalized:
        return "Outros"
    prefixes = {
        ("concl", "form"): "Concluído",
        ("ativ", "curs"): "Ativo",
        ("tranc",): "Trancado",
        ("cancel", "evad", "desl"): "Evasão/Cancelado",
    }
    for keys, label in prefixes.items():
        if any(normalized.startswith(key) for key in keys):
            return label
    return "Outros"


def parse_year(value, fallback_date: Optional[pd.Timestamp]) -> Optional[int]:
    if value is not None and not pd.isna(value):
        if isinstance(value, (int,)):
            return int(value)
        if isinstance(value, float):
            if not math.isnan(value):
                return int(value)
        text = str(value).strip()
        match = re.search(r"(19|20)\d{2}", text)
        if match:
            return int(match.group())
    if fallback_date is not None and not pd.isna(fallback_date):
        return int(fallback_date.year)
    return None


def has_special_need(value) -> str:
    normalized = normalize_text(value)
    if not normalized:
        return "Não"
    negative_markers = {
        "nao",
        "naopossui",
        "naoseaplica",
        "naodeclarado",
        "naoinformado",
        "sem",
        "0",
    }
    if any(normalized.startswith(marker) for marker in negative_markers):
        return "Não"
    if normalized in {"n", "na"}:
        return "Não"
    return "Sim"


def months_between(start: Optional[pd.Timestamp], end: Optional[pd.Timestamp]) -> float:
    if start is None or pd.isna(start) or end is None or pd.isna(end):
        return math.nan
    delta_days = (end - start).days
    return round(delta_days / 30.4375, 2)


def load_dataframe(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    ext = path.suffix.lower()
    engine = None
    if ext == ".xls":
        engine = "xlrd"
    elif ext in {".xlsx", ".xlsm"}:
        engine = "openpyxl"
    try:
        return pd.read_excel(path, engine=engine)
    except ImportError as err:
        sys.exit(f"Dependência ausente para leitura de {ext}: {err}")


def preprocess(df: pd.DataFrame) -> Tuple[pd.DataFrame, set]:
    df = df.copy()
    resolved = resolve_columns(df.columns)
    df = df.rename(columns={source: target for target, source in resolved.items()})
    available_sources = set(resolved.keys())

    # Ensure canonical columns exist
    for canonical in COLUMN_SYNONYMS:
        if canonical not in df.columns:
            df[canonical] = pd.NA

    for col in DATE_COLUMNS:
        df[col] = ensure_datetime(df[col])

    if "situacao_curso" in available_sources and df["situacao_curso"].notna().any():
        status_series = df["situacao_curso"]
    else:
        status_series = df["situacao_sistema"]
    df["status_simplificado"] = status_series.apply(simplify_status)

    df["percentual_progresso_num"] = df["percentual_progresso"].apply(parse_percentage)
    df["bucket_progresso"] = df["percentual_progresso_num"].apply(bucketize_progress)

    if "necessidades_especiais" in available_sources:
        df["tem_ne"] = df["necessidades_especiais"].apply(has_special_need)
    else:
        df["tem_ne"] = pd.NA

    today = pd.Timestamp(datetime.today().date())
    df["tempo_curso_meses"] = df.apply(
        lambda row: months_between(
            row.get("data_matricula"),
            row.get("data_conclusao")
            if row.get("status_simplificado") == "Concluído"
            else today,
        )
        if not pd.isna(row.get("data_matricula"))
        else math.nan,
        axis=1,
    )

    df["coorte_ano"] = df.apply(
        lambda row: parse_year(
            row.get("ano_ingresso"),
            row.get("data_matricula"),
        ),
        axis=1,
    )

    return df, available_sources


def resolve_status_column(df: pd.DataFrame, available_sources: set) -> str:
    if "situacao_curso" in available_sources and df["situacao_curso"].notna().any():
        return "situacao_curso"
    if "situacao_sistema" in available_sources and df["situacao_sistema"].notna().any():
        return "situacao_sistema"
    return "status_simplificado"


def write_csv(df: pd.DataFrame, path: Path) -> None:
    df.to_csv(path, index=False, sep=";", encoding="utf-8")


def build_alunos_por_situacao(
    df: pd.DataFrame,
    status_column: Optional[str] = None,
    available_sources: Optional[set] = None,
):
    if status_column is None:
        status_column = resolve_status_column(df, available_sources or set(df.columns))
    series = df[status_column].fillna("Não informado")
    grouped = (
        series.groupby(series)
        .size()
        .reset_index(name="qtd")
        .sort_values("qtd", ascending=False)
        .rename(columns={status_column: "Situacao"})
    )
    grouped = grouped.rename(columns={series.name: "Situacao"})
    grouped.columns = ["Situacao", "qtd"]
    return grouped


def build_dist_progresso(df: pd.DataFrame):
    filtered = df[df["bucket_progresso"].notna()]
    grouped = (
        filtered.groupby("bucket_progresso")
        .size()
        .reset_index(name="qtd")
        .rename(columns={"bucket_progresso": "Bucket_Progresso"})
    )
    if grouped.empty:
        return grouped
    grouped["Bucket_Progresso"] = pd.Categorical(
        grouped["Bucket_Progresso"], categories=BUCKET_ORDER, ordered=True
    )
    grouped = grouped.sort_values("Bucket_Progresso").reset_index(drop=True)
    return grouped


def build_categoria(df: pd.DataFrame, column: str, output_column: str):
    return contar_categoria_simples(
        df,
        column,
        nome_coluna_saida=output_column,
        incluir_percentual=True,
        nome_percentual="pct_total",
        casas_percentual=2,
    )


def build_modalidade(df: pd.DataFrame):
    return build_categoria(df, "modalidade", "Modalidade")


def build_tipo_escola(df: pd.DataFrame):
    return build_categoria(df, "tipo_escola_origem", "Tipo_Escola_Origem")


def build_natureza_participacao(df: pd.DataFrame):
    return build_categoria(df, "natureza_participacao", "Natureza_Participacao")


def build_transporte_combinado(df: pd.DataFrame):
    """Gera o dataset de transporte combinado.""" 
    df_copy = df.copy()
    # Combine as colunas, tratando valores ausentes
    df_copy["transporte_combinado"] = (
        df_copy["transporte_tipo"].fillna("Não informado")
        + " - "
        + df_copy["transporte_publico"].fillna("Não informado")
    )
    # Limpa entradas que são apenas separadores
    df_copy["transporte_combinado"] = df_copy["transporte_combinado"].replace(
        "Não informado - Não informado", "Não informado"
    )
    return build_categoria(df_copy, "transporte_combinado", "Transporte_Tipo")


def build_situacao_escola(df: pd.DataFrame):
    """Gera o dataset combinado de situação e tipo de escola de origem."""
    return (
        df.groupby(["status_simplificado", "tipo_escola_origem"])
        .size()
        .reset_index(name="qtd")
    )


def build_natureza_escola(df: pd.DataFrame):
    """Gera o dataset combinado de natureza de participação e tipo de escola."""
    return (
        df.groupby(["natureza_participacao", "tipo_escola_origem"])
        .size()
        .reset_index(name="qtd")
    )


def build_cotas(df: pd.DataFrame):
    """Gera o dataset combinado de cotas MEC e Sistec."""
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


BUILDERS = {
    "alunos_por_situacao.csv": build_alunos_por_situacao,
    "modalidade.csv": build_modalidade,
    "dist_percentual_progresso.csv": build_dist_progresso,
    "turno.csv": lambda df: build_categoria(df, "turno", "Turno"),
    "forma_ingresso.csv": lambda df: build_categoria(
        df, "forma_ingresso", "Forma_Ingresso"
    ),
    "cota_mec.csv": lambda df: build_categoria(df, "cota_mec", "Cota_MEC"),
    "cota_sistec.csv": lambda df: build_categoria(df, "cota_sistec", "Cota_Sistec"),
    "cotas.csv": build_cotas,
    "etnia_raca.csv": lambda df: build_categoria(df, "etnia_raca", "Etnia_Raca"),
    "necessidades_especiais.csv": lambda df: build_categoria(df, "tem_ne", "Tem_NE"),
    "tipo_escola_origem.csv": build_tipo_escola,
    "natureza_participacao.csv": build_natureza_participacao,
    "transporte_tipo.csv": build_transporte_combinado,
    "natureza_escola.csv": build_natureza_escola,
    "situacao_escola.csv": build_situacao_escola,
}


def has_required_columns(df: pd.DataFrame, requires: Iterable[str]) -> bool:
    for column in requires:
        if column not in df.columns:
            return False
        series = df[column]
        if isinstance(series, pd.Series) and series.dropna().empty:
            return False
    return True


def has_required_sources(available: set, spec: Dict) -> bool:
    sources_all: List[str] = spec.get("sources_all", [])
    for column in sources_all:
        if column not in available:
            return False
    sources_any: List[List[str]] = spec.get("sources_any", [])
    for group in sources_any:
        if not any(column in available for column in group):
            return False
    return True


def build_datasets(input_path: Path, output_dir: Path) -> None:
    df = load_dataframe(input_path)
    df, available_sources = preprocess(df)
    output_dir.mkdir(parents=True, exist_ok=True)

    for filename, spec in OUTPUT_SPECS.items():
        requires = spec.get("requires", [])
        builder = BUILDERS.get(filename)
        if builder is None:
            continue
        if not has_required_sources(available_sources, spec):
            print(f"Dataset pulado (fontes ausentes): {filename}")
            continue
        if not has_required_columns(df, requires):
            print(f"Dataset pulado (dados insuficientes): {filename}")
            continue
        generated = builder(df)
        if generated is None or generated.empty:
            print(f"Dataset pulado (sem dados): {filename}")
            continue
        write_csv(generated, output_dir / filename)
        print(f"Gerado: {filename}")


def parse_args(argv: Optional[Iterable[str]] = None):
    parser = argparse.ArgumentParser(description="Gera datasets agregados em CSV")
    parser.add_argument("--in", dest="input_path", required=True, help="Arquivo mestre (.xls/.xlsx)")
    parser.add_argument("--out", dest="output_dir", required=True, help="Diretório de saída para CSVs")
    return parser.parse_args(argv)


def main(argv: Optional[Iterable[str]] = None) -> None:
    args = parse_args(argv)
    input_path = Path(args.input_path)
    output_dir = Path(args.output_dir)
    build_datasets(input_path, output_dir)


if __name__ == "__main__":
    main()
