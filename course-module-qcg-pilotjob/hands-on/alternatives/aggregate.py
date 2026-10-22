"""Aggregate exactly the successful average outputs named on the command line."""

import sys
from pathlib import Path

if len(sys.argv) < 2:
    sys.exit("No average outputs were selected")
rows = []
for name in sys.argv[1:]:
    lines = Path(name).read_text().splitlines()
    if len(lines) != 1 or len(lines[0].split(",")) != 2:
        sys.exit(f"Expected one average row in {name}")
    rows.extend(lines)
print("\n".join(sorted(rows)))
