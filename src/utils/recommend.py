import pandas as pd

from src.models.cluster_pipeline import load_artifacts, recommend_by_title


def run(top_n: int = 5) -> pd.DataFrame:
    df, _, _, _ = load_artifacts()
    if df.empty:
        raise RuntimeError("Clustered dataset is empty")

    first_title = str(df.iloc[0]["title"])
    recommendations = recommend_by_title(first_title, top_n=top_n)
    print(f"Recommendation smoke test for: {first_title}")
    print(recommendations)
    return recommendations
