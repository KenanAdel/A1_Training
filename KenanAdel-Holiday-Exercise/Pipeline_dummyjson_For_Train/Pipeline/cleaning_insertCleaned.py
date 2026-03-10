import pandas as pd
import psycopg2
import json
from psycopg2 import extras
import schedule
import time

def cleaning_and_inserting():
    dsn = "dbname=training user=postgres password=kenan123 host=localhost port=5432"
    q = """
    SELECT * FROM raw_products 
    WHERE id NOT IN (SELECT id FROM clean_raw_products)
    """

    with psycopg2.connect(dsn) as con:
            with con.cursor() as cur:
                cur.execute(q)
                result = cur.fetchall()
            con.commit()
    df = pd.DataFrame(result , columns=['id' , 'title' , 'category' , 'price' , 'discount_percentage' , 'rating' , 'stock' , 'brand' , 'sku' , 'extracted_at'])

    df['price'] = df['price'].astype(float)

    df['discount_percentage'] = df['discount_percentage'].astype(float)

    df['rating'] = df['rating'].astype(float)

    df['brand'] = df['brand'].fillna('UNKNOWN_BRAND')

    df['category'] = df['category'].replace({
    "motorcycle" : "motor-cycle",
    "smartphones" : "smart-phones"
    })

    df['priceAfterDiscount'] = (df['price'] * (1 - (df['discount_percentage'].fillna(0) / 100))).round(2)

    cols = ['id' , 'title' , 'category' , 'price' , 'discount_percentage' ,'priceAfterDiscount','rating' , 'stock' , 'brand' , 'sku' , 'extracted_at']

    df = df[cols]

    dsn = "dbname=training user=postgres password=kenan123 host=localhost port=5432"
    q = """
        INSERT INTO clean_raw_products (id, title, category, price, discountPercentage,priceAfterDiscount, rating, stock, brand, sku,extracted_at)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s,%s,%s)
        ON CONFLICT (id) DO NOTHING;
        """
    data = [tuple(x) for x in df.values]

    with psycopg2.connect(dsn) as con:
            with con.cursor() as cur:
                extras.execute_batch(cur,q,data)
            con.commit()

schedule.every(1).hour.do(cleaning_and_inserting)

while True:
    schedule.run_pending()
    time.sleep(1)

# cleaning_and_inserting()