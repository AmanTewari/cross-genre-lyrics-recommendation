"""Dataset pipeline verification — Step 1.

Loads a lyrics CSV, applies cleaning and deduplication, filters to English
entries, saves the result, and prints verification checks.

Usage (CLI):
    python src/preprocessing/clean_dataset.py
    python src/preprocessing/clean_dataset.py --input data/raw/my_songs.csv --output data/processed/clean_lyrics_dataset.csv

Required columns in the input CSV:
    title, artist, lyrics
"""
from __future__ import annotations

import argparse
import hashlib
import re
from pathlib import Path

import pandas as pd


# ---------------------------------------------------------------------------
# Path helpers
# ---------------------------------------------------------------------------

def detect_app_root(start: Path) -> Path:
    """Walk up the directory tree to find the repository root."""
    base = start
    if base.name == '.venv':
        base = base.parent
    p = base
    for _ in range(10):
        if (p / '.git').exists() or any((p / n).exists() for n in ('readme.md', 'README.md')):
            return p.resolve()
        if p.parent == p:
            break
        p = p.parent
    return base.resolve()


# ---------------------------------------------------------------------------
# 1.2 Null / short-entry removal
# ---------------------------------------------------------------------------

def remove_nulls_and_short(df: pd.DataFrame, min_chars: int = 50) -> pd.DataFrame:
    """Drop rows with null lyrics or stripped length <= min_chars."""
    df = df.dropna(subset=['lyrics']).copy()
    df = df[df['lyrics'].str.strip().str.len() > min_chars].copy()
    return df


# ---------------------------------------------------------------------------
# 1.3 Text normalisation
# ---------------------------------------------------------------------------

def normalize_text(text: str) -> str:
    """Lowercase and strip a text field."""
    if not isinstance(text, str):
        return ''
    return text.lower().strip()


def normalize_fields(df: pd.DataFrame) -> pd.DataFrame:
    """Apply normalize_text to title, artist, and lyrics columns."""
    df = df.copy()
    df['title'] = df['title'].map(normalize_text)
    df['artist'] = df['artist'].map(normalize_text)
    df['lyrics'] = df['lyrics'].map(normalize_text)
    return df


# ---------------------------------------------------------------------------
# 1.4 Duplicate removal
# ---------------------------------------------------------------------------

def hash_lyrics(text: str) -> str:
    """Return the MD5 hex digest of a lyrics string."""
    if not isinstance(text, str):
        return hashlib.md5(b'').hexdigest()
    return hashlib.md5(text.encode('utf-8')).hexdigest()


def remove_duplicates(df: pd.DataFrame) -> pd.DataFrame:
    """Remove exact-row, title+artist, and lyrics-hash duplicates."""
    # A. Exact row duplicates
    df = df.drop_duplicates().copy()

    # B. Duplicate songs (title + artist composite key)
    df = df.drop_duplicates(subset=['title', 'artist']).copy()

    # C. Duplicate lyrics identified by MD5 hash
    df['lyrics_hash'] = df['lyrics'].map(hash_lyrics)
    df = df.drop_duplicates(subset=['lyrics_hash']).copy()

    # Drop the internal hash column — it is an implementation detail, not output data
    df = df.drop(columns=['lyrics_hash'])

    return df


# ---------------------------------------------------------------------------
# 1.5 English filter (heuristic, no NLP)
# ---------------------------------------------------------------------------

# Regex matching strings that contain only characters typical of English text.
# Uses fullmatch so the *entire* string must conform.
# Hyphen is placed at the end of the character class to avoid range ambiguity.
_ENGLISH_PATTERN = re.compile(r'^[a-zA-Z0-9\s.,!?\'"-]+$')


def is_english(text: str) -> bool:
    """Return True if text consists solely of common English characters."""
    if not isinstance(text, str) or not text.strip():
        return False
    return bool(_ENGLISH_PATTERN.match(text))


def filter_english(df: pd.DataFrame) -> pd.DataFrame:
    """Keep only rows whose lyrics pass the English heuristic filter."""
    return df[df['lyrics'].map(is_english)].copy()


# ---------------------------------------------------------------------------
# 1.6 / 1.7 Save and verify
# ---------------------------------------------------------------------------

def save_dataset(df: pd.DataFrame, out_path: Path) -> None:
    """Write the cleaned DataFrame to CSV."""
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)


def run_verification(df: pd.DataFrame) -> bool:
    """Print verification checks and return True if all pass."""
    shape = df.shape
    dup_title_artist = int(df.duplicated(subset=['title', 'artist']).sum())
    # Recompute lyrics hash on the fly for the verification check
    dup_lyrics_hash = int(df['lyrics'].map(hash_lyrics).duplicated().sum())

    print(f"Final shape: {shape}")
    print(f"Duplicates (title+artist): {dup_title_artist}")
    print(f"Duplicates (lyrics hash):  {dup_lyrics_hash}")

    passed = dup_title_artist == 0 and dup_lyrics_hash == 0
    if passed:
        print("Verification PASSED — dataset is clean and deduplicated.")
    else:
        print("Verification FAILED — duplicates remain; check pipeline steps.")
    return passed


# ---------------------------------------------------------------------------
# Main pipeline
# ---------------------------------------------------------------------------

def run_pipeline(input_csv: Path, output_csv: Path) -> pd.DataFrame:
    """Execute the full dataset pipeline verification and return the clean DataFrame."""
    # --- 1.1 Load ---
    if not input_csv.exists():
        raise FileNotFoundError(f"Input CSV not found: {input_csv}")

    df = pd.read_csv(input_csv)
    print(f"Loaded: {df.shape}")
    print(f"Columns: {list(df.columns)}")

    required = {'title', 'artist', 'lyrics'}
    missing = required - set(df.columns)
    if missing:
        raise KeyError(f"Missing required columns: {missing}")

    # --- 1.2 Remove nulls and short entries ---
    df = remove_nulls_and_short(df)
    print(f"After null/short removal: {df.shape}")

    # --- 1.3 Normalise text fields ---
    df = normalize_fields(df)
    print(f"After normalisation: {df.shape}")

    # --- 1.4 Remove duplicates ---
    df = remove_duplicates(df)
    print(f"After deduplication: {df.shape}")

    # --- 1.5 English filter ---
    df = filter_english(df)
    print(f"After English filter: {df.shape}")

    # --- 1.6 Save ---
    save_dataset(df, output_csv)
    print(f"Saved to: {output_csv}")

    # --- 1.7 Verification ---
    passed = run_verification(df)
    if not passed:
        raise RuntimeError("Pipeline verification failed — duplicates detected in output.")

    return df


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description='Dataset pipeline verification: clean, deduplicate, filter, verify.'
    )
    parser.add_argument('--input', type=Path, help='Path to raw input CSV.')
    parser.add_argument('--output', type=Path, help='Path to write clean output CSV.')
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    app_root = detect_app_root(Path.cwd())
    default_input = app_root / 'data' / 'raw' / 'your_dataset.csv'
    default_output = app_root / 'data' / 'processed' / 'clean_lyrics_dataset.csv'

    input_csv = args.input if args.input is not None else default_input
    output_csv = args.output if args.output is not None else default_output

    run_pipeline(input_csv, output_csv)


if __name__ == '__main__':
    main()
