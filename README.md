# 🎵 Music Recommender Simulation

## Project Summary

In this project you will build and explain a small music recommender system.

Your goal is to:

- Represent songs and a user "taste profile" as data
- Design a scoring rule that turns that data into recommendations
- Evaluate what your system gets right and wrong
- Reflect on how this mirrors real world AI recommenders

Replace this paragraph with your own summary of what your version does.

---

## How The System Works

Explain your design in plain language.

Some prompts to answer:

- What features does each `Song` use in your system
  - For example: genre, mood, energy, tempo
- What information does your `UserProfile` store
- How does your `Recommender` compute a score for each song
- How do you choose which songs to recommend

Technically it uses all of the features to build a profile of the song, but give extra weight to mood, energy, valence, with slightly increased weights on genre and tempo. This ensures a strong cohesion within the playlist created by recommending the next song. 
Here are the weights:
Feature	Weight
mood	0.25
energy	0.20
valence	0.20
genre	0.15
tempo (normalized)	0.08
danceability	0.07
acousticness	0.05

Userprofile stores favorite_genre, favorite_mood, target_energy, and likes_accoustic.
It uses the formula: seed_score = Σ weight_f × sim_f(user_target, current_song). to output a score between 0 and 1.
It looks at the remaining, unplayed songs and calculates a new score using a profile score as well as a flow_score which is a weighted similarity between each song and the current song. If there is a good seed_score between available, it will prioritize that, otherwise it falls back onto the users profile preferences. As a part of the score weight, large energy jumps are subtracted from the score. The options are ranged in a list where the most favorable is selected next.

Some potential biases that might present in testing are favoring energy and valence. This would be because there is an extremely wide range of genres and mood in the small set of songs. In addition to that mood, energy, and valence make up 65% of the score. 

---

## Getting Started

### Setup

1. Create a virtual environment (optional but recommended):

   ```bash
   python -m venv .venv
   source .venv/bin/activate      # Mac or Linux
   .venv\Scripts\activate         # Windows

2. Install dependencies

```bash
pip install -r requirements.txt
```

3. Run the app:

```bash
python -m src.main
```

### Running Tests

Run the starter tests with:

```bash
pytest
```

You can add more tests in `tests/test_recommender.py`.

---

## Sample Recommendation Output

Paste a sample of your recommender's output here as a text block so a reader can see what it produces:

```
========================================================
Top recommendations for Sunny Commuter
========================================================

1. Rooftop Lights                                 0.97
   Indigo Parade | indie pop | happy
   - genre matches (indie pop)
   - mood matches (happy)
   - energy 0.76 is close to target 0.72
   - valence 0.81 is close to target 0.78
   - danceability 0.82 is close to target 0.75
   - tempo 124 bpm is close to target
   - acousticness fits preference

2. Sunrise City                                   0.81
   Neon Echo | pop | happy
   - mood matches (happy)
   - energy 0.82 is close to target 0.72
   - valence 0.84 is close to target 0.78
   - danceability 0.79 is close to target 0.75
   - tempo 118 bpm is close to target
   - acousticness fits preference

3. Salt and Sunday                                0.67
   Luz Ribeiro | latin | playful
   - mood is related (playful ~ happy)
   - energy 0.64 is close to target 0.72
   - valence 0.85 is close to target 0.78
   - danceability 0.80 is close to target 0.75
   - tempo 104 bpm is close to target

4. Bassline Cathedral                             0.63
   Subtone Collective | edm | euphoric
   - mood is related (euphoric ~ happy)
   - valence 0.88 is close to target 0.78
   - tempo 128 bpm is close to target

5. Night Drive Loop                               0.53
   Neon Echo | synthwave | moody
   - energy 0.75 is close to target 0.72
   - danceability 0.73 is close to target 0.75
   - tempo 110 bpm is close to target
   - acousticness fits preference

========================================================
```

**Screenshot or video** *(optional)*: <!-- Insert a screenshot or demo video link here -->

---

## Experiments You Tried

Use this section to document the experiments you ran. For example:

- What happened when you changed the weight on genre from 2.0 to 0.5
- What happened when you added tempo or valence to the score
- How did your system behave for different types of users

---

## Limitations and Risks

Summarize some limitations of your recommender.

Examples:

- It only works on a tiny catalog
- It does not understand lyrics or language
- It might over favor one genre or mood

You will go deeper on this in your model card.

---

## Reflection

Read and complete `model_card.md`:

[**Model Card**](model_card.md)

Write 1 to 2 paragraphs here about what you learned:

- about how recommenders turn data into predictions
- about where bias or unfairness could show up in systems like this



