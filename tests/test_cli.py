import json

import pandas as pd
import pytest

from metaprivBIDS.cli import main


@pytest.fixture
def input_file(tmp_path):
    path = tmp_path / "input.csv"
    pd.DataFrame(
        {
            "ID": [101, 202, 303, 404, 505],
            "age": [25.5, 35.5, 45.5, 25.5, 35.5],
            "city": ["A", "B", "A", "C", "B"],
            "diagnosis": ["x", "x", "y", "z", "y"],
        }
    ).to_csv(path, index=False)
    return path


def test_inspect_and_privacy_commands(input_file, tmp_path, capsys):
    profile = tmp_path / "profile.csv"
    assert main(["inspect", str(input_file), "--output", str(profile)]) == 0
    assert set(pd.read_csv(profile)["column"]) == {"ID", "age", "city", "diagnosis"}
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
        (["bin", "--column", "age", "--bins", "3"], "age"),
        (["bin", "--column", "age", "--width", "10"], "age"),
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


def test_pseudonymize_command_exports_released_data_and_key(input_file, tmp_path):
    output = tmp_path / "released.csv"
    key_output = tmp_path / "identifier_key.csv"

    assert main([
        "pseudonymize", str(input_file), "--id-column", "ID",
        "--output", str(output), "--key-output", str(key_output),
    ]) == 0

    released = pd.read_csv(output)
    key = pd.read_csv(key_output)
    assert released["ID"].str.fullmatch(r"[A-Za-z0-9]{3}").all()
    assert released["ID"].is_unique
    assert list(key.columns) == ["ID_original", "ID_replacement"]
    restored_ids = released.merge(
        key, left_on="ID", right_on="ID_replacement", validate="one_to_one"
    )["ID_original"].tolist()
    assert restored_ids != [101, 202, 303, 404, 505]


def test_binning_exports_array_range_labels(tmp_path):
    source = tmp_path / "ages.csv"
    output = tmp_path / "aggregated.csv"
    pd.DataFrame({"age": [20, 24, 25, 30, None]}).to_csv(source, index=False)

    assert main([
        "bin", str(source), "--column", "age", "--bins", "2",
        "--output", str(output),
    ]) == 0

    ages = pd.read_csv(output)["age"]
    assert ages.iloc[:4].tolist() == ["[20,25]", "[20,25]", "[25,30]", "[25,30]"]
    assert pd.isna(ages.iloc[-1])


@pytest.mark.parametrize("extension,separator", [("csv", ","), ("tsv", "\t")])
def test_binning_median_exports_numeric_age_and_range_array(tmp_path, extension, separator):
    source = tmp_path / "participants.tsv"
    output = tmp_path / f"anonymised.{extension}"
    pd.DataFrame({"participant_id": ["sub-01", "sub-02", "sub-03", "sub-04"],
                  "age": [20, 24, 30, None]}).to_csv(source, sep="\t", index=False, na_rep="n/a")
    assert main([
        "bin", str(source), "--column", "age", "--width", "5", "--median",
        "--output", str(output),
    ]) == 0
    result = pd.read_csv(output, sep=separator)
    assert result["age"].iloc[:3].tolist() == [22.5, 22.5, 32.5]
    assert [json.loads(value) for value in result["age_range"].iloc[:3]] == [
        [20, 25], [20, 25], [30, 35]
    ]
    assert result.loc[3, ["age", "age_range"]].isna().all()
    if extension == "tsv":
        assert output.read_text().splitlines()[1] == "sub-01\t22.5\t[20,25]"
        assert output.read_text().splitlines()[-1] == "sub-04\tn/a\tn/a"


def test_binning_exports_updated_dictionary_alongside_tsv(tmp_path):
    source = tmp_path / "participants.tsv"
    dictionary = tmp_path / "participants.json"
    output = tmp_path / "anonymised.tsv"
    pd.DataFrame({"age": [20, 24, 30]}).to_csv(source, sep="\t", index=False)
    original = {"age": {"Description": "Exact age", "Units": "year"},
                "sex": {"Description": "Reported sex"}}
    dictionary.write_text(json.dumps(original))

    assert main(["bin", str(source), "--column", "age", "--width", "5", "--median",
                 "--metadata", str(dictionary), "--output", str(output)]) == 0
    metadata = json.loads(output.with_suffix(".json").read_text())
    assert metadata["age"]["LongName"] == "Median age from binning"
    assert "age_range" in metadata["age"]["Description"]
    assert "[lower,upper]" in metadata["age_range"]["Description"]
    assert metadata["sex"] == original["sex"]
    assert json.loads(dictionary.read_text()) == original
    assert pd.read_csv(output, sep="\t")["age"].tolist() == [22.5, 22.5, 32.5]


def test_binning_rejects_dictionary_overwrite_before_export(tmp_path):
    source = tmp_path / "participants.tsv"
    dictionary = tmp_path / "participants.json"
    output = tmp_path / "anonymised.tsv"
    pd.DataFrame({"age": [20, 24]}).to_csv(source, sep="\t", index=False)
    dictionary.write_text('{"age":{"Description":"Exact age"}}')
    with pytest.raises(SystemExit):
        main(["bin", str(source), "--column", "age", "--width", "5", "--median",
              "--metadata", str(dictionary), "--metadata-output", str(dictionary),
              "--output", str(output)])
    assert not output.exists()
    assert json.loads(dictionary.read_text())["age"]["Description"] == "Exact age"
