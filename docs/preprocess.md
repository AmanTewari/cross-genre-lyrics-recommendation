# `src/preprocessing/preprocess.py`

## Purpose

Legacy preprocessing script for the Spotify lyrics dataset. It performs two streaming passes over the raw CSV to clean the data before feature extraction.

## What it does

* Detects the repository root from the current working directory.
* Reads `data/raw/songs_with_attributes_and_lyrics.csv` in chunks.
* Filters rows with missing lyrics.
* Filters out short lyrics using a word-count threshold.
* Filters non-English rows using an ASCII ratio heuristic.
* Normalizes title, artist, and lyric text.
* Removes duplicates using composite title+artist keys and lyric hashes.
* Writes a cleaned CSV to `data/processed/clean_lyrics_dataset.csv`.

## Key functions

* `detect_app_root(start)` - finds the project root.
* `ascii_ratio(text)` - measures how much of a string is standard ASCII.
* `normalize_meta(s)` - normalizes metadata text.
* `normalize_title_strong(s)` - aggressive title normalization.
* `normalize_lyrics(text)` - lowercases and cleans lyric text while preserving line breaks.
* `clean_chunk(chunk)` - cleans one chunk of raw input.
* `pass1_compute_bounds(...)` - computes IQR-based word-count bounds.
* `pass2_write_output(...)` - writes the final cleaned dataset.
* `run_pipeline(...)` - executes the full preprocessing flow.

## Output

* `data/processed/clean_lyrics_dataset.csv`

## Notes

* This file is a legacy notebook-style script and runs immediately at import time because of the final `run_pipeline()` call.
* The active preprocessing output is `data/processed/clean_lyrics_dataset.csv`, which is consumed by the feature extraction step.