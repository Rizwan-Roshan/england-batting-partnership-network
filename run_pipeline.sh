#!/bin/bash
# Runs the whole project, from the Cricsheet zip file to the PDF report.
# Every notebook is executed and saved with its outputs, so opening a notebook shows the latest run.
# If a notebook fails (for example a data check that does not pass), the script stops right there.
set -euo pipefail
cd "$(dirname "$0")/notebooks"

NOTEBOOKS=(
  00_run_tests
  01_source_manifest
  02_filter_matches
  03_extract_partnerships
  04_validate_observations
  05_build_networks
  06_compute_measures
  07_make_figures
  08_write_report
)

for notebook in "${NOTEBOOKS[@]}"; do
  echo "== running $notebook.ipynb"
  jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=900 --ExecutePreprocessor.kernel_name=python3 "$notebook.ipynb"
done

# Write down the Python and package versions of this run.
python3 - <<'PY'
import importlib.metadata as metadata, platform, pathlib
packages = ["networkx", "pandas", "numpy", "scipy", "matplotlib", "python-docx", "nbformat", "nbconvert", "ipykernel"]
lines = [f"python {platform.python_version()}"] + [f"{name} {metadata.version(name)}" for name in packages]
pathlib.Path("../outputs/logs/environment.txt").write_text("\n".join(lines) + "\n")
PY
echo "done"
