# `src/preprocessing/spotify_preprocess.py`

## Purpose

CLI-friendly version of the Spotify preprocessing pipeline. It mirrors the two-pass cleaning logic with explicit argument parsing and logging.

## What it does

* Detects the repository root.
* Validates that the raw CSV has the expected columns.
* Performs chunked cleaning of the raw Spotify lyrics file.
* Removes nulls, short rows, non-English text, and duplicates.
* Computes IQR-based word-count bounds in pass 1.
* Applies the same filtering in pass 2 and writes a single cleaned output file.

## Key functions

* `ascii_ratio(text)` - ASCII heuristic used for English filtering.
* `normalize_meta(s)` - metadata cleanup helper.
* `normalize_title_strong(s)` / `normalize_title(s)` - title normalization helpers.
* `normalize_lyrics(text)` - lyric text normalization.
* `md5_hash(s)` - lyric fingerprint helper for duplicate removal.
* `detect_app_root(start)` - resolves the project root.
* `clean_chunk(chunk)` - applies all per-chunk cleaning steps.
* `pass1_compute_bounds(...)` - derives the acceptable lyric length range.
* `pass2_write_output(...)` - writes the cleaned output CSV.
* `parse_args()` - handles CLI input.
* `main()` - runs the preprocessing pipeline.

## Output

* Default: `data/processed/spotify_clean.csv`

## Notes

* This script is designed for command-line use.
* It keeps preprocessing deterministic by using fixed heuristics and no learned components.