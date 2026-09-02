# metaprivBIDS

While sharing neuroimaging data, demographic and clinical information of participants must be associated to provide meaningful analysis for prognosis, diagnosis and biomarker identification. MetaprivBIDS assesses and reduces disclosure risk in such demographic and clinical associated data. It provides reusable Python functions, a complete command-line interface, and a local browser interface. SUDA2 is supplied by the established R package `sdcMicro`; all other operations run in Python.

## citation

Please cite: Kibsgaard, E., Sue Jwa, A., Markiewicz, C.J., Rodriguez Gonzalez D., Sainz Pardo, J. Poldrack, R.A. and Pernet C.R. (2026). Assessing metadata privacy in neuroimaging. Imaging Neuroscience 4 IMAG.a.1144. doi: https://doi.org/10.1162/IMAG.a.1144

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

Every analysis and transformation can run without the GUI. The examples use
`conda run`, so the same commands work in PowerShell, Git Bash, and Linux
without activating the environment first. If the environment is already
activated, omit `conda run --name metaprivbids`.

Use `metaprivBIDS COMMAND --help` to see the complete option reference for any
command.

### Inspect data and measure privacy

```console
conda run --name metaprivbids metaprivBIDS inspect Use_Case_Data/adult_mini.csv
conda run --name metaprivbids metaprivBIDS inspect Use_Case_Data/adult_mini.csv --continuous-threshold 45 --output column_profile.csv
conda run --name metaprivbids metaprivBIDS privacy Use_Case_Data/adult_mini.csv --columns age,education,marital-status,occupation,relationship,sex --sensitive salary-class
conda run --name metaprivbids metaprivBIDS k-global Use_Case_Data/adult_mini.csv --columns age,education,marital-status,occupation --output k_global.csv
conda run --name metaprivbids metaprivBIDS k-combined Use_Case_Data/adult_mini.csv --columns age,education,marital-status,occupation --min-size 2 --max-size 4 --output k_combined.csv
```

`inspect` classifies columns using the supplied unique-value threshold.
`privacy` reports the number of unique records, k-anonymity, and l-diversity
when a sensitive attribute is supplied. `k-global` evaluates each selected
column separately; `k-combined` evaluates combinations between `--min-size`
and `--max-size`.

### Transform numeric and categorical values

```console
conda run --name metaprivbids metaprivBIDS round input.csv --column age --exponent 1 --mode nearest --output rounded.csv
conda run --name metaprivbids metaprivBIDS bin input.csv --column age --bins 5 --output binned_by_count.csv
conda run --name metaprivbids metaprivBIDS bin input.csv --column age --width 10 --output binned_by_width.csv
conda run --name metaprivbids metaprivBIDS remove-decimals input.csv --column age --output whole_numbers.csv
conda run --name metaprivbids metaprivBIDS noise input.csv --column age --distribution laplacian --scale 2 --seed 42 --output laplacian_noise.csv
conda run --name metaprivbids metaprivBIDS noise input.csv --column age --distribution gaussian --scale 2 --seed 42 --output gaussian_noise.csv
conda run --name metaprivbids metaprivBIDS combine input.csv --column occupation --values Sales,Service --replacement Customer-facing --output generalized.csv
```

Rounding supports `nearest`, `up`, and `down`. The exponent specifies the
nearest power of ten: `0` rounds to units, `1` to tens, and `2` to hundreds.
The exponent must be zero or positive.
Binning uses equal-width intervals. Choose exactly one method: `--bins` sets
the number of intervals, while `--width` sets the interval increment. Noise
supports `laplacian` and `gaussian`; `--seed` makes a run reproducible.

### Replace direct identifiers and shuffle rows

```console
conda run --name metaprivbids metaprivBIDS pseudonymize input.csv --id-column ID --output released.csv --key-output identifier_key.csv
```

This command replaces every direct identifier with a unique alphanumeric value
of the same displayed length and randomly reorders the released rows. The
separate key contains the old-to-new mapping. Treat the key as sensitive data:
store it separately from the released dataset and do not distribute it with
the anonymised file.

### Compute CIG, RIG, and PIF

```console
conda run --name metaprivbids metaprivBIDS cig input.csv --columns age,education,occupation --percentile 95 --output cig_values.csv --summary-output cig_summary.csv --outliers-output rig_outliers.csv --outlier-threshold 2.2414
```

`--output` saves the row- and cell-level CIG/RIG results,
`--summary-output` saves the variable summary, and `--outliers-output` saves
RIG outliers detected with the supplied MAD threshold. Use `--mask-value nan`
or another value when it should be treated as masked during the calculation.

### Compute SUDA2 through R/sdcMicro

```console
conda run --name metaprivbids metaprivBIDS suda input.csv --columns age,education,occupation --sample-fraction 0.2 --output suda_scores.csv --contribution-percent-output suda_contribution_percent.csv --attribute-contributions-output suda_attribute_contributions.csv --attribute-level-output suda_attribute_levels.csv
```

The main output contains record-level disclosure scores. The three optional
exports contain contribution percentages, attribute contributions, and
attribute-level contributions. Use `--missing-value NUMBER` when the R method
needs an explicit missing-value code. Add `--legacy-scores` only when legacy
score scaling is required.

### Inspect JSON metadata

```console
conda run --name metaprivbids metaprivBIDS metadata metadata.json
conda run --name metaprivbids metaprivBIDS metadata metadata.json --column age
```

Without `--column`, the complete JSON metadata file is printed. With it, only
the metadata associated with that column is printed.

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
reference and [docs/examples.rst](docs/examples.rst) for the illustrated
browser workflow.

Contributors can regenerate all GUI documentation screenshots from the current
application and bundled sample data:

```console
conda run --name metaprivbids uv pip install -e ".[screenshots]"
conda run --name metaprivbids python scripts/capture_docs_screenshots.py
```

## Methods

- k-anonymity and l-diversity
- K-global and K-combined variable contribution
- SUDA2 through `sdcMicro`
- cell/row information gain and Personal Information Factor (PIF)
- direct-identifier replacement with a separately exported key and shuffled
  row order; replacement IDs retain the original displayed length while using
  letters and digits; equal-width binning, rounding, decimal removal,
  categorical generalisation, and Laplacian or
  Gaussian noise

metaprivBIDS is licensed under the MIT License.
