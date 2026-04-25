import csv
from typing import List, Dict

import numpy as np
from sentence_transformers import SentenceTransformer


def _song_to_text(song: Dict) -> str:
    return f"{song['genre']} {song['mood']} energy {song['energy']}"


def _cosine_similarity(a: np.ndarray, b: np.ndarray) -> float:
    norm = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / (norm + 1e-10))


class RAGRetriever:
    """Embeds songs from a CSV and retrieves top-K by cosine similarity to a query."""

    def __init__(self, csv_path: str, model_name: str = "all-MiniLM-L6-v2") -> None:
        self._songs = self._load_csv(csv_path)
        self._model = SentenceTransformer(model_name)
        descriptions = [_song_to_text(s) for s in self._songs]
        self._embeddings: np.ndarray = self._model.encode(
            descriptions, normalize_embeddings=True
        )

    def _load_csv(self, csv_path: str) -> List[Dict]:
        songs: List[Dict] = []
        with open(csv_path, newline="", encoding="utf-8") as f:
            for row in csv.DictReader(f):
                row["energy"] = float(row["energy"])
                row["tempo_bpm"] = float(row["tempo_bpm"])
                songs.append(row)
        return songs

    def retrieve(self, query: str, k: int = 10) -> List[Dict]:
        """Return the top-k songs whose descriptions are most similar to the query."""
        query_emb: np.ndarray = self._model.encode(
            [query], normalize_embeddings=True
        )[0]
        scores = [_cosine_similarity(query_emb, emb) for emb in self._embeddings]
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        return [self._songs[i] for i in top_indices]
