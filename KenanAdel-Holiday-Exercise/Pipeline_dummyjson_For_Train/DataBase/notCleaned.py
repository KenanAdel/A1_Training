import psycopg2

dsn = "dbname=training user=postgres password=kenan123 host=localhost port=5432"
def creat_notCleaned():
    q= """CREATE TABLE IF NOT EXISTS raw_products (
    id INTEGER PRIMARY KEY,
    title TEXT,
    category TEXT,
    price NUMERIC,
    discountPercentage NUMERIC,
    rating NUMERIC,
    stock INTEGER,
    brand TEXT,
    sku TEXT,
    extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);"""
    with psycopg2.connect(dsn) as con:
        with con.cursor() as cur:
            cur.execute(q)
        con.commit()

# creat_notCleaned()