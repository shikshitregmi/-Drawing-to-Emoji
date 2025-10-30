import json
import numpy as np
from sklearn.neighbors import NearestNeighbors
from sklearn.feature_extraction.text import TfidfVectorizer
import os


class EmojiMatcher:
    def __init__(self, emoji_db_path="assets/emoji_database.json"):
        self.emoji_db_path = emoji_db_path
        self.emojis = {}
        self.categories = set()
        self.vectorizer = None
        self.knn_model = None
        self.feature_vectors = None
        self._load_emoji_database()
        self._train_model()

    def _load_emoji_database(self):
        """Load emoji database from JSON file"""
        try:
            with open(self.emoji_db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.emojis = data['emojis']

            # Extract categories and prepare training data
            self.categories = set(emoji_data['category'] for emoji_data in self.emojis.values())

        except FileNotFoundError:
            print(f"Emoji database not found at {self.emoji_db_path}")
            self.emojis = {}

    def _train_model(self):
        """Train the KNN model for emoji matching"""
        if not self.emojis:
            return

        # Prepare training data: combine all keywords for each emoji
        emoji_descriptions = []
        self.emoji_list = []

        for emoji, data in self.emojis.items():
            description = ' '.join(data['keywords'])
            emoji_descriptions.append(description)
            self.emoji_list.append(emoji)

        # Create TF-IDF vectors
        self.vectorizer = TfidfVectorizer(stop_words='english', max_features=1000)
        self.feature_vectors = self.vectorizer.fit_transform(emoji_descriptions).toarray()

        # Train KNN model
        self.knn_model = NearestNeighbors(n_neighbors=5, metric='cosine')
        self.knn_model.fit(self.feature_vectors)

    def text_to_emoji(self, text, top_k=5):
        """Convert text to matching emojis"""
        if not text or not self.knn_model:
            return ["❓"] * top_k

        # Transform input text
        text_vector = self.vectorizer.transform([text]).toarray()

        # Find nearest neighbors
        distances, indices = self.knn_model.kneighbors(text_vector, n_neighbors=top_k)

        # Get matching emojis
        matching_emojis = [self.emoji_list[i] for i in indices[0]]
        return matching_emojis

    def get_emoji_by_category(self, category):
        """Get all emojis in a specific category"""
        return [emoji for emoji, data in self.emojis.items() if data['category'] == category]

    def get_emoji_info(self, emoji):
        """Get information about a specific emoji"""
        return self.emojis.get(emoji, {"keywords": [], "category": "unknown"})

    def search_emojis(self, query):
        """Search emojis by keyword"""
        matching_emojis = []
        for emoji, data in self.emojis.items():
            if any(query.lower() in keyword.lower() for keyword in data['keywords']):
                matching_emojis.append(emoji)
        return matching_emojis

    def get_all_categories(self):
        """Get all available categories"""
        return sorted(self.categories)