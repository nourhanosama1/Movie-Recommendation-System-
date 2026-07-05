from model import build_model, get_movie_list, recommend_movie

def main():
    # Build the model
    build_model()
    titles = get_movie_list()

    # TEMP: just test from terminal for now
    print("Total movies:", len(titles))
    print("Example title:", titles[0])
    print("\nRecommendations for:", titles[0])
    for rec in recommend_movie(titles[0], top_n=5):
        print("-", rec)

if __name__ == "__main__":
    main()

