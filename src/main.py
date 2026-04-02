"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv") 

    # Starter example profile
    user_prefs = {
        "favorite_genre": "pop",
        "favorite_mood": "happy",
        "target_energy": 0.8,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)

    print("\n" + "=" * 40)
    print("  Top Recommendations")
    print("=" * 40)
    for i, (song, score, reasons) in enumerate(recommendations, start=1):
        print(f"\n{i}. {song['title']} by {song['artist']}")
        print(f"   Score : {score:.2f} / 4.00")
        print(f"   Why   : {reasons}")
    print("\n" + "=" * 40)


if __name__ == "__main__":
    main()
