"""
Entry point for the AI-powered Music Recommender.
Run with: python -m src.main
"""

import logging
import sys
from pathlib import Path

# Configure logging before other imports so every module's logger inherits settings.
_LOG_DIR = Path(__file__).parent.parent / "logs"
_LOG_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    handlers=[
        logging.FileHandler(_LOG_DIR / "session.log"),
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

from src.ai_agent import AIAgent
from src.rag_retriever import RAGRetriever


def _print_recommendations(query: str, recommendations: list) -> None:
    print(f"\nTop recommendations for: '{query}'\n" + "-" * 44)
    for i, rec in enumerate(recommendations, start=1):
        tag = " [UNCERTAIN]" if rec.get("uncertain") else ""
        print(f"{i}. {rec['title']} by {rec['artist']}{tag}")
        print(f"   Why        : {rec['explanation']}")
        print(f"   Confidence : {rec['confidence']:.2f}")
        print()


def main() -> None:
    csv_path = str(Path(__file__).parent.parent / "data" / "songs.csv")

    logger.info("Initializing RAG retriever")
    retriever = RAGRetriever(csv_path)

    try:
        agent = AIAgent()
    except ValueError as exc:
        logger.error("Cannot start AI agent: %s", exc)
        print(f"Error: {exc}")
        sys.exit(1)

    print("\nMusic Recommender — AI-powered")
    print("=" * 44)

    query = input("What kind of music are you in the mood for? ").strip()
    if not query:
        print("No query entered. Exiting.")
        return

    logger.info("User query: %s", query)

    candidates = retriever.retrieve(query, k=10)
    logger.info("RAG retrieved %d candidates", len(candidates))

    recommendations = agent.recommend(query, candidates, candidates)
    logger.info("Final recommendations: %s", recommendations)

    _print_recommendations(query, recommendations)


if __name__ == "__main__":
    main()
