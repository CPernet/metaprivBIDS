# metaprivBIDS

metaprivBIDS assesses and reduces disclosure risk in CSV and TSV data. It
provides reusable Python functions, a complete command-line interface, and a
local browser interface. SUDA2 is supplied by the established R package
`sdcMicro`; all other operations run in Python.

## Reproducible installation

Install Miniforge or another Conda distribution, then run:

```console
conda env create -f environment.yml
conda activate metaprivbids
uv pip install -e ".[test]"
```

Conda owns the compiled runtime boundary: Python 3.12, R 4.4, `sdcMicro`,
`rpy2`, and the Windows R shell tools. `uv` installs the editable Python
package, browser GUI, and test dependencies into that same active environment.
Do not run `uv sync` against this environment because it may remove packages
managed by Conda.

Verify the installation:

```console
python -m pytest -q
metaprivBIDS --help
```

## Command line

Every analysis and transformation can run without a GUI:

```console
metaprivBIDS inspect Use_Case_Data/adult_mini.csv
metaprivBIDS privacy Use_Case_Data/adult_mini.csv \
  --columns age,education,marital-status,occupation,relationship,sex \
  --sensitive salary-class
metaprivBIDS k-global Use_Case_Data/adult_mini.csv \
  --columns age,education,marital-status,occupation --output k_global.csv
metaprivBIDS round input.csv --column age --exponent 1 --output rounded.csv
metaprivBIDS noise input.csv --column age --distribution laplacian \
  --scale 2 --seed 42 --output noisy.csv
metaprivBIDS combine input.csv --column occupation \
  --values Sales,Service --replacement Customer-facing --output generalized.csv
metaprivBIDS cig input.csv --columns age,education,occupation --output cig.csv
metaprivBIDS suda input.csv --columns age,education,occupation --output suda.csv
```

Additional commands include `k-combined`, `remove-decimals`, and `metadata`.
Run `metaprivBIDS COMMAND --help` for all parameters and result export options.

For an executable end-to-end walkthrough, install the notebook tools and open
`MetaprivBIDS_CoreLogic_Tutorial.ipynb` from the repository root:

```console
uv pip install -e ".[notebook]"
jupyter lab MetaprivBIDS_CoreLogic_Tutorial.ipynb
```

## Python API

The GUI and CLI call the same non-interactive functions:

```python
from metaprivBIDS.corelogic import calculate_privacy_metrics, load_tabular_data

data = load_tabular_data("Use_Case_Data/adult_mini.csv")
metrics = calculate_privacy_metrics(
    data,
    ["age", "education", "occupation"],
    sensitive_attribute="salary-class",
)
print(metrics)
```

Functions never display dialogs or mutate the input dataframe. Transformations
return a new dataframe, which makes them suitable for scripts and tests.

## Browser interface

After installation, start the local application with:

```console
metaprivBIDS-gui
```

The server binds to `127.0.0.1`; uploaded data and results remain on the local
machine. See [docs/functionality.md](docs/functionality.md) for the feature
inventory and implementation sequence.

## Methods

- k-anonymity and l-diversity
- K-global and K-combined variable contribution
- SUDA2 through `sdcMicro`
- cell/row information gain and Personal Information Factor (PIF)
- rounding, decimal removal, categorical generalisation, and Laplacian or
  Gaussian noise

metaprivBIDS is licensed under the MIT License.
