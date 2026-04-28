from __future__ import annotations

from pathlib import Path

import joblib
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.metrics.pairwise import cosine_distances
from sklearn.preprocessing import StandardScaler


FEATURE_COLUMNS = [
    "total_words",
    "unique_words",
    "lexical_diversity",
    "repetition_score",
    "top_word_frequency_ratio",
    "num_lines",
    "avg_line_length",
    "line_length_variance",
    "emotion_word_count",
    "emotion_density",
]

TRAINING_SAMPLE_SIZE = 20_000


def project_root() -> Path:
    return Path(__file__).resolve().parents[2]


def paths() -> dict[str, Path]:
    root = project_root()
    return {
        "feature_matrix": root / "data" / "processed" / "feature_matrix.csv",
        "scaled_features": root / "data" / "processed" / "scaled_features.npy",
        "scaler": root / "models" / "scaler.pkl",
        "kmeans": root / "models" / "kmeans_model.pkl",
        "clustered_dataset": root / "data" / "processed" / "clustered_dataset.csv",
        "silhouette_plot": root / "reports" / "silhouette_plot.png",
        "elbow_plot": root / "reports" / "elbow_plot.png",
    }


def load_feature_matrix(feature_matrix_path: Path | None = None) -> pd.DataFrame:
    feature_matrix_path = feature_matrix_path or paths()["feature_matrix"]
    if not feature_matrix_path.exists():
        raise FileNotFoundError(f"Feature matrix not found at {feature_matrix_path}")
    df = pd.read_csv(feature_matrix_path, low_memory=False)
    missing = [col for col in FEATURE_COLUMNS if col not in df.columns]
    if missing:
        raise KeyError(f"Missing required numeric feature columns: {missing}")
    if "title" not in df.columns or "artist" not in df.columns:
        raise KeyError("Missing required traceability columns: title, artist")
    return df


def prepare_matrix(df: pd.DataFrame) -> np.ndarray:
    return df[FEATURE_COLUMNS].to_numpy(dtype=float)


def deterministic_sample_indices(total_rows: int, sample_size: int) -> np.ndarray:
    sample_size = min(sample_size, total_rows)
    if sample_size <= 0:
        return np.array([], dtype=int)
    return np.linspace(0, total_rows - 1, num=sample_size, dtype=int)


def fit_scaler(X: np.ndarray) -> tuple[StandardScaler, np.ndarray]:
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)
    return scaler, X_scaled


def save_scaler_and_matrix(scaler: StandardScaler, X_scaled: np.ndarray, scaled_path: Path, scaler_path: Path) -> None:
    scaled_path.parent.mkdir(parents=True, exist_ok=True)
    scaler_path.parent.mkdir(parents=True, exist_ok=True)
    np.save(scaled_path, X_scaled)
    joblib.dump(scaler, scaler_path)


def compute_elbow_and_silhouette(
    X_scaled: np.ndarray,
    k_range: range,
    silhouette_sample_size: int = 10_000,
) -> tuple[list[float], list[float], int]:
    inertia_values: list[float] = []
    silhouette_scores: list[float] = []

    sample_size = min(silhouette_sample_size, len(X_scaled))

    for k in k_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(X_scaled)
        inertia_values.append(float(kmeans.inertia_))
        score = silhouette_score(
            X_scaled,
            labels,
            sample_size=sample_size if sample_size < len(X_scaled) else None,
            random_state=42,
        )
        silhouette_scores.append(float(score))

    optimal_k = int(k_range[np.argmax(silhouette_scores)])
    return inertia_values, silhouette_scores, optimal_k


def save_plots(k_range: range, inertia_values: list[float], silhouette_scores: list[float], elbow_path: Path, silhouette_path: Path) -> None:
    elbow_path.parent.mkdir(parents=True, exist_ok=True)
    silhouette_path.parent.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 5))
    plt.plot(list(k_range), inertia_values, marker="o")
    plt.title("Elbow Method")
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("Inertia")
    plt.tight_layout()
    plt.savefig(elbow_path, dpi=150)
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.plot(list(k_range), silhouette_scores, marker="o")
    plt.title("Silhouette Score vs K")
    plt.xlabel("K")
    plt.ylabel("Silhouette Score")
    plt.tight_layout()
    plt.savefig(silhouette_path, dpi=150)
    plt.close()


def fit_final_model(X_scaled: np.ndarray, optimal_k: int) -> tuple[KMeans, np.ndarray]:
    kmeans = KMeans(n_clusters=optimal_k, random_state=42, n_init=10)
    labels = kmeans.fit_predict(X_scaled)
    return kmeans, labels


def save_clustered_dataset(df: pd.DataFrame, labels: np.ndarray, out_path: Path) -> pd.DataFrame:
    clustered = df.copy()
    clustered["cluster"] = labels.astype(int)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    clustered.to_csv(out_path, index=False)
    return clustered


def print_validation(clustered: pd.DataFrame, final_silhouette: float) -> float:
    print("Cluster distribution:")
    print(clustered["cluster"].value_counts().sort_index())
    print("Silhouette score (final):")
    print(final_silhouette)
    return float(final_silhouette)


