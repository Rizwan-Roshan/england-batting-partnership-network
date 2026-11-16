#!/bin/bash
# Run the whole project, from the raw archive to the PDF report.
# Each notebook is executed in place, so its saved outputs show the latest run.
# The script stops at the first notebook that fails (for example a failed validation gate).
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
  07_export_graphml
  08_make_figures
  09_write_report
)

for notebook in "${NOTEBOOKS[@]}"; do
  echo "== running $notebook.ipynb"
  jupyter nbconvert --to notebook --execute --inplace \
    --ExecutePreprocessor.timeout=900 --ExecutePreprocessor.kernel_name=python3 "$notebook.ipynb"
done

# Record the software versions used for this run.
python3 - <<'PY'
import importlib.metadata as metadata, platform, pathlib
packages = ["networkx", "pandas", "numpy", "scipy", "matplotlib", "python-docx", "nbformat", "nbconvert", "ipykernel"]
lines = [f"python {platform.python_version()}"] + [f"{name} {metadata.version(name)}" for name in packages]
pathlib.Path("../outputs/logs/environment.txt").write_text("\n".join(lines) + "\n")
PY
echo "done"
