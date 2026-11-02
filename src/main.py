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

    # Taste profile: "Sunny Commuter" - upbeat, danceable, mostly electronic/produced
    user_prefs = {
        "genre": "indie pop",
        "mood": "happy",
        "energy": 0.72,
        "valence": 0.78,
        "tempo_bpm": 115,
        "danceability": 0.75,
        "likes_acoustic": False,
    }

    recommendations = recommend_songs(user_prefs, songs, k=5)
    print_recommendations(recommendations, heading="Top recommendations for Sunny Commuter")


def print_recommendations(recommendations, heading: str) -> None:
    """Prints ranked (song, score, explanation) results as a readable list."""
    width = 56
    print()
    print("=" * width)
    print(heading)
    print("=" * width)

    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        title = f"{rank}. {song['title']}"
        print(f"\n{title:<{width - 8}}{score:>6.2f}")
        print(f"   {song['artist']} | {song['genre']} | {song['mood']}")

        reasons = explanation.split("; ") if explanation else ["no strong matches"]
        for reason in reasons:
            print(f"   - {reason}")

    print("\n" + "=" * width)


if __name__ == "__main__":
    main()
