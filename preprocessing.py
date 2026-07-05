import pandas as pd
from poster_fetcher import fetch_poster


def preprocess_movies(input_csv: str, output_csv: str):
    """
    Cleans movie data and (optionally) fetches posters.
    """
    print(">>> Loading movie data...")
    df = pd.read_csv(input_csv)

    # Basic cleaning
    print(">>> Cleaning text fields...")
    df["title"] = df["title"].fillna("").str.strip()
    df["overview"] = df["overview"].fillna("").str.strip()
    df["genres"] = df["genres"].fillna("").astype(str)

    # OPTIONAL: fetch posters (remove this block if you don't want posters here)
    print(">>> Fetching posters...")
    df["poster_path"] = df["title"].apply(fetch_poster)

    print(">>> Saving cleaned data to:", output_csv)
    df.to_csv(output_csv, index=False)
    print(">>> Preprocessing complete.")
