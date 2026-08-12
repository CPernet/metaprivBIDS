"""Command-line interface for privacy analysis and anonymisation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Sequence

import numpy as np
import pandas as pd

from .corelogic import (
    add_noise,
    calculate_k_combined,
    calculate_k_global,
    calculate_mad_outliers,
    calculate_privacy_metrics,
    combine_categorical_values,
    compute_cig,
    compute_suda2,
    load_json_metadata,
    load_tabular_data,
    profile_columns,
    remove_decimals,
    round_values,
    summarize_cig,
)


def _columns(value: str) -> list[str]:
    columns = [column.strip() for column in value.split(",") if column.strip()]
    if not columns:
        raise argparse.ArgumentTypeError("Provide one or more comma-separated columns.")
    return columns


def _mask_value(value: str | None) -> Any | None:
    if value is None:
        return None
    if value.lower() == "nan":
        return np.nan
    try:
        return float(value)
    except ValueError:
        return value


def _write_or_print(data: pd.DataFrame, output: str | None, include_index: bool = False) -> None:
    if output:
        data.to_csv(output, index=include_index)
        print(f"Saved {output}")
    else:
        print(data.to_string())


def _save_transformed(data: pd.DataFrame, output: str) -> None:
    separator = "\t" if Path(output).suffix.lower() == ".tsv" else ","
    data.to_csv(output, sep=separator, index=False)
    print(f"Saved {output}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="metaprivBIDS",
        description="Assess and mitigate disclosure risk in CSV/TSV datasets.",
    )
    subcommands = parser.add_subparsers(dest="command", required=True)

    inspect_parser = subcommands.add_parser("inspect", help="Profile a CSV/TSV dataset.")
    inspect_parser.add_argument("input")
    inspect_parser.add_argument("--continuous-threshold", type=int, default=45)
    inspect_parser.add_argument("--output")

    privacy = subcommands.add_parser("privacy", help="Compute unique rows, k, and l.")
    privacy.add_argument("input")
    privacy.add_argument("--columns", required=True, type=_columns)
    privacy.add_argument("--sensitive")

    k_global = subcommands.add_parser("k-global", help="Compute per-column K-global effects.")
    k_global.add_argument("input")
    k_global.add_argument("--columns", required=True, type=_columns)
    k_global.add_argument("--output")

    k_combined = subcommands.add_parser("k-combined", help="Compute combined-column effects.")
    k_combined.add_argument("input")
    k_combined.add_argument("--columns", required=True, type=_columns)
    k_combined.add_argument("--min-size", type=int, default=3)
    k_combined.add_argument("--max-size", type=int, default=7)
    k_combined.add_argument("--output")

    rounding = subcommands.add_parser("round", help="Round one numeric column.")
    rounding.add_argument("input")
    rounding.add_argument("--column", required=True)
    rounding.add_argument("--exponent", required=True, type=int)
    rounding.add_argument("--mode", choices=["nearest", "up", "down"], default="nearest")
    rounding.add_argument("--output", required=True)

    truncate = subcommands.add_parser("remove-decimals", help="Truncate decimals in one column.")
    truncate.add_argument("input")
    truncate.add_argument("--column", required=True)
    truncate.add_argument("--output", required=True)

    noise = subcommands.add_parser("noise", help="Add noise to one numeric column.")
    noise.add_argument("input")
    noise.add_argument("--column", required=True)
    noise.add_argument("--distribution", choices=["laplacian", "gaussian"], required=True)
    noise.add_argument("--scale", type=float, default=1.0)
    noise.add_argument("--seed", type=int)
    noise.add_argument("--output", required=True)

    combine = subcommands.add_parser("combine", help="Generalize categorical values.")
    combine.add_argument("input")
    combine.add_argument("--column", required=True)
    combine.add_argument("--values", required=True, type=_columns)
    combine.add_argument("--replacement", required=True)
    combine.add_argument("--output", required=True)

    cig = subcommands.add_parser("cig", help="Compute CIG, RIG, and PIF.")
    cig.add_argument("input")
    cig.add_argument("--columns", required=True, type=_columns)
    cig.add_argument("--percentile", type=float, default=95)
    cig.add_argument("--mask-value")
    cig.add_argument("--output")
    cig.add_argument("--summary-output")
    cig.add_argument("--outliers-output")
    cig.add_argument("--outlier-threshold", type=float, default=2.2414)

    suda = subcommands.add_parser("suda", help="Compute SUDA2 through R/sdcMicro.")
    suda.add_argument("input")
    suda.add_argument("--columns", required=True, type=_columns)
    suda.add_argument("--sample-fraction", type=float, default=0.2)
    suda.add_argument("--missing-value", type=float)
    suda.add_argument("--legacy-scores", action="store_true")
    suda.add_argument("--output")
    suda.add_argument("--contribution-percent-output")
    suda.add_argument("--attribute-contributions-output")
    suda.add_argument("--attribute-level-output")

    metadata = subcommands.add_parser("metadata", help="Inspect JSON column metadata.")
    metadata.add_argument("input")
    metadata.add_argument("--column")
    return parser


def run(args: argparse.Namespace) -> int:
    if args.command == "metadata":
        metadata = load_json_metadata(args.input)
        value = metadata.get(args.column) if args.column else metadata
        if args.column and args.column not in metadata:
            raise ValueError(f"Metadata has no entry for column '{args.column}'.")
        print(json.dumps(value, indent=2, ensure_ascii=False))
        return 0

    data = load_tabular_data(args.input)
    if args.command == "inspect":
        _write_or_print(profile_columns(data, args.continuous_threshold), args.output)
    elif args.command == "privacy":
        print(json.dumps(calculate_privacy_metrics(data, args.columns, args.sensitive), indent=2))
    elif args.command == "k-global":
        _write_or_print(calculate_k_global(data, args.columns), args.output)
    elif args.command == "k-combined":
        _write_or_print(
            calculate_k_combined(data, args.columns, args.min_size, args.max_size), args.output
        )
    elif args.command == "round":
        _save_transformed(round_values(data, args.column, args.exponent, args.mode), args.output)
    elif args.command == "remove-decimals":
        _save_transformed(remove_decimals(data, args.column), args.output)
    elif args.command == "noise":
        _save_transformed(
            add_noise(data, args.column, args.distribution, args.scale, args.seed), args.output
        )
    elif args.command == "combine":
        _save_transformed(
            combine_categorical_values(data, args.column, args.values, args.replacement),
            args.output,
        )
    elif args.command == "cig":
        result = compute_cig(data, args.columns, args.percentile, _mask_value(args.mask_value))
        print(f"PIF at percentile {result.percentile:g}: {result.pif_value:.6g}")
        _write_or_print(result.values, args.output, include_index=True)
        if args.summary_output:
            summarize_cig(result.values).to_csv(args.summary_output, index=True)
        if args.outliers_output:
            calculate_mad_outliers(result.values["RIG"], args.outlier_threshold).to_csv(
                args.outliers_output, index=True
            )
    elif args.command == "suda":
        result = compute_suda2(
            data,
            args.columns,
            sample_fraction=args.sample_fraction,
            missing_value=args.missing_value,
            original_scores=not args.legacy_scores,
        )
        _write_or_print(result.data_with_scores, args.output, include_index=True)
        outputs = [
            (args.contribution_percent_output, result.contribution_percent),
            (args.attribute_contributions_output, result.attribute_contributions),
            (args.attribute_level_output, result.attribute_level_contributions),
        ]
        for output, frame in outputs:
            if output:
                frame.to_csv(output, index=True)
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        return run(parser.parse_args(argv))
    except (OSError, ValueError, RuntimeError) as error:
        parser.error(str(error))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
