from fastapi import FastAPI
import json
import os
from datetime import datetime

app = FastAPI()
DATA_FILE = "/usr/local/bin/data.json"

def get_data():
    with open(DATA_FILE, 'r') as file:
        data = json.load(file)
        for row in data:
            if "scraped_at" in row:
                row["scraped_at"] = datetime.fromtimestamp(float(row["scraped_at"]) / 1000).strftime('%Y-%m-%d %H:%M:%S')
        return data

@app.get("/")
def home():
    return {
        "welcome": "Hey Welcome in KenanPKG_Api",
        "step_1": "/quotes for all quotes",
        "step_2": "/authors for all authors",
        "step_3": "/quotes/tag/tag_name",
        "step_4": "/quotes/author/author_name"
    }


@app.get("/quotes")
def get_all_quotes_by_author():
    data = get_data()
    return data

@app.get("/authors")
def get_authors_only():
    data = get_data()

    authors_list = set([row['author'] for row in data if row['author']])
    return {"authors": list(authors_list)}


@app.get("/quotes/tag/{tag_name}")
def get_quotes_by_specific_tag(tag_name: str):
    data = get_data()
    
    results = [
        {
            "title": row["title"], 
            "author": row["author"],
            "tags": row["tags"]
        } 
        for row in data 
        if row["tags"] and tag_name.lower() in [t.lower() for t in row["tags"]]
    ]
    
    if not results:
        return "sorry no Tags with this name"
    
    return results


@app.get("/quotes/author/{author_name}")
def get_quotes_by_author(author_name: str):
    data = get_data()
    
    results = [
        {
            "title": row["title"], 
            "author": row["author"],
            "tags": row["tags"]
        } 
        for row in data 
        if row["author"] and author_name.lower() in row["author"].lower()
    ]
    
    if not results:
        return "sorry no author with this name"
    
    return results