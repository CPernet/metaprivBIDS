"""Backward-compatible class facade over the functional core API."""

from __future__ import annotations

from typing import Any, Sequence

import pandas as pd

from .functions import (
    PseudonymizationResult,
    add_noise,
    bin_numeric_values,
    calculate_k_anonymity,
    calculate_k_combined,
    calculate_k_global,
    calculate_l_diversity,
    calculate_mad_outliers,
    calculate_privacy_metrics,
    combine_categorical_values,
    compute_cig,
    compute_suda2,
    load_tabular_data,
    profile_columns,
    pseudonymize_identifiers,
    revert_column,
    round_values,
    summarize_cig,
)


class metaprivBIDS_core_logic:
    """Compatibility wrapper retained for notebooks and existing integrations.

    New code should import the module-level functions from
    :mod:`metaprivBIDS.corelogic`.
    """

    def __init__(self) -> None:
        self.original_columns: dict[str, pd.Series] = {}
        self.combined_values_history: dict[str, list[tuple[list[Any], Any]]] = {}

    def load_data(self, file_path: str) -> dict[str, Any]:
        data = load_tabular_data(file_path)
        profiles = profile_columns(data)
        return {
            "data": data,
            "original_data": data.copy(),
            "column_unique_counts": dict(zip(profiles["column"], profiles["unique_count"])),
            "column_types": list(
                profiles[["column", "unique_count", "type"]].itertuples(index=False, name=None)
            ),
        }

    def find_lowest_unique_columns(
        self, data: pd.DataFrame, selected_columns: Sequence[str]
    ) -> dict[str, dict[str, float | int]]:
        result = calculate_k_global(data, selected_columns)
        return {
            row.column: {
                "unique_count_after_removal": int(row.unique_rows_after_removal),
                "difference": int(row.difference),
                "normalized_difference": float(row.normalized_difference),
            }
            for row in result.itertuples(index=False)
        }

    def calculate_k_anonymity(
        self, data: pd.DataFrame, selected_columns: Sequence[str]
    ) -> int:
        return calculate_k_anonymity(data, selected_columns)

    def calculate_l_diversity(
        self,
        data: pd.DataFrame,
        selected_columns: Sequence[str],
        sensitive_attr: str,
    ) -> int:
        return calculate_l_diversity(data, selected_columns, sensitive_attr)

    def calculate_unique_rows(
        self,
        data: pd.DataFrame,
        selected_columns: Sequence[str],
        sensitive_attr: str | None = None,
    ) -> dict[str, int | None]:
        return calculate_privacy_metrics(data, selected_columns, sensitive_attr)

    def compute_combined_column_contribution(
        self,
        data: pd.DataFrame,
        selected_columns: Sequence[str],
        min_size: int = 3,
        max_size: int = 7,
    ) -> pd.DataFrame:
        result = calculate_k_combined(data, selected_columns, min_size, max_size)
        return result.rename(
            columns={
                "combination": "Combination",
                "unique_rows": "Unique Rows",
                "unique_rows_excluding_columns": "Unique Rows Excluding Columns",
                "score": "Score",
            }
        )

    def round_values(
        self,
        data: pd.DataFrame,
        column_name: str,
        precision: int,
        mode: str = "up",
    ) -> pd.DataFrame:
        self.original_columns.setdefault(column_name, data[column_name].copy())
        return round_values(data, column_name, precision, mode=mode)

    def pseudonymize_identifiers(
        self,
        data: pd.DataFrame,
        identifier_column: str,
    ) -> PseudonymizationResult:
        return pseudonymize_identifiers(data, identifier_column)

    def bin_numeric_values(
        self,
        data: pd.DataFrame,
        column_name: str,
        *,
        bins: int | None = None,
        width: float | None = None,
    ) -> pd.DataFrame:
        self.original_columns.setdefault(column_name, data[column_name].copy())
        return bin_numeric_values(data, column_name, bins=bins, width=width)

    def revert_to_original(self, data: pd.DataFrame, column_name: str) -> pd.DataFrame:
        if column_name not in self.original_columns:
            raise ValueError(f"No original data available for column {column_name}.")
        original = data.copy()
        original[column_name] = self.original_columns[column_name]
        return revert_column(data, original, column_name)

    def add_noise(
        self,
        data: pd.DataFrame,
        column_name: str,
        noise_type: str,
        scale: float = 1.0,
        seed: int | None = None,
    ) -> pd.DataFrame:
        self.original_columns.setdefault(column_name, data[column_name].copy())
        distribution = "laplacian" if noise_type == "laplacian" else "gaussian"
        return add_noise(data, column_name, distribution, scale=scale, seed=seed)

    def combine_values(
        self,
        data: pd.DataFrame,
        column_name: str,
        values: Sequence[Any] | None = None,
        replacement: Any | None = None,
    ) -> pd.DataFrame:
        if values is None or replacement is None:
            raise ValueError("values and replacement must be supplied explicitly.")
        self.original_columns.setdefault(column_name, data[column_name].copy())
        result = combine_categorical_values(data, column_name, values, replacement)
        self.combined_values_history.setdefault(column_name, []).append((list(values), replacement))
        return result

    def compute_cig(
        self,
        data: pd.DataFrame,
        selected_columns: Sequence[str],
        percentile: float = 95,
        mask_value: Any | None = None,
    ) -> tuple[float, pd.DataFrame]:
        result = compute_cig(data, selected_columns, percentile, mask_value)
        return result.pif_value, result.values

    def describe_cig(self, cig_data: pd.DataFrame) -> pd.DataFrame:
        return summarize_cig(cig_data)

    def compute_suda2(
        self,
        data: pd.DataFrame,
        selected_columns: Sequence[str],
        sample_fraction: float = 0.2,
        missing_value: float | None = None,
    ) -> dict[str, pd.DataFrame]:
        result = compute_suda2(data, selected_columns, sample_fraction, missing_value)
        return {
            "data_with_scores": result.data_with_scores,
            "contribution_percent": result.contribution_percent,
            "attribute_contributions": result.attribute_contributions,
            "attribute_level_contributions": result.attribute_level_contributions,
        }

    def save_boxplot(
        self, df: pd.DataFrame, column_name: str, k: float = 2.2414
    ) -> pd.DataFrame:
        if column_name not in df.columns:
            raise ValueError(f"Column '{column_name}' not found in the DataFrame.")
        return calculate_mad_outliers(df[column_name], threshold=k)
