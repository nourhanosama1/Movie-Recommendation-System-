import os
import re
import requests
from PIL import Image
from io import BytesIO
print(">>> poster_fetcher module imported")

TMDB_API_KEY = "1b69d92ccd255b5cb754b5c2b11a9814"

POSTERS_DIR = "posters"
POSTER_SIZE = (150, 220)

os.makedirs(POSTERS_DIR, exist_ok=True)


def title_to_filename(title: str) -> str:
    base = title.lower()
    base = re.sub(r"[^a-z0-9]+", "_", base)
    base = base.strip("_")
    return base + ".jpg"


def fetch_poster(title: str):
    print(">>> fetch_poster called with:", title)
    filename = title_to_filename(title)
    filepath = os.path.join(POSTERS_DIR, filename)

    # 1) Already cached?
    if os.path.exists(filepath):
        print(f"[CACHE] Using existing poster: {filepath}")
        return filepath

    print(f"[TMDB] Searching poster for: {title}")

    url = "https://api.themoviedb.org/3/search/movie"
    params = {
        "api_key": TMDB_API_KEY,
        "query": title
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        print("[TMDB] Status code:", response.status_code)
        if response.status_code != 200:
            print("[TMDB] Error response:", response.text[:300])
            return None
        data = response.json()
    except Exception as e:
        print("[TMDB] Request failed:", e)
        return None

    if "results" not in data or len(data["results"]) == 0:
        print(f"[TMDB] No results for: {title}")
        return None

    poster_path = data["results"][0].get("poster_path")
    if not poster_path:
        print(f"[TMDB] No poster_path for: {title}")
        return None

    img_url = f"https://image.tmdb.org/t/p/w500{poster_path}"
    print("[TMDB] Downloading image from:", img_url)

    try:
        img_data = requests.get(img_url, timeout=10).content
        img = Image.open(BytesIO(img_data))
        img = img.resize(POSTER_SIZE, Image.LANCZOS)
        img.save(filepath)
        print(f"[TMDB] Saved poster to: {filepath}")
        return filepath
    except Exception as e:
        print("[TMDB] Error downloading/saving image:", e)
        return None
