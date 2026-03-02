#!/bin/bash
# Compiles rules/*.md into AGENTS.md
# Usage: ./scripts/build.sh

RULES_DIR="$(dirname "$0")/../rules"
OUTPUT="$(dirname "$0")/../AGENTS.md"

echo "# VoltDB Development — Compiled Rules" > "$OUTPUT"
echo "" >> "$OUTPUT"
echo "> Auto-generated from rules/*.md — do not edit directly." >> "$OUTPUT"
echo "" >> "$OUTPUT"

for f in "$RULES_DIR"/[!_]*.md; do
  echo "---" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
  cat "$f" >> "$OUTPUT"
  echo "" >> "$OUTPUT"
done

echo "Built AGENTS.md from $(ls "$RULES_DIR"/[!_]*.md | wc -l | tr -d ' ') rules."
