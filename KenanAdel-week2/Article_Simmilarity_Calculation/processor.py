import csv
import re
from models import Article
## start cleaning and reading articles
class TextProcessor:
    def __init__(self, csv_filepath):
        self.csv_filepath = csv_filepath
        
    def read_and_clean_data(self):
        articles = []
        with open(self.csv_filepath, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cleaned_tokens = self._clean_text(row['content'])
                article = Article(
                    article_id=row['id'],
                    title=row['title'],
                    original_content=row['content'],
                    cleaned_tokens=cleaned_tokens
                )
                articles.append(article)
        return articles
        
    def _clean_text(self, text):
        text = text.lower()
        text = re.sub(r'[^a-z\s]', ' ', text)
        return text.split()
    
## end cleaning and reading articles

