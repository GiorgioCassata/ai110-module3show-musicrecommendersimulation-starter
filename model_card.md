# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

Give your model a short, descriptive name.  
Example: **VibeFinder 1.0**  

**FlowFinder 1.0**

---

## 2. Intended Use  

Describe what your recommender is designed to do and who it is for. 

Prompts:  

- What kind of recommendations does it generate  
- What assumptions does it make about the user  
- Is this for real users or classroom exploration  

FlowFinder suggests which song should play next. It works in two steps: it checks how well the song playing now fits the listener, then ranks the rest of the catalog to pick the next one. The goal is a playlist that flows, where each song feels like a natural step from the one before. It does this by creating a ranked list of the top songs to play next, each with the reasons behind its score.
The user can be described by a single fixed taste profile (favorite genre and mood, plus target energy, valence, tempo and danceability, and whether they like acoustic music). It assumes people want songs that feel similar to what just played.
This is a classroom exploration, but could still have a real-world use. All it would require is a more integrated implementation.


---

## 3. How the Model Works  

Explain your scoring approach in simple language.  

Prompts:  

- What features of each song are used (genre, energy, mood, etc.)  
- What user preferences are considered  
- How does the model turn those into a score  
- What changes did you make from the starter logic  

Every song is described by seven things: its genre, its mood, how energetic it is, how happy or positive it sounds (valence), how fast it is (tempo), how danceable it is, and how acoustic it is.
The listener has a taste profile with a target for each of these. To score a song, the model checks how close each feature is to the target. Genre and mood are checked for a match, and mood gives half credit for a related mood, such as chill and relaxed. The numeric features count for more when they are closer. These checks are combined into one score between 0 and 1.
Not every feature counts equally. Mood, energy and valence count the most, because songs that agree on those tend to sit well together in a playlist. Genre comes next, then tempo, danceability and acousticness.
The model works in two parts:
1. It scores the song that is playing against the listener's profile. A high score means the current song is a good guide to what the listener wants.
2. Each remaining song gets a score for fit to the listener and a score for how similar it is to the current song, and the two are blended. The better the current song fits the listener, the more the next pick follows the current song. If it fits poorly, the model relies on the listener's profile instead. Songs are then marked down for a big jump in energy or for coming from the same artist as the current song, and the highest score plays next.
The starter logic returned the first songs in the file with no scoring. I added CSV loading, the weighted scoring, the two-part ranking, the penalties, a readable results display, and unit tests.

---

## 4. Data  

Describe the dataset the model uses.  

Prompts:  

- How many songs are in the catalog  
- What genres or moods are represented  
- Did you add or remove data  
- Are there parts of musical taste missing in the dataset  

The dataset, or catalog, has 20 songs in it. For genres, it contains pop, indie pop, lofi, rock, ambient, jazz, synthwave, country, hip hop, r&b, edm, metal, classical, latin, folk, reggae and blues. For moods, it contains happy, chill, intense, relaxed, moody, focused, nostalgic, confident, romantic, euphoric, angry, melancholic, playful, wistful, laid-back and sad. 
I added 10 more and removed none. Each new song has a genre and mood that no other song has.
Yes, most of the genres are Western popular music. With only 20 songs, it is impossible to capture the wide range of musics and cultures around the world. There is also more to music than what we have categorized. Language is one thing, but there is no distinction between instrumental versus vocal. There is no date or era that these songs come from. Some groups of people only want to listen to a defining decade rather than a specific genre or mood.

---

## 5. Strengths  

Where does your system seem to work well  

Prompts:  

- User types for which it gives reasonable results  
- Any patterns you think your scoring captures correctly  
- Cases where the recommendations matched your intuition  


A user who describe their taste through feel, such as upbeat and danceable or calm and acoustic, should be served best, because most of the weight is on mood, energy and valence. 
Every recommendation comes with reasons, so it is easy to see why a song ranked where it did. I think it captures a sense of what the music is given the information at hand. I believe my scoring would have smooth mixing between songs. 
The system seems to make recommendation that match my intuition across different profiles. Given the defualt happy profile, the five songs recommended each have multiple reasons to match the current profile in way of mood, tempo, energy, etc. Even though there aren't many genres with multiple songs in the catalog, they also match intuition. (pop, indie pop, edm rather than genres such as blues or folk)

