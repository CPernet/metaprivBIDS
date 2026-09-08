"""Reusable, non-interactive privacy and anonymisation functions.

The functions in this module contain no GUI dialogs, terminal prompts, file
pickers, or plotting side effects.  They are shared by the command-line and
browser interfaces.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
import json
import math
import os
from pathlib import Path
import random
import string
from typing import Any, Iterable, Literal, Sequence

import numpy as np
import pandas as pd


NoiseDistribution = Literal["laplacian", "gaussian"]
RoundingMode = Literal["nearest", "up", "down"]


@dataclass(frozen=True)
class CigResult:
    """Cell/row information gain values and the requested PIF percentile."""

    pif_value: float
    percentile: float
    values: pd.DataFrame


@dataclass(frozen=True)
class SudaResult:
    """All SUDA2 outputs consumed by the CLI and GUI."""

    data_with_scores: pd.DataFrame
    contribution_percent: pd.DataFrame
    attribute_contributions: pd.DataFrame
    attribute_level_contributions: pd.DataFrame


@dataclass(frozen=True)
class PseudonymizationResult:
    """A shuffled working copy, its separate identifier key, and row order."""

    data: pd.DataFrame
    key: pd.DataFrame
    row_order: tuple[int, ...]
    identifier_column: str


def _require_columns(data: pd.DataFrame, columns: Sequence[str]) -> list[str]:
    selected = list(columns)
    if not selected:
        raise ValueError("Select at least one column.")
    missing = [column for column in selected if column not in data.columns]
    if missing:
        raise ValueError(f"Columns not found: {', '.join(missing)}")
    return selected


def load_tabular_data(file_path: str | Path) -> pd.DataFrame:
    """Load a CSV or TSV file and normalize surrounding column whitespace."""

    path = Path(file_path)
    if path.suffix.lower() not in {".csv", ".tsv"}:
        raise ValueError("Input must be a CSV or TSV file.")
    separator = "\t" if path.suffix.lower() == ".tsv" else ","
    data = pd.read_csv(path, sep=separator, skipinitialspace=True)
    if data.empty and len(data.columns) == 0:
        raise ValueError("The input file contains no tabular data.")
    data.columns = data.columns.astype(str).str.strip()
    if data.columns.duplicated().any():
        duplicates = data.columns[data.columns.duplicated()].tolist()
        raise ValueError(f"Duplicate column names after trimming: {duplicates}")
    return data


def profile_columns(data: pd.DataFrame, continuous_threshold: int = 45) -> pd.DataFrame:
    """Return unique counts and inferred categorical/continuous column types."""

    if continuous_threshold < 1:
        raise ValueError("continuous_threshold must be positive.")
    rows = []
    for column in data.columns:
        unique_count = int(data[column].nunique(dropna=True))
        rows.append(
            {
                "column": column,
                "unique_count": unique_count,
                "type": "Continuous" if unique_count > continuous_threshold else "Categorical",
                "dtype": str(data[column].dtype),
                "missing_count": int(data[column].isna().sum()),
            }
        )
    return pd.DataFrame(rows).sort_values("unique_count", ascending=False, ignore_index=True)


def calculate_k_anonymity(data: pd.DataFrame, selected_columns: Sequence[str]) -> int:
    selected = _require_columns(data, selected_columns)
    group_sizes = data.groupby(selected, dropna=False).size()
    return int(group_sizes.min())


def calculate_l_diversity(
    data: pd.DataFrame,
    selected_columns: Sequence[str],
    sensitive_attribute: str,
) -> int:
    selected = _require_columns(data, selected_columns)
    _require_columns(data, [sensitive_attribute])
    if sensitive_attribute in selected:
        raise ValueError("The sensitive attribute cannot also be a quasi-identifier.")
    diversity = data.groupby(selected, dropna=False)[sensitive_attribute].nunique(dropna=False)
    return int(diversity.min())


def calculate_privacy_metrics(
    data: pd.DataFrame,
    selected_columns: Sequence[str],
    sensitive_attribute: str | None = None,
) -> dict[str, int | None]:
    selected = _require_columns(data, selected_columns)
    counts = data[selected].value_counts(dropna=False)
    return {
        "total_rows": len(data),
        "total_columns": len(data.columns),
        "num_selected_columns": len(selected),
        "num_unique_rows": int((counts == 1).sum()),
        "k_anonymity": calculate_k_anonymity(data, selected),
        "l_diversity": (
            calculate_l_diversity(data, selected, sensitive_attribute)
            if sensitive_attribute
            else None
        ),
    }


def _distinct_combination_count(data: pd.DataFrame, columns: Sequence[str]) -> int:
    """Count observed combinations, including missing values and the empty tuple."""
    if not columns:
        return int(len(data) > 0)
    return len(data[list(columns)].drop_duplicates())


def calculate_k_global(data: pd.DataFrame, selected_columns: Sequence[str]) -> pd.DataFrame:
    """Measure each variable's effect on the number of distinct combinations.

    Divide the decrease after removal by the number of distinct non-missing
    values of that variable, rounded to one decimal place. The legacy output
    name ``unique_rows_after_removal`` refers to distinct combinations, not
    singleton records. Missing values participate in combination counts.
    """

    selected = _require_columns(data, selected_columns)
    all_unique_count = _distinct_combination_count(data, selected)
    rows: list[dict[str, Any]] = []
    for column in selected:
        remaining = [candidate for candidate in selected if candidate != column]
        after_removal = _distinct_combination_count(data, remaining)
        difference = all_unique_count - after_removal
        unique_values = int(data[column].nunique(dropna=True))
        normalized = round(difference / unique_values, 1) if unique_values else np.nan
        rows.append(
            {
                "column": column,
                "unique_rows_after_removal": after_removal,
                "difference": difference,
                "normalized_difference": normalized,
            }
        )
    return pd.DataFrame(rows).sort_values(
        "normalized_difference", ascending=False, ignore_index=True
    )


def calculate_k_combined(
    data: pd.DataFrame,
    selected_columns: Sequence[str],
    min_size: int = 3,
    max_size: int = 7,
) -> pd.DataFrame:
    """Measure the effect of removing subsets using distinct combinations.

    The score is the decrease in full-selection combinations after removing
    a subset, divided by that subset's distinct-combination count. Legacy
    ``unique_rows`` output names refer to distinct combinations, not singletons.
    Missing values participate in all combination counts.
    """

    selected = _require_columns(data, selected_columns)
    if min_size < 1 or max_size < min_size or max_size > len(selected):
        raise ValueError(
            f"Combination sizes must satisfy 1 <= min_size <= max_size <= {len(selected)}."
        )
    total_unique = _distinct_combination_count(data, selected)
    rows: list[dict[str, Any]] = []
    for size in range(min_size, max_size + 1):
        for combination in combinations(selected, size):
            combination_columns = list(combination)
            unique_rows = _distinct_combination_count(data, combination_columns)
            remaining = [column for column in selected if column not in combination_columns]
            excluded_unique = _distinct_combination_count(data, remaining)
            score = (
                (total_unique - excluded_unique) / unique_rows if unique_rows else np.nan
            )
            rows.append(
                {
                    "combination": ", ".join(combination_columns),
                    "unique_rows": unique_rows,
                    "unique_rows_excluding_columns": excluded_unique,
                    "score": score,
                }
            )
    return pd.DataFrame(rows)


def round_values(
    data: pd.DataFrame,
    column_name: str,
    exponent: int,
    mode: RoundingMode = "nearest",
) -> pd.DataFrame:
    """Round a numeric column to a power of ten without mutating the input."""

    _require_columns(data, [column_name])
    if exponent < 0:
        raise ValueError("exponent must be zero or positive.")
    if mode not in {"nearest", "up", "down"}:
        raise ValueError("mode must be 'nearest', 'up', or 'down'.")
    numeric = pd.to_numeric(data[column_name], errors="raise")
    factor = 10**exponent
    scaled = numeric / factor
    rounded = scaled.round() if mode == "nearest" else (np.ceil(scaled) if mode == "up" else np.floor(scaled))
    result = data.copy()
    result[column_name] = rounded * factor
    return result


def _format_bin_edge(value: float) -> str:
    if math.isclose(value, 0.0, abs_tol=1e-12):
        value = 0.0
    return f"{value:.12g}"


def bin_numeric_values(
    data: pd.DataFrame,
    column_name: str,
    *,
    bins: int | None = None,
    width: float | None = None,
) -> pd.DataFrame:
    """Replace numeric values with equal-width interval labels.

    Exactly one of ``bins`` (a requested number of intervals across the
    observed range) or ``width`` (interval size aligned to its multiples) must
    be supplied. Missing values remain missing and the input is not mutated.
    """

    _require_columns(data, [column_name])
    if (bins is None) == (width is None):
        raise ValueError("Provide exactly one of bins or width.")
    if bins is not None:
        try:
            numeric_bins = float(bins)
        except (TypeError, ValueError) as error:
            raise ValueError("bins must be an integer of at least 2.") from error
        if (
            isinstance(bins, bool)
            or not math.isfinite(numeric_bins)
            or not numeric_bins.is_integer()
            or numeric_bins < 2
        ):
            raise ValueError("bins must be an integer of at least 2.")
        bins = int(numeric_bins)
    if width is not None:
        try:
            width = float(width)
        except (TypeError, ValueError) as error:
            raise ValueError("width must be a positive finite number.") from error
        if not math.isfinite(width) or width <= 0:
            raise ValueError("width must be a positive finite number.")

    numeric = pd.to_numeric(data[column_name], errors="raise")
    observed = numeric.dropna()
    result = data.copy()
    if observed.empty:
        result[column_name] = pd.Series(pd.NA, index=data.index, dtype="string")
        return result

    minimum = float(observed.min())
    maximum = float(observed.max())
    if minimum == maximum:
        label = f"[{_format_bin_edge(minimum)}, {_format_bin_edge(maximum)}]"
        result[column_name] = numeric.map(lambda value: pd.NA if pd.isna(value) else label).astype("string")
        return result

    if bins is not None:
        edges = np.linspace(minimum, maximum, bins + 1, dtype=float)
    else:
        bin_width = float(width)
        lower = math.floor(minimum / bin_width) * bin_width
        interval_count = max(1, math.ceil((maximum - lower) / bin_width))
        if lower + interval_count * bin_width <= maximum:
            interval_count += 1
        edges = lower + np.arange(interval_count + 1, dtype=float) * bin_width

    cut_edges = edges.copy()
    cut_edges[-1] = np.nextafter(cut_edges[-1], math.inf)
    labels = [
        f"[{_format_bin_edge(left)}, {_format_bin_edge(right)}{']' if index == len(edges) - 2 else ')'}"
        for index, (left, right) in enumerate(zip(edges[:-1], edges[1:]))
    ]
    result[column_name] = pd.cut(
        numeric,
        bins=cut_edges,
        labels=labels,
        right=False,
        include_lowest=True,
        ordered=True,
    )
    return result


def pseudonymize_identifiers(
    data: pd.DataFrame,
    identifier_column: str,
    *,
    seed: int | None = None,
) -> PseudonymizationResult:
    """Replace IDs with same-length alphanumeric values and reorder rows.

    System randomness is used by default. ``seed`` exists for deterministic
    tests and reproducible demonstrations; production callers should omit it.
    """

    _require_columns(data, [identifier_column])
    if data.empty:
        raise ValueError("Cannot generate identifiers for an empty dataset.")
    original_ids = data[identifier_column]
    if original_ids.isna().any() or original_ids.astype(str).str.strip().eq("").any():
        raise ValueError("The identifier column must not contain missing or blank values.")
    if original_ids.duplicated().any():
        raise ValueError("The identifier column must contain unique values.")

    generator = random.SystemRandom() if seed is None else random.Random(seed)
    text_ids = original_ids.astype(str).tolist()
    existing_text = set(text_ids)
    generated_text: set[str] = set()
    replacements = [""] * len(text_ids)
    alphabet = string.ascii_letters + string.digits
    alphabet_set = set(alphabet)
    groups: dict[int, list[int]] = {}
    for index, value in enumerate(text_ids):
        groups.setdefault(len(value), []).append(index)

    for length, indices in groups.items():
        occupied = sum(
            1
            for value in existing_text
            if len(value) == length and set(value) <= alphabet_set
        )
        if len(alphabet) ** length - occupied < len(indices):
            raise ValueError(
                f"Not enough unused {length}-character IDs are available. "
                "Use longer source identifiers."
            )
        for index in indices:
            while True:
                candidate = "".join(generator.choice(alphabet) for _ in range(length))
                if candidate in existing_text or candidate in generated_text:
                    continue
                generated_text.add(candidate)
                replacements[index] = candidate
                break

    transformed = data.copy()
    transformed[identifier_column] = replacements
    row_order = list(range(len(transformed)))
    generator.shuffle(row_order)
    if len(row_order) > 1 and row_order == list(range(len(row_order))):
        row_order = row_order[1:] + row_order[:1]
    transformed = transformed.iloc[row_order].reset_index(drop=True)

    original_name = f"{identifier_column}_original"
    replacement_name = f"{identifier_column}_replacement"
    key = pd.DataFrame(
        {
            original_name: original_ids.to_numpy(copy=True),
            replacement_name: replacements,
        }
    ).sort_values(replacement_name, ignore_index=True)
    return PseudonymizationResult(
        data=transformed,
        key=key,
        row_order=tuple(row_order),
        identifier_column=identifier_column,
    )


def remove_decimals(data: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """Truncate a numeric column toward zero without mutating the input."""

    _require_columns(data, [column_name])
    numeric = pd.to_numeric(data[column_name], errors="raise")
    result = data.copy()
    result[column_name] = np.trunc(numeric).astype("Int64" if numeric.isna().any() else int)
    return result


def add_noise(
    data: pd.DataFrame,
    column_name: str,
    distribution: NoiseDistribution,
    scale: float = 1.0,
    seed: int | None = None,
) -> pd.DataFrame:
    """Add reproducible Laplacian or Gaussian noise to a numeric column."""

    _require_columns(data, [column_name])
    if distribution not in {"laplacian", "gaussian"}:
        raise ValueError("distribution must be 'laplacian' or 'gaussian'.")
    if scale <= 0:
        raise ValueError("scale must be positive.")
    numeric = pd.to_numeric(data[column_name], errors="raise")
    generator = np.random.default_rng(seed)
    noise = (
        generator.laplace(0.0, scale, len(data))
        if distribution == "laplacian"
        else generator.normal(0.0, scale, len(data))
    )
    result = data.copy()
    result[column_name] = numeric + noise
    return result


def add_laplacian_noise(
    data: pd.DataFrame,
    column_name: str,
    scale: float = 1.0,
    seed: int | None = None,
) -> pd.DataFrame:
    return add_noise(data, column_name, "laplacian", scale=scale, seed=seed)


def add_gaussian_noise(
    data: pd.DataFrame,
    column_name: str,
    scale: float = 1.0,
    seed: int | None = None,
) -> pd.DataFrame:
    return add_noise(data, column_name, "gaussian", scale=scale, seed=seed)


def combine_categorical_values(
    data: pd.DataFrame,
    column_name: str,
    values: Iterable[Any],
    replacement: Any,
) -> pd.DataFrame:
    """Replace two or more categorical values with one generalized value."""

    _require_columns(data, [column_name])
    selected_values = list(values)
    if len(selected_values) < 2:
        raise ValueError("Select at least two values to combine.")
    missing = [value for value in selected_values if value not in set(data[column_name].dropna())]
    if missing:
        raise ValueError(f"Values not found in {column_name}: {missing}")
    result = data.copy()
    result[column_name] = result[column_name].replace(selected_values, replacement)
    return result


def revert_column(
    data: pd.DataFrame,
    original_data: pd.DataFrame,
    column_name: str,
) -> pd.DataFrame:
    """Restore one column from the initially loaded dataframe."""

    _require_columns(data, [column_name])
    _require_columns(original_data, [column_name])
    if not data.index.equals(original_data.index):
        raise ValueError("Current and original data must have the same index.")
    result = data.copy()
    result[column_name] = original_data[column_name].copy()
    return result


def load_json_metadata(file_path: str | Path) -> dict[str, Any]:
    with Path(file_path).open("r", encoding="utf-8") as stream:
        metadata = json.load(stream)
    if not isinstance(metadata, dict):
        raise ValueError("Metadata JSON must contain an object at the top level.")
    return metadata


def compute_cig(
    data: pd.DataFrame,
    selected_columns: Sequence[str],
    percentile: float = 95,
    mask_value: Any | None = None,
) -> CigResult:
    """Compute CIG, RIG, and the requested PIF percentile."""

    selected = _require_columns(data, selected_columns)
    if not 0 <= percentile <= 100:
        raise ValueError("percentile must be between 0 and 100.")
    source = data[selected].copy()
    if source.empty:
        raise ValueError("Data is empty.")
    if isinstance(mask_value, str) and mask_value.lower() == "nan":
        mask_value = np.nan
    mask = source.isna() if pd.isna(mask_value) and mask_value is not None else None
    if mask_value is not None and not pd.isna(mask_value):
        mask = source.eq(mask_value)
    calculation_data = source.astype(object).where(source.notna(), "NaN")
    try:
        import piflib.pif_calculator as pif
    except ImportError as error:
        raise RuntimeError("CIG requires the Python package 'piflib'.") from error
    values = pd.DataFrame(pif.compute_cigs(calculation_data), index=source.index)
    values.columns = selected
    if mask is not None:
        values = values.mask(mask, 0)
    values["RIG"] = values.sum(axis=1)
    values = values.sort_values("RIG", ascending=False)
    pif_value = float(np.percentile(values["RIG"], percentile))
    return CigResult(pif_value=pif_value, percentile=percentile, values=values)


def summarize_cig(cig_values: pd.DataFrame) -> pd.DataFrame:
    if cig_values.empty:
        raise ValueError("CIG values are empty.")
    values = cig_values.drop(columns=["RIG"], errors="ignore")
    return values.describe().drop(index="count").T


def calculate_mad_outliers(
    values: pd.Series,
    threshold: float = 2.2414,
) -> pd.DataFrame:
    """Return robust z-scores and two-sided MAD outlier flags."""

    if threshold <= 0:
        raise ValueError("threshold must be positive.")
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if len(numeric) < 5:
        raise ValueError("At least five numeric values are required.")
    median = float(np.median(numeric))
    mad = float(np.median(np.abs(numeric - median)))
    if mad == 0:
        numeric = numeric[numeric != 0]
        if len(numeric) < 5:
            raise ValueError("MAD is zero and fewer than five non-zero values remain.")
        median = float(np.median(numeric))
        mad = float(np.median(np.abs(numeric - median)))
    if mad == 0:
        raise ValueError("MAD remains zero after excluding zero values.")
    robust_sigma = mad / 0.6745
    z_scores = (numeric - median) / robust_sigma
    return pd.DataFrame(
        {
            "value": numeric,
            "z_score": z_scores,
            "is_outlier": np.abs(z_scores) > threshold,
        },
        index=numeric.index,
    )


def compute_suda2(
    data: pd.DataFrame,
    selected_columns: Sequence[str],
    sample_fraction: float = 0.2,
    missing_value: float | None = None,
    original_scores: bool = True,
) -> SudaResult:
    """Run ``sdcMicro::suda2`` through a lazily loaded rpy2 backend."""

    selected = _require_columns(data, selected_columns)
    if not 0 <= sample_fraction <= 1:
        raise ValueError("sample_fraction must be between 0 and 1.")
    os.environ.setdefault("RPY2_CFFI_MODE", "ABI")
    try:
        from rpy2 import robjects
        from rpy2.robjects import pandas2ri
        from rpy2.robjects.conversion import localconverter
        from rpy2.robjects.packages import importr
    except ImportError as error:
        raise RuntimeError(
            "SUDA2 requires rpy2 plus a compatible R runtime and sdcMicro installation."
        ) from error
    try:
        sdc_micro = importr("sdcMicro")
    except Exception as error:
        raise RuntimeError("R package 'sdcMicro' is not available to rpy2.") from error

    encoded = data[selected].copy()
    for column in encoded.select_dtypes(include=["object", "category", "string"]).columns:
        encoded[column] = encoded[column].astype("category").cat.codes
    with localconverter(robjects.default_converter + pandas2ri.converter):
        r_data = robjects.conversion.py2rpy(encoded.astype(float))
    kwargs: dict[str, Any] = {
        "DisFraction": sample_fraction,
        "original_scores": original_scores,
    }
    if missing_value is not None:
        kwargs["missing"] = missing_value
    result = sdc_micro.suda2(r_data, **kwargs)
    scores = list(result.rx2("score"))
    dis_scores = [round(float(value), 4) for value in result.rx2("disScore")]
    contribution_array = np.asarray(result.rx2("contributionPercent"), dtype=float)
    contribution_percent = pd.DataFrame(
        contribution_array,
        columns=selected,
        index=data.index,
    )
    attribute_contributions = pd.DataFrame(
        {
            "variable": list(result.rx2("attribute_contributions").rx2("variable")),
            "contribution": list(result.rx2("attribute_contributions").rx2("contribution")),
        }
    ).sort_values("contribution", ascending=False, ignore_index=True)
    attribute_contributions["contribution"] = attribute_contributions["contribution"].round(2)
    attribute_level_contributions = pd.DataFrame(
        {
            "variable": list(result.rx2("attribute_level_contributions").rx2("variable")),
            "attribute": list(result.rx2("attribute_level_contributions").rx2("attribute")),
            "contribution": list(result.rx2("attribute_level_contributions").rx2("contribution")),
        }
    )
    attribute_level_contributions["contribution"] = attribute_level_contributions[
        "contribution"
    ].round(2)
    attribute_level_contributions = attribute_level_contributions.sort_values(
        ["variable", "contribution"], ascending=[True, False], ignore_index=True
    )
    scored = encoded.copy()
    scored["dis-score"] = dis_scores
    scored["score"] = scores
    return SudaResult(
        data_with_scores=scored,
        contribution_percent=contribution_percent,
        attribute_contributions=attribute_contributions,
        attribute_level_contributions=attribute_level_contributions,
    )
