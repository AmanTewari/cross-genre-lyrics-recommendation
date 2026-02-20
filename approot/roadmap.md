# FULL DEVELOPMENT ROADMAP (Code-Level)

Project: Lyrics-Based Music Recommendation
Method: Unsupervised Pattern Recognition + K-Means

This is the complete coding roadmap from raw CSV → final recommendation system.

---

# PHASE 1 — DATA INGESTION

Objective: Load raw dataset safely.

Tasks:

* Load CSV from `data/raw/`
* Select required columns
* Basic null inspection
* Save cleaned column subset to `data/interim/`

Output:
`data/interim/filtered_dataset.csv`

---

# PHASE 2 — DATA PREPROCESSING

Objective: Clean and standardize dataset.

## 2.1 Structural Filtering

* Remove null lyrics
* Remove very short lyrics
* Filter English
* Drop unnecessary columns

## 2.2 Identifier Normalization

* Normalize title
* Normalize artist
* Remove suffixes (live/remastered)

## 2.3 Duplicate Removal

* Remove exact row duplicates
* Remove duplicate (title + artist)
* Normalize lyrics
* Remove duplicate lyrics via hash

Output:
`data/processed/clean_lyrics_dataset.csv`

Dataset now:

* English-only
* Deduplicated
* Clean structure

---

# PHASE 3 — FEATURE ENGINEERING

Objective: Convert lyrics into numeric pattern vectors.

For each song extract:

Lexical Features:

* total_words
* unique_words
* lexical_diversity

Repetition Features:

* repetition_score
* top_word_frequency

Structural Features:

* number_of_lines
* average_line_length
* line_length_variance

Emotion Indicators:

* emotion_word_count
* emotion_density

Combine into fixed-length numeric vector.

Output:
Feature matrix (NumPy / DataFrame)

Save:
`data/processed/feature_matrix.csv`

---

# PHASE 4 — FEATURE SCALING

Objective: Normalize numeric features.

* Apply StandardScaler
* Save fitted scaler
* Save scaled feature matrix

Reason:
K-Means is distance-based.

Output:
Scaled feature matrix.

---

# PHASE 5 — MODEL TRAINING

Objective: Learn lyrical pattern clusters.

Steps:

* Determine optimal K using:

  * Elbow method
  * Silhouette score
* Train K-Means
* Assign cluster label to each song
* Save trained model

Output:

* Cluster labels
* Trained KMeans model
* Silhouette score

Save:
`models/kmeans_model.pkl`

---

# PHASE 6 — RECOMMENDATION SYSTEM

Objective: Recommend similar songs.

Input:
Song title (or index)

Process:

1. Identify cluster
2. Compute similarity within cluster
3. Rank by cosine/Euclidean distance
4. Return top N songs

Output:
Ranked recommendations list

---

# PHASE 7 — EVALUATION

Quantitative:

* Silhouette score
* Intra-cluster vs inter-cluster distance

Qualitative:

* Inspect cluster themes
* Cross-genre distribution check

No accuracy % claims.

---

# PHASE 8 — PIPELINE INTEGRATION

Create main pipeline:

main.py should:

1. Run preprocessing
2. Run feature extraction
3. Train model
4. Evaluate
5. Allow recommendation query

Single command execution.

---

# DEVELOPMENT ORDER

1. clean_dataset.py
2. deduplicate.py
3. extract_features.py
4. scale_features.py
5. train_kmeans.py
6. evaluate_clusters.py
7. recommend.py
8. main.py integration

Do not jump to clustering before preprocessing is finalized.

---

# VISUAL FLOW

Raw CSV
→ Filter & Clean
→ Deduplicate
→ Feature Extraction
→ Scaling
→ K-Means Clustering
→ Cluster Labels
→ Similarity Ranking
→ Recommendation

---

# MASTER TLDR (Paste into Notepad)

Full Code Roadmap:

Phase 1: Load raw CSV → keep required columns.
Phase 2: Clean data → filter English → normalize identifiers → remove duplicates → save processed dataset.
Phase 3: Extract numeric lyric features (word count, diversity, repetition, line metrics, emotion counts).
Phase 4: Scale features using StandardScaler.
Phase 5: Train K-Means → choose K via elbow + silhouette → save model.
Phase 6: Recommendation = find cluster → rank by similarity → return top N.
Phase 7: Evaluate using silhouette + structural coherence.
Phase 8: Integrate everything in main.py pipeline.

End goal: Fully modular, unsupervised lyric pattern recommendation system.
