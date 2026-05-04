# Step 5 Evaluation and System Validation

## Purpose

This step validates the lyric recommendation system after clustering and recommendation generation are complete.

The system is unsupervised, so validation focuses on cluster structure and recommendation behavior rather than label-based metrics.

## What is validated

* Cluster quality
* Separation between clusters
* Recommendation relevance
* Cross-genre behavior when a genre column is available

## Allowed metrics

* Silhouette score
* Intra-cluster distance
* Inter-cluster distance
* Cluster size distribution
* Qualitative inspection of sampled songs per cluster

## Metrics to avoid

* Accuracy
* Precision
* Recall
* Confusion matrix

These require ground-truth labels, which this project does not use.

## Input artifacts

* `data/processed/clustered_dataset.csv`
* `data/processed/scaled_features.npy`
* `models/kmeans_model.pkl`
* `models/scaler.pkl`

## Key validation checks

### Silhouette score

Recomputes clustering quality using the scaled feature matrix and the cluster labels stored in the dataset.

Interpretation:

* Greater than 0.5: strong clustering
* 0.3 to 0.5: acceptable clustering
* Below 0.3: weak clustering

### Cluster size distribution

Checks whether the clustering result is balanced enough to be useful.

Look for:

* No single dominant cluster
* No clusters with extremely few items

### Intra-cluster vs inter-cluster distance

For a chosen cluster, intra-cluster distance should be lower than inter-cluster distance.

That supports the claim that songs in the same cluster are closer to one another than to songs outside the cluster.

### Qualitative inspection

Inspect a few songs per cluster to confirm that the groupings make sense in terms of lyrical structure and repetition patterns.

### Recommendation validation

Run a title-based recommendation query and confirm that:

* The input song is excluded
* Results come only from the same cluster
* Distances are sorted ascending
* The returned songs look structurally similar

### Cross-genre behavior

If a `genre` column exists, inspect genre distribution by cluster to show that the system is not just separating by genre.

## Recommended execution path

The project provides a Step 5 runner at:

* `pipeline/run_step5.py`

The main pipeline also includes Step 5:

* `pipeline/main_pipeline.py`

The batch launcher includes Step 5 as well:

* `run_pipeline.bat`

## Expected output

The validation step should print:

* Silhouette score
* Cluster size distribution
* Intra vs inter distance report
* Sample songs from each cluster
* Recommendation output for a probe song

If a genre column exists, it should also print the cross-genre distribution.

## Defense statement

This system is evaluated using silhouette score, cluster separation, and qualitative inspection rather than accuracy metrics, because it is an unsupervised learning pipeline without labeled targets.