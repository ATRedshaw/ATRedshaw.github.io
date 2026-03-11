If you’ve ever tried to decide what film to watch with other people you know it’s a diplomatic nightmare. I built WhirlWatch to solve that. On the surface it’s a full-stack web application for creating shared TV and film watchlists. Under the hood it’s a practical exercise in turning a massive, highly unpredictable Large Language Model into a reliable structured data engine. 

I didn't want to build just another toy app that acts as a thin wrapper around a chat window. I wanted to see what it takes to use an LLM to drive actual product logic, complete with database lookups, entity matching and collaborative filtering.

![Suggestions page input section](assets/images/projects/whirlwatch/suggestions-input.png)
_Figure: The AI suggestions input interface. Users filter by genre, media type and language while the LLM handles the semantic search on the 80 character free text input._

![The resulting suggestions list, showing the matched title, poster image and metadata for each recommendation](/assets/images/projects/whirlwatch/suggestions-output.png)
_Figure: The resulting suggestions list, showing the matched title, poster image and metadata for each recommendation. All data is pulled directly from TMDB via the verified title match, ensuring the LLM's hallucinations never make it to the user._

## Wrangling the LLM: The Recommendation Pipeline

This is where the actual data science and engineering comes in. The problem with LLMs is that they are notorious liars. If you ask one for a film recommendation it might give you a brilliant, highly relevant answer. It might also hallucinate a sequel that doesn't exist or slightly mangle the title. 

If you pass a mangled title directly into a database like TMDB (The Movie Database) you get zero results and the user gets an empty screen. The pipeline I built fixes this.

The flow looks like this:
`User query → Groq LLM (llama-3.1-8b-instant) → JSON title list → fuzzy match → TMDB lookup → enriched results`

### Forcing Structured Output
First comes the prompt engineering. I treat the LLM strictly as a data generation function rather than a chatbot. The system prompt gives it a persona ("MovieSage") but more importantly it strictly enforces a JSON-only output format:

```json[
  {"Name": "<Title 1>", "Type": "Movie" | "TV"}
]
```
I pass context variables like `genre_hint`, `max_items` and `language` directly into the system prompt. If the model spits out markdown, pleasantries or anything that isn't a valid JSON array then the pipeline breaks. Thankfully Llama-3.1 is remarkably good at following these constraints.

### Fuzzy Matching: Bridging AI and Reality
Once the LLM gives me a list of titles I have to verify them. This is where the pipeline gets put to the test. I take every JSON object and run it against TMDB's search API. 

Because of the LLM hallucination issue ("Blade Runner" vs "Blade Runner 2049" or weird punctuation) the first TMDB result isn't always the right one. I run the returned TMDB titles against the original LLM-generated title using `RapidFuzz` and score them based on token ratios.

```python
ratio = fuzz.ratio(item["Name"].lower(), result[title_field].lower())
if best_match and highest_ratio >= 60:
    best_match["media_type"] = media_type
    results.append(best_match)
```

By enforcing a 60% match threshold I filter out the absolute nonsense. Only the best match per title survives. The frontend never sees the raw LLM output. It only sees real TMDB-verified titles with correct poster images and metadata. It effectively turns a probabilistic text generator into a deterministic API.

## The Relational Headache of Group Opinions

Building the data model was surprisingly tricky. The naive approach to a watchlist is to have a `MediaInList` table and just slap a rating column on it. 

That falls apart the second you introduce shared lists. If I share a list with three mates we all need our own rating for the same film and we need to be able to average those ratings out to see the group's consensus. 

To solve this I completely decoupled media membership from user ratings.

![Data model diagram](/assets/images/projects/whirlwatch/ER-diagram.png)
_Figure: The entity relationship diagram. Decoupling UserMediaRating from MediaInList prevents data duplication while allowing for complex group aggregations._

The core entities are:
*   **Media:** The canonical record (just a TMDB ID and media type).
*   **MediaList & SharedList:** Who owns what and who has access.
*   **UserMediaRating:** A user's personal watch status and rating for a specific film which is entirely independent of any list.

When someone adds a film to a shared list the backend quietly generates blank `UserMediaRating` rows for everyone in that group. When you want the average group rating for a film the Flask backend runs a query aggregating the scores of every user who has access to that specific list. It’s clean, it avoids data duplication and it makes cross-referencing watch statuses trivial.

## The Rest of the Stack

While the AI pipeline is the star of the show it is wrapped in a proper production-ready full-stack application.

*   **Backend:** Python, Flask, SQLAlchemy and deployed on PythonAnywhere.
*   **Frontend:** React 18, Tailwind CSS and hosted on Render.
*   **Auth:** JWT-based access and refresh tokens.

I also built a "Roulette" feature. At its core it is a highly customisable constraint-satisfaction query. You can filter the random spin by media type, specific users who added the film or watch statuses. You can even set it to only pick titles that are strictly marked as 'unwatched' by every single person in the group. Wrapping that logic in a spinning roulette-wheel UI makes resolving the inevitable "what do we watch?" argument significantly more fun.

## Hindsight and Next Steps

There are two glaring things I'd change if I were to rewrite this tomorrow.

First is the fact that the TMDB proxy adds noticeable latency. When you load a list of 20 items the backend hits the TMDB API 20 times in sequence to grab the latest metadata. It’s slow. I need to implement proper caching or batch those requests. 

Second is the 60% fuzzy match threshold in the AI pipeline. I chose 60% based entirely on intuition and trial-and-error. It works fine in practice but spoken like a true data scientist: it's not rigorous. A proper test set of known-bad LLM outputs mapped to their correct TMDB targets would let me optimise that threshold properly rather than relying on a lucky guess.