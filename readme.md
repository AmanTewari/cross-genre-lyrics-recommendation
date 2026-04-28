# Lyrics-Based Music Recommendation System

**Unsupervised Pattern Recognition Approach**

---

## Project Overview

This project develops a lyrics-driven music recommendation system using unsupervised machine learning and structured pattern recognition techniques.

Unlike conventional systems that rely on user behavior, audio features, or genre classification, this model focuses exclusively on measurable lyrical characteristics. Songs are grouped based on structural and lexical patterns derived from their lyrics, enabling cross-genre recommendation based purely on textual similarity.

The system emphasizes interpretability, modular design, and academic defensibility.

---

## Objectives

* Build a lyrics-only recommendation framework
* Extract structured numerical features from song lyrics
* Apply unsupervised clustering to identify natural similarity groups
* Generate recommendations using distance-based similarity
* Maintain explainability and reproducibility

---

## Methodology

The system follows a structured pipeline:

1. **Data Ingestion**
   Load structured lyric dataset (CSV format).

2. **Preprocessing**

   * Filter English lyrics
   * Remove null or corrupted entries
   * Normalize title and artist fields
   * Remove duplicate songs
   * Clean lyrical text while preserving structural properties

3. **Feature Engineering**
   Extract numeric features including:

   * Total word count
   * Unique word count
   * Lexical diversity ratio
   * Repetition metrics
   * Line structure statistics
   * Emotion keyword density

4. **Vector Representation & Scaling**
   Convert each song into a normalized numeric feature vector.

5. **Clustering**
   Apply K-Means clustering to group structurally similar songs.

6. **Recommendation Logic**

   * Identify cluster membership
   * Rank songs within cluster using distance metrics
   * Return top-N similar songs

7. **Evaluation**

   * Silhouette score
   * Intra-cluster vs inter-cluster distance comparison
   * Cross-genre distribution analysis

---

## Dataset

Primary dataset options:

