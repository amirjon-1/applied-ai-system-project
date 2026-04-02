"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def print_recommendations(profile_name: str, recommendations: list) -> None:
    """Prints a labeled recommendation block for a given user profile."""
    print("\n" + "=" * 40)
    print(f"  {profile_name}")
    print("=" * 40)
    for i, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"\n{i}. {song['title']} by {song['artist']}")
        print(f"   Score : {score:.2f} / 4.00")
        print(f"   Why   : {reasons}")
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")

    high_energy_pop = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.90,
    }

    chill_lofi = {
        "favorite_genre": "lofi",
        "favorite_mood": "chill",
        "target_energy": 0.38,
    }

    intense_rock = {
        "favorite_genre": "rock",
        "favorite_mood": "intense",
        "target_energy": 0.91,
    }

    profiles = [
        ("High Energy Pop", high_energy_pop),
        ("Chill Lofi",      chill_lofi),
        ("Intense Rock",    intense_rock),
    ]

    for name, prefs in profiles:
        results = recommend_songs(prefs, songs, k=5)
        print_recommendations(name, results)


if __name__ == "__main__":
    main()
