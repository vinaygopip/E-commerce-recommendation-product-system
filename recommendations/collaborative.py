"""
Collaborative Filtering Engine
Uses User-Item interaction matrix from UserActivity events (Views, Cart, Wishlist, Purchases, Ratings)
with Item-Item and User-Item collaborative similarity.
"""

import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity
import joblib
from pathlib import Path
from django.conf import settings
from recommendations.models import UserActivity

COLLAB_MODEL_PATH = Path(settings.BASE_DIR) / 'ml_models' / 'collaborative_matrix.pkl'


class CollaborativeFilteringRecommender:
    def __init__(self):
        self.item_sim_df = None
        self.user_item_matrix = None
        self.load_or_train()

    def train(self):
        """Constructs User-Item interaction matrix from activities and calculates Item-Item similarity."""
        activities = UserActivity.objects.filter(product__isnull=False).values(
            'user_id', 'session_key', 'product_id', 'score_weight'
        )

        if not activities.exists():
            return False

        data = []
        for act in activities:
            # User key can be user_id or guest session_key
            u_key = f"u_{act['user_id']}" if act['user_id'] else f"s_{act['session_key']}"
            data.append({
                'user_key': u_key,
                'product_id': act['product_id'],
                'weight': act['score_weight']
            })

        df = pd.DataFrame(data)
        if df.empty:
            return False

        # Group by user and product, summing interaction weights
        interaction_df = df.groupby(['user_key', 'product_id'])['weight'].sum().reset_index()

        # Pivot to create User-Item matrix
        user_item = interaction_df.pivot(index='user_key', columns='product_id', values='weight').fillna(0)
        self.user_item_matrix = user_item

        # Compute Item-Item Cosine Similarity matrix (Item vectors across all users)
        item_vectors = user_item.T # Rows are products, columns are users
        if item_vectors.shape[0] < 2:
            return False

        item_sim = cosine_similarity(item_vectors)
        self.item_sim_df = pd.DataFrame(item_sim, index=item_vectors.index, columns=item_vectors.index)

        # Save to artifacts
        Path(settings.BASE_DIR / 'ml_models').mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'item_sim_df': self.item_sim_df,
            'user_item_matrix': self.user_item_matrix
        }, COLLAB_MODEL_PATH)

        # Also export CSV dataset to datasets/ for academic project evaluation and inspection
        datasets_dir = Path(settings.BASE_DIR) / 'datasets'
        datasets_dir.mkdir(parents=True, exist_ok=True)
        interaction_df.to_csv(datasets_dir / 'user_product_interactions.csv', index=False)

        return True

    def load_or_train(self):
        if COLLAB_MODEL_PATH.exists():
            try:
                data = joblib.load(COLLAB_MODEL_PATH)
                self.item_sim_df = data['item_sim_df']
                self.user_item_matrix = data['user_item_matrix']
                return True
            except Exception:
                pass
        return self.train()

    def get_related_products(self, product_id, top_n=6):
        """Returns products frequently co-interacted with the specified product."""
        if self.item_sim_df is None:
            if not self.load_or_train():
                return []

        if product_id not in self.item_sim_df.index:
            return []

        sim_series = self.item_sim_df.loc[product_id].drop(index=product_id, errors='ignore')
        top_similar = sim_series.sort_values(ascending=False).head(top_n)

        results = [(int(pid), float(score)) for pid, score in top_similar.items() if score > 0.01]
        return results

    def get_user_collaborative_scores(self, user_key, candidate_ids):
        """Predicts collaborative preference scores for candidates given a user's past interaction history."""
        scores = {pid: 0.0 for pid in candidate_ids}
        if self.item_sim_df is None or self.user_item_matrix is None:
            if not self.load_or_train():
                return scores

        if user_key not in self.user_item_matrix.index:
            return scores

        user_vector = self.user_item_matrix.loc[user_key]
        interacted_items = user_vector[user_vector > 0]

        if interacted_items.empty:
            return scores

        for cand_id in candidate_ids:
            if cand_id in self.item_sim_df.columns:
                # Weighted similarity from user's interacted items
                sim_slice = self.item_sim_df.loc[interacted_items.index, cand_id]
                weights = interacted_items.loc[sim_slice.index]
                score = (sim_slice * weights).sum() / (weights.sum() + 1e-5)
                scores[cand_id] = float(score)

        return scores


collaborative_recommender = CollaborativeFilteringRecommender()
