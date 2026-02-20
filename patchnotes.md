patch 0.0.1
initial file management.
patch 0.0.2
Spotify preprocessing goal:

Load raw CSV → keep id, name→title, artists→artist, lyrics → drop audio features → remove null/short lyrics → filter English → normalize title/artist → remove duplicates → normalize lyrics → remove duplicate lyrics via hash → remove outliers → save to data/processed/spotify_clean.csv.