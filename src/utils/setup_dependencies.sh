#!/bin/bash

# In case of a failure of any command.

set -e

# Setting up variables.
# --- 1. Project Structure ---
echo "📁 Creating directory structure..."

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" &>/dev/null && pwd)"

ROOT_DIR="$(dirname "$SCRIPT_DIR")"

# Move to the root dir so all the relative routes start from there.

cd "$ROOT_DIR" || exit

echo " Initializing project Structure yea $ROOT_DIR"

mkdir -p bin data/raw data/processed configs docs notebooks scripts tests data/ref

# Installation of Dorado.

if [ ! -f "bin/dorado" ]; then
  echo "Downloading Dorado"
  # Version 0.5.0 you can change if needed.
  curl -L "https://cdn.oxfordnanoportal.com/software/analysis/dorado-0.5.0-linux-x64.tar.gz" -o dorado.tar.gz
  tar -xzf dorado.tar.gz

  # move dorado to /bin
  mv dorado-0.5.0-linux-x64/bin/dorado bin/
  mv dorado-0.5.0-linux-x64/lib bin/

  # Cleanning the tar and extracted folder.
  rm -rf dorado-0.5.0-linux-x64 dorado.tar.gz
  echo "Dorado Installed in bin/"
fi

DATA_URL="https://data.narodni-repozitar.cz/general/datasets/dj8ys-a4r49/files/"
RAW_STRAIN_DATA_DIR="data/raw/strains.txt"
TARGET_DIR="data/raw/"

while IFS= read -r STRAIN_ID; do
  echo " Processing Strain: $STRAIN_ID"
  mkdir -p "$TARGET_DIR/$STRAIN_ID"
done <"$RAW_STRAIN_DATA_DIR"

# Create OUT_DIR and DORADO_DIR

# Download the data.

# Go and look to the data/index/data_ids.txt file that contain the idnex

# Start the downlad from the database.
# In this case we will use a database that has the sequence of
# some bacterias for a trainning of a 1CNN-Mamba hybrid to identyfy motif
# and antibiotic resistant bacterias.

# create folders, and put the data in the folders.
