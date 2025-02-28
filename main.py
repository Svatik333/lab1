import tkinter as tk
from tkinter import messagebox, ttk, scrolledtext
from pymongo import MongoClient, errors
from collections import defaultdict

class User:
    """Клас для представлення користувача"""
    def __init__(self, username="DefaultUser"):
        self.username = username
        self.watched_movies = []
        self.genre_counts = defaultdict(int)
        self.director_counts = defaultdict(int)
        self.actor_counts = defaultdict(int)

    def add_watched_movie(self, movie):
        """Додає фільм до переглянутих і оновлює вподобання"""
        self.watched_movies.append(movie)
        for genre in movie['Genre'].split(','):
            self.genre_counts[genre.strip()] += 1
        self.director_counts[movie['Director'].strip()] += 1
        for actor in movie['Actors'].split(','):
            self.actor_counts[actor.strip()] += 1

class MongoDBManager:
    def __init__(self):
        try:
            self.client = MongoClient("mongodb+srv://Sviatiy:h4IcKVQwXmbPIgwp@kino.glfs69y.mongodb.net/?retryWrites=true&w=majority&appName=Kino")
            self.db = self.client['Kino']
            self.collection = self.db['movies']
        except errors.ConnectionError as e:
            print("Error connecting to MongoDB: ", e)
            raise

    def get_movies_by_title_start(self, title_start):
        regex_pattern = f"^{title_start}"
        try:
            return list(self.collection.find({"Title": {"$regex": regex_pattern, "$options": "i"}}))
        except errors.PyMongoError as e:
            print("Error querying MongoDB: ", e)
            return []

class Settings:
    def __init__(self, num_recommendations=5, min_genre_count=3, min_director_count=3, min_actor_count=3, language='English'):
        self.num_recommendations = num_recommendations
        self.min_genre_count = min_genre_count
        self.min_director_count = min_director_count
        self.min_actor_count = min_actor_count
        self.language = language

    def get_labels(self):
        labels = {
            'English': {
                'title_label': "Start typing movie title:",
                'add_button': "Add to Watched",
                'recommend_button': "Recommend",
                'settings_button': "Settings",
                'quit_button': "QUIT",
                'num_recommendations': "Number of Recommendations:",
                'min_genre_count': "Minimum Genre Count:",
                'min_director_count': "Minimum Director Count:",
                'min_actor_count': "Minimum Actor Count:",
                'save_button': "Save",
                'language': "Language:"
            },
            'Ukrainian': {
                'title_label': "Почніть вводити назву фільму:",
                'add_button': "Додати до переглянутих",
                'recommend_button': "Рекомендувати",
                'settings_button': "Налаштування",
                'quit_button': "ВИЙТИ",
                'num_recommendations': "Кількість рекомендацій:",
                'min_genre_count': "Мінімальна кількість жанрів:",
                'min_director_count': "Мінімальна кількість режисерів:",
                'min_actor_count': "Мінімальна кількість акторів:",
                'save_button': "Зберегти",
                'language': "Мова:"
            }
        }
        return labels[self.language]

