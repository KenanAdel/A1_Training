import pandas as pd
import psycopg2
import json
from psycopg2 import extras
import html

def cleaning_and_inserting():
    dsn = "dbname=BeautifulSoup_not_cleand user=postgres password=kenan123 host=localhost port=5432"
    q = """SELECT * FROM raw_products"""
    with psycopg2.connect(dsn) as con:
            with con.cursor() as cur:
                cur.execute(q)
                result = cur.fetchall()
            con.commit()

    df = pd.DataFrame(result , columns=['id' , 'title' , 'description' , 'price' , 'size' , 'color' , 'sku' , 'category' , 'photo_url' , 'extracted_at'])

    df['price'] = df['price'].astype(float)

    df['title'] = df['title'].str.strip()

    df['size'] = df['size'].replace('NA' , 'no sizes')

    df['color'] = df['color'].replace('NA' , 'no colors')

    df['category'] = df['category'].str.lower().str.replace('category:', '')

    df['description'] = df['description'].apply(html.unescape)

    q = """
    INSERT INTO clean_raw_products (id, title, description, price, size, color, sku, category, photo_url,extracted_at)
    VALUES ( %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)
    ON CONFLICT (id) DO NOTHING;
    """

    data = [tuple(x) for x in df.values]
    with psycopg2.connect(dsn) as con:
            with con.cursor() as cur:
                extras.execute_batch(cur,q,data)
            con.commit()



# cleaning_and_inserting()