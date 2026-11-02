import csv
from operator import itemgetter
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool
    target_valence: float = 0.5
    target_tempo_bpm: float = 100
    target_danceability: float = 0.5

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

def load_songs(csv_path: str) -> List[Dict]:
    """
    Loads songs from a CSV file.
    Required by src/main.py
    """
    print(f"Loading songs from {csv_path}...")
    int_fields = ("id",)
    float_fields = ("energy", "tempo_bpm", "valence", "danceability", "acousticness")

    songs = []
    with open(csv_path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            for field in int_fields:
                row[field] = int(row[field])
            for field in float_fields:
                row[field] = float(row[field])
            songs.append(row)

    print (f"Loaded songs: {len(songs)}")
    return songs

WEIGHTS = {
    "mood": 0.25,
    "energy": 0.20,
    "valence": 0.20,
    "genre": 0.15,
    "tempo_bpm": 0.08,
    "danceability": 0.07,
    "acousticness": 0.05,
}

# Moods that earn partial credit when they are not an exact match.
RELATED_MOODS = [
    {"chill", "relaxed"},
    {"chill", "focused"},
    {"relaxed", "laid-back"},
    {"happy", "playful"},
    {"happy", "euphoric"},
    {"intense", "angry"},
    {"sad", "melancholic"},
    {"nostalgic", "wistful"},
]

TEMPO_MIN_BPM = 60
TEMPO_RANGE_BPM = 120
STRONG_MATCH = 0.85


def _normalize_tempo(bpm: float) -> float:
    """Scales tempo to 0-1 so it is comparable with the other features."""
    return min(max((bpm - TEMPO_MIN_BPM) / TEMPO_RANGE_BPM, 0.0), 1.0)


def _mood_similarity(target: str, actual: str) -> float:
    """Returns 1.0 for an exact mood match, 0.5 for a related mood, else 0.0."""
    if target == actual:
        return 1.0
    if {target, actual} in RELATED_MOODS:
        return 0.5
    return 0.0


def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """
    Scores a single song against user preferences.
    Required by recommend_songs() and src/main.py

    Returns (score, reasons) where score is 0-1. Features missing from
    user_prefs are skipped and the remaining weights are renormalized.
    """
    similarities: Dict[str, float] = {}
    reasons: List[str] = []

    if "genre" in user_prefs:
        similarities["genre"] = 1.0 if user_prefs["genre"] == song["genre"] else 0.0
        if similarities["genre"]:
            reasons.append(f"genre matches ({song['genre']})")

    if "mood" in user_prefs:
        similarities["mood"] = _mood_similarity(user_prefs["mood"], song["mood"])
        if similarities["mood"] == 1.0:
            reasons.append(f"mood matches ({song['mood']})")
        elif similarities["mood"] > 0:
            reasons.append(f"mood is related ({song['mood']} ~ {user_prefs['mood']})")

    for feature in ("energy", "valence", "danceability"):
        if feature in user_prefs:
            similarities[feature] = 1 - abs(user_prefs[feature] - song[feature])
            if similarities[feature] >= STRONG_MATCH:
                reasons.append(
                    f"{feature} {song[feature]:.2f} is close to target {user_prefs[feature]:.2f}"
                )

    if "tempo_bpm" in user_prefs:
        similarities["tempo_bpm"] = 1 - abs(
            _normalize_tempo(user_prefs["tempo_bpm"]) - _normalize_tempo(song["tempo_bpm"])
        )
        if similarities["tempo_bpm"] >= STRONG_MATCH:
            reasons.append(f"tempo {song['tempo_bpm']:.0f} bpm is close to target")

    if "likes_acoustic" in user_prefs:
        target = 0.8 if user_prefs["likes_acoustic"] else 0.2
        similarities["acousticness"] = 1 - abs(target - song["acousticness"])
        if similarities["acousticness"] >= STRONG_MATCH:
            reasons.append("acousticness fits preference")

    total_weight = sum(WEIGHTS[f] for f in similarities)
    if total_weight == 0:
        return 0.0, reasons
    score = sum(WEIGHTS[f] * s for f, s in similarities.items()) / total_weight
    return score, reasons

FLOW_ALPHA_SCALE = 0.6
ENERGY_JUMP_LIMIT = 0.4
ENERGY_JUMP_PENALTY = 0.10
SAME_ARTIST_PENALTY = 0.05


def _flow_score(current: Dict, candidate: Dict) -> float:
    """Weighted similarity between two songs across all seven features."""
    sims = {
        "genre": 1.0 if current["genre"] == candidate["genre"] else 0.0,
        "mood": _mood_similarity(current["mood"], candidate["mood"]),
        "tempo_bpm": 1 - abs(
            _normalize_tempo(current["tempo_bpm"]) - _normalize_tempo(candidate["tempo_bpm"])
        ),
    }
    for feature in ("energy", "valence", "danceability", "acousticness"):
        sims[feature] = 1 - abs(current[feature] - candidate[feature])
    return sum(WEIGHTS[f] * s for f, s in sims.items())


def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    current_song: Optional[Dict] = None,
    recently_played: Optional[List[int]] = None,
) -> List[Tuple[Dict, float, str]]:
    """
    Functional implementation of the recommendation logic.
    Required by src/main.py

    Without current_song, songs are ranked purely by fit to user_prefs.
    With current_song, each candidate's profile score is blended with its
    similarity to the current song (Part 2 of the algorithm), and the song
    ids in recently_played are excluded.
    Returns (song_dict, score, explanation), best first.
    """
    excluded = set(recently_played or [])
    alpha = 0.0
    if current_song is not None:
        excluded.add(current_song["id"])
        seed_score, _ = score_song(user_prefs, current_song)
        alpha = FLOW_ALPHA_SCALE * seed_score

    ranked = []
    for song in songs:
        if song["id"] in excluded:
            continue

        profile_score, reasons = score_song(user_prefs, song)
        score = profile_score

        if current_song is not None:
            flow = _flow_score(current_song, song)
            score = alpha * flow + (1 - alpha) * profile_score
            reasons.append(f"flow with current song {flow:.2f}")

            if abs(song["energy"] - current_song["energy"]) > ENERGY_JUMP_LIMIT:
                score -= ENERGY_JUMP_PENALTY
                reasons.append("penalty: large energy jump")
            if song["artist"] == current_song["artist"]:
                score -= SAME_ARTIST_PENALTY
                reasons.append("penalty: same artist as current song")

        ranked.append((song, score, "; ".join(reasons)))

    ranked.sort(key=itemgetter(1), reverse=True)
    return ranked[:k]
