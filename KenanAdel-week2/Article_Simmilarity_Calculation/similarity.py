import numpy as np
import pickle
from models import Article

class SimilarityModel:
    def __init__(self, articles):
        self.articles = articles
        self.global_vocab = set()
        self.global_vocab_list = []
        self.vector_matrix = None
        self.similarity_matrix = None

### start Extract all unique words from all articles to form a dictionary
    def build_vocabulary(self):
        for article in self.articles:
            for token in article.cleaned_tokens:
                self.global_vocab.add(token)
                
        self.global_vocab_list = sorted(list(self.global_vocab))
### end Extract all unique words from all articles to form a dictionary

### start Converting texts  into vectors so that the machine can understand them
    def generate_vectors(self):
        if not self.global_vocab_list:
            self.build_vocabulary()
            
        vectors = []
        for article in self.articles:
            article_words = set(article.cleaned_tokens)
            
            vec = [1 if word in article_words else 0 for word in self.global_vocab_list]
            vectors.append(vec)
            
        self.vector_matrix = np.array(vectors, dtype=float)
### end Converting texts  into vectors so that the machine can understand them

### start calculates the similarity between each article and all other articles
    def calculate_cosine_similarity(self):
        if self.vector_matrix is None:
            self.generate_vectors()
            
        dot_products = np.dot(self.vector_matrix, self.vector_matrix.T)
        norms = np.linalg.norm(self.vector_matrix, axis=1)
        norms_matrix = np.outer(norms, norms)
        
        self.similarity_matrix = dot_products / (norms_matrix + 1e-9) #Ebselon
### end calculates the similarity between each article and all other articles

### start Store final results to save time
    def save_similarities(self, filename='similarities.pkl'):
        if self.similarity_matrix is None:
            self.calculate_cosine_similarity()
            
        with open(filename, 'wb') as f:
            pickle.dump(self.similarity_matrix, f)
### end Store final results to save time

### start takes the article ID number and returns the 3 most similar articles
    def get_top_3_similar_articles(self, article_id):
        if self.similarity_matrix is None:
            raise ValueError("Similarity matrix has not been calculated yet")
            
        target_idx = -1
        for idx in range(len(self.articles)):
            if str(self.articles[idx].id) == str(article_id):
                target_idx = idx
                break
                
        if target_idx == -1:
            raise ValueError(f"Article with id '{article_id}' not found")
            
        similarities = self.similarity_matrix[target_idx]
        sorted_indices = np.argsort(similarities)[::-1]
        
        top_3_results = []
        for idx in sorted_indices:
            if idx == target_idx:
                continue 
                
            title = self.articles[idx].title
            similarity_percentage = similarities[idx] * 100 
            top_3_results.append((title, similarity_percentage)) 
            
            if len(top_3_results) == 3:
                break
                
        return top_3_results
### end takes the article ID number and returns the 3 most similar articles