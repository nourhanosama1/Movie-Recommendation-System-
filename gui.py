# gui.py

import os
import tkinter as tk
from PIL import Image, ImageTk

from model import build_model, recommend_movie
from poster_fetcher import fetch_poster


# ----------------- Build model & load titles ----------------- #

print("Building recommendation model...")
titles = build_model()
cleaned_titles = [t for t in titles if isinstance(t, str) and t.strip()]
ALL_MOVIES = sorted(cleaned_titles)
print("Movies loaded:", len(ALL_MOVIES))


# ----------------- GUI Setup ----------------- #

window = tk.Tk()
window.title("🎬 Movie Recommendation System")
window.geometry("1000x720")
window.configure(bg="#0d0d0d")


# ----------------- Main Card ----------------- #

card = tk.Frame(window, bg="#1a1a1a", padx=30, pady=30)
card.pack(fill="both", expand=True, padx=20, pady=20)


# ----------------- Title ----------------- #

tk.Label(
    card,
    text="🍿 Movie Recommendation System",
    font=("Segoe UI", 26, "bold"),
    bg="#1a1a1a",
    fg="#e50914"
).pack(pady=(0, 10))

tk.Label(
    card,
    text="Search for a movie, then get similar recommendations with posters",
    font=("Segoe UI", 14),
    bg="#1a1a1a",
    fg="#bbbbbb"
).pack(pady=(0, 20))


# ----------------- Search Bar ----------------- #

search_frame = tk.Frame(card, bg="#1a1a1a")
search_frame.pack(anchor="center", pady=(0, 5))

tk.Label(
    search_frame,
    text="🔎 Search Movie:",
    font=("Segoe UI", 14, "bold"),
    bg="#1a1a1a",
    fg="white"
).pack(side="left", padx=(0, 10))

search_var = tk.StringVar()
selected_movie = tk.StringVar()

search_entry = tk.Entry(
    search_frame,
    textvariable=search_var,
    font=("Segoe UI", 12),
    width=50
)
search_entry.pack(side="left")


# ----------------- Suggestions ----------------- #

suggestions_listbox = tk.Listbox(
    card,
    height=6,
    width=50,
    font=("Segoe UI", 11),
    bg="#111111",
    fg="white",
    selectbackground="#e50914",
    activestyle="none",
    borderwidth=0,
    highlightthickness=1,
    highlightbackground="#333333"
)
suggestions_listbox.pack(pady=(0, 15))


# ----------------- Button ----------------- #

recommend_btn = tk.Button(
    card,
    text="🎥 Recommend Similar Movies",
    font=("Segoe UI", 13, "bold"),
    bg="#e50914",
    fg="white",
    activebackground="#b20710",
    relief=tk.FLAT,
    padx=25,
    pady=8
)
recommend_btn.pack(pady=10)


status_label = tk.Label(
    card,
    text="Type a movie name to see suggestions.",
    font=("Segoe UI", 11),
    bg="#1a1a1a",
    fg="#bbbbbb"
)
status_label.pack(pady=(5, 0))


# ----------------- Posters Area ----------------- #

posters_container = tk.Frame(card, bg="#1a1a1a")
posters_container.pack(fill="both", expand=True, pady=20)

posters_canvas = tk.Canvas(
    posters_container,
    bg="#1a1a1a",
    highlightthickness=0
)
posters_canvas.pack(side="left", fill="both", expand=True)

scrollbar = tk.Scrollbar(
    posters_container,
    orient="vertical",
    command=posters_canvas.yview
)
scrollbar.pack(side="right", fill="y")

posters_canvas.configure(yscrollcommand=scrollbar.set)

posters_frame = tk.Frame(posters_canvas, bg="#1a1a1a")
posters_window = posters_canvas.create_window(
    (0, 0),
    window=posters_frame,
    anchor="nw"
)


def update_scroll_region(event):
    posters_canvas.configure(scrollregion=posters_canvas.bbox("all"))


def resize_posters_frame(event):
    posters_canvas.itemconfig(posters_window, width=event.width)


posters_frame.bind("<Configure>", update_scroll_region)
posters_canvas.bind("<Configure>", resize_posters_frame)

poster_images_cache = []


# ----------------- Logic ----------------- #

def update_suggestions():
    query = search_var.get().strip().lower()
    suggestions_listbox.delete(0, tk.END)

    for w in posters_frame.winfo_children():
        w.destroy()

    if not query:
        selected_movie.set("")
        status_label.config(text="Type a movie name to see suggestions.")
        return

    matches = [t for t in ALL_MOVIES if query in t.lower()]

    if not matches:
        status_label.config(text=f"No movies found for '{search_var.get()}'")
        return

    for t in matches[:15]:
        suggestions_listbox.insert(tk.END, t)

    status_label.config(text=f"Found {len(matches)} result(s). Click one to select.")


def on_suggestion_click(event):
    if not suggestions_listbox.curselection():
        return
    title = suggestions_listbox.get(suggestions_listbox.curselection()[0])
    search_var.set(title)
    selected_movie.set(title)
    status_label.config(text=f"Selected: {title}")


def on_search_key(event):
    if event.keysym == "Return":
        if suggestions_listbox.size() > 0:
            suggestions_listbox.selection_set(0)
            title = suggestions_listbox.get(0)
            search_var.set(title)
            selected_movie.set(title)
            status_label.config(text=f"Selected: {title}")
        return
    update_suggestions()


def show_recommendations():
    global poster_images_cache
    movie = selected_movie.get() or search_var.get()

    for w in posters_frame.winfo_children():
        w.destroy()
    poster_images_cache = []

    if not movie or movie not in ALL_MOVIES:
        status_label.config(text="Please choose a movie from the suggestions.")
        return

    recommend_btn.config(state="disabled")
    status_label.config(text=f"Getting recommendations for: {movie}")
    window.update_idletasks()

    recs = recommend_movie(movie, top_n=20)

    max_per_row = 5
    for idx, title in enumerate(recs):
        r, c = divmod(idx, max_per_row)

        card_frame = tk.Frame(posters_frame, bg="#111111", padx=10, pady=10)
        card_frame.grid(row=r, column=c, padx=10, pady=10)

        tk.Label(
            card_frame,
            text=title,
            font=("Segoe UI", 11, "bold"),
            bg="#111111",
            fg="white",
            wraplength=160,
            justify="center"
        ).pack(pady=(0, 8))

        poster = fetch_poster(title)
        if poster and os.path.exists(poster):
            img = Image.open(poster).resize((160, 240))
            photo = ImageTk.PhotoImage(img)
            poster_images_cache.append(photo)
            tk.Label(card_frame, image=photo, bg="#111111").pack()
        else:
            tk.Label(
                card_frame,
                text="No poster available",
                font=("Segoe UI", 10),
                bg="#111111",
                fg="gray"
            ).pack(pady=20)

    for i in range(max_per_row):
        posters_frame.grid_columnconfigure(i, weight=1)

    status_label.config(text=f"Showing recommendations for: {movie}")
    recommend_btn.config(state="normal")


# ----------------- Bindings ----------------- #

search_entry.bind("<KeyRelease>", on_search_key)
suggestions_listbox.bind("<<ListboxSelect>>", on_suggestion_click)
recommend_btn.config(command=show_recommendations)

window.mainloop()