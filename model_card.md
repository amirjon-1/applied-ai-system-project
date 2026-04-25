# Model Card: VibeFinderAI 2.0

---

## 1. Model Name

**VibeFinderAI 2.0**

Successor to VibeMatch 1.0 (rule-based, Modules 1–3). The 2.0 release adds semantic retrieval and AI-generated explanations.

---

## 2. Intended Use

VibeFinderAI 2.0 is a personal music discovery assistant for natural language queries. A user types a description of how they feel or what activity they are doing — *"something slow and melancholic for a rainy evening"* or *"aggressive gym music"* — and the system returns three song recommendations with plain-English explanations and a confidence rating for each pick.

The system is intended for individual, casual use as a learning prototype. It is not designed for production deployment, does not personalize over time, and does not connect to any streaming service or external music catalog.

---

## 3. How It Works

VibeFinderAI 2.0 has two cooperating layers.

**Layer 1 — Semantic Retrieval (RAG)**

Every song in the catalog is converted into a short text phrase that combines its genre, mood, and energy level — for example, *"lofi chill energy 0.42"*. A small language model called `all-MiniLM-L6-v2` (from the sentence-transformers library) reads each of those phrases and turns it into a list of numbers, called an embedding, that captures its meaning. When a user submits a query, the same model turns the query into an embedding and the system finds the songs whose embeddings are numerically closest to the query. Songs that are conceptually similar — not just keyword-identical — rank highly. This retrieval step returns the top ten candidates.

**Layer 2 — AI Agent Reasoning (Gemini)**

The ten candidates and the original user query are handed to Google's Gemini 2.0 Flash language model. Gemini reads the full list and reasons about which three are the best fit. For each of its three picks it writes one or two sentences explaining the choice in plain language, assigns a confidence score between 0 and 1 to reflect how certain it is, and flags any pick it is unsure about. The response is required to come back as structured JSON so that the application can parse it reliably.

**Fallback**

If the Gemini call fails for any reason — network error, malformed output, quota limit — the system quietly falls back to the original rule-based scorer from VibeMatch 1.0. It scores every candidate on genre, mood, and energy match, returns the top three, and marks all of them as uncertain. The failure is written to the session log but no error is shown to the user.

---

## 4. Data

The catalog is `data/songs.csv`, a hand-curated file of **18 songs**. The original starter file shipped with 10 songs and 8 more were added to improve genre diversity during the Module 1–3 phase.

**Genres represented:** pop, lofi, rock, ambient, jazz, synthwave, indie pop, classical, hip-hop, r&b, country, metal, reggae, blues, electronic

**Moods represented:** happy, chill, intense, focused, relaxed, moody, melancholic, confident, romantic, nostalgic, angry, uplifting, sad, dreamy

**Numeric features per song:** `energy` (0–1), `tempo_bpm`, `valence` (0–1), `danceability` (0–1), `acousticness` (0–1)

**Limitations of the data:**
- 18 songs is an extremely small catalog. Most genres have only one or two representatives, so recommendation diversity is structurally limited.
- All songs are fictional with invented artist names. The catalog does not reflect any real chart, era, or cultural moment.
- Genre and mood labels were assigned by the project author and reflect one person's categorization conventions.
- The catalog skews toward English-language Western genres. Non-Western traditions — Afrobeats, K-pop, cumbia, qawwali, etc. — are completely absent.
- No demographic data was collected and no real listening history informed which songs were included.

---

## 5. Strengths

**Semantic understanding.** The RAG layer finds musically relevant songs even when the user's phrasing shares no exact words with catalog labels. A query like *"music for a 3am drive"* can surface synthwave and ambient songs without any rule encoding that relationship.

**Natural language queries.** Users are not required to know the catalog's genre or mood vocabulary. Any freeform description can serve as input, lowering the barrier compared to the original `UserProfile` struct.

**Explainability.** Every recommendation comes with a generated explanation that connects the song's attributes to the user's query in plain language. This is more useful than a numeric score because it tells the user *why* a song fits, not just *how much*.

**Self-reported uncertainty.** Gemini flags recommendations it is not confident about. The `[UNCERTAIN]` tag in the output lets users calibrate their trust rather than treating every pick as equally authoritative.

**Graceful fallback.** The system never returns an error to the user. If the AI layer fails, the rule-based scorer takes over silently, ensuring the application always produces output.

---

## 6. Limitations and Bias

**Small catalog.** With only 18 songs, the retriever often surfaces the same small set of candidates across different queries. Results for less common genres — blues, reggae, classical — will be weak because there is only one song per genre.

**English-only queries.** The embedding model was trained primarily on English text. Non-English queries may embed poorly and produce irrelevant retrievals. The catalog itself contains no non-English songs, compounding this limitation.

