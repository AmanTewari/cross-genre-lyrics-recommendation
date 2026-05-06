from flask import Flask, request, jsonify
import traceback

from pathlib import Path
import sys

import numpy as np

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.models.cluster_pipeline import load_artifacts, paths
from src.features.extract_features import extract_features
from sklearn.metrics.pairwise import cosine_distances

app = Flask(__name__)


@app.after_request
def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
    return response


def compute_similarity_percent(dist):
    # Convert cosine distance (0..2) to approximate percentage similarity
    sim = max(0.0, 1.0 - dist)  # 1 - distance
    return round(sim * 100, 1)


@app.route('/api/analyze_lyrics', methods=['POST', 'OPTIONS'])
def analyze_lyrics():
    try:
        if request.method == 'OPTIONS':
            return ('', 204)

        data = request.get_json(force=True)
        lyrics = data.get('lyrics', '')
        top_n = int(data.get('top_n', 6))

        if not lyrics or len(lyrics.split()) < 5:
            return jsonify({'error': 'Please provide at least 5 words of lyrics'}), 400

        # Load artifacts
        df, X_scaled, kmeans, scaler = load_artifacts()

        # Extract features and scale
        feat = np.array(extract_features(lyrics)).reshape(1, -1)
        feat_scaled = scaler.transform(feat)

        # Predict cluster
        cluster_label = int(kmeans.predict(feat_scaled)[0])

        # compute similarity to cluster center (cosine distance)
        center = kmeans.cluster_centers_[cluster_label].reshape(1, -1)
        dist_to_center = float(cosine_distances(feat_scaled, center)[0][0])
        similarity_percent = compute_similarity_percent(dist_to_center)

        # find nearest songs within that cluster
        cluster_indices = df.index[df['cluster'] == cluster_label].tolist()
        if len(cluster_indices) == 0:
            recommendations = []
        else:
            cluster_vectors = X_scaled[cluster_indices]
            distances = cosine_distances(feat_scaled, cluster_vectors)[0]
            ranked = np.argsort(distances)[: top_n]
            recommendations = []
            for r in ranked:
                idx = cluster_indices[int(r)]
                rec = {
                    'title': str(df.loc[idx, 'title']),
                    'artist': str(df.loc[idx, 'artist']),
                    'distance': float(distances[int(r)]),
                    'similarity': compute_similarity_percent(float(distances[int(r)])),
                }
                recommendations.append(rec)

        # simple cluster tags (match frontend defaults)
        default_tags = [
            {'tag': 'Emotional', 'desc': 'Emotional and introspective'},
            {'tag': 'Narrative', 'desc': 'Story-driven lyrics'},
            {'tag': 'Repetitive', 'desc': 'Repetitive hooks and choruses'},
            {'tag': 'Minimalist', 'desc': 'Sparse, minimal lines'},
            {'tag': 'Melodic', 'desc': 'Melodic phrasing emphasis'},
            {'tag': 'Rhythmic', 'desc': 'Rhythmic phrasing, short lines'},
            {'tag': 'Storytelling', 'desc': 'Narrative arc and characters'},
            {'tag': 'Abstract', 'desc': 'Abstract imagery and metaphors'},
            {'tag': 'Romantic', 'desc': 'Romantic themes and longing'},
            {'tag': 'Reflective', 'desc': 'Reflective, quiet storytelling'},
        ]

        return jsonify({
            'cluster': int(cluster_label),
            'similarity_percent': similarity_percent,
            'recommendations': recommendations,
            'cluster_tags': default_tags,
            'k': int(kmeans.n_clusters),
        })
    except Exception as e:
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # Run on port 5001 to avoid conflicts
    app.run(host='127.0.0.1', port=5001, debug=False)