class Application(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.pack()
        self.settings = Settings()
        self.create_widgets()

    def create_widgets(self):
        labels = self.settings.get_labels()

        self.title_label = tk.Label(self, text=labels['title_label'])
        self.title_label.pack()

        self.title_entry = ttk.Combobox(self, width=60)
        self.title_entry.pack()
        self.title_entry.bind('<KeyRelease>', self.update_movie_list)

        self.watch_button = tk.Button(self, text=labels['add_button'], command=self.add_to_watched)
        self.watch_button.pack()

        self.recommend_button = tk.Button(self, text=labels['recommend_button'], command=self.recommend_movies)
        self.recommend_button.pack()

        self.text_area = scrolledtext.ScrolledText(self, width=70, height=20)
        self.text_area.pack()

        self.settings_button = tk.Button(self, text=labels['settings_button'], command=self.open_settings)
        self.settings_button.pack()

        self.quit_button = tk.Button(self, text=labels['quit_button'], fg="red", command=self.master.destroy)
        self.quit_button.pack()

    def update_movie_list(self, event):
        title_start = self.title_entry.get()
        movies = db.get_movies_by_title_start(title_start)
        self.title_entry['values'] = [movie['Title'] for movie in movies]

    def add_to_watched(self):
        title = self.title_entry.get()
        movie = [m for m in db.get_movies_by_title_start(title) if m['Title'] == title]
        if movie:
            user.add_watched_movie(movie[0])
            messagebox.showinfo("Movie Added", f"Added {movie[0]['Title']} to watched list")
        else:
            messagebox.showerror("Error", "Select a movie from the list")

    def recommend_movies(self):
        self.text_area.delete('1.0', tk.END)
        self.recommend_by_genre()
        self.recommend_by_director()
        self.recommend_by_actor()

    def recommend_by_genre(self):
        """Рекомендації за жанром з детальною інформацією і сортуванням по рейтингу"""
        for genre, count in user.genre_counts.items():
            if count >= self.settings.min_genre_count:
                genre_movies = list(db.collection.find({'Genre': {'$regex': f'.*{genre}.*', '$options': 'i'}}))
                genre_movies = [movie for movie in genre_movies if movie['_id'] not in [m['_id'] for m in user.watched_movies]]
                genre_movies.sort(key=lambda x: x['Rating'], reverse=True)
                self.text_area.insert(tk.END, f"\nRecommended Movies in Genre '{genre}':\n")
                for movie in genre_movies[:self.settings.num_recommendations]:
                    self.text_area.insert(tk.END, f"- {movie['Title']} ({movie['Year']}), Rating: {movie['Rating']}\n")

    def recommend_by_director(self):
        """Рекомендації за режисером"""
        for director, count in user.director_counts.items():
            if count >= self.settings.min_director_count:
                director_movies = list(db.collection.find({'Director': director}))
                director_movies = [movie for movie in director_movies if movie['_id'] not in [m['_id'] for m in user.watched_movies]]
                director_movies.sort(key=lambda x: x['Rating'], reverse=True)
                self.text_area.insert(tk.END, f"\nMovies Directed by '{director}':\n")
                for movie in director_movies[:self.settings.num_recommendations]:
                    self.text_area.insert(tk.END, f"- {movie['Title']} ({movie['Year']}), Rating: {movie['Rating']}\n")

    def recommend_by_actor(self):
        """Рекомендації за актором"""
        for actor, count in user.actor_counts.items():
            if count >= self.settings.min_actor_count:
                actor_movies = list(db.collection.find({'Actors': {'$regex': f'.*{actor}.*', '$options': 'i'}}))
                actor_movies = [movie for movie in actor_movies if movie['_id'] not in [m['_id'] for m in user.watched_movies]]
                actor_movies.sort(key=lambda x: x['Rating'], reverse=True)
                self.text_area.insert(tk.END, f"\nMovies Featuring Actor '{actor}':\n")
                for movie in actor_movies[:self.settings.num_recommendations]:
                    self.text_area.insert(tk.END, f"- {movie['Title']} ({movie['Year']}), Rating: {movie['Rating']}\n")

    def open_settings(self):
        settings_window = tk.Toplevel(self)
        settings_window.title("Settings")

        labels = self.settings.get_labels()

        tk.Label(settings_window, text=labels['num_recommendations']).grid(row=0, column=0, sticky='w')
        num_recommendations = tk.Entry(settings_window)
        num_recommendations.insert(0, str(self.settings.num_recommendations))
        num_recommendations.grid(row=0, column=1)

        tk.Label(settings_window, text=labels['min_genre_count']).grid(row=1, column=0, sticky='w')
        min_genre_count = tk.Entry(settings_window)
        min_genre_count.insert(0, str(self.settings.min_genre_count))
        min_genre_count.grid(row=1, column=1)

        tk.Label(settings_window, text=labels['min_director_count']).grid(row=2, column=0, sticky='w')
        min_director_count = tk.Entry(settings_window)
        min_director_count.insert(0, str(self.settings.min_director_count))
        min_director_count.grid(row=2, column=1)

        tk.Label(settings_window, text=labels['min_actor_count']).grid(row=3, column=0, sticky='w')
        min_actor_count = tk.Entry(settings_window)
        min_actor_count.insert(0, str(self.settings.min_actor_count))
        min_actor_count.grid(row=3, column=1)

        tk.Label(settings_window, text=labels['language']).grid(row=4, column=0, sticky='w')
        language = ttk.Combobox(settings_window, values=['English', 'Ukrainian'])
        language.set(self.settings.language)
        language.grid(row=4, column=1)

        def save_settings():
            self.settings.num_recommendations = int(num_recommendations.get())
            self.settings.min_genre_count = int(min_genre_count.get())
            self.settings.min_director_count = int(min_director_count.get())
            self.settings.min_actor_count = int(min_actor_count.get())
            self.settings.language = language.get()
            settings_window.destroy()
            self.refresh_ui()

        save_button = tk.Button(settings_window, text=labels['save_button'], command=save_settings)
        save_button.grid(row=5, column=0, columnspan=2)

    def refresh_ui(self):
        labels = self.settings.get_labels()

        self.title_label.config(text=labels['title_label'])
        self.watch_button.config(text=labels['add_button'])
        self.recommend_button.config(text=labels['recommend_button'])
        self.settings_button.config(text=labels['settings_button'])
        self.quit_button.config(text=labels['quit_button'])

root = tk.Tk()
root.title("movie recommender")
db = MongoDBManager()
user = User("DefaultUser")
app = Application(master=root)
app.mainloop()
