import asyncio

import pandas as pd
from nicegui import ui
from nicegui.testing.user_simulation import user_simulation

from metaprivBIDS.browser_app import WorkspaceState, _safe_outliers, create_page


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


def test_constant_outlier_input_is_safe():
    result = _safe_outliers(pd.Series([0.0] * 6))
    assert list(result.columns) == ["value", "z_score", "is_outlier"]
    assert result.empty


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

    asyncio.run(scenario())
