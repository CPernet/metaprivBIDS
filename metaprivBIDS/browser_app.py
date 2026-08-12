"""Local, cross-platform browser interface for metaprivBIDS."""

from __future__ import annotations

from dataclasses import dataclass, field
from io import BytesIO
import json
import os
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd
import plotly.graph_objects as go
from nicegui import events, run, ui

from .corelogic import (
    CigResult,
    SudaResult,
    add_noise,
    calculate_k_combined,
    calculate_k_global,
    calculate_mad_outliers,
    calculate_privacy_metrics,
    combine_categorical_values,
    compute_cig,
    compute_suda2,
    profile_columns,
    remove_decimals,
    revert_column,
    round_values,
    summarize_cig,
)


APP_CSS = """
:root {
  --mp-ink: #17212b;
  --mp-muted: #607080;
  --mp-border: #dfe6e9;
  --mp-primary: #087f8c;
  --mp-accent: #f3a712;
  --mp-canvas: #f5f8f8;
}
body { background: var(--mp-canvas); color: var(--mp-ink); }
.mp-shell { width: min(1500px, 96vw); margin: 0 auto; }
.mp-hero { background: linear-gradient(125deg, #073b4c, #087f8c); color: white;
  border-radius: 0 0 24px 24px; box-shadow: 0 10px 32px rgba(7,59,76,.16); }
.mp-panel { background: white; border: 1px solid var(--mp-border); border-radius: 16px;
  box-shadow: 0 4px 18px rgba(23,33,43,.06); }
.mp-metric { min-width: 150px; flex: 1; background: #f7fbfb; border-left: 4px solid var(--mp-primary); }
.mp-eyebrow { color: #087f8c; letter-spacing: .08em; text-transform: uppercase;
  font-size: .74rem; font-weight: 700; }
.mp-muted { color: var(--mp-muted); }
.q-tab--active { color: var(--mp-primary) !important; }
"""


@dataclass
class WorkspaceState:
    filename: str = ""
    data: pd.DataFrame | None = None
    original: pd.DataFrame | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    history: dict[str, list[tuple[list[Any], Any]]] = field(default_factory=dict)
    privacy_result: dict[str, Any] | None = None
    k_global_result: pd.DataFrame | None = None
    k_combined_result: pd.DataFrame | None = None
    cig_result: CigResult | None = None
    suda_result: SudaResult | None = None

    @property
    def loaded(self) -> bool:
        return self.data is not None

    @property
    def columns(self) -> list[str]:
        return [] if self.data is None else list(self.data.columns)

    @property
    def numeric_columns(self) -> list[str]:
        if self.data is None:
            return []
        return list(self.data.select_dtypes(include=np.number).columns)

    @property
    def categorical_columns(self) -> list[str]:
        if self.data is None:
            return []
        return [column for column in self.columns if column not in self.numeric_columns]


def _records(frame: pd.DataFrame, limit: int | None = None) -> list[dict[str, Any]]:
    shown = frame.head(limit) if limit else frame
    return json.loads(shown.to_json(orient="records", date_format="iso"))


def _columns(frame: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {
            "name": str(column),
            "label": str(column),
            "field": str(column),
            "sortable": True,
            "align": "left",
        }
        for column in frame.columns
    ]


def _download_frame(frame: pd.DataFrame, filename: str, include_index: bool = False) -> None:
    ui.download(frame.to_csv(index=include_index).encode("utf-8"), filename=filename)


def _data_table(frame: pd.DataFrame, *, limit: int | None = 500) -> None:
    if frame.empty:
        ui.label("No rows to display.").classes("mp-muted")
        return
    ui.table(columns=_columns(frame), rows=_records(frame, limit), row_key=None,
             pagination=15).classes("w-full").props("flat bordered dense")
    if limit and len(frame) > limit:
        ui.label(f"Showing the first {limit:,} of {len(frame):,} rows.").classes("text-xs mp-muted")


