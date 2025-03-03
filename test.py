import pytest
from unittest.mock import MagicMock, patch
from collections import defaultdict
from main import User, MongoDBManager, Settings


# Тести для класу User
def test_user_initialization():
    user = User("TestUser")
    assert user.username == "TestUser"
    assert user.watched_movies == []
    assert isinstance(user.genre_counts, defaultdict)
    assert isinstance(user.director_counts, defaultdict)
    assert isinstance(user.actor_counts, defaultdict)


def test_user_add_watched_movie():
    user = User("TestUser")
    movie = {"Title": "Inception", "Genre": "Sci-Fi, Thriller", "Director": "Christopher Nolan",
             "Actors": "Leonardo DiCaprio, Joseph Gordon-Levitt"}
    user.add_watched_movie(movie)

    assert len(user.watched_movies) == 2  # ПОМИЛКА: Очікуваний результат неправильний
    assert user.genre_counts["Sci-Fi"] == 1
    assert user.genre_counts["Thriller"] == 1
    assert user.director_counts["Christopher Nolan"] == 1
    assert user.actor_counts["Leonardo DiCaprio"] == 1
    assert user.actor_counts["Joseph Gordon-Levitt"] == 1


# Тести для класу MongoDBManager
@patch("your_module.MongoClient")
def test_mongodb_connection(mock_mongo_client):
    mock_db = MagicMock()
    mock_mongo_client.return_value["Kino"] = mock_db
    db_manager = MongoDBManager()
    assert db_manager.db == mock_db


def test_get_movies_by_title_start():
    db_manager = MongoDBManager()
    db_manager.collection = MagicMock()
    db_manager.collection.find.return_value = [{"Title": "Inception"}, {"Title": "Inside Out"}]

    movies = db_manager.get_movies_by_title_start("Incep")
    assert len(movies) == 2
    assert movies[0]["Title"] == "Inception"

    db_manager.collection.find.return_value = []
    movies = db_manager.get_movies_by_title_start("Unknown")
    assert movies == []


# Тести для класу Settings
def test_settings_initialization():
    settings = Settings(num_recommendations=10, min_genre_count=5, min_director_count=4, min_actor_count=3,
                        language="Ukrainian")
    assert settings.num_recommendations == 10
    assert settings.min_genre_count == 5
    assert settings.min_director_count == 4
    assert settings.min_actor_count == 3
    assert settings.language == "Ukrainian"


def test_settings_get_labels():
    settings = Settings(language="Ukrainian")
    labels = settings.get_labels()
    assert labels["title_label"] == "Почніть вводити назву фільму:"
    settings.language = "English"
    labels = settings.get_labels()
    assert labels["title_label"] == "Start typing movie title:"
