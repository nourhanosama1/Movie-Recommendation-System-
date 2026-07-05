import os
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.preprocessing import Normalizer
 
DATA_DIR = "data"
titles_path = os.path.join(DATA_DIR, "titles.csv")
credits_path = os.path.join(DATA_DIR, "credits.csv")

out_cleaned = os.path.join(DATA_DIR, "cleaned_movies.csv")
out_matrix = os.path.join(DATA_DIR, "feature_matrix.csv")

print("Loading raw data...")
titles = pd.read_csv(titles_path)
credits = pd.read_csv(credits_path)

print("Merging movies + credits...")
df = titles.merge(credits, on="id", how="left")

# ---------------- Build text for each movie ---------------- #

title = df["title"].fillna("")
description = df["description"].fillna("")
genres = df["genres"].astype(str).fillna("")
cast = df["cast"].astype(str).fillna("")
director = df["director"].astype(str).fillna("")
companies = df["production_companies"].astype(str).fillna("")

# Weighting:
# - description x2
# - genres x3
# - companies x2 (Disney, Pixar, etc.)
# - cast x1
# - director x1
# - title x1
df["features_text"] = (
    description + " " + description + " " +           # description ×2
    genres + " " + genres + " " + genres + " " +      # genres ×3
    companies + " " + companies + " " +               # companies ×2
    cast + " " +
    director + " " +
    title                                             # title ×1
)

df["features_text"] = df["features_text"].fillna("")

print("Vectorizing text with TF-IDF (unigrams + bigrams)...")
vectorizer = TfidfVectorizer(
    stop_words="english",
    max_features=10000,
    ngram_range=(1, 2)
)

tfidf_matrix = vectorizer.fit_transform(df["features_text"])
print("TF-IDF shape:", tfidf_matrix.shape)

# ---------------- LSA (TruncatedSVD) ---------------- #

n_components = 200
print(f"Applying TruncatedSVD to reduce to {n_components} dimensions...")

svd = TruncatedSVD(n_components=n_components, random_state=42)
lsa_matrix = svd.fit_transform(tfidf_matrix)

normalizer = Normalizer(copy=False)
lsa_matrix = normalizer.fit_transform(lsa_matrix)

print("LSA feature matrix shape:", lsa_matrix.shape)

# ---------------- Save outputs ---------------- #

print("Saving cleaned_movies.csv...")
df.to_csv(out_cleaned, index=False)

print("Saving feature_matrix.csv...")
pd.DataFrame(lsa_matrix).to_csv(out_matrix, index=False)

print("\nDONE!")
print(" - data/cleaned_movies.csv updated")
print(" - data/feature_matrix.csv updated (includes companies)")
