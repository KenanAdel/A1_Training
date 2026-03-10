import requests
import psycopg2
import schedule
import time

dsn = "dbname=training user=postgres password=kenan123 host=localhost port=5432"

## start get latest_id
def get_latest_id():
    q = """SELECT MAX(id) FROM raw_products"""
    with psycopg2.connect(dsn) as con:
        with con.cursor() as cur:
            cur.execute(q)
            result = cur.fetchone()[0]
        con.commit()

        return result if result is not None else 0
## end get latest_id

## start get the data
def get_data():
    last_id = get_latest_id()
    url = "https://dummyjson.com/Products"
    params = {
        'skip': last_id, 
        'limit': 30
    }

    response = requests.get(url, params=params)
    response.raise_for_status()
        
    new_products = response.json()['products']

    if not new_products:
        print("Don't found any new data")
        return []
    
    print(f"There is {len(new_products)} data founded")
    return new_products
## end get the data

## start insert the data to postgres
def insert_data(products):
    query = """
    INSERT INTO raw_products (id, title, category, price, discountPercentage, rating, stock, brand, sku)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
    ON CONFLICT (id) DO NOTHING;
    """
    
    with psycopg2.connect(dsn) as con:
        with con.cursor() as cur:
            for item in products:
                values = (
                    item.get('id'),
                    item.get('title'),
                    item.get('category'),
                    item.get('price'),
                    item.get('discountPercentage'),
                    item.get('rating'),
                    item.get('stock'),
                    item.get('brand'),
                    item.get('sku')
                )
                cur.execute(query, values)
            con.commit()
    print("All new data inserted successfully")
## end insert the data to postgres


def run_all():
    products = get_data()
    if not products:
        print("There is'nt any data ")
    else:
        insert_data(products)


schedule.every(1).minute.do(run_all)

while True:
    schedule.run_pending()
    time.sleep(1)