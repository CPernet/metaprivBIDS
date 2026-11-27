import asyncio

import pandas as pd
import pytest
from nicegui import ui
from nicegui.testing.user_simulation import user_simulation

from metaprivBIDS.corelogic import revert_column
from metaprivBIDS.browser_app import (
    WorkspaceState,
    _disclosure_score_outlier_figure,
    _eligible_quasi_identifiers,
    _rig_outlier_figure,
    _safe_outliers,
    create_page,
)


def test_workspace_state_derives_column_roles():
    ages = list(range(50))
    state = WorkspaceState(
        data=pd.DataFrame({"age": ages, "city": ["A", "B"] * 25}),
        original=pd.DataFrame({"age": ages, "city": ["A", "B"] * 25}),
    )
    assert state.loaded
    assert state.columns == ["age", "city"]
    assert state.numeric_columns == ["age"]
    assert state.categorical_columns == ["city"]

    state.column_roles["age"] = "Categorical"
    state.column_roles["city"] = "Continuous"
    assert state.numeric_columns == ["city"]
    assert state.categorical_columns == ["age"]


def test_sensitive_attribute_is_excluded_from_quasi_identifiers():
    columns = ["ID", "age", "city", "diagnosis"]

    assert _eligible_quasi_identifiers(columns, "diagnosis", "ID") == ["age", "city"]
    assert _eligible_quasi_identifiers(columns, None) == columns


def test_direct_identifier_is_not_offered_as_a_transformable_column():
    data = pd.DataFrame({
        "ID": list(range(100, 150)),
        "age": list(range(50)),
        "city": ["A", "B"] * 25,
    })
    state = WorkspaceState(
        data=data,
        original=data.copy(),
        identifier_column="ID",
    )

    assert state.numeric_columns == ["age"]
    assert state.categorical_columns == ["city"]


def test_constant_outlier_input_is_safe():
    result = _safe_outliers(pd.Series([0.0] * 6))
    assert list(result.columns) == ["value", "z_score", "is_outlier"]
    assert result.empty


def test_rig_outlier_hover_identifies_source_row():
    values = pd.Series([0.2, 5.1], index=["participant-01", "participant-17"])

    trace = _rig_outlier_figure(values).data[0]

    assert list(trace.customdata) == ["participant-01", "participant-17"]
    assert trace.hovertemplate == "Source row: %{customdata}<extra></extra>"


def test_disclosure_outlier_hover_identifies_source_row():
    values = pd.Series([0.4, 9.8], index=[12, 41])

    trace = _disclosure_score_outlier_figure(values).data[0]

    assert trace.name == "dis-score"
    assert list(trace.customdata) == ["12", "41"]
    assert trace.hovertemplate == "Source row: %{customdata}<extra></extra>"


def test_browser_page_constructs_without_data():
    workspace = create_page()
    assert not workspace.state.loaded


def test_browser_page_constructs_with_loaded_data():
    data = pd.DataFrame({"age": [20, 30], "city": ["A", "B"]})
    workspace = create_page(WorkspaceState(
        filename="example.csv",
        data=data,
        original=data.copy(),
    ))
    assert workspace.state.loaded


def test_refresh_replaces_empty_state_and_populates_risk_selectors():
    async def scenario():
        workspace_holder = {}

        def root():
            workspace_holder["workspace"] = create_page()

        async with user_simulation(root=root) as user:
            await user.open("/")
            await user.should_see("No data loaded")

            workspace = workspace_holder["workspace"]
            data = pd.DataFrame({"age": list(range(50)), "city": ["A", "B"] * 25})
            workspace.state = WorkspaceState(
                filename="example.csv",
                data=data,
                original=data.copy(),
            )
            workspace.refresh_all()

            await user.should_not_see("No data loaded")
            await user.should_see("Data loaded locally")
            selects = user.find(kind=ui.select).elements
            risk_selects = [
                element for element in selects
                if element.props.get("label") in {
                    "Quasi-identifiers",
                    "Sensitive attribute (optional)",
                }
            ]
            assert len(risk_selects) == 3
            assert all(set(element.options) == {"age", "city"} for element in risk_selects)

            select_all_controls = [
                element
                for element in user.find(kind=ui.checkbox).elements
                if element.text == "Select all quasi-identifiers"
            ]
            assert len(select_all_controls) == 4

            for test_id in (
                "contribution-quasi-identifiers",
                "pif-quasi-identifiers",
                "suda-quasi-identifiers",
            ):
                selection = next(
                    element
                    for element in user.find(kind=ui.select).elements
                    if element.props.get("data-testid") == test_id
                )
                select_all = next(
                    element
                    for element in select_all_controls
                    if element.props.get("data-testid") == f"{test_id}-select-all"
                )
                assert set(selection.options) == {"age", "city"}
                select_all.set_value(True)
                await asyncio.sleep(0)
                assert selection.value == ["age", "city"]

                selection.set_value(["age"])
                await asyncio.sleep(0)
                assert select_all.value is False

    asyncio.run(scenario())


def test_gui_pseudonymization_realigns_restore_copy_and_retains_key():
    async def scenario():
        holder = {}
        original = pd.DataFrame(
            {"ID": [101, 202, 303, 404], "age": [21, 35, 48, 62]}
        )
        working = original.copy()
        working["age"] = [20, 30, 50, 60]

        def root():
            holder["workspace"] = create_page(WorkspaceState(
                filename="example.csv",
                data=working,
                original=original,
            ))

        async with user_simulation(root=root) as user:
            await user.open("/")
            workspace = holder["workspace"]
            with user.client:
                workspace._apply_pseudonymization("ID")

            assert workspace.state.identifier_key is not None
            assert workspace.state.identifier_column == "ID"
            assert workspace.state.column_roles["ID"] == "Categorical"
            restored = revert_column(
                workspace.state.data, workspace.state.original, "age"
            )
            reconstructed = restored.merge(
                workspace.state.identifier_key,
                left_on="ID",
                right_on="ID_replacement",
                validate="one_to_one",
            ).sort_values("ID_original")
            assert reconstructed["age"].tolist() == [21, 35, 48, 62]
            await user.should_see("Download identifier key")

    asyncio.run(scenario())


