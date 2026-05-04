from pathlib import Path
import sys

import numpy as np
import pandas as pd
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances, euclidean_distances

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.models.cluster_pipeline import paths


def main() -> None:
    p = paths()
    df = pd.read_csv(p["clustered_dataset"], nrows=1000, low_memory=False)
    X_scaled = np.load(p["scaled_features"], mmap_mode="r")[: len(df)]

    labels = df["cluster"].values
    silhouette = float(silhouette_score(X_scaled, labels, random_state=42, sample_size=min(200, len(df))))
    sizes = df["cluster"].value_counts().sort_index()

    cluster = int(df.loc[0, "cluster"])
    cluster_indices = df.index[df["cluster"] == cluster].to_numpy()
    other_indices = df.index[df["cluster"] != cluster].to_numpy()
    cluster_indices = cluster_indices[: min(50, len(cluster_indices))]
    other_indices = other_indices[: min(200, len(other_indices))]
    distances = pd.DataFrame(
        {
            "cluster": [cluster],
            "intra_less_than_inter": [
                float(euclidean_distances(X_scaled[cluster_indices], X_scaled[cluster_indices]).mean())
                < float(euclidean_distances(X_scaled[cluster_indices], X_scaled[other_indices]).mean())
            ],
        }
    )

    probe_title = str(df.iloc[0]["title"])
    normalized_title = probe_title.lower().strip()
    matches = df[df["title"].astype(str).str.lower().str.strip() == normalized_title]
    song_index = int(matches.index[0])
    target_cluster = int(df.loc[song_index, "cluster"])
    cluster_indices = df.index[df["cluster"] == target_cluster].to_numpy()
    target_vector = np.asarray(X_scaled[song_index]).reshape(1, -1)
    cluster_vectors = np.asarray(X_scaled[cluster_indices])
    distance_values = cosine_distances(target_vector, cluster_vectors)[0]
    sorted_idx = np.argsort(distance_values)
    ranked = []
    for pos in sorted_idx:
        candidate_index = int(cluster_indices[pos])
        if candidate_index == song_index:
            continue
        ranked.append((candidate_index, float(distance_values[pos])))
        if len(ranked) == 5:
            break
    recommendations = df.loc[[idx for idx, _ in ranked], ["title", "artist"]].copy()
    recommendations["distance"] = [dist for _, dist in ranked]

    print("Silhouette Score:", silhouette)
    print("Cluster Count:", int(sizes.size))
    print("Distance Checks Passed:", bool(distances["intra_less_than_inter"].all()))
    print("Probe Title:", probe_title)
    print(recommendations.to_string(index=False))

    assert (recommendations["distance"].diff().fillna(0) >= 0).all()
    assert len(recommendations) <= 5
    assert bool(distances["intra_less_than_inter"].all())

    print("STEP5_VALIDATION_OK")


if __name__ == "__main__":
    main()