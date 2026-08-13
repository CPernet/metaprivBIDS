# metaprivBIDS

metaprivBIDS assesses and reduces disclosure risk in CSV and TSV data. It
provides reusable Python functions, a complete command-line interface, and a
local browser interface. SUDA2 is supplied by the established R package
`sdcMicro`; all other operations run in Python.

## Reproducible installation

Install a current [Miniforge](https://github.com/conda-forge/miniforge) release,
clone this repository, and open PowerShell, Git Bash, or a Linux terminal in
the repository root.

The easiest installation commands are shell-specific only at the launcher:

```powershell
# Windows PowerShell
powershell -ExecutionPolicy Bypass -File .\scripts\install.ps1
```

```bash
# Git Bash or Linux Bash
bash scripts/install.sh
```

Both scripts locate a default Miniforge/Conda installation, create or update
the environment, and install the Python application. For manual installation,
open the Start-menu **Miniforge Prompt** on Windows or any Conda-enabled Linux
terminal. These commands are then identical in PowerShell and Bash:

```console
conda env create --file environment.yml
conda run --name metaprivbids uv pip install -e .
conda run --name metaprivbids metaprivBIDS --help
```

No environment activation is required. `conda run` explicitly executes each
command inside `metaprivbids`, which avoids PowerShell and Bash initialization
differences. Conda owns Python 3.12, R 4.4, `sdcMicro`, `rpy2`, `uv`, and the
Windows-only R shell tools. `uv` installs the editable Python application and
browser dependencies into that same Conda environment.

Do not run `uv sync` against this environment because it may remove packages
managed by Conda. To update an existing checkout, use:

```console
conda env update --name metaprivbids --file environment.yml
conda run --name metaprivbids uv pip install -e .
```

### Contributor and notebook extras

Install and run tests without activating the environment:

```console
conda run --name metaprivbids uv pip install -e ".[test]"
conda run --name metaprivbids python -m pytest -q
```

PowerShell and Bash both accept the double-quoted `".[test]"` argument. The
quotes prevent shells from interpreting the square brackets.

## Command line

Every analysis and transformation can run without a GUI:

```console
conda run --name metaprivbids metaprivBIDS inspect Use_Case_Data/adult_mini.csv
conda run --name metaprivbids metaprivBIDS privacy Use_Case_Data/adult_mini.csv --columns age,education,marital-status,occupation,relationship,sex --sensitive salary-class
conda run --name metaprivbids metaprivBIDS k-global Use_Case_Data/adult_mini.csv --columns age,education,marital-status,occupation --output k_global.csv
conda run --name metaprivbids metaprivBIDS round input.csv --column age --exponent 1 --output rounded.csv
conda run --name metaprivbids metaprivBIDS noise input.csv --column age --distribution laplacian --scale 2 --seed 42 --output noisy.csv
conda run --name metaprivbids metaprivBIDS combine input.csv --column occupation --values Sales,Service --replacement Customer-facing --output generalized.csv
conda run --name metaprivbids metaprivBIDS cig input.csv --columns age,education,occupation --output cig.csv
conda run --name metaprivbids metaprivBIDS suda input.csv --columns age,education,occupation --output suda.csv
```

Additional commands include `k-combined`, `remove-decimals`, and `metadata`.
Run `metaprivBIDS COMMAND --help` for all parameters and result export options.

For an executable end-to-end walkthrough, install the notebook tools and open
`MetaprivBIDS_CoreLogic_Tutorial.ipynb` from the repository root:

```console
conda run --name metaprivbids uv pip install -e ".[notebook]"
conda run --name metaprivbids jupyter lab MetaprivBIDS_CoreLogic_Tutorial.ipynb
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
conda run --name metaprivbids metaprivBIDS-gui
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
