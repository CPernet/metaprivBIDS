import asyncio

import pandas as pd
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
