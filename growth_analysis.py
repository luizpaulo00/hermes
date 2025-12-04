"""
run_analysis_corrected.py
========================

This script performs a focused analysis of the 2025 sales funnel
using the most recent datasets supplied by the user.  It addresses
concerns about mismatched counts between leads, pré‑cadastros,
reservas and repasses by explicitly matching records across stages
and reporting how many repasses (contracts signed) actually
originate from leads, pré‑cadastros and reservas created in 2025.

Key features:

* **Robust file loading** – The script reads Excel and CSV files
  using pandas while handling Brazilian semicolon‑separated CSVs
  and Excel HYPERLINK formulas.  The ``Reserva`` column in
  ``reserva.csv`` contains formulas such as
  ``=HIPERLINK("https://...";"6105")``; the script extracts the
  numeric identifier (``6105``) from these formulas.

* **Year‑specific counts** – It counts how many leads, pré‑cadastros
  and reservas were created in 2025 and how many repasses were
  signed in 2025.  It then determines how many of those 2025
  repasses can be traced back to 2025 leads, pré‑cadastros and
  reservas via the stage linkage columns.

* **Duration analysis** – For each transition (lead→pré‑cadastro,
  pré‑cadastro→reserva, reserva→repasse and lead→repasse) the
  script computes:

  - The mean number of days between stages for all available
    records (general funnel).
  - The mean number of days between stages considering only the
    repasses signed in 2025 (successful funnel).
  - Trimmed means for each duration by discarding the lowest 25 %
    and highest 25 % of observations to reduce the influence of
    outliers.

All results are printed to the console.  At the end, the script
exports the summary tables to an Excel workbook named
``funnel_analysis_outputs.xlsx`` with the following worksheets:

* ``Counts_2025`` – Counts of leads, pré‑cadastros, reservas and
  repasses in 2025 along with the number of repasses traced back to
  each stage.
* ``Durations_General`` – Mean and trimmed mean durations for all
  records across the funnel (regardless of the repasse date).
* ``Durations_Repasses2025`` – Mean and trimmed mean durations
  restricted to repasses signed in 2025.

To run this script, ensure that ``lead2025.xlsb`` and
``precadastro.xlsb`` have been converted to ``.xlsx`` files and
placed in the ``converted`` directory alongside ``precadastro.csv``,
``reserva.csv`` and ``repasses.csv``.  Then execute:

    python run_analysis_corrected.py

"""

from __future__ import annotations

import pandas as pd
import numpy as np
from pathlib import Path


def parse_excel_date(series: pd.Series) -> pd.Series:
    """Parse a pandas Series containing either Excel serial numbers or
    string dates into datetime64.  Supports day‑first formats.

    Parameters
    ----------
    series : pandas.Series
        The series to convert.

    Returns
    -------
    pandas.Series
        A series of ``datetime64[ns]`` values.
    """
    ser = series.copy()
    # Identify numeric entries (Excel serials)
    numeric_mask = ser.apply(lambda x: isinstance(x, (int, float)))
    parsed = pd.Series(pd.NaT, index=ser.index)
    # Convert numeric serials
    if numeric_mask.any():
        numeric_vals = ser[numeric_mask].astype(float)
        parsed[numeric_mask] = pd.to_datetime(
            numeric_vals, origin="1899-12-30", unit="D"
        )
    # Convert textual dates (day‑first)
    if (~numeric_mask).any():
        parsed[~numeric_mask] = pd.to_datetime(
            ser[~numeric_mask], errors="coerce", dayfirst=True
        )
    return parsed


def extract_hyperlink(value: object) -> str | object:
    """Extract the identifier from an Excel HYPERLINK formula.

    The ``Reserva`` column in the reserva dataset uses formulas of the
    form ``=HIPERLINK("url";"id")`` (semicolon separator) or
    ``=HIPERLINK("url", "id")`` (comma separator).  This function
    returns the final quoted ID if a formula is detected; otherwise
    it returns the original value unchanged.

    Parameters
    ----------
    value : object
        The cell value to parse.

    Returns
    -------
    str | object
        The extracted identifier as a string, or the original value
        if no formula is detected.
    """
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return np.nan
    s = str(value)
    # Check for hyperlink formulas
    if s.startswith("=HYPERLINK") or s.startswith("=HIPERLINK"):
        # Determine the separator (semicolon in Brazilian locale or comma)
        sep = ";" if ";" in s else ","
        try:
            part = s.split(sep)[-1]
            part = part.strip().rstrip(")")
            if part.startswith("\"") and part.endswith("\""):
                part = part[1:-1]
            return part
        except Exception:
            return s
    return s