def _section(title: str, description: str) -> None:
    ui.label(title).classes("text-xl font-semibold")
    ui.label(description).classes("mp-muted mb-3")


def _metric(label: str, value: Any) -> None:
    with ui.card().classes("mp-metric p-4"):
        ui.label(label).classes("text-xs uppercase tracking-wide mp-muted")
        ui.label("—" if value is None else str(value)).classes("text-2xl font-semibold")


def _safe_outliers(values: pd.Series) -> pd.DataFrame:
    """Return an empty typed result when a constant series has no MAD outliers."""

    try:
        return calculate_mad_outliers(values)
    except ValueError:
        return pd.DataFrame(columns=["value", "z_score", "is_outlier"])


class BrowserWorkspace:
    """Build one isolated in-memory workspace for a browser client."""

    def __init__(self) -> None:
        self.state = WorkspaceState()

    def _notify_error(self, error: Exception) -> None:
        ui.notify(str(error), type="negative", close_button=True, timeout=8000)

    def _require_data(self) -> pd.DataFrame:
        if self.state.data is None:
            raise ValueError("Load a CSV or TSV dataset first.")
        return self.state.data

    def refresh_all(self) -> None:
        self.data_panel.refresh()
        self.risk_panel.refresh()
        self.transform_panel.refresh()
        self.pif_panel.refresh()
        self.suda_panel.refresh()

    async def load_dataset(self, event: events.UploadEventArguments) -> None:
        try:
            suffix = Path(event.file.name).suffix.lower()
            if suffix not in {".csv", ".tsv"}:
                raise ValueError("Choose a CSV or TSV file.")
            payload = await event.file.read()
            separator = "\t" if suffix == ".tsv" else ","
            data = pd.read_csv(BytesIO(payload), sep=separator, skipinitialspace=True)
            data.columns = data.columns.astype(str).str.strip()
            if data.columns.duplicated().any():
                raise ValueError("Column names must be unique after trimming whitespace.")
            self.state = WorkspaceState(
                filename=event.file.name,
                data=data,
                original=data.copy(deep=True),
            )
            self.refresh_all()
            ui.notify(f"Loaded {len(data):,} rows from {event.file.name}.", type="positive")
        except Exception as error:
            self._notify_error(error)

    async def load_metadata(self, event: events.UploadEventArguments) -> None:
        try:
            metadata = await event.file.json()
            if not isinstance(metadata, dict):
                raise ValueError("Metadata JSON must contain an object at the top level.")
            self.state.metadata = metadata
            self.data_panel.refresh()
            ui.notify("Metadata loaded.", type="positive")
        except Exception as error:
            self._notify_error(error)

    @ui.refreshable
    def data_panel(self) -> None:
        with self.data_tab:
            with ui.card().classes("mp-panel w-full p-5"):
                _section("Data workspace", "Load and inspect a local CSV or TSV dataset.")
                with ui.row().classes("w-full items-start gap-5"):
                    ui.upload(
                        label="Choose CSV or TSV",
                        auto_upload=True,
                        on_upload=self.load_dataset,
                    ).props("accept=.csv,.tsv flat bordered color=teal-8").classes("grow")
                    ui.upload(
                        label="Optional JSON metadata",
                        auto_upload=True,
                        on_upload=self.load_metadata,
                    ).props("accept=.json flat bordered color=teal-8").classes("grow")

            if not self.state.loaded:
                with ui.card().classes("mp-panel w-full p-8 items-center"):
                    ui.icon("dataset", size="48px").classes("text-teal-700")
                    ui.label("No dataset loaded").classes("text-lg font-medium")
                    ui.label("Data stays in this local browser session.").classes("mp-muted")
                return

            data = self._require_data()
            with ui.row().classes("w-full gap-4"):
                _metric("Rows", f"{len(data):,}")
                _metric("Columns", len(data.columns))
                _metric("Missing cells", f"{int(data.isna().sum().sum()):,}")
                _metric("Source", self.state.filename)

            with ui.card().classes("mp-panel w-full p-5"):
                with ui.row().classes("w-full items-center justify-between"):
                    _section("Data preview", "The current working copy after any transformations.")
                    ui.button(
                        "Download CSV",
                        icon="download",
                        on_click=lambda: _download_frame(data, "metaprivBIDS_data.csv"),
                    ).props("outline color=teal-8")
                _data_table(data)

            with ui.card().classes("mp-panel w-full p-5"):
                _section("Column profile", "Distinct values, inferred role, storage type, and missingness.")
                _data_table(profile_columns(data), limit=None)

            with ui.card().classes("mp-panel w-full p-5"):
                _section("Metadata", "Inspect the JSON entry associated with a dataset column.")
                column = ui.select(self.state.columns, label="Column").classes("w-80")
                output = ui.code("No metadata loaded.", language="json").classes("w-full")

                def show_metadata() -> None:
                    value = self.state.metadata.get(column.value, {})
                    output.set_content(json.dumps(value, indent=2, ensure_ascii=False))

                column.on_value_change(lambda _: show_metadata())

    def _run_privacy(self, qi: list[str], sensitive: str | None) -> None:
        try:
            self.state.privacy_result = calculate_privacy_metrics(
                self._require_data(), qi, sensitive
            )
            self.risk_panel.refresh()
        except Exception as error:
            self._notify_error(error)

    def _run_k_global(self, qi: list[str]) -> None:
        try:
            self.state.k_global_result = calculate_k_global(self._require_data(), qi)
            self.risk_panel.refresh()
        except Exception as error:
            self._notify_error(error)

    def _run_k_combined(self, qi: list[str], min_size: int, max_size: int) -> None:
        try:
            self.state.k_combined_result = calculate_k_combined(
                self._require_data(), qi, int(min_size), int(max_size)
            )
            self.risk_panel.refresh()
        except Exception as error:
            self._notify_error(error)

    @ui.refreshable
    def risk_panel(self) -> None:
        with self.risk_tab:
            with ui.card().classes("mp-panel w-full p-5"):
                _section("Privacy summary", "Select quasi-identifiers and an optional sensitive attribute.")
                qi = ui.select(
                    self.state.columns,
                    label="Quasi-identifiers",
                    multiple=True,
                ).props("use-chips").classes("w-full")
                sensitive = ui.select(
                    self.state.columns,
                    label="Sensitive attribute (optional)",
                    clearable=True,
                ).classes("w-full")
                ui.button(
                    "Calculate privacy metrics",
                    icon="shield",
                    on_click=lambda: self._run_privacy(qi.value or [], sensitive.value),
                ).props("unelevated color=teal-8").bind_enabled_from(self.state, "loaded")

                if self.state.privacy_result:
                    with ui.row().classes("w-full gap-3 mt-4"):
                        labels = {
                            "total_rows": "Rows",
                            "total_columns": "Columns",
                            "num_selected_columns": "Selected",
                            "num_unique_rows": "Sample unique",
                            "k_anonymity": "k-anonymity",
                            "l_diversity": "l-diversity",
                        }
                        for key, label in labels.items():
                            _metric(label, self.state.privacy_result[key])

            with ui.card().classes("mp-panel w-full p-5"):
                _section("Variable contribution", "Rank individual or combined quasi-identifiers.")
                contribution_qi = ui.select(
                    self.state.columns, label="Quasi-identifiers", multiple=True
                ).props("use-chips").classes("w-full")
                with ui.row().classes("items-end gap-3"):
                    minimum = ui.number("Minimum combination", value=3, min=1, step=1)
                    maximum = ui.number("Maximum combination", value=7, min=1, step=1)
                    ui.button(
                        "K-global",
                        on_click=lambda: self._run_k_global(contribution_qi.value or []),
                    ).props("outline color=teal-8")
                    ui.button(
                        "K-combined",
                        on_click=lambda: self._run_k_combined(
                            contribution_qi.value or [], minimum.value, maximum.value
                        ),
                    ).props("outline color=teal-8")

                if self.state.k_global_result is not None:
                    ui.separator().classes("my-4")
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("K-global result").classes("text-lg font-medium")
                        ui.button(
                            "Export",
                            icon="download",
                            on_click=lambda: _download_frame(
                                self.state.k_global_result, "k_global.csv"
                            ),
                        ).props("flat color=teal-8")
                    _data_table(self.state.k_global_result, limit=None)
                if self.state.k_combined_result is not None:
                    ui.separator().classes("my-4")
                    with ui.row().classes("w-full items-center justify-between"):
                        ui.label("K-combined result").classes("text-lg font-medium")
                        ui.button(
                            "Export",
                            icon="download",
                            on_click=lambda: _download_frame(
                                self.state.k_combined_result, "k_combined.csv"
                            ),
                        ).props("flat color=teal-8")
                    _data_table(self.state.k_combined_result, limit=None)

    def _apply_transform(self, operation: Callable[[], pd.DataFrame], message: str) -> None:
        try:
            self.state.data = operation()
            self.state.privacy_result = None
            self.state.k_global_result = None
            self.state.k_combined_result = None
            self.state.cig_result = None
            self.state.suda_result = None
            self.refresh_all()
            ui.notify(message, type="positive")
        except Exception as error:
            self._notify_error(error)

    @ui.refreshable
    def transform_panel(self) -> None:
        with self.transform_tab:
            with ui.card().classes("mp-panel w-full p-5"):
                _section("Numeric transformations", "Apply one reversible operation to the working copy.")
                numeric = ui.select(self.state.numeric_columns, label="Numeric column").classes("w-full")
                with ui.row().classes("w-full items-end gap-3"):
                    exponent = ui.number("Power of ten", value=1, min=0, step=1)
                    rounding_mode = ui.select(
                        ["nearest", "up", "down"], value="nearest", label="Rounding mode"
                    )
                    ui.button(
                        "Round",
                        on_click=lambda: self._apply_transform(
                            lambda: round_values(
                                self._require_data(), numeric.value, int(exponent.value), rounding_mode.value
                            ),
                            f"Rounded {numeric.value}.",
                        ),
                    ).props("outline color=teal-8")
                    ui.button(
                        "Remove decimals",
                        on_click=lambda: self._apply_transform(
                            lambda: remove_decimals(self._require_data(), numeric.value),
                            f"Removed decimals from {numeric.value}.",
                        ),
                    ).props("outline color=teal-8")
                with ui.row().classes("w-full items-end gap-3 mt-2"):
                    distribution = ui.select(
                        ["laplacian", "gaussian"], value="laplacian", label="Noise distribution"
                    )
                    scale = ui.number("Scale / standard deviation", value=1.0, min=0.000001)
                    seed = ui.number("Random seed (optional)", value=None, step=1)
                    ui.button(
                        "Add noise",
                        icon="blur_on",
                        on_click=lambda: self._apply_transform(
                            lambda: add_noise(
                                self._require_data(),
                                numeric.value,
                                distribution.value,
                                float(scale.value),
                                None if seed.value is None else int(seed.value),
                            ),
                            f"Added {distribution.value} noise to {numeric.value}.",
                        ),
                    ).props("unelevated color=teal-8")

            with ui.card().classes("mp-panel w-full p-5"):
                _section("Categorical generalisation", "Combine values under a new, broader label.")
                category = ui.select(
                    self.state.categorical_columns, label="Categorical column"
                ).classes("w-full")
                values = ui.select([], label="Values to combine", multiple=True).props("use-chips").classes("w-full")

                def update_values() -> None:
                    data = self.state.data
                    options = [] if data is None or not category.value else sorted(
                        data[category.value].dropna().astype(str).unique().tolist()
                    )
                    values.set_options(options)

                category.on_value_change(lambda _: update_values())
                replacement = ui.input("Replacement label").classes("w-full")

                def combine() -> None:
                    column_name = category.value
                    selected = values.value or []
                    label = replacement.value
                    try:
                        transformed = combine_categorical_values(
                            self._require_data(), column_name, selected, label
                        )
                        self.state.history.setdefault(column_name, []).append(
                            (list(selected), label)
                        )
                        self._apply_transform(
                            lambda: transformed,
                            f"Generalised values in {column_name}.",
                        )
                    except Exception as error:
                        self._notify_error(error)

                ui.button("Combine values", icon="account_tree", on_click=combine).props(
                    "unelevated color=teal-8"
                )

                if self.state.history:
                    ui.separator().classes("my-4")
                    ui.label("Generalisation hierarchy").classes("text-lg font-medium")
                    lines = ["flowchart LR"]
                    node = 0
                    for column_name, operations in self.state.history.items():
                        lines.append(f'  C{node}["{column_name}"]')
                        root = f"C{node}"
                        node += 1
                        for inputs, output in operations:
                            output_id = f"N{node}"
                            lines.append(f'  {output_id}["{output}"] --> {root}')
                            for value in inputs:
                                input_id = f"N{node}_{abs(hash(str(value))) % 100000}"
                                lines.append(f'  {input_id}["{value}"] --> {output_id}')
                            node += 1
                    ui.mermaid("\n".join(lines)).classes("w-full")

            with ui.card().classes("mp-panel w-full p-5"):
                _section("Revert and export", "Restore one original column or download the working copy.")
                restore = ui.select(self.state.columns, label="Column to restore").classes("w-full")
                with ui.row().classes("gap-3"):
                    ui.button(
                        "Restore column",
                        icon="undo",
                        on_click=lambda: self._apply_transform(
                            lambda: revert_column(
                                self._require_data(), self.state.original, restore.value
                            ),
                            f"Restored {restore.value}.",
                        ),
                    ).props("outline color=teal-8")
                    ui.button(
                        "Download current data",
                        icon="download",
                        on_click=lambda: _download_frame(
                            self._require_data(), "metaprivBIDS_anonymised.csv"
                        ),
                    ).props("unelevated color=teal-8")

    async def _run_cig(
        self, selected: list[str], percentile: float, mask_value: str | None
    ) -> None:
        try:
            parsed_mask: Any | None = mask_value or None
            if parsed_mask and parsed_mask.lower() == "nan":
                parsed_mask = np.nan
            elif parsed_mask:
                try:
                    parsed_mask = float(parsed_mask)
                except ValueError:
                    pass
            with ui.notification(timeout=None, spinner=True) as notice:
                notice.message = "Computing information gain…"
                self.state.cig_result = await run.io_bound(
                    compute_cig,
                    self._require_data(),
                    selected,
                    float(percentile),
                    parsed_mask,
                )
                notice.dismiss()
            self.pif_panel.refresh()
        except Exception as error:
            self._notify_error(error)

    @ui.refreshable
    def pif_panel(self) -> None:
        with self.pif_tab:
            with ui.card().classes("mp-panel w-full p-5"):
                _section("PIF and information gain", "Compute cell (CIG), row (RIG), and percentile risk.")
                selected = ui.select(
                    self.state.columns, label="Variables", multiple=True
                ).props("use-chips").classes("w-full")
                with ui.row().classes("w-full items-end gap-3"):
                    percentile = ui.number("PIF percentile", value=95, min=0, max=100)
                    mask = ui.input("Mask value (optional; use nan for missing)")
                    ui.button(
                        "Compute PIF",
                        icon="analytics",
                        on_click=lambda: self._run_cig(
                            selected.value or [], percentile.value, mask.value
                        ),
                    ).props("unelevated color=teal-8")

            result = self.state.cig_result
            if result is None:
                return
            summary = summarize_cig(result.values)
            outliers = _safe_outliers(result.values["RIG"])
            with ui.row().classes("w-full gap-4"):
                _metric(f"PIF at p{result.percentile:g}", f"{result.pif_value:.4g}")
                _metric("RIG outliers", int(outliers["is_outlier"].sum()))
                _metric("Rows scored", len(result.values))

            with ui.card().classes("mp-panel w-full p-5"):
                with ui.row().classes("w-full justify-between items-center"):
                    _section("CIG / RIG values", "Sorted from highest to lowest row information gain.")
                    ui.button(
                        "Export",
                        icon="download",
                        on_click=lambda: _download_frame(result.values, "cig_rig.csv", True),
                    ).props("flat color=teal-8")
                _data_table(result.values.reset_index(names="source_row"))

            with ui.card().classes("mp-panel w-full p-5"):
                _section("Variable summary", "The leading mean CIG value is the strongest average contributor.")
                mean_leader = summary["mean"].idxmax()
                ui.label(f"Highest mean CIG: {mean_leader}").classes("mp-eyebrow")
                _data_table(summary.reset_index(names="variable"), limit=None)

            with ui.row().classes("w-full gap-5 items-stretch"):
                with ui.card().classes("mp-panel grow p-5"):
                    _section("CIG heat map", "Rows are ordered by descending RIG.")
                    heat_values = result.values.drop(columns="RIG")
                    figure = go.Figure(go.Heatmap(
                        z=heat_values.to_numpy(), x=heat_values.columns, colorscale="Tealgrn"
                    ))
                    figure.update_layout(margin=dict(l=30, r=10, t=10, b=30), height=430)
                    ui.plotly(figure).classes("w-full")
                with ui.card().classes("mp-panel grow p-5"):
                    _section("RIG outliers", "Two-sided robust MAD rule (threshold 2.2414).")
                    figure = go.Figure(go.Box(y=result.values["RIG"], name="RIG", boxpoints="outliers"))
                    figure.update_layout(margin=dict(l=30, r=10, t=10, b=30), height=430)
                    ui.plotly(figure).classes("w-full")
                    ui.button(
                        "Export outliers",
                        icon="download",
                        on_click=lambda: _download_frame(outliers, "rig_outliers.csv", True),
                    ).props("flat color=teal-8")

    async def _run_suda(
        self,
        selected: list[str],
        fraction: float,
        missing: float | None,
        original_scores: bool,
    ) -> None:
        try:
            with ui.notification(timeout=None, spinner=True) as notice:
                notice.message = "Running SUDA2 through sdcMicro…"
                self.state.suda_result = await run.io_bound(
                    compute_suda2,
                    self._require_data(),
                    selected,
                    float(fraction),
                    missing,
                    original_scores,
                )
                notice.dismiss()
            self.suda_panel.refresh()
        except Exception as error:
            self._notify_error(error)

    @ui.refreshable
    def suda_panel(self) -> None:
        with self.suda_tab:
            with ui.card().classes("mp-panel w-full p-5"):
                _section("SUDA2", "Identify risky records and attribute contributions with sdcMicro.")
                selected = ui.select(
                    self.state.columns, label="Variables", multiple=True
                ).props("use-chips").classes("w-full")
                with ui.row().classes("w-full items-end gap-3"):
                    fraction = ui.number("Sampling fraction", value=0.2, min=0, max=1, step=0.05)
                    missing = ui.number("Missing-value code (optional)", value=None)
                    scores = ui.switch("Original SUDA scores", value=True)
                    ui.button(
                        "Run SUDA2",
                        icon="fingerprint",
                        on_click=lambda: self._run_suda(
                            selected.value or [], fraction.value, missing.value, scores.value
                        ),
                    ).props("unelevated color=teal-8")

            result = self.state.suda_result
            if result is None:
                return
            outliers = _safe_outliers(result.data_with_scores["dis-score"])
            with ui.row().classes("w-full gap-4"):
                _metric("Rows scored", len(result.data_with_scores))
                _metric("Positive scores", int((result.data_with_scores["score"] > 0).sum()))
                _metric("MAD outliers", int(outliers["is_outlier"].sum()))

            frames = {
                "Row scores": (result.data_with_scores, "suda_scores.csv", True),
                "Cell contribution %": (result.contribution_percent, "suda_cell_contribution.csv", True),
                "Variable contribution": (result.attribute_contributions, "suda_variables.csv", False),
                "Attribute levels": (result.attribute_level_contributions, "suda_levels.csv", False),
            }
            with ui.card().classes("mp-panel w-full p-5"):
                for label, (frame, filename, include_index) in frames.items():
                    with ui.expansion(label, icon="table_view").classes("w-full"):
                        ui.button(
                            "Export",
                            icon="download",
                            on_click=lambda f=frame, n=filename, i=include_index: _download_frame(f, n, i),
                        ).props("flat color=teal-8")
                        _data_table(frame.reset_index(names="source_row") if include_index else frame)

            with ui.row().classes("w-full gap-5"):
                with ui.card().classes("mp-panel grow p-5"):
                    _section("Disclosure score", "Distribution and box-plot outliers.")
                    figure = go.Figure(go.Box(
                        y=result.data_with_scores["dis-score"], name="dis-score", boxpoints="outliers"
                    ))
                    figure.update_layout(margin=dict(l=30, r=10, t=10, b=30), height=400)
                    ui.plotly(figure).classes("w-full")
                    ui.button(
                        "Export outliers",
                        icon="download",
                        on_click=lambda: _download_frame(outliers, "suda_outliers.csv", True),
                    ).props("flat color=teal-8")
                with ui.card().classes("mp-panel grow p-5"):
                    _section("Variable contribution", "Relative contribution reported by SUDA2.")
                    contribution = result.attribute_contributions
                    figure = go.Figure(go.Bar(
                        x=contribution["variable"], y=contribution["contribution"],
                        marker_color="#087f8c",
                    ))
                    figure.update_layout(margin=dict(l=30, r=10, t=10, b=30), height=400)
                    ui.plotly(figure).classes("w-full")

    def build(self) -> None:
        pass


