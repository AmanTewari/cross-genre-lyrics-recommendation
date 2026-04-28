import pandas as pd
from pathlib import Path

clean = pd.read_csv(Path('data/processed/clean_lyrics_dataset.csv'))
features = pd.read_csv(Path('data/processed/feature_matrix.csv'))

expected_feature_cols = [
    'total_words', 'unique_words', 'lexical_diversity', 'repetition_score',
    'top_word_frequency_ratio', 'num_lines', 'avg_line_length',
    'line_length_variance', 'emotion_word_count', 'emotion_density'
]

print('clean_rows', len(clean))
print('feature_rows', len(features))
print('shape', features.shape)
print('missing_feature_cols', [c for c in expected_feature_cols if c not in features.columns])
print('na_total', int(features.isnull().sum().sum()))
print('na_by_col')
print(features.isnull().sum().to_string())
print('duplicates_title_artist', int(features.duplicated(subset=['title','artist']).sum()))
print('duplicates_numeric', int(features.duplicated(subset=expected_feature_cols).sum()))
