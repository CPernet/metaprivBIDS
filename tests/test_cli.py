import json

import pandas as pd
import pytest

from metaprivBIDS.cli import main


@pytest.fixture
def input_file(tmp_path):
    path = tmp_path / "input.csv"
    pd.DataFrame(
        {
            "age": [25.5, 35.5, 45.5, 25.5, 35.5],
            "city": ["A", "B", "A", "C", "B"],
            "diagnosis": ["x", "x", "y", "z", "y"],
        }
    ).to_csv(path, index=False)
    return path


def test_inspect_and_privacy_commands(input_file, tmp_path, capsys):
    profile = tmp_path / "profile.csv"
    assert main(["inspect", str(input_file), "--output", str(profile)]) == 0
    assert set(pd.read_csv(profile)["column"]) == {"age", "city", "diagnosis"}
    assert main([
        "privacy", str(input_file), "--columns", "age,city", "--sensitive", "diagnosis"
    ]) == 0
    output = capsys.readouterr().out
    payload = json.loads(output[output.index("{"):])
    assert payload["k_anonymity"] == 1


@pytest.mark.parametrize(
    ("arguments", "column"),
    [
        (["round", "--column", "age", "--exponent", "1"], "age"),
        (["remove-decimals", "--column", "age"], "age"),
        (["noise", "--column", "age", "--distribution", "gaussian", "--seed", "4"], "age"),
        (["combine", "--column", "city", "--values", "A,B", "--replacement", "Large"], "city"),
    ],
)
def test_anonymisation_commands(input_file, tmp_path, arguments, column):
    output = tmp_path / f"{arguments[0]}.csv"
    argv = [arguments[0], str(input_file), *arguments[1:], "--output", str(output)]
    assert main(argv) == 0
    transformed = pd.read_csv(output)
    original = pd.read_csv(input_file)
    assert not transformed[column].equals(original[column])


def test_k_commands(input_file, tmp_path):
    global_output = tmp_path / "global.csv"
    assert main([
        "k-global", str(input_file), "--columns", "age,city", "--output", str(global_output)
    ]) == 0
    combined_output = tmp_path / "combined.csv"
    assert main([
        "k-combined", str(input_file), "--columns", "age,city", "--min-size", "1",
        "--max-size", "2", "--output", str(combined_output)
    ]) == 0
    assert not pd.read_csv(global_output).empty
    assert len(pd.read_csv(combined_output)) == 3
