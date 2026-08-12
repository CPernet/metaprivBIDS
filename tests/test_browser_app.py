import pandas as pd

from metaprivBIDS.browser_app import WorkspaceState, _safe_outliers, create_page


def test_workspace_state_derives_column_roles():
    state = WorkspaceState(
        data=pd.DataFrame({"age": [20, 30], "city": ["A", "B"]}),
        original=pd.DataFrame({"age": [20, 30], "city": ["A", "B"]}),
    )
    assert state.loaded
    assert state.columns == ["age", "city"]
    assert state.numeric_columns == ["age"]
    assert state.categorical_columns == ["city"]


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
