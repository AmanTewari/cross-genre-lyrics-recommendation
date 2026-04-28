# `src/models/cluster_pipeline.py`

## Purpose

Deterministic clustering and recommendation pipeline for the feature matrix.

## What it does

* Loads `data/processed/feature_matrix.csv`.
* Selects the 10 numeric feature columns.
* Fits a `StandardScaler` and saves the scaled matrix.
* Chooses `K` from 2 to 15 using silhouette score on a deterministic training sample.
* Trains a final KMeans model.
* Saves clustering artifacts and diagnostic plots.
* Exposes same-cluster cosine-distance recommendation helpers.

## Key constants

* `FEATURE_COLUMNS` - the fixed numeric feature list.
* `TRAINING_SAMPLE_SIZE` - deterministic sample size used for K selection.

## Key functions

* `project_root()` - resolves the repository root.
* `paths()` - returns all artifact locations.
* `load_feature_matrix(...)` - loads and validates the input feature matrix.
* `prepare_matrix(df)` - extracts the numeric training array.
* `deterministic_sample_indices(...)` - creates a fixed sampling pattern.
* `fit_scaler(X)` - fits a `StandardScaler`.
* `save_scaler_and_matrix(...)` - persists the scaler and scaled features.
* `compute_elbow_and_silhouette(...)` - calculates inertia and silhouette scores for K selection.
* `save_plots(...)` - writes elbow and silhouette charts.
* `fit_final_model(...)` - trains the final KMeans model.
* `save_clustered_dataset(...)` - attaches cluster labels and writes the labeled dataset.
* `train_pipeline(...)` - runs the full training workflow.
* `load_artifacts(...)` - reloads the persisted model and data artifacts.
* `recommend_by_index(...)` - same-cluster cosine-distance ranking by row index.
* `recommend_by_title(...)` - strict title-based recommendation entry point.
* `debug_cluster(...)` - prints the contents of a song's cluster.

## Outputs

* `data/processed/scaled_features.npy`
* `models/scaler.pkl`
* `models/kmeans_model.pkl`
* `data/processed/clustered_dataset.csv`
* `reports/elbow_plot.png`
* `reports/silhouette_plot.png`

## Notes

* The pipeline is deterministic: no random recommendations and no manual K override.
* Recommendations are restricted to the same cluster and ranked by cosine distance.