# `src/features/extract_features.py`

## Purpose

Deterministic feature extraction module that converts cleaned lyric text into a fixed 10-feature numeric representation.

## What it does

* Loads `data/processed/clean_lyrics_dataset.csv`.
* Verifies that the required columns exist: `lyrics`, `title`, and `artist`.
* Computes exactly 10 numeric features per song.
* Writes `data/processed/feature_matrix.csv`.
* Prints basic shape, descriptive statistics, and missing-value checks.

## Feature set

1. `total_words`
2. `unique_words`
3. `lexical_diversity`
4. `repetition_score`
5. `top_word_frequency_ratio`
6. `num_lines`
7. `avg_line_length`
8. `line_length_variance`
9. `emotion_word_count`
10. `emotion_density`

## Key functions

* `load_dataset(csv_path)` - loads the cleaned CSV.
* `validate_columns(df)` - enforces the required schema.
* `extract_features(lyrics)` - returns the 10-feature vector for a single lyric string.
* `build_feature_matrix(df)` - applies feature extraction across the dataset.
* `main(...)` - saves the feature matrix to disk.

## Output

* `data/processed/feature_matrix.csv`

## Notes

* No TF-IDF, embeddings, stemming, or external lexicons are used.
* Emotion terms are hardcoded in `EMOTION_WORDS`.