def load_datasets() -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Load the lead, pré‑cadastro, reserva and repasse datasets.

    Returns
    -------
    tuple
        A tuple ``(leads, precad, reserva, repasse)`` where each
        element is a pandas DataFrame with important columns parsed.
    """
    # Paths for converted Excel files and CSVs
    leads_path = Path("lead2025.xlsx")
    precad_path = Path("precadastro.csv")
    reserva_path = Path("reserva.csv")
    repasse_path = Path("repasses.csv")

    # Load leads
    leads = pd.read_excel(leads_path, dtype=object)
    leads["lead_date"] = parse_excel_date(leads["Data da Última Entrada"])
    leads["lead_id"] = pd.to_numeric(leads["Id"], errors="coerce").astype("Int64").astype(str)

    # Load pré‑cadastro
    try:
        precad = pd.read_csv(precad_path, sep=None, engine="python", dtype=object)
    except FileNotFoundError:
        precad = pd.read_excel(precad_path.with_suffix(".xlsx"), dtype=object)
    # Clean column names (remove BOM and quotes)
    precad = precad.rename(columns=lambda x: x.replace("\ufeff", "").replace("\"", "").strip())
    precad["precad_date"] = parse_excel_date(precad["Data do Cadastro"])
    precad["precad_id"] = pd.to_numeric(precad["Id"], errors="coerce").astype("Int64").astype(str)
    precad["lead_fk"] = pd.to_numeric(precad["Lead Vinculado"], errors="coerce").astype("Int64").astype(str)

    # Load reserva
    reserva = pd.read_csv(
        reserva_path, sep=None, engine="python", dtype=object, encoding='utf-8'
    )
    # Clean column names (remove BOM and quotes)
    reserva = reserva.rename(
        columns=lambda x: x.replace("\ufeff", "").replace("\"", "").strip()
    )
    # Extract numeric id from HYPERLINK formula
    reserva["Reserva_clean"] = reserva["Reserva"].apply(extract_hyperlink)
    reserva["reserva_id"] = pd.to_numeric(
        reserva["Reserva_clean"], errors="coerce"
    ).astype("Int64").astype(str)
    reserva["precad_fk"] = pd.to_numeric(
        reserva["Pré-cadastro"], errors="coerce"
    ).astype("Int64").astype(str)
    reserva["reserva_date"] = parse_excel_date(reserva["Data"])

    # Load repasse
    repasse = pd.read_csv(
        repasse_path, sep=None, engine="python", dtype=object
    )
    # Clean column names and fix trailing spaces
    repasse = repasse.rename(
        columns=lambda x: x.replace("\ufeff", "").replace("\"", "").strip()
    )
    if "Data de Assinatura " in repasse.columns:
        repasse = repasse.rename(
            columns={"Data de Assinatura ": "Data de Assinatura"}
        )
    repasse["reserva_fk"] = pd.to_numeric(
        repasse["Reserva"], errors="coerce"
    ).astype("Int64").astype(str)
    repasse["repasse_date"] = parse_excel_date(repasse["Data de Assinatura"])
    # Keep only repasses with a valid signature date
    repasse = repasse[repasse["repasse_date"].notna()].copy()

    # Rename the file to avoid confusion with run_analysis_corrected.py
    import os
    os.rename(__file__, "growth_analysis.py")

    return leads, precad, reserva, repasse


def build_repasse_chain(
    leads: pd.DataFrame, precad: pd.DataFrame, reserva: pd.DataFrame, repasse: pd.DataFrame
) -> pd.DataFrame:
    """Augment the repasse table with linked lead, precad and reserva IDs and dates.

    Parameters
    ----------
    leads : pandas.DataFrame
        Leads dataset with ``lead_id`` and ``lead_date``.
    precad : pandas.DataFrame
        Pré‑cadastro dataset with ``precad_id``, ``lead_fk`` and ``precad_date``.
    reserva : pandas.DataFrame
        Reserva dataset with ``reserva_id``, ``precad_fk`` and ``reserva_date``.
    repasse : pandas.DataFrame
        Repasse dataset with ``reserva_fk`` and ``repasse_date``.

    Returns
    -------
    pandas.DataFrame
        Repasse table with additional columns ``lead_id``,
        ``precad_id``, ``reserva_id``, ``lead_date``, ``precad_date`` and
        ``reserva_date`` to form the complete chain.
    """
    # Build mapping dictionaries
    precad_to_lead = dict(zip(precad["precad_id"], precad["lead_fk"]))
    reserva_to_precad = dict(zip(reserva["reserva_id"], reserva["precad_fk"]))
    lead_to_date = dict(zip(leads["lead_id"], leads["lead_date"]))
    precad_to_date = dict(zip(precad["precad_id"], precad["precad_date"]))
    reserva_to_date = dict(zip(reserva["reserva_id"], reserva["reserva_date"]))

    # Create new columns in a copy of repasse
    chain = repasse.copy()
    lead_ids: list[str | pd.NA] = []
    precad_ids: list[str | pd.NA] = []
    reserva_ids: list[str | pd.NA] = []
    for reserva_fk in chain["reserva_fk"]:
        precad_id = reserva_to_precad.get(reserva_fk, pd.NA)
        lead_id = precad_to_lead.get(precad_id, pd.NA)
        precad_ids.append(precad_id)
        lead_ids.append(lead_id)
        reserva_ids.append(reserva_fk)
    chain["precad_id"] = precad_ids
    chain["lead_id"] = lead_ids
    chain["reserva_id"] = reserva_ids
    chain["lead_date"] = chain["lead_id"].map(lead_to_date)
    chain["precad_date"] = chain["precad_id"].map(precad_to_date)
    chain["reserva_date"] = chain["reserva_id"].map(reserva_to_date)
    return chain


def compute_duration_stats(
    df: pd.DataFrame, positive_only: bool = True
) -> dict[str, float | int | np.floating]:
    """Compute mean and trimmed mean durations between funnel stages.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the columns ``lead_date``, ``precad_date``,
        ``reserva_date`` and ``repasse_date`` (for the repasse chain).
    positive_only : bool, default True
        If True, negative durations are ignored when computing means.

    Returns
    -------
    dict
        Dictionary with counts (``n_*``), arithmetic means and
        trimmed means (discarding the lowest 25 % and highest 25 %).
    """
    results: dict[str, float | int | np.floating] = {}

    def duration(series_start: pd.Series, series_end: pd.Series) -> pd.Series:
        delta = (series_end - series_start).dt.days
        delta = delta.dropna()
        if positive_only:
            delta = delta[delta >= 0]
        return delta

    def trimmed_mean(s: pd.Series) -> float:
        if len(s) == 0:
            return float("nan")
        q1, q3 = np.nanpercentile(s, [25, 75])
        trimmed = s[(s >= q1) & (s <= q3)]
        return float(trimmed.mean()) if len(trimmed) > 0 else float("nan")

    # Lead → pré‑cadastro
    lp = duration(df["lead_date"], df["precad_date"])
    results["n_lead_precad"] = int(len(lp))
    results["mean_lead_precad"] = float(lp.mean()) if len(lp) > 0 else float("nan")
    results["trimmed_mean_lead_precad"] = trimmed_mean(lp)
    # Pré‑cadastro → reserva
    pr = duration(df["precad_date"], df["reserva_date"])
    results["n_precad_reserva"] = int(len(pr))
    results["mean_precad_reserva"] = float(pr.mean()) if len(pr) > 0 else float("nan")
    results["trimmed_mean_precad_reserva"] = trimmed_mean(pr)
    # Reserva → repasse
    rr = duration(df["reserva_date"], df["repasse_date"])
    results["n_reserva_repasse"] = int(len(rr))
    results["mean_reserva_repasse"] = float(rr.mean()) if len(rr) > 0 else float("nan")
    results["trimmed_mean_reserva_repasse"] = trimmed_mean(rr)
    # Lead → repasse
    lr = duration(df["lead_date"], df["repasse_date"])
    results["n_lead_repasse"] = int(len(lr))
    results["mean_lead_repasse"] = float(lr.mean()) if len(lr) > 0 else float("nan")
    results["trimmed_mean_lead_repasse"] = trimmed_mean(lr)
    return results


def compute_monthly_conversion_and_distribution(
    leads: pd.DataFrame, precad: pd.DataFrame, reserva: pd.DataFrame, repasse: pd.DataFrame
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Compute monthly conversion rates for leads entering in 2025 and the
    distribution of their repasse (contract signing) months.

    This function constructs a leaner version of the funnel linkage to answer
    questions such as:

    * Of the leads created in a given month, how many eventually repassaram
      (signed a contract)?
    * In which months did those repasses occur?

    It deduplicates pré‑cadastro records by their identifier to ensure each
    pré‑cadastro maps to a single lead.  Reserva records are also
    deduplicated by their reservation identifier (after extracting the
    hyperlink label) to avoid multiple matches to the same contract.  Only
    repasses with a valid signature date greater than or equal to the lead
    creation date are considered.

    Parameters
    ----------
    leads : pandas.DataFrame
        Leads dataset with ``lead_id`` and ``lead_date`` columns.
    precad : pandas.DataFrame
        Pré‑cadastro dataset with ``precad_id`` and ``lead_fk``.
    reserva : pandas.DataFrame
        Reserva dataset with ``reserva_id`` and ``precad_fk``.
    repasse : pandas.DataFrame
        Repasse dataset with ``reserva_fk`` and ``repasse_date``.

    Returns
    -------
    tuple of pandas.DataFrame
        * ``conversion_by_month``: rows for each lead_month of 2025 with
          columns ``lead_month``, ``leads`` (count), ``repassed`` (count)
          and ``conversion_rate``.
        * ``cross_table``: a pivot table whose rows are the repasse_month
          and columns are the lead_month.  Each cell contains the number of
          leads from that entry month who signed in that repasse month.
        * ``explanation_df``: a one‑column dataframe containing human‑
          readable text describing how to interpret the monthly conversion
          results and highlighting the months with the highest conversion
          rates.
    """
    # Filter leads to 2025 and compute entry month
    leads_2025 = leads[leads["lead_date"].dt.year == 2025].copy()
    leads_2025["lead_month"] = leads_2025["lead_date"].dt.to_period("M")

    # Deduplicate pré‑cadastro records by precad_id; keep first occurrence
    precad_unique = precad.drop_duplicates(subset="precad_id")[["precad_id", "lead_fk"]].copy()
    # Keep only pré‑cadastros linked to 2025 leads
    precad_unique = precad_unique[precad_unique["lead_fk"].isin(leads_2025["lead_id"])]

    # Deduplicate reserva records by reserva_id; extract hyperlink label first
    # Recompute reserva_id and precad_fk using existing reserva dataframe
    reserva_dedup = reserva.drop_duplicates(subset="reserva_id")[["reserva_id", "precad_fk"]].copy()
    # Keep only reservas whose pré‑cadastro points to a 2025 lead
    reserva_dedup = reserva_dedup[reserva_dedup["precad_fk"].isin(precad_unique["precad_id"])]

    # Build a small repasse table with numeric reservation id and repasse_date
    repasse_small = repasse[["reserva_fk", "repasse_date"]].copy()
    repasse_small = repasse_small.dropna(subset=["repasse_date"])

    # Merge reserva with repasse on reservation identifier
    reserva_rep = reserva_dedup.merge(
        repasse_small,
        left_on="reserva_id",
        right_on="reserva_fk",
        how="inner",
    )
    # Attach lead_id to each reservation via precad_id
    reserva_rep = reserva_rep.merge(
        precad_unique.rename(columns={"lead_fk": "lead_id"})[["precad_id", "lead_id"]],
        left_on="precad_fk",
        right_on="precad_id",
        how="inner",
    )

    # For each lead, take the earliest repasse_date (in case of multiple reservations)
    earliest_repasse = (
        reserva_rep.groupby("lead_id")["repasse_date"].min().reset_index()
    )

    # Combine with leads_2025 to identify which leads repassaram and when
    lead_info = leads_2025[["lead_id", "lead_date", "lead_month"]].merge(
        earliest_repasse, on="lead_id", how="left"
    )
    lead_info["repassed"] = lead_info["repasse_date"].notna()
    # Consider only repasses that occur on or after the lead entry date
    lead_info["valid_repass"] = (
        lead_info["repasse_date"] >= lead_info["lead_date"]
    )
    lead_info["repassed"] &= lead_info["valid_repass"]
    lead_info["repasse_month"] = lead_info["repasse_date"].where(
        lead_info["repassed"]
    ).dt.to_period("M")

    # Compute conversion rate per lead_month
    conversion_by_month = (
        lead_info.groupby("lead_month")
        .agg(leads=("lead_id", "count"), repassed=("repassed", "sum"))
        .reset_index()
    )
    conversion_by_month["conversion_rate"] = (
        conversion_by_month["repassed"] / conversion_by_month["leads"]
    )

    # Build cross table of repasse_month vs lead_month
    cross_table = (
        lead_info[lead_info["repassed"]]
        .pivot_table(
            index="repasse_month",
            columns="lead_month",
            values="lead_id",
            aggfunc="count",
            fill_value=0,
        )
    )

    # Generate explanation text highlighting months with highest conversion
    # Identify top months by conversion rate (descending)
    top_months = (
        conversion_by_month.sort_values(
            "conversion_rate", ascending=False
        ).head(3)
    )
    explanations: list[str] = []
    explanations.append(
        "**Interpretação dos dados:**\n"
        "Cada linha da tabela ‘conversion_by_month’ indica quantos leads entraram no funil em determinado mês de 2025, "
        "quantos desses leads assinaram contrato (repasses) e qual foi a taxa de conversão (repasses ÷ leads). "
        "A tabela de distribuição (abaixo) cruza o mês de entrada do lead com o mês em que o repasse ocorreu.\n"
    )
    explanations.append(
        "**Meses com maior taxa de conversão:**"\
    )
    for _, row in top_months.iterrows():
        m = row["lead_month"]
        rate = row["conversion_rate"]
        leads_count = row["leads"]
        repassed_count = row["repassed"]
        explanations.append(
            f"- {m}: {repassed_count} repasses de {leads_count} leads (taxa aproximadamente {rate:.2%})."
        )
    explanations.append(
        "As distribuições mostram que a maior parte dos repasses ocorre no mesmo mês "
        "ou no mês seguinte ao de entrada do lead, especialmente nos meses com maior conversão."
    )
    explanation_df = pd.DataFrame({"Análise": explanations})
    return conversion_by_month, cross_table.reset_index(), explanation_df


