import pandas as pd
import requests
from bs4 import BeautifulSoup
import datetime


def scrap_data():
    baseurl = "https://quotes.toscrape.com/page/1/"
    data = []
    url = baseurl
    couunt = 1
    while url :
        response = requests.get(url)
        soup = BeautifulSoup(response.content , "html.parser")
        quotes = soup.find_all('div' , class_= 'quote')

        for quote in quotes:
            title = quote.find('span' , class_ = 'text').text.replace("“" , "").replace("”", "")
            title_condition = title if title else None
            author = quote.find('small' , class_ = 'author').text
            author_condition = author if author else None
            tags_elements = quote.find_all('a', class_='tag')
            tags= [ t.text for t in tags_elements]
            tags_condition = tags if tags else None
            

            data.append({
                'title' : title_condition,
                'author': author_condition,
                'tags' : tags_condition
            })
        next_page = soup.find("li", class_="next")
        url = f"https://quotes.toscrape.com/page/{couunt}/" if next_page else None
        couunt+=1
    return data

def clean_save_data(data):
    df = pd.DataFrame(data)
    df = df.dropna(subset=['tags'])
    df['scraped_at'] = pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')
    df['scraped_at'] = pd.to_datetime(df['scraped_at'])
    file_path = '/usr/local/bin/data.json'
    df.to_json(file_path ,indent=4 , orient='records')



if __name__ == "__main__":
    extracted_data = scrap_data()
    clean_save_data(extracted_data)

