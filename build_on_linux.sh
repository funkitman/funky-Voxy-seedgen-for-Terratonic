#!/usr/bin/env bash
set -euo pipefail
COMMIT=764038d59d09f892e3d09d62a37a512aa09f2bdf
BASE_DIR="$(cd "$(dirname "$0")" && pwd)"
WORK_DIR="${BASE_DIR}/work"
if [[ -e "$WORK_DIR" ]]; then
  echo "Stop: $WORK_DIR already exists. Rename or remove your old build manually." >&2
  exit 1
fi
command -v git >/dev/null
command -v java >/dev/null
command -v python3 >/dev/null
JAVA_MAJOR="$(java -version 2>&1 | sed -n '1s/.*version "\([0-9]*\).*/\1/p')"
if [[ "$JAVA_MAJOR" != "25" ]]; then
  echo "This upstream mod requires Java 25, found: $(java -version 2>&1 | head -1)" >&2
  echo "Set JAVA_HOME to JDK 25 before building." >&2
  exit 1
fi
mkdir -p "$WORK_DIR"
git clone https://github.com/lyuwenhan/minecraft-java-edition-mods.git "$WORK_DIR/upstream"
git -C "$WORK_DIR/upstream" checkout --detach "$COMMIT"
python3 "$BASE_DIR/apply_funky_terratonic.py" "$WORK_DIR/upstream/seedgen" --dry-run
python3 "$BASE_DIR/apply_funky_terratonic.py" "$WORK_DIR/upstream/seedgen"
# Preserve MIT license and upstream/Funky attribution inside the built JAR.
cp "$BASE_DIR/LICENSE" "$WORK_DIR/upstream/seedgen/src/main/resources/LICENSE"
cp "$BASE_DIR/ATTRIBUTION.md" "$WORK_DIR/upstream/seedgen/src/main/resources/ATTRIBUTION.md"
cd "$WORK_DIR/upstream/seedgen"
../gradlew --no-daemon build
mkdir -p "$BASE_DIR/output"
cp -v build/libs/*funky-terratonic*.jar "$BASE_DIR/output/"
cp "$BASE_DIR/LICENSE" "$BASE_DIR/output/LICENSE"
cp "$BASE_DIR/ATTRIBUTION.md" "$BASE_DIR/output/ATTRIBUTION.md"
cp "$BASE_DIR/THIRD_PARTY_NOTICES.md" "$BASE_DIR/output/THIRD_PARTY_NOTICES.md"
echo "Built JAR is in $BASE_DIR/output (use the non-sources JAR in Prism)"