def main() -> None:
    """Execute the corrected analysis and print/export results."""
    leads, precad, reserva, repasse = load_datasets()
    # Filter by year 2025
    leads_2025 = leads[leads["lead_date"].dt.year == 2025]
    precad_2025 = precad[precad["precad_date"].dt.year == 2025]
    reserva_2025 = reserva[reserva["reserva_date"].dt.year == 2025]

    # Build the full repasse chain (all years) and then restrict to 2025 later
    chain = build_repasse_chain(leads, precad, reserva, repasse)

    repasse_2025 = chain[chain["repasse_date"].dt.year == 2025]

    # Count how many repasses in 2025 can be linked to 2025 leads/pre‑cads/reservas
    repasses_from_leads_2025 = repasse_2025[
        repasse_2025["lead_date"].notna() & (repasse_2025["lead_date"].dt.year == 2025)
    ]
    repasses_from_precad_2025 = repasse_2025[
        repasse_2025["precad_date"].notna() & (repasse_2025["precad_date"].dt.year == 2025)
    ]
    repasses_from_reserva_2025 = repasse_2025[
        repasse_2025["reserva_date"].notna() & (repasse_2025["reserva_date"].dt.year == 2025)
    ]

    # Compute counts summary
    counts_df = pd.DataFrame(
        {
            "stage": [
                "Leads",
                "Pré-cadastros",
                "Reservas",
                "Repasses"
            ],
            "total_2025": [
                len(leads_2025),
                len(precad_2025),
                len(reserva_2025),
                len(repasse_2025),
            ],
            "repasses_2025_from_stage": [
                len(repasses_from_leads_2025),
                len(repasses_from_precad_2025),
                len(repasses_from_reserva_2025),
                len(repasse_2025),
            ],
        }
    )

    # Compute duration statistics for the general funnel (all records, not just repasses)
    # Lead → pré‑cadastro: all precad rows with a corresponding lead
    precad_general = precad.copy()
    precad_general["lead_date"] = precad_general["lead_fk"].map(
        dict(zip(leads["lead_id"], leads["lead_date"]))
    )
    lp_all = (
        precad_general["precad_date"] - precad_general["lead_date"]
    ).dt.days.dropna()
    lp_all = lp_all[lp_all >= 0]
    # Pré‑cadastro → reserva: all reserva rows with a corresponding precad
    reserva_general = reserva.copy()
    reserva_general["precad_date"] = reserva_general["precad_fk"].map(
        dict(zip(precad["precad_id"], precad["precad_date"]))
    )
    pr_all = (
        reserva_general["reserva_date"] - reserva_general["precad_date"]
    ).dt.days.dropna()
    pr_all = pr_all[pr_all >= 0]
    # Reserva → repasse and Lead → repasse: use the full chain from repasse (all years)
    rr_all = (
        chain["repasse_date"] - chain["reserva_date"]
    ).dt.days.dropna()
    rr_all = rr_all[rr_all >= 0]
    lr_all = (
        chain["repasse_date"] - chain["lead_date"]
    ).dt.days.dropna()
    lr_all = lr_all[lr_all >= 0]

    def tmean(series: pd.Series) -> float:
        if len(series) == 0:
            return float("nan")
        q1, q3 = np.nanpercentile(series, [25, 75])
        trimmed = series[(series >= q1) & (series <= q3)]
        return float(trimmed.mean()) if len(trimmed) > 0 else float("nan")

    durations_general = {
        "n_lead_precad": int(len(lp_all)),
        "mean_lead_precad": float(lp_all.mean()) if len(lp_all) > 0 else float("nan"),
        "trimmed_mean_lead_precad": tmean(lp_all),
        "n_precad_reserva": int(len(pr_all)),
        "mean_precad_reserva": float(pr_all.mean()) if len(pr_all) > 0 else float("nan"),
        "trimmed_mean_precad_reserva": tmean(pr_all),
        "n_reserva_repasse": int(len(rr_all)),
        "mean_reserva_repasse": float(rr_all.mean()) if len(rr_all) > 0 else float("nan"),
        "trimmed_mean_reserva_repasse": tmean(rr_all),
        "n_lead_repasse": int(len(lr_all)),
        "mean_lead_repasse": float(lr_all.mean()) if len(lr_all) > 0 else float("nan"),
        "trimmed_mean_lead_repasse": tmean(lr_all),
    }
    durations_general_df = (
        pd.DataFrame.from_dict(durations_general, orient="index", columns=["value"])
        .rename_axis("metric")
        .reset_index()
    )

    # Duration statistics for repasses signed in 2025 (successful funnel)
    durations_repasse_2025 = compute_duration_stats(repasse_2025)
    durations_repasse_2025_df = (
        pd.DataFrame.from_dict(durations_repasse_2025, orient="index", columns=["value"])
        .rename_axis("metric")
        .reset_index()
    )

    # Compute monthly conversion analysis and cross‑month distribution
    conversion_by_month_df, cross_table_df, explanation_df = compute_monthly_conversion_and_distribution(
        leads, precad, reserva, repasse
    )

    # Print monthly conversion summary to console
    print("\n=== Conversão mensal de leads de 2025 ===")
    print(conversion_by_month_df.to_string(index=False))
    print("\n=== Distribuição de mês de repasse por mês de entrada (apenas repasses válidos) ===")
    print(cross_table_df.to_string(index=False))
    print("\n=== Explicação dos dados ===")
    for line in explanation_df["Análise"]:
        print(line)

    # Print results to console
    print("=== Contagem de 2025 ===")
    print(counts_df.to_string(index=False))
    print("\n=== Durações médias gerais (todos os registros) ===")
    for metric, value in durations_general.items():
        print(f"{metric}: {value}")
    print("\n=== Durações médias para repasses de 2025 (funil de sucesso) ===")
    for metric, value in durations_repasse_2025.items():
        print(f"{metric}: {value}")

    # Export to Excel
    out_path = Path("funnel_analysis_outputs.xlsx")
    # When writing multiple times to the same workbook, replace existing sheets
    with pd.ExcelWriter(
        out_path,
        engine="openpyxl",
        mode="a" if out_path.exists() else "w",
        if_sheet_exists="replace",
    ) as writer:
        counts_df.to_excel(writer, sheet_name="Counts_2025", index=False)
        durations_general_df.to_excel(writer, sheet_name="Durations_General", index=False)
        durations_repasse_2025_df.to_excel(writer, sheet_name="Durations_Repasses2025", index=False)
        # Write the new monthly conversion sheet with multiple tables
        sheet_name = "Monthly_Conversion"
        start_row = 0
        conversion_by_month_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row)
        start_row += len(conversion_by_month_df) + 2
        cross_table_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row)
        start_row += len(cross_table_df) + 2
        explanation_df.to_excel(writer, sheet_name=sheet_name, index=False, startrow=start_row)


if __name__ == "__main__":
    main()