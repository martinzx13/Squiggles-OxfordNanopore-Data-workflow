# Squiggles-OxfordNanopore-Data-workflow

Pipeline for downloading Oxford Nanopore raw signal data (POD5), running targeted basecalling and alignment with Dorado, and preparing a feature store for training a MambaCNN model for antimicrobial resistance (AMR) prediction.

## Directory Structure

```
.
├── bin/              # Dorado binary + shared libraries
├── data/
│   ├── data_index/   # Sample/strain ID index
│   ├── raw/          # Downloaded POD5 files (per strain)
│   ├── processed/    # Alignment BAM files (per strain)
│   └── ref/          # Reference FASTA (AMR + MLST genes)
├── src/
│   ├── scripts/      # Pipeline scripts (Python)
│   │   ├── download_data.py       # Phase 1: download + verify
│   │   ├── run_dorado.py          # Phase 2: basecall + align
│   │   └── compile_features_store.py  # Phase 3: HDF5 feature store (WIP)
│   ├── utils/        # Shell utilities
│   │   └── setup_dependencies.sh  # Install Dorado + create dirs
│   ├── docs/         # Design docs, challenges, session summaries
│   └── notebooks/    # Colab-compatible full workflow
├── deep_env/         # Python virtual environment
├── tests/            # Integration tests
├── download.sh       # One-shot setup + download entry point
└── requirements.txt  # Python package dependencies
```

## Pipeline

| Phase | Script | Description |
|-------|--------|-------------|
| 1 | `src/scripts/download_data.py` | Multi-threaded POD5 download with HAC integrity verification |
| 2 | `src/scripts/run_dorado.py` | Targeted basecalling + alignment via Dorado, piped through `samtools sort` |
| 3 | `src/scripts/compile_features_store.py` | Coordinate-to-Signal mapping and HDF5 feature store compilation (WIP) |

## Quick Start

```bash
# 1. Install system-level dependency (samtools)
#    Linux (Debian/Ubuntu): sudo apt install samtools
#    macOS:                 brew install samtools
#    Linux (RHEL/Fedora):   sudo dnf install samtools

# 2. Set up Python environment
python3 -m venv deep_env
source deep_env/bin/activate
pip install -r requirements.txt

# 3. Download Dorado and prepare directories (auto-detects OS)
bash src/utils/setup_dependencies.sh

# 4. Download and verify raw data
python src/scripts/download_data.py

# 5. Run basecalling and alignment
python src/scripts/run_dorado.py

# 6. Compile feature store
python src/scripts/compile_features_store.py

# 7. Audit BAM quality
python src/scripts/audit_bam_quality.py
```

Or use the convenience entry point (Phase 1 only):

```bash
bash download.sh
```

## CLI Arguments

All pipeline scripts accept `--help` for available options:

| Script | Key arguments | Defaults |
|--------|--------------|----------|
| `download_data.py` | `--max-workers`, `--raw-dir`, `--index-file` | workers=4 |
| `run_dorado.py` | `--reference`, `--raw-dir`, `--processed-dir` | ref=`data/ref/resistance_genes.fasta` |
| `compile_features_store.py` | `--window-size`, `--coverage`, `--max-background`, `--index-file` | window=30000, cov=0.95, bg=500 |
| `audit_bam_quality.py` | `--coverage-threshold`, `--bam-dir` | cov=0.90 |

## Tests

Tests are standalone scripts (NOT pytest). The test requires a completed Phase 3 run:

```bash
python tests/test_feature_store.py
```

This validates the HDF5 feature store structure, class balance, strain coverage, and signal quality.

## Dependencies

- **Dorado 0.5.0** — basecalling and alignment (installed by `setup_dependencies.sh`; supports Linux x64/ARM64 and macOS x64/ARM64)
- **samtools** — BAM sorting and indexing (system package)
- **Python 3.10+** — pipeline orchestration
- See `requirements.txt` for Python package versions

## Docs

Design documents and technical notes are in `src/docs/`:

- `data_infrastructure_v1.md` — Full research roadmap (phases 1–3)
- `bam_audit_plan.md` — BAM quality filtering and audit plan
- `logical_challenges.md` — Floating Window and Move Table geometry
- `session_summary_20260506.md` — Architecture decisions and milestones

## License

MIT — see [LICENSE](LICENSE)