* [Spotify Songs with Attributes and Lyrics (Kaggle)](https://www.kaggle.com/datasets/bwandowando/spotify-songs-with-attributes-and-lyrics)

Required fields:

* Title
* Artist
* Lyrics

Optional (evaluation only):

* Genre

Audio features, popularity metrics, and external metadata are excluded from clustering.

---

## Project Structure

```
project-root/
│
├── data/
│   ├── raw/
│   ├── interim/
│   └── processed/
│
├── models/
├── docs/
├── src/
│   ├── preprocessing/
│   ├── features/
│   ├── models/
│   ├── evaluation/
│   └── utils/
│
├── notebooks/
├── configs/
├── reports/
│   ├── figures/
│   └── documentation/
│
├── main.py
├── requirements.txt
└── README.md
```

---

## Technologies Used

* Python
* Pandas
* NumPy
* Scikit-learn

---

## Automated Pipeline Execution

### Quick Start

Run the entire pipeline end-to-end in one command:

**Windows (PowerShell or Command Prompt):**
```bash
.\run_pipeline.bat
```

**Any OS (Python):**
```bash
python main_pipeline.py
```

### Pipeline Steps

The automated pipeline consists of four sequential steps:

| Step | Script | Module | Purpose |
|------|--------|--------|----------|
| 1 | `run_step1.py` | `src/preprocessing/` | Clean and deduplicate raw lyrics CSV |
| 2 | `run_step2.py` | `src/features/` | Extract 10 numeric features from cleaned lyrics |
| 3 | `run_step3.py` | `src/models/` | Scale features, select K, train KMeans clustering |
| 4 | `run_step4.py` | `src/utils/` | Test recommendation engine with smoke test |

### Run Individual Steps

```bash
python run_step1.py  # Preprocessing
python run_step2.py  # Feature extraction
python run_step3.py  # Clustering
python run_step4.py  # Recommendations
```

### Expected Artifacts

After successful execution:

* `data/processed/spotify_clean.csv` — deduplicated, filtered dataset
* `data/processed/feature_matrix.csv` — extracted features for each song
* `data/processed/scaled_features.npy` — normalized feature vectors
* `data/processed/clustered_dataset.csv` — songs with assigned cluster labels
* `models/scaler.pkl` — fitted StandardScaler
* `models/kmeans_model.pkl` — trained KMeans model
* `reports/elbow_plot.png` — K selection diagnostic
* `reports/silhouette_plot.png` — silhouette score by K

### Pipeline Architecture

Each core module exposes a `run()` function:

```
run_pipeline.bat
  ↓
main_pipeline.py (controller)
  ↓
run_step1.py → src/preprocessing/clean_dataset.py → src/preprocessing/preprocess.py::run()
  ↓
run_step2.py → src/features/extract_features.py::run()
  ↓
run_step3.py → src/models/train_kmeans.py → src/models/cluster_pipeline.py::run()
  ↓
run_step4.py → src/utils/recommend.py::run()
```

---

## Key Design Principles

* Unsupervised learning only
* No deep learning or transformer-based models
* No semantic embeddings
* Fully explainable feature-based similarity
* Modular and reproducible codebase

---

## Expected Outcome

Given an input song, the system:

1. Identifies its lyrical pattern cluster
2. Computes similarity within that cluster
3. Returns structurally similar songs across genres

The result is a genre-independent, interpretable lyric-based recommendation system.

---

## Academic Positioning

This project demonstrates the application of pattern recognition and unsupervised clustering to creative textual data. It provides an explainable alternative to black-box recommendation systems while maintaining computational efficiency and methodological transparency.

---

## License

This project is developed for academic purposes as part of a Minor Project submission.

---

## Recent changes

* **v0.0.5 — Feature Extraction Pipeline Initialization**

   * Added initial feature extraction module at `src/features/extract_features.py` that loads `data/processed/spotify_clean.csv`, validates required columns (`id`, `title`, `artist`, `lyrics`), removes rows with missing lyrics, and adds a helper `_word_count` column used for later feature extraction. Basic diagnostics (total, avg, min, max word counts) are printed on load.

* **v0.0.6 — Clean Feature Matrix and GUI Wrapper**

   * Added a deterministic 10-feature extraction layer that produces `data/processed/feature_matrix.csv` from `data/processed/clean_lyrics_dataset.csv`.
   * Added a tkinter GUI wrapper at `src/features/feature_gui.py` with true per-row progress and a feature correlation matrix visualization.

* **v0.0.7 — Scaling, Clustering, and Recommendation Pipeline**

   * Added `src/models/cluster_pipeline.py` to scale the feature matrix, select `K` deterministically, train KMeans, and persist clustering artifacts.
   * Added deterministic same-cluster cosine-distance recommendations with strict title matching and no randomness.

* **v0.0.8 — Automated Pipeline Controller**

   * Added `run()` entry points to all core modules: `preprocess.py`, `extract_features.py`, `feature_gui.py`, `cluster_pipeline.py`.
   * Created thin wrapper modules: `src/preprocessing/clean_dataset.py`, `src/models/train_kmeans.py`, `src/utils/recommend.py`.
   * Added root-level step scripts: `run_step1.py`, `run_step2.py`, `run_step3.py`, `run_step4.py`.
   * Added main controller: `main_pipeline.py` (orchestrates all steps with error handling).
   * Added batch file: `run_pipeline.bat` (one-click Windows execution with venv activation).
   * All changes preserve existing logic; no code duplication or restructuring.

---

## Current Python Modules

* `src/preprocessing/preprocess.py` - legacy two-pass preprocessing script for cleaning the raw Spotify lyrics CSV.
* `src/preprocessing/spotify_preprocess.py` - CLI version of the two-pass preprocessing pipeline with the same cleaning logic.
* `src/features/extract_features.py` - fixed 10-feature extractor that converts cleaned lyrics into numeric feature vectors.
* `src/features/feature_gui.py` - tkinter wrapper that runs feature extraction with visible progress and displays a correlation matrix.
* `src/models/cluster_pipeline.py` - scaling, K selection, KMeans training, artifact persistence, and recommendation helpers.

---

## Documentation

Knowledge-transfer notes for each Python module are stored in the `docs/` directory.