def test_gui_binning_median_checkbox_applies_numeric_age_and_range():
    async def scenario():
        holder = {}
        data = pd.DataFrame({"age": [20, 24, 30, None]})

        def root():
            holder["workspace"] = create_page(WorkspaceState(
                filename="participants.tsv", data=data.copy(), original=data.copy(),
                column_roles={"age": "Continuous"},
            ))

        async with user_simulation(root=root) as user:
            await user.open("/")
            # Rounding and binning each have a numeric-column selector.
            for element in user.find(kind=ui.select).elements:
                if element.props.get("label") == "Numeric column":
                    element.set_value("age")
            method = next(element for element in user.find(kind=ui.toggle).elements
                          if set(element.options) == {"bins", "width"})
            method.set_value("width")
            width = next(element for element in user.find(kind=ui.number).elements
                         if element.props.get("label") == "Fixed bin width")
            width.set_value(5)
            user.find("Use median and add range column").click()
            await asyncio.sleep(0)
            await user.should_see("Intervals: [20,25], [30,35]")
            user.find("Apply binning").click()
            await asyncio.sleep(0)

            state = holder["workspace"].state
            assert state.data["age"].iloc[:3].tolist() == [22.5, 22.5, 32.5]
            assert state.data["age_range"].iloc[:3].tolist() == ["[20,25]", "[20,25]", "[30,35]"]
            assert state.data.loc[3, ["age", "age_range"]].isna().all()
            assert state.column_roles["age"] == "Continuous"
            assert state.column_roles["age_range"] == "Categorical"
            assert "age_range" in state.categorical_columns
            pd.testing.assert_frame_equal(state.original, data)
            await user.should_see("Download current data (TSV)")

    asyncio.run(scenario())


def test_tsv_download_preserves_array_cells_and_bids_missing_values(monkeypatch):
    from metaprivBIDS.browser_app import _download_frame

    downloads = []
    monkeypatch.setattr(ui, "download", lambda content, **kwargs: downloads.append((content, kwargs)))
    frame = pd.DataFrame({"age": [22.5, None], "age_range": ["[20,25]", None]})
    _download_frame(frame, "participants.tsv")
    content, options = downloads[0]
    assert options["filename"] == "participants.tsv"
    assert content.decode("utf-8").splitlines() == [
        "age\tage_range", "22.5\t[20,25]", "n/a\tn/a"
    ]


@pytest.mark.parametrize("load_after,metadata", [
    (False, {"age": {"Description": "Exact age", "Units": "year"}, "sex": {"Description": "Reported sex"}}),
    (True, {"age": {"Description": "Exact age", "Units": "year"}, "sex": {"Description": "Reported sex"}}),
    (True, {}),
])
def test_gui_binning_updates_and_bundles_loaded_dictionary(monkeypatch, load_after, metadata):
    from copy import deepcopy
    from io import BytesIO
    import json
    from types import SimpleNamespace
    from zipfile import ZipFile

    downloads = []
    monkeypatch.setattr(ui, "download", lambda content, **kwargs: downloads.append((content, kwargs)))
    original_metadata = deepcopy(metadata)

    async def scenario():
        holder = {}
        data = pd.DataFrame({"age": [20, 24, 30, None]})

        def root():
            holder["workspace"] = create_page(WorkspaceState(
                filename="participants.tsv", data=data.copy(), original=data.copy(),
                metadata={} if load_after else metadata,
                column_roles={"age": "Continuous"},
            ))

        async with user_simulation(root=root) as user:
            await user.open("/")
            workspace = holder["workspace"]
            with user.client:
                workspace._apply_binning("age", "width", None, 5, True)
                if load_after:
                    async def read_json():
                        return metadata
                    await workspace.load_metadata(SimpleNamespace(file=SimpleNamespace(json=read_json)))
            await user.should_see("Download JSON dictionary")
            assert workspace.state.metadata["age"]["LongName"] == "Median age from binning"
            assert "age_range" in workspace.state.metadata
            user.find("Download current data (TSV)").click()
            content, options = downloads[-1]
            assert options["filename"] == "metaprivBIDS_anonymised.zip"
            with ZipFile(BytesIO(content)) as archive:
                assert set(archive.namelist()) == {"metaprivBIDS_anonymised.tsv", "metaprivBIDS_anonymised.json"}
                table = archive.read("metaprivBIDS_anonymised.tsv").decode()
                dictionary = json.loads(archive.read("metaprivBIDS_anonymised.json"))
            assert table.splitlines()[1] == "22.5\t[20,25]"
            assert table.splitlines()[-1] == "n/a\tn/a"
            assert dictionary == workspace.state.metadata
            assert dictionary["age_range"]["Units"] == "year"
            if "sex" in metadata:
                assert dictionary["sex"] == metadata["sex"]
            # Restoring age also restores its dictionary and removes its derived range.
            with user.client:
                restored = workspace._restore_column("age")
            pd.testing.assert_frame_equal(restored, data)
            assert workspace.state.metadata == original_metadata
            assert metadata == original_metadata

    asyncio.run(scenario())
