from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

EMOTION_WORDS = set([
    "love", "hate", "pain", "heart", "cry", "tears", "fear", "happy",
    "sad", "anger", "lonely", "alone", "joy", "death", "dream", "hope",
])


def load_dataset(csv_path: Path) -> pd.DataFrame:
    csv_path = Path(csv_path)
    if not csv_path.exists():
        raise FileNotFoundError(f"Processed CSV not found at {csv_path}")
    return pd.read_csv(csv_path, low_memory=False)


def validate_columns(df: pd.DataFrame) -> None:
    required = ["lyrics", "title", "artist"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise KeyError(f"Missing required columns: {missing}")


def extract_features(lyrics):
    lines = lyrics.split("\n")
    lines = [line.strip() for line in lines if line.strip() != ""]

    words = lyrics.split()
    words = [w.strip(".,!?\"'()-").lower() for w in words if w.strip() != ""]

    total_words = len(words)

    if total_words == 0:
        return [0] * 10

    unique_words = len(set(words))

    lexical_diversity = unique_words / total_words

    repetition_score = 1 - lexical_diversity

    word_counts = Counter(words)
    top_word_freq = word_counts.most_common(1)[0][1]
    top_word_frequency_ratio = top_word_freq / total_words

    num_lines = len(lines)

    line_lengths = [len(line.split()) for line in lines] if num_lines > 0 else [0]

    avg_line_length = np.mean(line_lengths)
    line_length_variance = np.var(line_lengths)

    emotion_count = sum(1 for w in words if w in EMOTION_WORDS)

    emotion_density = emotion_count / total_words

    return [
        total_words,
        unique_words,
        lexical_diversity,
        repetition_score,
        top_word_frequency_ratio,
        num_lines,
        avg_line_length,
        line_length_variance,
        emotion_count,
        emotion_density,
    ]


def build_feature_matrix(df: pd.DataFrame) -> pd.DataFrame:
    validate_columns(df)

    features = df["lyrics"].apply(extract_features)

    feature_matrix = pd.DataFrame(
        features.tolist(),
        columns=[
            "total_words",
            "unique_words",
            "lexical_diversity",
            "repetition_score",
            "top_word_frequency_ratio",
            "num_lines",
            "avg_line_length",
            "line_length_variance",
            "emotion_word_count",
            "emotion_density",
        ],
    )

    feature_matrix["title"] = df["title"].fillna("unknown_title").astype(str)
    feature_matrix["artist"] = df["artist"].fillna("unknown_artist").astype(str)

    return feature_matrix


def main(
    input_path: str | Path = "data/processed/clean_lyrics_dataset.csv",
    output_path: str | Path = "data/processed/feature_matrix.csv",
) -> pd.DataFrame:
    df = load_dataset(Path(input_path))
    feature_matrix = build_feature_matrix(df)

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    feature_matrix.to_csv(output_path, index=False)

    print(feature_matrix.shape)
    print(feature_matrix.describe())
    print(feature_matrix.isnull().sum())

    return feature_matrix


if __name__ == "__main__":
    main()
