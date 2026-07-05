
import os
import re
import json
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

# ---------------- Paths ---------------- #

DATA_DIR = "data"
CLEANED_FILE = os.path.join(DATA_DIR, "cleaned_movies.csv")
FEATURE_MATRIX_FILE = os.path.join(DATA_DIR, "feature_matrix.csv")

# ---------------- Globals (cached after build_model) ---------------- #

movies_df = None
movie_titles = None
similarity_matrix = None

# ---------------- Series / Franchise Helpers ---------------- #

_STOP = {"the", "a", "an"}

def _series_key(title: str, max_words: int = 2) -> str:
    
    if not isinstance(title, str):
        return ""

    t = title.lower()

    # Turn punctuation into spaces, keep letters/numbers/spaces
    t = re.sub(r"[-–:_()]", " ", t)
    t = re.sub(r"[^a-z0-9\s]", " ", t)

    # Remove 'part/episode...' and remove digits
    t = re.sub(r"\b(part|episode)\b.*", "", t)
    t = re.sub(r"\d+", "", t)

    # Collapse spaces
    t = re.sub(r"\s+", " ", t).strip()

    # Remove common articles and keep first max_words
    words = [w for w in t.split() if w not in _STOP]
    return " ".join(words[:max_words])

def _same_series(title1: str, title2: str) -> bool:
    """Return True if the two titles look like the same franchise/series."""
    k1 = _series_key(title1, max_words=2)
    k2 = _series_key(title2, max_words=2)
    return bool(k1 and k2 and (k1 == k2 or k1 in k2 or k2 in k1))

# ---------------- Build Model ---------------- #

def build_model():
    """
    Loads cleaned_movies.csv + feature_matrix.csv,
    computes cosine similarity between movie vectors,
    and precomputes sets (genres/cast/companies) for fast overlap checks.
    """
    global movies_df, movie_titles, similarity_matrix

    movies_df = pd.read_csv(CLEANED_FILE)

    # ---- helpers to parse JSON-like columns into Python sets ---- #
    def parse_json_list(s):
        if pd.isna(s):
            return []
        try:
            return json.loads(s)
        except Exception:
            return []

    def to_lower_set(s):
        return {str(x).strip().lower() for x in parse_json_list(s)}

    movies_df["genre_set"] = movies_df["genres"].apply(to_lower_set)
    movies_df["cast_set"] = movies_df["cast"].apply(to_lower_set)
    movies_df["company_set"] = movies_df["production_companies"].apply(to_lower_set)

    # load vectors and compute cosine similarity
    feature_matrix = pd.read_csv(FEATURE_MATRIX_FILE).values
    similarity_matrix = cosine_similarity(feature_matrix)

    movie_titles = list(movies_df["title"])
    return movie_titles

# ---------------- Recommend ---------------- # 

def recommend_movie(title: str, top_n: int = 20):
    """
    Final score for each candidate movie:

      base_sim       = cosine similarity between LSA vectors
      genre_overlap  = Jaccard overlap o genre sets
      brand_match    = 1 if share any production company
      actor_match    = 1 if share any cast member
      same_series    = 1 if franchise key matches

      final_score = 0.70 * base_sim
                  + 0.15 * genre_overlap
                  + 0.10 * brand_match
                  + 0.05 * actor_match
                  + 0.30 * same_series
    """
    global movies_df, movie_titles, similarity_matrix

    if movie_titles is None or similarity_matrix is None:
        raise ValueError("Model not built yet. Call build_model() first.")

    if title not in movie_titles:
        return []

    idx = movie_titles.index(title)

    base_genres = movies_df.loc[idx, "genre_set"]
    base_cast = movies_df.loc[idx, "cast_set"]
    base_companies = movies_df.loc[idx, "company_set"]

    scores = []

    for j, cand_title in enumerate(movie_titles):
        if j == idx:
            continue
        if not isinstance(cand_title, str) or not cand_title.strip():
            continue

        # 1) cosine similarity
        base_sim = float(similarity_matrix[idx, j])

        # candidate sets
        cand_genres = movies_df.loc[j, "genre_set"]
        cand_cast = movies_df.loc[j, "cast_set"]
        cand_companies = movies_df.loc[j, "company_set"]

        # 2) Jaccard genre overlap
        if base_genres or cand_genres:
            inter = len(base_genres & cand_genres)
            union = len(base_genres | cand_genres)
            genre_overlap = inter / union if union else 0.0
        else:
            genre_overlap = 0.0

        # 3) company + cast matches
        brand_match = 1.0 if (base_companies & cand_companies) else 0.0
        actor_match = 1.0 if (base_cast & cand_cast) else 0.0

        # 4) same franchise
        same_series = 1.0 if _same_series(title, cand_title) else 0.0

        # final score
        final_score = (
            0.70 * base_sim +
            0.15 * genre_overlap +
            0.10 * brand_match +
            0.05 * actor_match +
            0.30 * same_series
        )

        scores.append((cand_title, final_score))

    scores.sort(key=lambda x: x[1], reverse=True)
    return [t for (t, _) in scores[:top_n]]

# ---------------- Utilities ---------------- #

def get_movie_list():
    """Return list of titles (build_model() must be called first)."""
    global movie_titles
    if movie_titles is None:
        raise ValueError("Model is not built yet. Call build_model() first.")
    return movie_titles
