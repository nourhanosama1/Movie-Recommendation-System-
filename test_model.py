from model import build_model, recommend_movie

def main():
    titles = build_model()
    print("Total movies loaded:", len(titles))

    print("\nFirst 5 movies:")
    for t in titles[:5]:
        print("-", t)

    print("\nTesting recommendations for:", titles[0])
    recs = recommend_movie(titles[0], top_n=5)
    print("\nRecommendations:")
    for r in recs:
        print("-", r)

if __name__ == "__main__":
    main()
