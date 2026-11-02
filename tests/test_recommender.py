from pathlib import Path

import pytest

from src.recommender import (
    Song,
    UserProfile,
    Recommender,
    load_songs,
    score_song,
    recommend_songs,
)

SONGS_CSV = Path(__file__).resolve().parent.parent / "data" / "songs.csv"


def make_song(**overrides) -> dict:
    song = {
        "id": 1,
        "title": "Base Song",
        "artist": "Base Artist",
        "genre": "pop",
        "mood": "happy",
        "energy": 0.8,
        "tempo_bpm": 120.0,
        "valence": 0.8,
        "danceability": 0.8,
        "acousticness": 0.2,
    }
    song.update(overrides)
    return song


FULL_PREFS = {
    "genre": "pop",
    "mood": "happy",
    "energy": 0.8,
    "valence": 0.8,
    "tempo_bpm": 120,
    "danceability": 0.8,
    "likes_acoustic": False,
}

def make_small_recommender() -> Recommender:
    songs = [
        Song(
            id=1,
            title="Test Pop Track",
            artist="Test Artist",
            genre="pop",
            mood="happy",
            energy=0.8,
            tempo_bpm=120,
            valence=0.9,
            danceability=0.8,
            acousticness=0.2,
        ),
        Song(
            id=2,
            title="Chill Lofi Loop",
            artist="Test Artist",
            genre="lofi",
            mood="chill",
            energy=0.4,
            tempo_bpm=80,
            valence=0.6,
            danceability=0.5,
            acousticness=0.9,
        ),
    ]
    return Recommender(songs)


def test_recommend_returns_songs_sorted_by_score():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    results = rec.recommend(user, k=2)

    assert len(results) == 2
    # Starter expectation: the pop, happy, high energy song should score higher
    assert results[0].genre == "pop"
    assert results[0].mood == "happy"


def test_explain_recommendation_returns_non_empty_string():
    user = UserProfile(
        favorite_genre="pop",
        favorite_mood="happy",
        target_energy=0.8,
        likes_acoustic=False,
    )
    rec = make_small_recommender()
    song = rec.songs[0]

    explanation = rec.explain_recommendation(user, song)
    assert isinstance(explanation, str)
    assert explanation.strip() != ""


# --- load_songs ---

def test_load_songs_reads_all_rows_with_numeric_types():
    songs = load_songs(str(SONGS_CSV))

    assert len(songs) == 20
    first = songs[0]
    assert first["title"] == "Sunrise City"
    assert isinstance(first["id"], int)
    for field in ("energy", "tempo_bpm", "valence", "danceability", "acousticness"):
        assert isinstance(first[field], float)


# --- score_song ---

def test_score_song_perfect_match_scores_one():
    score, reasons = score_song(FULL_PREFS, make_song())

    assert score == pytest.approx(1.0)
    assert any("mood matches" in r for r in reasons)
    assert any("genre matches" in r for r in reasons)


def test_score_song_better_match_scores_higher_and_stays_in_range():
    close = make_song(energy=0.75, valence=0.7)
    far = make_song(
        genre="metal", mood="angry", energy=0.1, valence=0.1,
        tempo_bpm=60.0, danceability=0.1, acousticness=0.95,
    )

    close_score, _ = score_song(FULL_PREFS, close)
    far_score, _ = score_song(FULL_PREFS, far)

    assert close_score > far_score
    assert 0.0 <= far_score <= close_score <= 1.0


def test_score_song_skips_missing_prefs_and_renormalizes():
    prefs = {"genre": "pop"}

    match, _ = score_song(prefs, make_song(genre="pop"))
    miss, _ = score_song(prefs, make_song(genre="jazz"))

    assert match == pytest.approx(1.0)
    assert miss == pytest.approx(0.0)


def test_score_song_gives_partial_credit_for_related_mood():
    prefs = {"mood": "chill"}

    exact, _ = score_song(prefs, make_song(mood="chill"))
    related, reasons = score_song(prefs, make_song(mood="relaxed"))
    unrelated, _ = score_song(prefs, make_song(mood="angry"))

    assert exact == pytest.approx(1.0)
    assert related == pytest.approx(0.5)
    assert unrelated == pytest.approx(0.0)
    assert any("related" in r for r in reasons)


def test_score_song_weights_mood_more_than_genre():
    mood_only = make_song(genre="jazz", mood="happy")
    genre_only = make_song(genre="pop", mood="sad")
    prefs = {"genre": "pop", "mood": "happy"}

    mood_score, _ = score_song(prefs, mood_only)
    genre_score, _ = score_song(prefs, genre_only)

    assert mood_score > genre_score


# --- recommend_songs ---

def test_recommend_songs_without_current_song_ranks_by_profile():
    songs = [
        make_song(id=1, title="Far", genre="metal", mood="angry", energy=0.1, valence=0.1),
        make_song(id=2, title="Match"),
        make_song(id=3, title="Okay", genre="pop", mood="sad", energy=0.6),
    ]

    results = recommend_songs(FULL_PREFS, songs, k=3)

    assert [r[0]["title"] for r in results] == ["Match", "Okay", "Far"]
    scores = [r[1] for r in results]
    assert scores == sorted(scores, reverse=True)
    assert all(isinstance(r[2], str) and r[2] for r in results)


def test_recommend_songs_respects_k():
    songs = [make_song(id=i, title=f"Song {i}") for i in range(1, 8)]

    assert len(recommend_songs(FULL_PREFS, songs, k=3)) == 3


