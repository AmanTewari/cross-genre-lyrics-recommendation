# `src/features/feature_gui.py`

## Purpose

Tkinter-based controlled GUI wrapper around the fixed feature extraction pipeline.

## What it does

* Loads the cleaned lyrics dataset.
* Computes the 10 fixed features row by row.
* Updates a true progress bar during processing.
* Saves the resulting feature matrix to disk.
* Displays a feature correlation matrix after extraction completes.

## UI behavior

* Start button launches extraction in a background thread.
* Progress label shows the current row and total row count.
* Progress bar reflects true completion percentage.
* Correlation matrix is shown in the GUI using matplotlib embedded in tkinter.

## Key functions and classes

* `build_feature_matrix_with_progress(df, progress_callback)` - extracts features while reporting progress.
* `FeatureExtractionApp` - main tkinter application class.
* `start_process()` - launches the background extraction thread.
* `run_extraction()` - loads data, computes features, writes output, and computes the correlation matrix.
* `poll_queue()` - handles progress and completion events from the worker thread.
* `render_correlation_matrix(correlation_matrix)` - draws the visualization.

## Output

* `data/processed/feature_matrix.csv`

## Notes

* The visualization is a correlation matrix, not a confusion matrix, because the system is unsupervised and has no labels.
* Feature names are displayed with human-readable labels in the chart.