import json
import logging
import os
from typing import Any, Dict, List

from groq import Groq
from dotenv import load_dotenv

from src.recommender import recommend_songs

load_dotenv()

logger = logging.getLogger(__name__)

_SCHEMA = (
    '{"recommendations": ['
    '{"title": str, "artist": str, "explanation": str, "confidence": float 0.0-1.0, "uncertain": bool}'
    "]}"
)

_PROMPT = """\
You are a music recommendation assistant.

User query: {query}

Candidate songs:
{candidates}

From the candidates above, pick the best 3 that match the user's query.
For each pick:
  a) Explain in 1-2 sentences why it fits the query.
  b) Rate your confidence (0.0 to 1.0) that this is a good fit.
  c) Set "uncertain": true if confidence < 0.6.

Respond ONLY with valid JSON — no markdown, no extra text — matching this schema exactly:
{schema}
"""


class AIAgent:
    """Calls the Groq API to rank and explain song candidates from the RAG retriever."""

    def __init__(self) -> None:
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in the environment")
        self._client = Groq(api_key=api_key)
        self._model = "llama-3.1-8b-instant"

    def recommend(
        self,
        query: str,
        candidates: List[Dict],
        fallback_songs: List[Dict],
    ) -> List[Dict[str, Any]]:
        """Return top-3 recommendations. Falls back to rule-based scorer on failure."""
        try:
            return self._call_groq(query, candidates)
        except Exception as exc:
            logger.warning(
                "Groq call failed (%s); using rule-based fallback top-3", exc
            )
            return self._rule_based_fallback(fallback_songs)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _call_groq(self, query: str, candidates: List[Dict]) -> List[Dict[str, Any]]:
        candidate_lines = "\n".join(
            f"- {s['title']} by {s['artist']} | genre={s['genre']} | mood={s['mood']} | energy={s['energy']}"
            for s in candidates
        )
        prompt = _PROMPT.format(
            query=query, candidates=candidate_lines, schema=_SCHEMA
        )
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
        )
        raw: str = response.choices[0].message.content.strip()

        # Strip markdown code fences if the model wraps its output
        if raw.startswith("```"):
            parts = raw.split("```")
            raw = parts[1]
            if raw.startswith("json"):
                raw = raw[4:]

        data = json.loads(raw)
        recs: List[Dict] = data["recommendations"]
        for rec in recs:
            rec["confidence"] = float(rec["confidence"])
        return recs

    def _rule_based_fallback(self, songs: List[Dict]) -> List[Dict[str, Any]]:
        neutral_prefs: Dict = {
            "favorite_genre": "",
            "favorite_mood": "",
            "target_energy": 0.5,
        }
        top3 = recommend_songs(neutral_prefs, songs, k=3)
        return [
            {
                "title": song["title"],
                "artist": song["artist"],
                "explanation": f"Rule-based fallback recommendation. {reasons}",
                "confidence": 0.5,
                "uncertain": True,
            }
            for song, _score, reasons in top3
        ]
