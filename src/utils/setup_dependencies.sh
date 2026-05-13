#!/bin/bash

# In case of a failure of any command.

set -e

# Setting up variables.
# --- 1. Project Structure ---
echo "📁 Creating directory structure..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

ROOT_SRC_DIR="$(dirname "$SCRIPT_DIR")"

ROOT_DIR="$(dirname "$ROOT_SRC_DIR")"

# Move to the root dir so all the relative routes start from there.

cd "$ROOT_DIR" || { echo "Error: No se pudo acceder a $ROOT_DIR"; exit 1; }

echo " Initializing project Structure in $ROOT_DIR"

mkdir -p bin data/raw data/processed configs docs notebooks scripts tests data/ref

# Installation of Dorado.

if [ ! -f "bin/dorado" ]; then
  echo "Downloading Dorado"
  # Version 0.5.0 you can change if needed.
  curl -L "https://cdn.oxfordnanoportal.com/software/analysis/dorado-0.5.0-linux-x64.tar.gz" -o dorado.tar.gz
  tar -xzf dorado.tar.gz
  echo "Moving Dorado"

  # move dorado to /bin
  mv dorado-0.5.0-linux-x64/bin/dorado bin/
  mv dorado-0.5.0-linux-x64/lib bin/

  # Cleanning the tar and extracted folder.
  rm -rf dorado-0.5.0-linux-x64 dorado.tar.gz
  echo "Dorado Installed in bin/"
fi

