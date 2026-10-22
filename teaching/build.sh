#!/usr/bin/env bash
# Run on the course's remote build host with TeX Live and Pygments.
set -euo pipefail
cd "$(dirname "$0")"
latexmk -xelatex -shell-escape -interaction=nonstopmode -halt-on-error lesson.tex