**Western music bias.** The catalog covers genres almost entirely from North American and European traditions. Users looking for music from other cultural contexts will find nothing relevant.

**LLM hallucination risk.** Gemini generates explanations based on the structured song attributes it is given, but it is a generative model and may produce descriptions that sound plausible but do not accurately reflect the song. It cannot listen to the music; it only reads metadata.

**No long-term personalization.** The system does not learn from a user's past interactions. Each session starts from scratch. Two users with completely different tastes receive recommendations driven entirely by their query text, not any history.

**Genre and mood label brittleness.** The RAG embeddings are built from the catalog's genre and mood labels. If a song was labeled inconsistently (e.g., tagging an energetic track as "chill"), the embedding will mislead the retriever.

**Catalog size limits retrieval quality.** Requesting `k=10` candidates from an 18-song catalog means more than half of all songs are always retrieved regardless of semantic relevance. Gemini then selects from this large fraction, reducing the value of the retrieval step.

---

## 7. Evaluation

**Test suite**

Five automated tests in `tests/test_ai_system.py` cover the new components:

| Test | Result |
|---|---|
| RAG retriever returns exactly K results | Pass |
| Fallback triggers when Gemini raises an exception (mocked) | Pass |
| Fallback triggers when Gemini returns invalid JSON (mocked) | Pass |
| Confidence scores are floats in [0.0, 1.0] | Pass |
| Log file is written to disk | Pass |
| Full pipeline (RAG + mocked agent) returns non-empty results for 3 hardcoded queries | Pass |

All six test cases pass. The Gemini model itself is mocked in every test that calls the agent so the suite runs offline and does not require a live API key.

**Manual evaluation**

Three representative queries were tested against the live system:

- *"something chill to study late at night"* — retrieved lofi and ambient tracks; Gemini correctly identified them as study-appropriate and explained the energy and tempo rationale.
- *"aggressive and fast for the gym"* — retrieved metal, pop-intense, and rock tracks; confidence scores were high (0.83–0.97), matching expectation.
- *"feeling nostalgic and a little melancholic tonight"* — retrieved country, blues, and classical; Gemini flagged the classical pick as uncertain, which was appropriate given the weaker semantic connection to "nostalgic."

The fallback path was tested by temporarily revoking the API key; the system returned rule-based results with `uncertain=True` on all three picks and logged the fallback event, as expected.

---

## 8. AI Collaboration

**Instance where AI gave a helpful suggestion**

During development of the Gemini prompt, the initial draft asked the model to return recommendations in a plain numbered list. The model's outputs were readable but inconsistent in format — sometimes including extra commentary, sometimes returning Markdown, sometimes changing field names between calls. On suggestion from Claude (used as a coding assistant), the prompt was restructured to include an explicit JSON schema example and the instruction "Respond ONLY with valid JSON — no markdown, no extra text." This change made the outputs reliably parseable and reduced the fallback trigger rate in manual testing from roughly one-in-five calls to zero across ten consecutive tests.

**Instance where AI gave a flawed suggestion**

When designing the fallback logic, Claude initially suggested using the user's natural language query to extract genre and mood keywords via a second LLM call, then building a structured `UserProfile` from those keywords to pass into the rule-based scorer. The intention was to make the fallback smarter. In practice this was the wrong approach: the fallback exists precisely because the AI layer is unavailable or unreliable. Adding another LLM call inside the fallback path defeats the entire purpose — if Gemini is down, a keyword-extraction call to the same service will also fail. The suggestion was rejected in favor of a simple neutral `UserProfile` (target energy 0.5, empty genre and mood) that always works without any AI dependency.

---

## 9. Future Work

**Larger catalog.** The most impactful single improvement would be a real music dataset — even a few thousand tracks would give the retriever enough variety to surface meaningfully different candidates for different queries. Public datasets like the Million Song Dataset or FMA (Free Music Archive) are natural candidates.

**User listening history.** The current system is stateless. Adding a lightweight preference model — even just tracking which recommendations a user accepts or skips — would allow the system to personalize over time without requiring an explicit profile setup.

**Multi-modal features.** Song metadata is a proxy for the actual audio experience. Incorporating audio embeddings (e.g., from a model trained on mel-spectrograms) would let the retriever match on sonic texture — timbre, instrumentation, rhythm feel — rather than relying on text labels that are inherently imprecise.

**Query refinement loop.** Rather than a single-shot query → recommendations flow, the agent could ask one clarifying question when a query is ambiguous (e.g., *"Did you mean energetic electronic or something more mellow?"*) before committing to picks. This is a natural extension of the agentic pattern already in place.

**Structured confidence calibration.** The current confidence scores come from Gemini's self-report, which is not calibrated against any ground truth. A future version could compare Gemini's confidence scores against held-out user ratings to measure whether high-confidence picks actually satisfy users at a higher rate than low-confidence ones.
