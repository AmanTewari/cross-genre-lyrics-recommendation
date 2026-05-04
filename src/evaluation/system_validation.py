from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import euclidean_distances

from src.models.cluster_pipeline import load_artifacts, recommend_by_title


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def paths() -> dict[str, Path]:
    root = project_root()
    return {
        "pca_plot": root / "reports" / "cluster_pca.png",
    }


def compute_silhouette(df: pd.DataFrame, X_scaled: np.ndarray) -> float:
    labels = df["cluster"].values
    sample_size = min(200, len(X_scaled))
    return float(
        silhouette_score(
            X_scaled,
            labels,
            sample_size=sample_size if sample_size < len(X_scaled) else None,
            random_state=42,
        )
    )


def sampled_indices(indices: np.ndarray, max_samples: int) -> np.ndarray:
    if len(indices) <= max_samples:
        return indices
    return np.linspace(0, len(indices) - 1, num=max_samples, dtype=int)


def cluster_size_distribution(df: pd.DataFrame) -> pd.Series:
    return df["cluster"].value_counts().sort_index()


def intra_inter_distance_report(df: pd.DataFrame, X_scaled: np.ndarray) -> pd.DataFrame:
    rows: list[dict[str, float | int | bool]] = []
    max_cluster_samples = 50
    max_other_samples = 200

    for cluster in sorted(df["cluster"].unique()):
        cluster_indices = df.index[df["cluster"] == cluster].to_numpy()
        other_indices = df.index[df["cluster"] != cluster].to_numpy()

        cluster_sample = cluster_indices[sampled_indices(np.arange(len(cluster_indices)), max_cluster_samples)]
        other_sample = other_indices[sampled_indices(np.arange(len(other_indices)), max_other_samples)]

        intra = float(euclidean_distances(X_scaled[cluster_sample], X_scaled[cluster_sample]).mean())
        inter = float(euclidean_distances(X_scaled[cluster_sample], X_scaled[other_sample]).mean())

        rows.append(
            {
                "cluster": int(cluster),
                "size": int(len(cluster_indices)),
                "intra_distance": intra,
                "inter_distance": inter,
                "intra_less_than_inter": intra < inter,
            }
        )

    return pd.DataFrame(rows)


def qualitative_cluster_samples(df: pd.DataFrame, sample_size: int = 5) -> dict[int, pd.DataFrame]:
    samples: dict[int, pd.DataFrame] = {}
    for cluster in sorted(df["cluster"].unique()):
        samples[int(cluster)] = df[df["cluster"] == cluster][["title", "artist"]].head(sample_size)
    return samples


def cross_genre_distribution(df: pd.DataFrame) -> pd.DataFrame | None:
    if "genre" not in df.columns:
        return None
    return df.groupby("cluster")["genre"].value_counts().rename("count").reset_index()


def save_pca_plot(X_scaled: np.ndarray, labels: np.ndarray, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)

    pca = PCA(n_components=2, random_state=42)
    X_pca = pca.fit_transform(X_scaled)

    plt.figure(figsize=(8, 6))
    plt.scatter(X_pca[:, 0], X_pca[:, 1], c=labels, s=8, cmap="tab20")
    plt.title("Cluster Visualization (PCA)")
    plt.tight_layout()
    plt.savefig(out_path, dpi=150)
    plt.close()


def run(sample_title: str | None = None, top_n: int = 5, save_plot: bool = True) -> dict[str, object]:
    df, X_scaled, _, _ = load_artifacts()

    silhouette = compute_silhouette(df, X_scaled)
    sizes = cluster_size_distribution(df)
    distance_report = intra_inter_distance_report(df, X_scaled)
    samples = qualitative_cluster_samples(df)
    genre_report = cross_genre_distribution(df)

    if save_plot:
        save_pca_plot(X_scaled, df["cluster"].values, paths()["pca_plot"])

    probe_title = sample_title if sample_title is not None else str(df.iloc[0]["title"])
    recommendations = recommend_by_title(probe_title, top_n=top_n)

    print("Silhouette Score:", silhouette)
    print("\nCluster Size Distribution:")
    print(sizes)
    print("\nIntra vs Inter Distance Report:")
    print(distance_report.to_string(index=False))
    print("\nQualitative Cluster Samples:")
    for cluster, sample in samples.items():
        print(f"\nCluster {cluster}")
        print(sample.to_string(index=False))

    print(f"\nRecommendation Validation for: {probe_title}")
    print(recommendations.to_string(index=False))

    if genre_report is not None:
        print("\nCross-Genre Distribution:")
        print(genre_report.to_string(index=False))
    else:
        print("\nCross-Genre Distribution: genre column not available")

    return {
        "silhouette_score": silhouette,
        "cluster_sizes": sizes,
        "distance_report": distance_report,
        "samples": samples,
        "recommendations": recommendations,
        "cross_genre_distribution": genre_report,
        "pca_plot_path": paths()["pca_plot"] if save_plot else None,
    }