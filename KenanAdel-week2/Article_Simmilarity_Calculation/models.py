class Article:
    def __init__(self, article_id, title, original_content, cleaned_tokens):
        self.id = article_id
        self.title = title
        self.original_content = original_content
        self.cleaned_tokens = cleaned_tokens