def test_recommend_songs_excludes_current_and_recently_played():
    songs = [make_song(id=i, title=f"Song {i}") for i in range(1, 5)]
    current = songs[0]

    results = recommend_songs(
        FULL_PREFS, songs, k=10, current_song=current, recently_played=[2]
    )

    assert {r[0]["id"] for r in results} == {3, 4}


def test_recommend_songs_prefers_songs_that_flow_from_a_good_seed():
    # The current song matches the profile, so alpha is high and flow matters.
    current = make_song(id=1, title="Current", artist="A")
    similar = make_song(id=2, title="Similar", artist="B", energy=0.75)
    different = make_song(
        id=3, title="Different", artist="C", genre="metal", mood="angry",
        energy=0.2, valence=0.1, tempo_bpm=70.0, danceability=0.2, acousticness=0.9,
    )

    results = recommend_songs(
        FULL_PREFS, [current, different, similar], k=2, current_song=current
    )

    assert [r[0]["title"] for r in results] == ["Similar", "Different"]


def test_recommend_songs_penalizes_large_energy_jump():
    current = make_song(id=1, title="Current", artist="A", energy=0.9)
    jump = make_song(id=2, title="Jump", artist="B", energy=0.4)
    smooth = make_song(id=3, title="Smooth", artist="C", energy=0.8)

    results = recommend_songs(FULL_PREFS, [jump, smooth], k=2, current_song=current)
    explanations = {r[0]["title"]: r[2] for r in results}

    assert "penalty: large energy jump" in explanations["Jump"]
    assert "penalty: large energy jump" not in explanations["Smooth"]


def test_recommend_songs_penalizes_same_artist():
    current = make_song(id=1, title="Current", artist="Same Artist")
    repeat = make_song(id=2, title="Repeat", artist="Same Artist")
    other = make_song(id=3, title="Other", artist="Someone Else")

    results = recommend_songs(FULL_PREFS, [repeat, other], k=2, current_song=current)
    explanations = {r[0]["title"]: r[2] for r in results}

    assert "penalty: same artist as current song" in explanations["Repeat"]
    assert "penalty: same artist as current song" not in explanations["Other"]
    assert results[0][0]["title"] == "Other"


# --- Expected winners on the real catalog ---
# Each profile describes one song closely, so its expected winner should stay
# stable unless the weights or the catalog change enough to alter the ranking.

@pytest.fixture(scope="module")
def catalog():
    return load_songs(str(SONGS_CSV))


PROFILE_WINNERS = [
    pytest.param(
        {"genre": "metal", "mood": "angry", "energy": 0.97, "valence": 0.22,
         "tempo_bpm": 168, "danceability": 0.38, "likes_acoustic": False},
        "Iron Procession", id="metal-fan",
    ),
    pytest.param(
        {"genre": "classical", "mood": "melancholic", "energy": 0.18, "valence": 0.20,
         "tempo_bpm": 54, "danceability": 0.22, "likes_acoustic": True},
        "Nocturne in Blue", id="classical-listener",
    ),
    pytest.param(
        {"genre": "edm", "mood": "euphoric", "energy": 0.96, "valence": 0.88,
         "tempo_bpm": 128, "danceability": 0.91, "likes_acoustic": False},
        "Bassline Cathedral", id="edm-dancer",
    ),
    pytest.param(
        {"genre": "indie pop", "mood": "happy", "energy": 0.72, "valence": 0.78,
         "tempo_bpm": 115, "danceability": 0.75, "likes_acoustic": False},
        "Rooftop Lights", id="sunny-commuter",
    ),
    pytest.param(
        {"genre": "lofi", "mood": "chill", "energy": 0.35, "valence": 0.60,
         "tempo_bpm": 72, "danceability": 0.58, "likes_acoustic": True},
        "Library Rain", id="chill-lofi",
    ),
    pytest.param(
        {"genre": "lofi", "mood": "focused", "energy": 0.40, "valence": 0.59,
         "tempo_bpm": 80, "danceability": 0.60, "likes_acoustic": True},
        "Focus Flow", id="focused-lofi",
    ),
    pytest.param(
        {"genre": "jazz", "mood": "relaxed", "energy": 0.37, "valence": 0.71,
         "tempo_bpm": 90, "danceability": 0.54, "likes_acoustic": True},
        "Coffee Shop Stories", id="relaxed-jazz",
    ),
]


@pytest.mark.parametrize("prefs, expected_title", PROFILE_WINNERS)
def test_profile_gets_expected_top_song(catalog, prefs, expected_title):
    results = recommend_songs(prefs, catalog, k=5)

    assert results[0][0]["title"] == expected_title


def test_related_mood_song_ranks_near_the_top_for_metal_fan(catalog):
    prefs = PROFILE_WINNERS[0].values[0]

    top_three = [r[0]["title"] for r in recommend_songs(prefs, catalog, k=3)]

    # Storm Runner is rock/intense: not metal/angry, but a related mood and similar energy.
    assert "Storm Runner" in top_three


def test_recommendations_are_deterministic(catalog):
    prefs = PROFILE_WINNERS[3].values[0]

    first = recommend_songs(prefs, catalog, k=5)
    second = recommend_songs(prefs, catalog, k=5)

    assert [r[0]["id"] for r in first] == [r[0]["id"] for r in second]
    assert [r[1] for r in first] == [r[1] for r in second]