def train_pipeline(feature_matrix_path: Path | None = None) -> dict[str, object]:
    p = paths()
    feature_matrix = load_feature_matrix(feature_matrix_path)
    X = prepare_matrix(feature_matrix)

    scaler, X_scaled = fit_scaler(X)
    save_scaler_and_matrix(scaler, X_scaled, p["scaled_features"], p["scaler"])

    training_indices = deterministic_sample_indices(len(X_scaled), TRAINING_SAMPLE_SIZE)
    X_train = X_scaled[training_indices]

    k_range = range(2, min(16, len(feature_matrix)))
    if len(k_range) < 2:
        raise ValueError("Need at least 2 rows to determine K.")

    inertia_values, silhouette_scores, optimal_k = compute_elbow_and_silhouette(X_train, k_range)
    save_plots(k_range, inertia_values, silhouette_scores, p["elbow_plot"], p["silhouette_plot"])

    kmeans, train_labels = fit_final_model(X_train, optimal_k)
    joblib.dump(kmeans, p["kmeans"])

    labels = kmeans.predict(X_scaled)
    final_silhouette = silhouette_score(
        X_train,
        train_labels,
        sample_size=min(10_000, len(X_train)) if len(X_train) > 10_000 else None,
        random_state=42,
    )
    clustered = save_clustered_dataset(feature_matrix, labels, p["clustered_dataset"])
    print_validation(clustered, final_silhouette)

    return {
        "feature_matrix": feature_matrix,
        "X_scaled": X_scaled,
        "scaler": scaler,
        "kmeans": kmeans,
        "labels": labels,
        "clustered_dataset": clustered,
        "optimal_k": optimal_k,
        "silhouette_scores": silhouette_scores,
        "inertia_values": inertia_values,
        "final_silhouette": final_silhouette,
        "paths": p,
    }


def load_artifacts(
    clustered_path: Path | None = None,
    scaled_path: Path | None = None,
    kmeans_path: Path | None = None,
    scaler_path: Path | None = None,
) -> tuple[pd.DataFrame, np.ndarray, KMeans, StandardScaler]:
    p = paths()
    clustered_path = clustered_path or p["clustered_dataset"]
    scaled_path = scaled_path or p["scaled_features"]
    kmeans_path = kmeans_path or p["kmeans"]
    scaler_path = scaler_path or p["scaler"]

    df = pd.read_csv(clustered_path, low_memory=False)
    X_scaled = np.load(scaled_path)
    kmeans = joblib.load(kmeans_path)
    scaler = joblib.load(scaler_path)
    return df, X_scaled, kmeans, scaler


def recommend_by_index(
    song_index: int,
    top_n: int = 5,
    clustered_path: Path | None = None,
    scaled_path: Path | None = None,
    kmeans_path: Path | None = None,
    scaler_path: Path | None = None,
) -> pd.DataFrame:
    df, X_scaled, _, _ = load_artifacts(clustered_path, scaled_path, kmeans_path, scaler_path)

    if song_index not in df.index:
        raise IndexError("Song index out of range")

    target_cluster = int(df.loc[song_index, "cluster"])
    cluster_indices = df.index[df["cluster"] == target_cluster].tolist()

    target_vector = X_scaled[song_index].reshape(1, -1)
    cluster_vectors = X_scaled[cluster_indices]
    distances = cosine_distances(target_vector, cluster_vectors)[0]

    ranked_positions = np.argsort(distances)
    ranked_items: list[tuple[int, float]] = []

    for pos in ranked_positions:
        candidate_index = cluster_indices[pos]
        if candidate_index == song_index:
            continue
        ranked_items.append((candidate_index, float(distances[pos])))
        if len(ranked_items) == top_n:
            break

    if not ranked_items:
        return pd.DataFrame(columns=["title", "artist", "distance"])

    result_indices = [idx for idx, _ in ranked_items]
    result = df.loc[result_indices, ["title", "artist"]].copy()
    result["distance"] = [dist for _, dist in ranked_items]
    return result.reset_index(drop=True)


def recommend_by_title(
    title: str,
    top_n: int = 5,
    clustered_path: Path | None = None,
    scaled_path: Path | None = None,
    kmeans_path: Path | None = None,
    scaler_path: Path | None = None,
) -> pd.DataFrame:
    df, _, _, _ = load_artifacts(clustered_path, scaled_path, kmeans_path, scaler_path)
    normalized_title = str(title).lower().strip()
    matches = df[df["title"].astype(str).str.lower().str.strip() == normalized_title]

    if len(matches) == 0:
        raise ValueError("Song not found")

    song_index = int(matches.index[0])
    return recommend_by_index(song_index, top_n, clustered_path, scaled_path, kmeans_path, scaler_path)


def debug_cluster(song_index: int, clustered_path: Path | None = None, scaled_path: Path | None = None, kmeans_path: Path | None = None, scaler_path: Path | None = None) -> None:
    df, _, _, _ = load_artifacts(clustered_path, scaled_path, kmeans_path, scaler_path)
    cluster = int(df.loc[song_index, "cluster"])
    print(df[df["cluster"] == cluster][["title", "artist"]])


def main() -> None:
    train_pipeline()


if __name__ == "__main__":
    main()