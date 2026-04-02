# 🎧 Model Card: Music Recommender Simulation

## 1. Model Name  

VibeMatch 1.0

---

## 2. Intended Use  

This recommender suggests songs from a small catalog based on a user's favorite genre, mood, and energy level. It is built for classroom exploration and is not meant for real users or production use.

---

## 3. How the Model Works  

Each song gets a score based on how well it matches the user's preferences. A genre match adds the most points, a mood match adds fewer, and energy similarity adds a small bonus based on how close the song's energy is to what the user wants. The songs are then sorted by score and the top results are returned.

---

## 4. Data  

The catalog has 18 songs across 15 genres including pop, lofi, rock, jazz, metal, classical, and hip-hop. Moods include happy, chill, intense, sad, angry, and romantic. The original starter file had 10 songs and 8 more were added to improve genre diversity. The dataset is small and does not represent the full range of musical taste or culture.

---

## 5. Strengths  

The system works best when the user has a clear genre and mood preference that exists in the catalog. For example, the Chill Lofi profile gets three strong matches because there are multiple lofi songs with matching moods. The scoring is also easy to understand since every recommendation comes with a clear reason like "genre match" or "energy similarity."

---

## 6. Limitations and Bias 

Genre has the most points in the scoring system, so it tends to dominate the results. Users will almost always get recommendations from their favorite genre, even if songs from other genres would be a good fit. This creates a filter bubble where the system keeps recommending the same type of music. Some genres like lofi have more songs in the catalog than others, which means users of those genres get better recommendations. Genre and mood are also exact match only, so closely related genres like pop and indie pop are treated as completely different.

---

## 7. Evaluation  

Three user profiles were tested: High Energy Pop, Chill Lofi, and Intense Rock.

**High Energy Pop vs Chill Lofi**
These two profiles produced completely opposite results. High Energy Pop surfaced bright, fast songs like Sunrise City while Chill Lofi returned quiet, slow songs like Library Rain and Midnight Coding. The genre weight is what drives this split. Since genre is worth the most points, each profile stayed firmly in its own corner of the catalog.

**Chill Lofi vs Intense Rock**
Both profiles got their best genre match at the top of the list, but the Intense Rock profile only had one rock song in the catalog, Storm Runner, which scored a perfect 4.0. Chill Lofi had three lofi songs to fill the top spots. After the genre matches ran out, the Rock profile had to fall back on mood and energy alone, which shows how much the results depend on how many songs exist for each genre.

---

## 8. Future Work  

It would help to add more songs per genre so every user gets meaningful results. The system could also use tempo and valence in the score instead of just genre, mood, and energy. Adding some diversity so the top results are not all the same genre would also make recommendations feel more interesting.

---

## 9. Personal Reflection  

Building this showed how much a simple scoring rule controls what a user sees, and changing one weight can change the entire results. The biggest learning moment was seeing how genre dominance creates a filter bubble without even trying to. AI tools helped with writing and math but the score calculations always needed a double check. It was surprising that just three rules could produce results that actually feel like real recommendations. Next steps would be adding more songs per genre and building the user profile from listening history instead of typed input.
