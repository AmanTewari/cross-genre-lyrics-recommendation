# UI Pipeline Integration Guide

## Purpose

This document explains how a UI developer can call the existing pipeline artifacts without changing the recommendation logic.

The UI should be a thin wrapper around the trained system:

* exact song title input
* deterministic recommendation lookup
* ranked output display

## Core pipeline files

### Training and artifact generation

* `pipeline/run_step1.py` - preprocessing
* `pipeline/run_step2.py` - feature extraction
* `pipeline/run_step3.py` - clustering and model training
* `pipeline/run_step4.py` - recommendation smoke test
* `pipeline/run_step5.py` - evaluation and validation

### Main orchestrator

* `pipeline/main_pipeline.py` - runs the pipeline in sequence

### Windows launcher

* `run_pipeline.bat` - prompts the user for each step and launches the pipeline

## Recommendation interface

The main UI-facing function is:

* `src/models/cluster_pipeline.py::recommend_by_title(title, top_n=5)`

It returns a pandas DataFrame with:

* `title`
* `artist`
* `distance`

## Recommendation rules

The UI should not add new ranking logic.

It should preserve these rules:

* exact title match only
* same-cluster only
* cosine distance ranking inside the cluster
* exclude the input song from results
* sort distances ascending

## Required loaded artifacts

The UI can rely on the trained artifacts already produced by the pipeline:

* `data/processed/clustered_dataset.csv`
* `data/processed/scaled_features.npy`
* `models/kmeans_model.pkl`
* `models/scaler.pkl`

## Suggested UI flow

1. Accept an exact song title from the user.
2. Call `recommend_by_title(title, top_n=5)`.
3. Render the returned rows in a table or list.
4. Show the `distance` column so the user can see similarity ordering.
5. Handle `ValueError` from a missing title by showing a clear error message.

## Example usage

```python
from src.models.cluster_pipeline import recommend_by_title

results = recommend_by_title("unknown_title", top_n=5)
print(results)
```

## UI constraints

Keep the UI deterministic and simple.

Do not add:

* fuzzy search
* autocomplete
* hidden re-ranking logic
* additional ML layers

The UI should only expose the existing pipeline behavior.

## Useful implementation note

If the UI is launched from outside the repository root, add the repository root to `sys.path` before importing from `src` or `pipeline`.

That keeps the import behavior consistent across direct execution and packaged UI entrypoints.