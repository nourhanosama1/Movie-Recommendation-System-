# convert_tmdb_to_titles.py
# Converts TMDB 5000 Movies + Credits dataset
# into your project's titles.csv and credits.csv format.

import os
import json
import pandas as pd

DATA_DIR = "data"

TMDB_MOVIES = os.path.join(DATA_DIR, "tmdb_movies.csv")
TMDB_CREDITS = os.path.join(DATA_DIR, "tmdb_credits.csv")

OUT_TITLES = os.path.join(DATA_DIR, "titles.csv")
OUT_CREDITS = os.path.join(DATA_DIR, "credits.csv")

def parse_genres(genres_str):
    """Parse TMDB 'genres' JSON-like structure."""
    if pd.isna(genres_str):
        return "[]"
    try:
        data = json.loads(genres_str.replace("'", '"'))
        names = [d["name"] for d in data if "name" in d]
        return json.dumps(names, ensure_ascii=False)
    except:
        return "[]"
def parse_companies(companies_str):
    """Parse TMDB 'production_companies' JSON-like structure."""
    if pd.isna(companies_str):
        return "[]"
    try:
        data = json.loads(companies_str.replace("'", '"'))
        names = [d["name"] for d in data if "name" in d]
        return json.dumps(names, ensure_ascii=False)
    except:
        return "[]"


def extract_cast_credits(df_credits):
    """Build credits.csv with id, cast list, and directors."""
    movie_ids = []
    directors = []
    casts = []

    for _, row in df_credits.iterrows():
        mid = row["movie_id"]
        cast_json = row["cast"]
        crew_json = row["crew"]

        # Extract cast names
        try:
            cast_list = [c["name"] for c in json.loads(cast_json.replace("'", '"'))]
        except:
            cast_list = []

        # Extract directors
        try:
            crew_list = json.loads(crew_json.replace("'", '"'))
            director_names = [c["name"] for c in crew_list if c.get("job") == "Director"]
        except:
            director_names = []

        movie_ids.append(mid)
        casts.append(json.dumps(cast_list))
        directors.append(",".join(director_names))

    return pd.DataFrame({
        "id": movie_ids,
        "cast": casts,
        "director": directors
    })


def main():
    print("Loading TMDB movies...")
    df_movies = pd.read_csv(TMDB_MOVIES)
    print("Loading TMDB credits...")
    df_credits_raw = pd.read_csv(TMDB_CREDITS)

    print("Building titles.csv format...")

    titles = pd.DataFrame()
    titles["id"] = df_movies["id"]
    titles["title"] = df_movies["title"]
    titles["type"] = "MOVIE"
    titles["description"] = df_movies["overview"].fillna("")
    titles["release_year"] = df_movies["release_date"].fillna("").apply(lambda x: int(str(x)[:4]) if str(x)[:4].isdigit() else 0)
    titles["age_certification"] = ""
    titles["runtime"] = df_movies["runtime"].fillna(0)
    titles["genres"] = df_movies["genres"].apply(parse_genres)
    titles["production_countries"] = "[]"
    titles["seasons"] = ""
    titles["production_companies"] = df_movies["production_companies"].apply(parse_companies)
    titles["imdb_id"] = ""
    titles["imdb_score"] = 0
    titles["imdb_votes"] = 0
    titles["tmdb_popularity"] = df_movies["popularity"].fillna(0)
    titles["tmdb_score"] = df_movies["vote_average"].fillna(0)

    print("Saving titles.csv...")
    titles.to_csv(OUT_TITLES, index=False)

    print("Converting credits to internal format...")
    credits_df = extract_cast_credits(df_credits_raw)

    print("Saving credits.csv...")
    credits_df.to_csv(OUT_CREDITS, index=False)

    print("\nDONE!")
    print("New dataset created:")
    print(" - data/titles.csv")
    print(" - data/credits.csv")


if __name__ == "__main__":
    main()
