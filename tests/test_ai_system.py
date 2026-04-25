"""Automated tests for the AI-powered music recommender system."""

import json
import logging
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Ensure project root is on the path so `src.*` imports resolve.
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_retriever import RAGRetriever
from src.ai_agent import AIAgent

CSV_PATH = str(Path(__file__).parent.parent / "data" / "songs.csv")

SAMPLE_QUERIES = [
    "something chill and relaxing for studying",
    "high energy workout music",
    "sad rainy day vibes",
]


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def retriever() -> RAGRetriever:
    return RAGRetriever(CSV_PATH)


def _make_agent(
    generate_return_value: MagicMock | None = None,
    generate_side_effect: Exception | None = None,
) -> AIAgent:
    """Create an AIAgent with a fully mocked Groq client."""
    mock_create = MagicMock()
    if generate_side_effect is not None:
        mock_create.side_effect = generate_side_effect
    if generate_return_value is not None:
        mock_create.return_value = generate_return_value

    mock_client = MagicMock()
    mock_client.chat.completions.create = mock_create

    with (
        patch.dict(os.environ, {"GROQ_API_KEY": "test-key"}),
        patch("src.ai_agent.Groq", return_value=mock_client),
    ):
        return AIAgent()


def _valid_response() -> MagicMock:
    """Build a mock Groq response with valid JSON payload."""
    data = {
        "recommendations": [
            {
                "title": "Sunrise City",
                "artist": "Neon Echo",
                "explanation": "Upbeat happy pop song.",
                "confidence": 0.92,
                "uncertain": False,
            },
            {
                "title": "Midnight Coding",
                "artist": "LoRoom",
                "explanation": "Chill lofi perfect for focus.",
                "confidence": 0.85,
                "uncertain": False,
            },
            {
                "title": "Focus Flow",
                "artist": "LoRoom",
                "explanation": "Relaxed tempo aids concentration.",
                "confidence": 0.55,
                "uncertain": True,
            },
        ]
    }
    mock_message = MagicMock()
    mock_message.content = json.dumps(data)
    mock_choice = MagicMock()
    mock_choice.message = mock_message
    mock_resp = MagicMock()
    mock_resp.choices = [mock_choice]
    return mock_resp


# ---------------------------------------------------------------------------
# RAG retriever tests
# ---------------------------------------------------------------------------


def test_rag_returns_exactly_k_results(retriever: RAGRetriever) -> None:
    results = retriever.retrieve("chill music for studying", k=5)
    assert len(results) == 5


def test_rag_returns_k_results_when_k_equals_1(retriever: RAGRetriever) -> None:
    results = retriever.retrieve("loud rock", k=1)
    assert len(results) == 1


def test_rag_results_are_song_dicts(retriever: RAGRetriever) -> None:
    results = retriever.retrieve("energetic pop", k=3)
    required_keys = {"title", "artist", "genre", "mood", "energy"}
    for song in results:
        assert isinstance(song, dict)
        assert required_keys.issubset(song.keys())


# ---------------------------------------------------------------------------
# Fallback tests
# ---------------------------------------------------------------------------


def test_fallback_triggers_on_api_exception(
    retriever: RAGRetriever, caplog: pytest.LogCaptureFixture
) -> None:
    agent = _make_agent(generate_side_effect=Exception("network error"))
    candidates = retriever.retrieve("chill music", k=10)

    with caplog.at_level(logging.WARNING, logger="src.ai_agent"):
        results = agent.recommend("chill music", candidates, candidates)

    assert len(results) == 3
    assert all(r["uncertain"] is True for r in results)
    assert "fallback" in caplog.text.lower()


def test_fallback_triggers_on_invalid_json(
    retriever: RAGRetriever, caplog: pytest.LogCaptureFixture
) -> None:
    bad_response = MagicMock()
    bad_response.text = "this is not json {{{"
    agent = _make_agent(generate_return_value=bad_response)
    candidates = retriever.retrieve("rock", k=10)

    with caplog.at_level(logging.WARNING, logger="src.ai_agent"):
        results = agent.recommend("rock", candidates, candidates)

    assert len(results) == 3
    assert all(r["uncertain"] is True for r in results)


# ---------------------------------------------------------------------------
# Confidence score validation
# ---------------------------------------------------------------------------


def test_confidence_scores_are_floats_between_0_and_1(
    retriever: RAGRetriever,
) -> None:
    agent = _make_agent(generate_return_value=_valid_response())
    candidates = retriever.retrieve("happy pop", k=10)
    results = agent.recommend("happy pop", candidates, candidates)

    for rec in results:
        assert isinstance(rec["confidence"], float), f"Expected float, got {type(rec['confidence'])}"
        assert 0.0 <= rec["confidence"] <= 1.0, f"Confidence out of range: {rec['confidence']}"


# ---------------------------------------------------------------------------
# Logging test
# ---------------------------------------------------------------------------


def test_logging_writes_to_file(tmp_path: Path) -> None:
    log_file = tmp_path / "session.log"
    handler = logging.FileHandler(str(log_file))
    test_logger = logging.getLogger("test_session_log_unique_name")
    test_logger.addHandler(handler)
    test_logger.setLevel(logging.INFO)

    test_logger.info("Test query: chill music for studying")
    handler.flush()

    assert log_file.exists()
    content = log_file.read_text()
    assert "Test query: chill music for studying" in content


# ---------------------------------------------------------------------------
# Full pipeline smoke tests
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("query", SAMPLE_QUERIES)
def test_pipeline_returns_nonempty_results_for_sample_queries(
    retriever: RAGRetriever, query: str
) -> None:
    agent = _make_agent(generate_return_value=_valid_response())
    candidates = retriever.retrieve(query, k=10)
    results = agent.recommend(query, candidates, candidates)

    assert len(results) > 0
    for rec in results:
        assert rec.get("title"), "Recommendation missing title"
        assert rec.get("artist"), "Recommendation missing artist"
        assert rec.get("explanation"), "Recommendation missing explanation"
