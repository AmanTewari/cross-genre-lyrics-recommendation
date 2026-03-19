# Imports and path detection

# Import libraries we need for this notebook
import argparse  # For parsing command-line arguments (not used in notebook mode, but kept for compatibility)
import hashlib  # For creating unique fingerprints (hashes) of text
import re  # For pattern matching and text manipulation (regular expressions)
from pathlib import Path  # For working with file paths in a cross-platform way
import pandas as pd  # For reading and manipulating CSV data in tables (DataFrames)


# Find the main project folder by looking for repository root markers
# This helps the notebook work no matter where it's run from and avoids relying on the deprecated 'approot'
def detect_app_root(start: Path) -> Path:
    base = start
    # If we're inside a Python virtual environment folder, go up one level
    if base.name == '.venv':
        base = base.parent
    # Look for repository markers up the tree (.git or README)
    p = base
    for _ in range(10):
        if (p / '.git').exists() or (p / 'readme.md').exists() or (p / 'README.md').exists():
            return p.resolve()
        # Stop if we've reached the root of the file system
        if p.parent == p:
            break
        p = p.parent
    # If no marker is found, just use the current directory
    return base.resolve()


# Set up file paths for input and output
APP_ROOT = detect_app_root(Path.cwd())  # Find the main project folder
RAW_CSV = APP_ROOT / 'data' / 'raw' / 'songs_with_attributes_and_lyrics.csv'  # Where the original Spotify data is stored
OUT_CSV = APP_ROOT / 'data' / 'processed' / 'spotify_clean.csv'  # Where we'll save the cleaned data
CHUNK_SIZE = 50_000  # How many rows to process at once (smaller = less memory used, but slower)

# Print the paths so we can verify they're correct
print(f'app root      : {APP_ROOT}')
print(f'raw csv exists: {RAW_CSV.exists()}')  # Check if the input file actually exists
print(f'output target : {OUT_CSV}')
# Helpers

# Print a formatted log message with a stage label (e.g., [PASS1], [PASS2])
def log(stage: str, message: str) -> None:
    print(f'[{stage:>6}] {message}')


# Calculate what percentage of characters in a text are standard ASCII (not special unicode)
# Returns a number between 0 and 1; higher means more "normal" English characters
def ascii_ratio(text: str) -> float:
    if not isinstance(text, str) or len(text) == 0:
        return 0.0
    return sum(ord(c) < 128 for c in text) / len(text)


# Clean up song/artist metadata by removing live versions, remasters, and special characters
# Makes text lowercase and removes extra spaces
def normalize_meta(s: str) -> str:
    if not isinstance(s, str):
        return ''
    s = s.lower()
    # Remove "(live)", "(remastered)" etc. from song names
    s = re.sub(r"\([^)]*(live|remaster(ed)?).*?\)", '', s, flags=re.IGNORECASE)
    s = re.sub(r"[\-\u2013\u2014]\s*live\s*$", '', s, flags=re.IGNORECASE)
    # Remove anything in parentheses
    s = re.sub(r"\([^)]*\)", '', s)
    # Remove punctuation
    s = re.sub(r"[^\w\s]", ' ', s)
    return re.sub(r"\s+", ' ', s).strip()


# Aggressively normalize song titles for matching duplicates
# Converts to lowercase, removes punctuation, and collapses spaces
def normalize_title_strong(s: str) -> str:
    if not isinstance(s, str):
        return ''
    t = s.lower()
    # Strip leading/trailing punctuation
    t = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', t)
    # Replace all punctuation with spaces
    t = re.sub(r'[^A-Za-z0-9 ]+', ' ', t)
    # Collapse multiple spaces into one
    t = re.sub(r'\s+', ' ', t).strip()
    return t


