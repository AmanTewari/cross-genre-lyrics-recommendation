from __future__ import annotations

import queue
import threading
from pathlib import Path

import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import tkinter as tk
from collections import Counter
from tkinter import ttk

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from extract_features import EMOTION_WORDS, extract_features, load_dataset, validate_columns


INPUT_PATH = Path("data/processed/clean_lyrics_dataset.csv")
OUTPUT_PATH = Path("data/processed/feature_matrix.csv")

COLUMN_LABELS = {
    "total_words": "Total Words",
    "unique_words": "Unique Words",
    "lexical_diversity": "Lexical Diversity",
    "repetition_score": "Repetition Score",
    "top_word_frequency_ratio": "Top Word Frequency Ratio",
    "num_lines": "Number of Lines",
    "avg_line_length": "Avg Line Length",
    "line_length_variance": "Line Length Variance",
    "emotion_word_count": "Emotion Word Count",
    "emotion_density": "Emotion Density",
}


def build_feature_matrix_with_progress(df: pd.DataFrame, progress_callback) -> pd.DataFrame:
    validate_columns(df)

    feature_rows = []
    total_rows = len(df)

    for index, lyrics in enumerate(df["lyrics"], start=1):
        feature_rows.append(extract_features(lyrics))
        progress_callback(index, total_rows)

    feature_matrix = pd.DataFrame(
        feature_rows,
        columns=[
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
        ],
    )
    feature_matrix["title"] = df["title"].fillna("unknown_title").astype(str)
    feature_matrix["artist"] = df["artist"].fillna("unknown_artist").astype(str)
    return feature_matrix


class FeatureExtractionApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Feature Extraction Engine")
        self.root.geometry("1200x820")

        self.queue: queue.Queue = queue.Queue()
        self.worker_thread: threading.Thread | None = None
        self.correlation_canvas: FigureCanvasTkAgg | None = None

        self.progress_label = tk.Label(root, text="Idle", anchor="w")
        self.progress_label.pack(fill="x", padx=16, pady=(16, 6))

        self.progress_bar = ttk.Progressbar(root, orient="horizontal", length=500, mode="determinate")
        self.progress_bar.pack(fill="x", padx=16, pady=(0, 12))

        button_frame = tk.Frame(root)
        button_frame.pack(fill="x", padx=16, pady=(0, 12))

        self.start_button = tk.Button(button_frame, text="Start Extraction", command=self.start_process)
        self.start_button.pack(side="left")

        self.status_text = tk.Label(button_frame, text="Ready", anchor="w")
        self.status_text.pack(side="left", padx=12)

        self.plot_frame = tk.LabelFrame(root, text="Feature Correlation Matrix")
        self.plot_frame.pack(fill="both", expand=True, padx=16, pady=(0, 16))

        self.plot_placeholder = tk.Label(
            self.plot_frame,
            text="The correlation matrix will appear here after extraction completes.",
            justify="center",
        )
        self.plot_placeholder.pack(expand=True)

    def start_process(self):
        if self.worker_thread and self.worker_thread.is_alive():
            return

        self.start_button.config(state="disabled")
        self.status_text.config(text="Loading dataset...")
        self.progress_label.config(text="Starting...")
        self.progress_bar["value"] = 0

        self.worker_thread = threading.Thread(target=self.run_extraction, daemon=True)
        self.worker_thread.start()
        self.root.after(100, self.poll_queue)

    def run_extraction(self):
        try:
            df = load_dataset(INPUT_PATH)
            validate_columns(df)

            def progress_callback(current_row: int, total_rows: int) -> None:
                self.queue.put(("progress", current_row, total_rows))

            self.queue.put(("status", f"Processing {len(df)} rows..."))
            feature_matrix = build_feature_matrix_with_progress(df, progress_callback)
            OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
            feature_matrix.to_csv(OUTPUT_PATH, index=False)

            numeric_matrix = feature_matrix[
                [
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
            ]
            correlation_matrix = numeric_matrix.corr()
            self.queue.put(("done", feature_matrix, correlation_matrix))
        except Exception as exc:  # pragma: no cover - surfaced in GUI
            self.queue.put(("error", exc))

    def poll_queue(self):
        try:
            while True:
                message = self.queue.get_nowait()
                kind = message[0]

                if kind == "status":
                    self.status_text.config(text=message[1])
                elif kind == "progress":
                    current_row, total_rows = message[1], message[2]
                    progress_percent = (current_row / total_rows) * 100 if total_rows else 0
                    self.progress_bar["value"] = progress_percent
                    self.progress_label.config(text=f"Processing: {current_row}/{total_rows}")
                elif kind == "done":
                    feature_matrix, correlation_matrix = message[1], message[2]
                    self.progress_bar["value"] = 100
                    self.progress_label.config(text=f"Completed: {len(feature_matrix)} rows")
                    self.status_text.config(text=f"Saved to {OUTPUT_PATH}")
                    self.render_correlation_matrix(correlation_matrix)
                    self.start_button.config(state="normal")
                elif kind == "error":
                    exc = message[1]
                    self.progress_label.config(text=f"Error: {exc}")
                    self.status_text.config(text="Extraction failed")
                    self.start_button.config(state="normal")
        except queue.Empty:
            pass

        if self.worker_thread and self.worker_thread.is_alive():
            self.root.after(100, self.poll_queue)

    def render_correlation_matrix(self, correlation_matrix: pd.DataFrame) -> None:
        if self.correlation_canvas is not None:
            self.correlation_canvas.get_tk_widget().destroy()

        for widget in self.plot_frame.winfo_children():
            widget.destroy()

        figure, axis = plt.subplots(figsize=(10, 8))
        image = axis.imshow(correlation_matrix.values, cmap="viridis", vmin=-1, vmax=1)
        
        # Map column names to human-readable labels
        human_labels = [COLUMN_LABELS.get(col, col) for col in correlation_matrix.columns]
        
        axis.set_xticks(range(len(correlation_matrix.columns)))
        axis.set_xticklabels(human_labels, rotation=90)
        axis.set_yticks(range(len(correlation_matrix.index)))
        axis.set_yticklabels(human_labels)
        axis.set_title("Feature Correlation Matrix")
        figure.colorbar(image, ax=axis, fraction=0.046, pad=0.04)
        figure.tight_layout()

        self.correlation_canvas = FigureCanvasTkAgg(figure, master=self.plot_frame)
        self.correlation_canvas.draw()
        self.correlation_canvas.get_tk_widget().pack(fill="both", expand=True)


def main() -> None:
    root = tk.Tk()
    app = FeatureExtractionApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()