---

## 6. Limitations and Bias 

Where the system struggles or behaves unfairly. 

Prompts:  

- Features it does not consider  
- Genres or moods that are underrepresented  
- Cases where the system overfits to one preference  
- Ways the scoring might unintentionally favor some users  

Vocals ratio, language, artist popularity, and era were not considered. Almost every genre and mood has a single song. So nearly all are underrepresented in this small 20 song catalog. 
Mood, energy and valence carry 65% of the score, so a listener who cares mostly about genre, such as a jazz fan who likes jazz in any mood, gets weaker matches than a listener who just wants "happy and energetic". Because the next pick follows the current song, a playlist can also drift into a narrow band of similar songs. Though I've also found this to be true with services such as Spotify.
Users whose taste falls in the crowded categories are served better since they will have the largest selection of songs with good scores. The weights, penalties, mood table and song values were chosen by hand and have not been tested on real listeners. So it could also favor those who would score the songs similarly.

---

## 7. Evaluation  

How you checked whether the recommender behaved as expected. 

Prompts:  

- Which user profiles you tested  
- What you looked for in the recommendations  
- What surprised you  
- Any simple tests or comparisons you ran  

No need for numeric metrics unless you created some.

I tested seven profiles built around individual songs: a metal fan, a classical listener, an EDM dancer, the "Sunny Commuter" (indie pop, happy), a chill lofi listener, a focused lofi listener, and a relaxed jazz listener. For each one I checked that the song I expected came out on top, and I had the AI write these as automated tests. I also tested the scoring pieces on their own: a perfect match scores 1, related moods get partial score between 0 and 1, missing preferences are skipped, and the energy-jump and same-artist penalties apply.
I also looked at whether near-misses made sense. For the metal fan, Storm Runner (rock, intense) should rank near the top because its mood is related and its energy is close, even though its genre is different.
The only thing that stood out to me while evaluating the system was that the score did not need to be that high to match the profile reasonably well. The score is between 0 and 1, but many of the recommendations, especially 3rd-5th recs, onyly scored around 0.5. For a sad and gloomy profile I tested, the 3rd recommendation only scored 0.53, but was a wistful folk song that matched energy and valence very well. 
Aside from the tests in the test_recommender.py file, I did some non-specific testing by setting up different profiles in main and subjectively reviewing what the output would look like. 

---

## 8. Future Work  

Ideas for how you would improve the model next.  

Prompts:  

- Additional features or preferences  
- Better ways to explain recommendations  
- Improving diversity among the top results  
- Handling more complex user tastes  

Less of a feature, but it would be nice to expand the catalog to work with a more diverse set of songs in genre, origin, and era. The exisiting mood table could be expanded and something similar could be done for relating similar genres since it is currently fairly black and white.
Recommendation explanations dont need every single property to be communicated, especially when they don't heavilty weigh the score. Currently, explanations only communicate positive score contributions, but could also include when negative points are applied. 
Diversifying the top results could be done by serving songs that contrast single aspects of the profile. Such as songs with a distinctly different genre, but close enough for the other properties. 
Users should be able to have several profiles to accomodate their tastes. Such as study, workout, and dance profiles. They should also be able to set how much each feature matters on their own. Someone who has a dance profile might care a lot more that danceability and tempo properties are met rather than valance or genre. 


---

## 9. Personal Reflection  

A few sentences about your experience.  

Prompts:  

- What you learned about recommender systems  
- Something unexpected or interesting you discovered  
- How this changed the way you think about music recommendation apps  

I learned that it is difficult to make a recommender system that is powerful enough to accomodate such a wide range of users without being too strict, or forfeiting too much control to the user. While giving the user options to adjust, it adds a level of complexity that not everyone wants or needs. 
I thought it was interesting how much the system results relied on the catalog size and type of music inside of it. This makes large streaming services with a near-infinite catalog very strong, but in my experience their music recommendaitons are fairly limited. I would attribute it to the complexity of retaining users and making profits though.
I don't view music recommendation apps very fondly, but I think that is because they encounter some of the same issues I ran into during this exercise. Usually, falling into too narrow of a band for recommendations where there isnt enough variety, but no way to adjust how the recommendations are calculated. 