def create_page(state: WorkspaceState | None = None) -> BrowserWorkspace:
    ui.add_css(APP_CSS)
    with ui.header().classes("mp-hero p-0"):
        with ui.row().classes("mp-shell w-full items-center justify-between px-6 py-5"):
            with ui.column().classes("gap-0"):
                ui.label("metaprivBIDS").classes("text-2xl font-semibold")
                ui.label("Local disclosure-risk workbench").classes("text-sm opacity-80")
            ui.badge("LOCAL SESSION", color="amber-7").props("outline")

    workspace = BrowserWorkspace()
    if state is not None:
        workspace.state = state
    with ui.column().classes("mp-shell w-full gap-5 py-6"):
        with ui.tabs().classes("w-full bg-white rounded-xl shadow-sm") as tabs:
            workspace.data_tab = ui.tab("Data", icon="dataset")
            workspace.risk_tab = ui.tab("Risk", icon="shield")
            workspace.transform_tab = ui.tab("Transform", icon="tune")
            workspace.pif_tab = ui.tab("PIF", icon="analytics")
            workspace.suda_tab = ui.tab("SUDA2", icon="fingerprint")
        with ui.tab_panels(tabs, value=workspace.data_tab).classes("w-full bg-transparent p-0"):
            workspace.data_panel()
            workspace.risk_panel()
            workspace.transform_panel()
            workspace.pif_panel()
            workspace.suda_panel()
    return workspace


def register_pages() -> None:
    @ui.page("/")
    def index() -> None:
        create_page()


def main() -> None:
    register_pages()
    port = int(os.environ.get("METAPRIVBIDS_PORT", "8080"))
    ui.run(
        title="metaprivBIDS",
        host="127.0.0.1",
        port=port,
        reload=False,
        show=os.environ.get("METAPRIVBIDS_SHOW_BROWSER", "1") != "0",
        favicon="🔐",
    )


if __name__ in {"__main__", "__mp_main__"}:
    main()