# Standard title normalization (same as normalize_title_strong in this case)
# Kept separate in case different logic is needed later
def normalize_title(s: str) -> str:
    if not isinstance(s, str):
        return ''
    t = s.lower()
    t = re.sub(r'^[^A-Za-z0-9]+|[^A-Za-z0-9]+$', '', t)
    t = re.sub(r'[^A-Za-z0-9 ]+', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t


# Clean up lyrics text while preserving line breaks
# Keeps apostrophes (for words like "don't") but removes other punctuation
def normalize_lyrics(text: str) -> str:
    if not isinstance(text, str):
        return ''
    t = text.lower()
    # Keep letters, numbers, spaces, and apostrophes only
    t = re.sub(r"[^\w\s']", ' ', t)
    # Clean up each line individually, removing extra spaces
    lines = [re.sub(r'[ \t]+', ' ', line).strip() for line in t.splitlines()]
    return '\n'.join(lines)


# Create a unique fingerprint (hash) of a string for detecting duplicate lyrics
# Same lyrics always produce the same hash
def md5_hash(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()
# Cleaning and streaming passes

# Define which columns to read from the raw CSV file
# We only need: song ID, song name, artist names, and lyrics text
RAW_COLS = ['id', 'name', 'artists', 'lyrics']


def clean_chunk(chunk: pd.DataFrame) -> pd.DataFrame:
    """
    Clean up a batch of songs by:
    1. Filtering out low-quality data (short lyrics, non-English text)
    2. Standardizing artist and title names for easier comparison
    3. Creating unique identifiers to detect duplicates
    """
    # Rename columns to be clearer: 'name' becomes 'title', 'artists' becomes 'artist'
    chunk = chunk.rename(columns={'name': 'title', 'artists': 'artist'})
    
    # Remove any songs that don't have lyrics
    chunk = chunk[chunk['lyrics'].notna()].copy()

    # Count how many words are in each song's lyrics
    chunk['_word_count'] = chunk['lyrics'].astype(str).str.split().str.len()
    # Keep only songs with at least 30 words (filters out very short/incomplete lyrics)
    chunk = chunk[chunk['_word_count'] >= 30].copy()
    
    # Calculate what percentage of the lyrics are normal English characters (not emojis, special symbols, etc.)
    chunk['_ascii'] = chunk['lyrics'].astype(str).map(ascii_ratio)
    # Keep only songs where at least 90% of characters are normal ASCII (filters out non-English songs)
    chunk = chunk[chunk['_ascii'] >= 0.90].copy()

    # Clean up artist names: make lowercase, remove brackets and quotes, fix spacing
    chunk['artist'] = chunk['artist'].astype(str).str.lower()
    chunk['artist'] = chunk['artist'].str.replace(r'\[|\]', '', regex=True)
    chunk['artist'] = chunk['artist'].str.replace("'", '', regex=False)
    chunk['artist'] = chunk['artist'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Create a standardized version of the song title (for finding duplicates)
    # Removes punctuation, makes lowercase, etc.
    chunk['title'] = chunk['title'].astype(str)
    chunk['normalized_title'] = chunk['title'].map(normalize_title_strong)

    # Create a standardized version of the artist name (also for finding duplicates)
    chunk['normalized_artist'] = chunk['artist'].str.lower()
    chunk['normalized_artist'] = chunk['normalized_artist'].str.replace(r'[^A-Za-z0-9 ]+', ' ', regex=True)
    chunk['normalized_artist'] = chunk['normalized_artist'].str.replace(r'\s+', ' ', regex=True).str.strip()

    # Clean up the lyrics text while keeping line breaks
    chunk['lyrics'] = chunk['lyrics'].astype(str).map(normalize_lyrics)

    # Create another version of lyrics with everything lowercase and no punctuation
    # This helps detect duplicate songs even if the lyrics formatting is slightly different
    chunk['normalized_lyrics'] = chunk['lyrics'].str.lower()
    chunk['normalized_lyrics'] = chunk['normalized_lyrics'].str.replace(r'[^\\w\\s]', ' ', regex=True)
    chunk['normalized_lyrics'] = chunk['normalized_lyrics'].str.replace(r'\\s+', ' ', regex=True).str.strip()

    # Create a unique key combining title + artist to identify duplicate songs
    chunk['_comp_key'] = chunk['normalized_title'].fillna('') + '_' + chunk['normalized_artist'].fillna('')
    # Create a unique fingerprint of the lyrics to catch songs with identical lyrics but different metadata
    chunk['_lyrics_hash'] = chunk['lyrics'].map(md5_hash)
    return chunk


def pass1_compute_bounds(raw_csv: Path, chunk_size: int, usecols) -> tuple[int, int, int, int]:
    """
    FIRST PASS: Read through the entire dataset to:
    1. Remove duplicate songs
    2. Figure out what's a "normal" song length (to filter out outliers later)
    
    Returns: (min_words, max_words, total_rows_read, rows_after_dedup)
    """
    # Keep track of songs we've already seen (to avoid duplicates)
    seen_comp_keys: set[str] = set()  # Tracks unique title+artist combinations
    seen_lyrics_hash: set[str] = set()  # Tracks unique lyrics
    word_counts: list[int] = []  # Collect word counts to calculate statistics
    rows_in = rows_kept = 0  # Count how many rows we process vs. keep

    # Read the file in chunks (batches) to avoid loading the entire file into memory
    for i, chunk in enumerate(pd.read_csv(raw_csv, usecols=usecols, chunksize=chunk_size, low_memory=False)):
        rows_in += len(chunk)  # Track total rows read
        chunk = clean_chunk(chunk)  # Clean and standardize this batch
        
        # Keep only songs we haven't seen before (removes duplicates)
        mask_new = (~chunk['_comp_key'].isin(seen_comp_keys)) & (~chunk['_lyrics_hash'].isin(seen_lyrics_hash))
        chunk = chunk[mask_new]
        
        # Remember these songs so we can detect duplicates in future chunks
        seen_comp_keys.update(chunk['_comp_key'])
        seen_lyrics_hash.update(chunk['_lyrics_hash'])
        
        # Save the word counts for calculating statistics later
        word_counts.extend(chunk['_word_count'].astype(int).tolist())
        rows_kept += len(chunk)
        log('PASS1', f'chunk {i:03d}: kept {len(chunk):6d} | total in {rows_in:7d}')

    # Make sure we have at least some data left after filtering
    if not word_counts:
        raise RuntimeError('No rows survived initial filtering; check the raw CSV and filters.')

    # Calculate "normal" song length using statistics (IQR method)
    # This helps us filter out extremely short or extremely long songs
    wc_series = pd.Series(word_counts)
    q1, q3 = wc_series.quantile(0.25), wc_series.quantile(0.75)  # 25th and 75th percentiles
    iqr = q3 - q1  # Interquartile range
    lo = max(1, int(q1 - 1.5 * iqr))  # Minimum "normal" word count
    hi = int(q3 + 1.5 * iqr)  # Maximum "normal" word count
    log('PASS1', f'done: input {rows_in:,} -> kept {rows_kept:,}; IQR bounds [{lo}, {hi}]')
    return lo, hi, rows_in, rows_kept


def pass2_write_output(raw_csv: Path, out_csv: Path, chunk_size: int, usecols, lo: int, hi: int) -> int:
    """
    SECOND PASS: Read through the dataset again and write the final cleaned data to a new file
    This time we also filter by word count using the bounds calculated in pass 1
    
    Returns: number of rows written to the output file
    """
    # Create the output folder if it doesn't exist
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    # Delete the output file if it already exists (we're starting fresh)
    if out_csv.exists():
        out_csv.unlink()

    # Track duplicates again (we need to do this again since we're re-reading the file)
    seen_comp_keys: set[str] = set()
    seen_lyrics_hash: set[str] = set()
    rows_written = 0

    # Read the file in chunks again
    for i, chunk in enumerate(pd.read_csv(raw_csv, usecols=usecols, chunksize=chunk_size, low_memory=False)):
        chunk = clean_chunk(chunk)  # Clean and standardize
        
        # Remove duplicates
        mask_new = (~chunk['_comp_key'].isin(seen_comp_keys)) & (~chunk['_lyrics_hash'].isin(seen_lyrics_hash))
        chunk = chunk[mask_new]
        seen_comp_keys.update(chunk['_comp_key'])
        seen_lyrics_hash.update(chunk['_lyrics_hash'])
        
        # Filter by word count: keep only songs with "normal" length (between lo and hi)
        chunk = chunk[(chunk['_word_count'] >= lo) & (chunk['_word_count'] <= hi)].copy()
        
        # Select only the columns we want in the final output (use normalized fields only)
        out = pd.DataFrame({
            'id': chunk['id'],
            'title': chunk['normalized_title'],
            'artist': chunk['normalized_artist'],
            'lyrics': chunk['normalized_lyrics']
        })
        
        # Write to file: first chunk creates new file with headers, subsequent chunks append
        mode = 'w' if rows_written == 0 else 'a'  # 'w' = write new, 'a' = append
        header = rows_written == 0  # Only write column names on the first chunk
        out.to_csv(out_csv, mode=mode, header=header, index=False)
        
        rows_written += len(out)
        log('PASS2', f'chunk {i:03d}: wrote {len(out):6d} | total out {rows_written:,}')
    
    log('PASS2', f'complete: final rows {rows_written:,} -> {out_csv}')
    return rows_written
# Run the pipeline (edit parameters here if needed)
def run_pipeline(raw_csv: Path = RAW_CSV, out_csv: Path = OUT_CSV, chunk_size: int = CHUNK_SIZE) -> None:
    # Stop early if the input file doesn't exist
    if not raw_csv.exists():
        raise FileNotFoundError(f'Raw CSV not found at {raw_csv}')

    # Make sure chunk size is a reasonable integer
    chunk_size = max(1_000, int(chunk_size))

    # Choose which columns to read from the raw file
    usecols = RAW_COLS

    # Print the run settings
    log('START', f'raw: {raw_csv}')
    log('START', f'out : {out_csv}')
    log('START', f'chunks: {chunk_size}')

    # First pass: scan the data to drop obvious junk and find normal lyric length bounds
    lo, hi, rows_in, rows_kept = pass1_compute_bounds(raw_csv, chunk_size, usecols)

    # Second pass: re-read the data, apply all filters, and write the cleaned output
    rows_written = pass2_write_output(raw_csv, out_csv, chunk_size, usecols, lo, hi)

    # Final summary of what happened
    log('DONE', f'input {rows_in:,} | kept after pass1 {rows_kept:,} | written {rows_written:,}')

# Execute the full pipeline with the current settings
run_pipeline()