"""
Content-Based Recommendation Engine
Uses TF-IDF Vectorization and Cosine Similarity on product metadata
(Category, Brand, Title, Description, and Features/Keywords).
"""

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import joblib
import warnings
from sklearn.exceptions import InconsistentVersionWarning
warnings.filterwarnings("ignore", category=InconsistentVersionWarning)
from pathlib import Path
from django.conf import settings
from products.models import Product

MODEL_PATH = Path(settings.BASE_DIR) / 'ml_models' / 'content_based_matrix.pkl'
VECTORIZER_PATH = Path(settings.BASE_DIR) / 'ml_models' / 'tfidf_vectorizer.pkl'


class ContentBasedRecommender:
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.product_ids = []
        self.id_to_idx = {}
        self.idx_to_id = {}
        self.load_or_train()

    def _prepare_corpus(self, products):
        """Creates a combined rich text representation for each product."""
        corpus = []
        ids = []
        for p in products:
            cat_name = p.category.name if p.category else ""
            brand_name = p.brand.name if p.brand else ""
            features = p.features or ""
            desc = p.description or ""
            name = p.name or ""
            
            # Weight important terms by repeating key attributes
            text = f"{name} {name} {cat_name} {cat_name} {brand_name} {features} {desc}"
            corpus.append(text)
            ids.append(p.id)
        return corpus, ids

    def train(self):
        """Fits TF-IDF on all active products in the database and caches the similarity matrix."""
        products = list(Product.objects.filter(is_active=True).select_related('category', 'brand'))
        if not products:
            return False

        corpus, ids = self._prepare_corpus(products)
        self.product_ids = ids
        self.id_to_idx = {pid: idx for idx, pid in enumerate(ids)}
        self.idx_to_id = {idx: pid for idx, pid in enumerate(ids)}

        self.vectorizer = TfidfVectorizer(
            stop_words='english',
            ngram_range=(1, 2),
            max_features=5000,
            sublinear_tf=True
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
        
        # Compute pairwise cosine similarity matrix
        sim_matrix = cosine_similarity(self.tfidf_matrix, self.tfidf_matrix)

        # Save artifacts
        Path(settings.BASE_DIR / 'ml_models').mkdir(parents=True, exist_ok=True)
        joblib.dump({
            'sim_matrix': sim_matrix,
            'product_ids': self.product_ids,
            'id_to_idx': self.id_to_idx,
            'idx_to_id': self.idx_to_id
        }, MODEL_PATH)
        joblib.dump(self.vectorizer, VECTORIZER_PATH)
        return True

    def load_or_train(self):
        """Loads cached model or trains if cache doesn't exist."""
        if MODEL_PATH.exists() and VECTORIZER_PATH.exists():
            try:
                data = joblib.load(MODEL_PATH)
                self.sim_matrix = data['sim_matrix']
                self.product_ids = data['product_ids']
                self.id_to_idx = data['id_to_idx']
                self.idx_to_id = data['idx_to_id']
                self.vectorizer = joblib.load(VECTORIZER_PATH)
                return True
            except Exception:
                pass
        return self.train()

    def get_similar_products(self, product_id, top_n=6):
        """Returns product IDs and similarity scores for a specific product."""
        if not hasattr(self, 'sim_matrix') or self.sim_matrix is None:
            if not self.load_or_train():
                return []

        if product_id not in self.id_to_idx:
            # New product not yet in index, retrain
            self.train()
            if product_id not in self.id_to_idx:
                return []

        idx = self.id_to_idx[product_id]
        sim_scores = list(enumerate(self.sim_matrix[idx]))
        
        # Sort by similarity descending, skipping itself
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        results = []
        for i, score in sim_scores:
            if i != idx and score > 0.05:
                results.append((self.idx_to_id[i], float(score)))
            if len(results) >= top_n:
                break
        return results

    def get_content_scores_for_products(self, target_product_ids, candidate_ids):
        """Calculates aggregated content similarity scores for candidate products given target product IDs."""
        if not hasattr(self, 'sim_matrix') or self.sim_matrix is None:
            if not self.load_or_train():
                return {pid: 0.0 for pid in candidate_ids}

        scores = {pid: 0.0 for pid in candidate_ids}
        valid_targets = [pid for pid in target_product_ids if pid in self.id_to_idx]
        if not valid_targets:
            return scores

        for target_id in valid_targets:
            target_idx = self.id_to_idx[target_id]
            for cand_id in candidate_ids:
                if cand_id in self.id_to_idx and cand_id != target_id:
                    cand_idx = self.id_to_idx[cand_id]
                    sim = self.sim_matrix[target_idx][cand_idx]
                    if sim > scores[cand_id]:
                        scores[cand_id] = float(sim)
        return scores

    def get_similar_products_by_text(self, query_text, top_n=6, min_score=0.12):
        """Finds most similar products in catalog for any raw search string using TF-IDF cosine similarity."""
        if not query_text or not hasattr(self, 'vectorizer') or self.vectorizer is None or self.tfidf_matrix is None:
            if not self.load_or_train():
                return []
        
        try:
            import re
            tokens = [t for t in re.findall(r'\w+', query_text.lower()) if len(t) > 2 and t not in {'item', 'product', 'products', 'the', 'and', 'for', 'with', 'best', 'buy', 'online'}]
            if not tokens:
                return []

            query_vec = self.vectorizer.transform([query_text])
            if query_vec.nnz == 0:
                return []

            # If multi-word query (3+ tokens), require at least 2 matching vocabulary tokens
            if len(tokens) >= 3 and query_vec.nnz < 2:
                return []

            sim_scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
            ranked_indices = sim_scores.argsort()[::-1]
            
            results = []
            for idx in ranked_indices:
                score = float(sim_scores[idx])
                if score >= min_score and idx in self.idx_to_id:
                    results.append((self.idx_to_id[idx], round(score, 3)))
                if len(results) >= top_n:
                    break
            return results
        except Exception:
            return []


content_recommender = ContentBasedRecommender()
