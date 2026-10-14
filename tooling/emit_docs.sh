#!/usr/bin/env bash
# Emit .md, .ll, .llm.txt per layer. Idempotent. Safe to re-run.
set -uo pipefail
cd "$HOME/aether" || { echo "no repo"; exit 1; }

DOCROOT="docs"
mkdir -p "$DOCROOT"

emit_tree() {
  # emit_tree <layer-name> <dir>
  local name="$1" dir="$2"
  [ -d "$dir" ] || return 0
  local out_md="$DOCROOT/$name.md"
  local out_ll="$DOCROOT/$name.ll"
  local out_txt="$DOCROOT/$name.llm.txt"

  {
    echo "# Layer: $name"
    echo
    echo "Directory: \`$dir\`"
    echo
    echo "## Files"
    echo
    find "$dir" -type f \
      ! -path '*/__pycache__/*' ! -path '*/.git/*' ! -path '*/.venv/*' \
      | sort | sed 's/^/    /'
    echo
    echo "## Contents"
    echo
    while IFS= read -r f; do
      case "$f" in
        *.pyc|*.pyo|*.so|*.dylib|*.png|*.jpg|*.jpeg|*.gif|*.pdf|*.safetensors|*.gguf|*.bin) continue ;;
      esac
      echo "### \`$f\`"
      echo
      echo '```'
      sed -n '1,2000p' "$f"
      echo '```'
    done < <(find "$dir" -type f \
      ! -path '*/__pycache__/*' ! -path '*/.git/*' ! -path '*/.venv/*' \
      | sort)
  } > "$out_md"

  # .ll — line-oriented, one record per file with a header line
  {
    echo ";; layer: $name"
    echo ";; dir:   $dir"
    while IFS= read -r f; do
      case "$f" in
        *.pyc|*.pyo|*.so|*.dylib|*.png|*.jpg|*.jpeg|*.gif|*.pdf|*.safetensors|*.gguf|*.bin) continue ;;
      esac
      echo "FILE $f"
      sed -n '1,2000p' "$f"
      echo "ENDFILE $f"
    done < <(find "$dir" -type f \
      ! -path '*/__pycache__/*' ! -path '*/.git/*' ! -path '*/.venv/*' \
      | sort)
  } > "$out_ll"

  # .llm.txt — flat, prose-friendly, single-file-per-layer
  {
    echo "LAYER $name"
    echo "DIR $dir"
    echo
    while IFS= read -r f; do
      case "$f" in
        *.pyc|*.pyo|*.so|*.dylib|*.png|*.jpg|*.jpeg|*.gif|*.pdf|*.safetensors|*.gguf|*.bin) continue ;;
      esac
      echo "----- $f -----"
      sed -n '1,2000p' "$f"
      echo "----- end $f -----"
    done < <(find "$dir" -type f \
      ! -path '*/__pycache__/*' ! -path '*/.git/*' ! -path '*/.venv/*' \
      | sort)
  } > "$out_txt"

  printf "  %-14s md=%6s ll=%6s txt=%6s\n" \
    "$name" \
    "$(wc -c < "$out_md" | tr -d ' ')" \
    "$(wc -c < "$out_ll" | tr -d ' ')" \
    "$(wc -c < "$out_txt" | tr -d ' ')"
}

echo "== emitting per-layer docs =="
for layer in ac ag ax nature data sovereign schemas registries examples; do
  emit_tree "$layer" "$layer"
done

# top-level single-file artifacts (not directories)
emit_file() {
  # emit_file <name> <path>
  local name="$1" path="$2"
  [ -f "$path" ] || return 0
  local out_md="$DOCROOT/$name.md"
  local out_ll="$DOCROOT/$name.ll"
  local out_txt="$DOCROOT/$name.llm.txt"

  {
    echo "# Artifact: $name"
    echo
    echo "Path: \`$path\`"
    echo
    echo '```'
    sed -n '1,4000p' "$path"
    echo '```'
  } > "$out_md"

  {
    echo ";; artifact: $name"
    echo "FILE $path"
    sed -n '1,4000p' "$path"
    echo "ENDFILE $path"
  } > "$out_ll"

  {
    echo "ARTIFACT $name"
    echo "PATH $path"
    echo
    sed -n '1,4000p' "$path"
  } > "$out_txt"

  printf "  %-14s md=%6s ll=%6s txt=%6s\n" \
    "$name" \
    "$(wc -c < "$out_md" | tr -d ' ')" \
    "$(wc -c < "$out_ll" | tr -d ' ')" \
    "$(wc -c < "$out_txt" | tr -d ' ')"
}

echo
echo "== emitting single-file artifacts =="
for f in \
  "components:data/components.json" \
  "capabilities:data/capabilities.json" \
  "nature_catalog:data/nature.txt" \
  "algorithms:data/algorithms.json" \
  "manifest_schema:schemas/manifest.schema.yaml" \
  "manifest_example:examples/auth/manifest.yaml" \
  "registry_schema:registries/SCHEMA.md"
do
  name="${f%%:*}"
  path="${f##*:}"
  emit_file "$name" "$path"
done

# combined index
{
  echo "# Layer Index"
  echo
  echo "Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo
  echo "## Layers"
  for layer in ac ag ax nature data sovereign schemas registries examples; do
    [ -d "$layer" ] || continue
    echo "- [$layer](./$layer.md) — [.ll](./$layer.ll) — [.llm.txt](./$layer.llm.txt)"
  done
  echo
  echo "## Artifacts"
  for f in \
    "components:data/components.json" \
    "capabilities:data/capabilities.json" \
    "nature_catalog:data/nature.txt" \
    "algorithms:data/algorithms.json" \
    "manifest_schema:schemas/manifest.schema.yaml" \
    "manifest_example:examples/auth/manifest.yaml" \
    "registry_schema:registries/SCHEMA.md"
  do
    name="${f%%:*}"
    echo "- [$name](./$name.md) — [.ll](./$name.ll) — [.llm.txt](./$name.llm.txt)"
  done
} > "$DOCROOT/INDEX.md"

echo
echo "wrote $DOCROOT/INDEX.md"
ls -1 "$DOCROOT" | sort | sed 's/^/    /'
