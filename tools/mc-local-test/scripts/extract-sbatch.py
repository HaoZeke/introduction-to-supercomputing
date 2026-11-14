#!/usr/bin/env python3
"""Pull the #SBATCH scripts out of a course README and syntax-check them."""

import argparse
import re
import subprocess
import sys
from pathlib import Path

FENCE = re.compile(r"^```[^\n]*\n(.*?)^```[^\n]*$", re.M | re.S)
JOBNAME = re.compile(r"^#SBATCH\s+-J\s+(\S+)", re.M)


def sbatch_blocks(text):
    blocks = []
    for body in FENCE.findall(text):
        if "#SBATCH" not in body:
            continue
        if not body.endswith("\n"):
            body += "\n"
        blocks.append(body)
    return blocks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("readme", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--expect", type=int, default=2)
    args = parser.parse_args()

    blocks = sbatch_blocks(args.readme.read_text())
    if len(blocks) != args.expect:
        print(
            f"expected {args.expect} SBATCH scripts in {args.readme}, found {len(blocks)}",
            file=sys.stderr,
        )
        return 1

    for index, body in enumerate(blocks, 1):
        match = JOBNAME.search(body)
        name = match.group(1) if match else f"job{index}"
        if args.out:
            args.out.mkdir(parents=True, exist_ok=True)
            path = args.out / f"{index:02d}-{name}.slurm"
            path.write_text(body)
            subprocess.check_call(["bash", "-n", str(path)])
            print(path)
        else:
            subprocess.run(["bash", "-n"], input=body, text=True, check=True)
            print(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
