#!/bin/bash
# Reproduce everything from the raw archive. Stops at the first failed gate.
set -euo pipefail
cd "$(dirname "$0")"
python3 -m pytest -q
for s in 01_build_manifest 02_filter_matches 03_extract_partnerships 04_validate_observations \
         05_build_networks 06_compute_metrics 07_export_graphml 08_make_figures 09_build_report; do
  echo "== $s"
  python3 "scripts/$s.py"
done
scripts/10_export_pdf.sh
python3 -c "
import importlib.metadata as m, platform, pathlib
pk = ['networkx', 'pandas', 'numpy', 'scipy', 'matplotlib', 'python-docx', 'pytest']
pathlib.Path('outputs/logs/environment.txt').write_text(
    'python ' + platform.python_version() + '\n' + '\n'.join(f'{p} {m.version(p)}' for p in pk) + '\n')"
