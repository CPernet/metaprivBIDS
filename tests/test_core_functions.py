import json

import numpy as np
import pandas as pd
import pytest

from metaprivBIDS.corelogic import (
    add_gaussian_noise,
    add_laplacian_noise,
    calculate_k_combined,
    calculate_k_global,
    calculate_l_diversity,
    calculate_mad_outliers,
    calculate_privacy_metrics,
    combine_categorical_values,
    compute_cig,
    compute_suda2,
    load_json_metadata,
    load_tabular_data,
    metaprivBIDS_core_logic,
    profile_columns,
    remove_decimals,
    revert_column,
    round_values,
    summarize_cig,
)


@pytest.fixture
def data():
    return pd.DataFrame(
        {
            "age": [25, 35, 45, 25, 35, 52],
            "city": ["A", "B", "A", "C", "B", "D"],
            "department": ["HR", "Engineering", "Marketing", "HR", "Engineering", "Legal"],
            "diagnosis": ["x", "x", "y", "z", "y", "z"],
        }
    )


def test_load_and_profile(tmp_path, data):
    path = tmp_path / "data.tsv"
    renamed = data.rename(columns={"age": " age "})
    renamed.to_csv(path, sep="\t", index=False)
    loaded = load_tabular_data(path)
    assert "age" in loaded.columns
    profile = profile_columns(loaded, continuous_threshold=3)
    assert set(profile.columns) == {
        "column", "unique_count", "type", "dtype", "missing_count"
    }
    assert profile.set_index("column").loc["age", "type"] == "Continuous"


def test_load_skips_spaces_after_delimiters(tmp_path):
    path = tmp_path / "spaced.csv"
    path.write_text("age, category\n20, Alpha\n30, Beta\n", encoding="utf-8")
    loaded = load_tabular_data(path)
    assert loaded["category"].tolist() == ["Alpha", "Beta"]


def test_privacy_metrics_and_l_diversity(data):
    result = calculate_privacy_metrics(data, ["age", "city"], "diagnosis")
    assert result == {
        "total_rows": 6,
        "total_columns": 4,
        "num_selected_columns": 2,
        "num_unique_rows": 4,
        "k_anonymity": 1,
        "l_diversity": 1,
    }
    with pytest.raises(ValueError, match="cannot also"):
        calculate_l_diversity(data, ["age", "diagnosis"], "diagnosis")


def test_k_global_and_k_combined(data):
    global_result = calculate_k_global(data, ["age", "city", "department"])
    assert list(global_result.columns) == [
        "column", "unique_rows_after_removal", "difference", "normalized_difference"
    ]
    combined = calculate_k_combined(data, ["age", "city", "department"], 1, 2)
    assert len(combined) == 6
    assert set(combined.columns) == {
        "combination", "unique_rows", "unique_rows_excluding_columns", "score"
    }


@pytest.mark.parametrize(
    ("mode", "expected"),
    [
        ("nearest", [20, 40, 40, 20, 40, 50]),
        ("up", [30, 40, 50, 30, 40, 60]),
        ("down", [20, 30, 40, 20, 30, 50]),
    ],
)
def test_rounding_modes(data, mode, expected):
    result = round_values(data, "age", exponent=1, mode=mode)
    assert result["age"].tolist() == expected
    assert data["age"].tolist() == [25, 35, 45, 25, 35, 52]


def test_remove_decimals():
    data = pd.DataFrame({"value": [1.9, -1.9, 2.0]})
    assert remove_decimals(data, "value")["value"].tolist() == [1, -1, 2]


def test_noise_is_reproducible_and_distribution_specific(data):
    laplace_a = add_laplacian_noise(data, "age", scale=2, seed=7)
    laplace_b = add_laplacian_noise(data, "age", scale=2, seed=7)
    gaussian = add_gaussian_noise(data, "age", scale=2, seed=7)
    pd.testing.assert_frame_equal(laplace_a, laplace_b)
    assert not laplace_a["age"].equals(data["age"])
    assert not laplace_a["age"].equals(gaussian["age"])


def test_combine_and_revert_are_non_mutating(data):
    combined = combine_categorical_values(data, "city", ["A", "B"], "Large")
    assert combined["city"].tolist() == ["Large", "Large", "Large", "C", "Large", "D"]
    assert data["city"].tolist() == ["A", "B", "A", "C", "B", "D"]
    reverted = revert_column(combined, data, "city")
    pd.testing.assert_series_equal(reverted["city"], data["city"])


def test_metadata(tmp_path):
    path = tmp_path / "metadata.json"
    path.write_text(json.dumps({"age": {"Description": "Age in years"}}), encoding="utf-8")
    assert load_json_metadata(path)["age"]["Description"] == "Age in years"


def test_cig_summary_and_outliers(monkeypatch, data):
    import piflib.pif_calculator

    def fake_compute(frame):
        return pd.DataFrame(
            {column: np.arange(1, len(frame) + 1, dtype=float) for column in frame.columns},
            index=frame.index,
        )

    monkeypatch.setattr(piflib.pif_calculator, "compute_cigs", fake_compute)
    result = compute_cig(data, ["age", "city"], percentile=50)
    assert result.pif_value == 7.0
    assert result.values.iloc[0]["RIG"] == 12.0
    summary = summarize_cig(result.values)
    assert list(summary.index) == ["age", "city"]
    outliers = calculate_mad_outliers(result.values["RIG"])
    assert {"value", "z_score", "is_outlier"} <= set(outliers.columns)


def test_compatibility_class_requires_explicit_combinations(data):
    core = metaprivBIDS_core_logic()
    with pytest.raises(ValueError, match="supplied explicitly"):
        core.combine_values(data, "city")
    combined = core.combine_values(data, "city", ["A", "B"], "Large")
    assert core.combined_values_history["city"] == [(["A", "B"], "Large")]
    assert "Large" in combined["city"].values


def test_suda2_uses_conda_r_runtime(data):
    pytest.importorskip("rpy2")
    result = compute_suda2(data, ["age", "city", "department"])
    assert len(result.data_with_scores) == len(data)
    assert {"score", "dis-score"}.issubset(result.data_with_scores.columns)
    assert set(result.attribute_contributions["variable"]) == {
        "age",
        "city",
        "department",
    }
