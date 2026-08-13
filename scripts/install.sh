#!/usr/bin/env bash
set -euo pipefail

repository_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$repository_root"

conda_executable=""
if command -v conda >/dev/null 2>&1; then
    conda_executable="$(command -v conda)"
else
    for candidate in \
        "$HOME/miniforge3/bin/conda" \
        "$HOME/miniforge3/Scripts/conda.exe" \
        "$HOME/mambaforge/bin/conda" \
        "$HOME/mambaforge/Scripts/conda.exe" \
        "$HOME/miniconda3/bin/conda" \
        "$HOME/miniconda3/Scripts/conda.exe" \
        "$HOME/anaconda3/bin/conda" \
        "$HOME/anaconda3/Scripts/conda.exe"; do
        if [[ -x "$candidate" ]]; then
            conda_executable="$candidate"
            break
        fi
    done
fi

if [[ -z "$conda_executable" ]]; then
    echo "Conda was not found. Install Miniforge, then run this script again." >&2
    exit 1
fi

echo "Using Conda: $conda_executable"
if "$conda_executable" run --name metaprivbids python --version >/dev/null 2>&1; then
    echo "Updating the existing metaprivbids environment..."
    "$conda_executable" env update --name metaprivbids --file environment.yml
else
    echo "Creating the metaprivbids environment..."
    "$conda_executable" env create --file environment.yml
fi

"$conda_executable" run --name metaprivbids uv pip install -e .

echo
echo "Installation complete."
echo "Start the GUI with:"
printf "  '%s' run --name metaprivbids metaprivBIDS-gui\n" "$conda_executable"
