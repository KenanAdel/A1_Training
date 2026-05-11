import pandas as pd 
import sqlalchemy
from sqlalchemy import create_engine,text
from datetime import datetime

engine = create_engine('postgresql://postgres:kenan123@localhost:5432/hi_DB')
engine_load = create_engine("postgresql://postgres:kenan123@localhost:5432/hi_DWH")

#this code was written by Kenan Adel
def get_data_from_DB():
    query = "SELECT * FROM orders"
    query_order_item = "SELECT * FROM order_items"
    query_customer = "SELECT * FROM users"
    query_products = "SELECT * FROM products"
    query_categories = "SELECT * FROM categories"
    query_brands = "SELECT * FROM brands"
    query_branches = "SELECT * FROM branches"
    query_currencies = "SELECT * FROM currencies"

    try:
        with engine.connect() as con:
            df_orders = pd.read_sql(text(query) , con)

        with engine.connect() as con:
            df_order_items = pd.read_sql(text(query_order_item) , con)

        with engine.connect() as con:
            df_users = pd.read_sql(text(query_customer), con)

        with engine.connect() as con:
            df_product = pd.read_sql(text(query_products), con)

        with engine.connect() as con:
            df_categories = pd.read_sql(text(query_categories) , con)

        with engine.connect() as con:
            df_brands = pd.read_sql(text(query_brands) , con)


        with engine.connect() as con:
            df_branches = pd.read_sql(text(query_branches) , con)

        with engine.connect() as con:
            df_currencies = pd.read_sql(text(query_currencies) , con)
    except Exception as e:
        print(f"Error : {e}")

    return df_orders , df_order_items , df_users, df_product, df_categories, df_brands,df_branches,df_currencies


#this code was written by Kenan Adel
def transform_data(df_orders , df_order_items , df_users, df_product, df_categories, df_brands,df_branches,df_currencies):
    try:
        df_product = pd.merge(df_product , df_categories, on='category_id', how='left')
        df_product = pd.merge(df_product, df_brands , on='brand_id' , how='left')
        df_product = df_product.drop(columns=['parent_category_id','created_at_x'])
        df_product= df_product.rename(columns={'created_at_y': 'created_at'})
        df_product['product_sk'] = range(1, len(df_product) +1)
        new = df_product.pop('product_sk')
        df_product.insert(0 , 'product_sk' , new)
        df_product['start_date'] = datetime.now().strftime('%Y%m%d')
        df_product['end_date'] = None
        df_product['is_active'] = True

        df_branches = df_branches.drop(columns=['location_details'])
        df_branches['branch_sk'] = range(1 , len(df_branches)+1)
        new = df_branches.pop('branch_sk')
        df_branches.insert(0 , 'branch_sk' , new)
        df_branches['start_date'] = datetime.now().strftime('%Y%m%d')
        df_branches['end_date'] = None
        df_branches['is_active'] = True

        df_users= pd.merge(df_users, df_currencies , left_on='preferred_currency_id',right_on='currency_id', how='left')
        df_users = df_users.drop(columns=['preferred_currency_id','created_at_x'])
        df_users= df_users.rename(columns={'created_at_y': 'created_at'})
        df_users['user_sk'] = range(1 , len(df_users) +1)
        new = df_users.pop('user_sk')
        df_users.insert(0, 'user_sk', new)
        df_users['start_date'] = datetime.now()
        df_users['end_date'] = None
        df_users['is_active'] = True

        df_orders = pd.merge(df_orders , df_currencies,on='currency_id' , how='left')
        df_orders['order_date'] = df_orders['order_date'].dt.date
        mask = df_orders['total_amount'] * df_orders['exchange_rate_to_sar']
        df_orders['amount_after_echange'] = mask
        new =df_orders.pop('amount_after_echange')
        df_orders.insert(12,'amount_after_echange',new)

        start_date = "2021-01-01"
        end_date = "2026-12-30"
        date = pd.date_range(start=start_date , end=end_date , freq='D')
        df_dim_date= pd.DataFrame(date , columns=['date'])
        df_dim_date['date_key'] = df_dim_date['date'].dt.strftime('%Y%m%d').astype(int)
        df_dim_date['year'] = df_dim_date['date'].dt.year
        df_dim_date['month'] = df_dim_date['date'].dt.month
        df_dim_date['day'] = df_dim_date['date'].dt.day
        df_dim_date['day_name'] = df_dim_date['date'].dt.day_name()
        df_dim_date['month_name'] = df_dim_date['date'].dt.month_name()
        df_dim_date['quarter'] = df_dim_date['date'].dt.quarter
        df_dim_date['is_weekend'] = df_dim_date['date'].dt.dayofweek.isin([4, 5])
        df_dim_date['week_of_year'] = df_dim_date['date'].dt.isocalendar().week

        df_order_items = pd.merge(df_order_items,df_orders[['order_id','subtotal','tax_amount','status','exchange_rate_to_sar']], on='order_id', how='left')
        mask = df_order_items['unit_sale_price'] *df_order_items['quantity'] / df_order_items['subtotal'] * df_order_items['tax_amount']
        df_order_items['tax_line'] = mask
        new = df_order_items.pop('tax_line')
        df_order_items.insert(8,'tax_line',new)
        df_order_items['line_subtotal_sar'] = (df_order_items['unit_sale_price'] * df_order_items['quantity']) * df_order_items['exchange_rate_to_sar']
        df_order_items['line_purchase_sar'] = (df_order_items['unit_purchase_price'] * df_order_items['quantity']) * df_order_items['exchange_rate_to_sar']
        df_order_items['line_tax_sar'] = df_order_items['tax_line'] * df_order_items['exchange_rate_to_sar']
        df_order_items['line_profit_sar'] = df_order_items['line_subtotal_sar'] - df_order_items['line_purchase_sar']
        df_order_items = df_order_items.drop(columns=['subtotal','tax_amount','exchange_rate_to_sar','unit_sale_price','unit_purchase_price','tax_line'])
        df_order_items = pd.merge(df_order_items , df_product[['product_id' , 'product_sk']] , on='product_id', how='left')
        new = df_order_items.pop('product_sk')
        df_order_items.insert(2 , 'product_sk' , new)
        df_order_items= df_order_items.drop(columns=['product_id'])
        df_orders = pd.merge(df_orders, df_users[['user_id', 'user_sk']] , on='user_id' , how='left')
        df_order_items = pd.merge(df_order_items, df_orders[['order_id' , 'user_sk']] , on='order_id' , how='left')
        new = df_order_items.pop('user_sk')
        df_order_items.insert(2, 'user_sk' ,new)
        df_orders = pd.merge(df_orders , df_branches[['branch_id' , 'branch_sk']] , on='branch_id' , how='left')
        df_order_items = pd.merge(df_order_items , df_orders[['order_id' , 'branch_sk']] , on='order_id' , how='left')
        new = df_order_items.pop('branch_sk')
        df_order_items.insert(4 , 'branch_sk' , new)
        df_order_items = pd.merge(df_order_items,df_orders[['order_id' , 'order_date']] , on= 'order_id' , how='left')
        df_order_items['date_key'] = pd.to_datetime(df_order_items['order_date']).dt.strftime('%Y%m%d').astype(int)
        new = df_order_items.pop('date_key')
        df_order_items.insert(2 , 'date_key' , new)
        df_order_items = df_order_items.drop(columns=['order_date'])
    except Exception as e :
        print(f'Error: {e}')
    return df_users , df_branches,df_product, df_dim_date , df_order_items


#this code was written by Kenan Adel
def load_to_dwh(df_users , df_branches,df_product,df_dim_date,df_order_items):
    try:
        df_users.to_sql('dim_user',engine_load , if_exists='replace' , index=False)
        df_branches.to_sql('dim_branch' , engine_load , if_exists='replace', index=False)
        df_product.to_sql('dim_product' , engine_load , if_exists='replace', index= False)
        df_dim_date.to_sql('dim_date' , engine_load , if_exists='replace' , index= False)
        df_order_items.to_sql('fact_sales',engine_load, if_exists='replace' , index=False)
        with engine_load.connect() as con:
            con.execute(text('ALTER TABLE dim_user ADD PRIMARY KEY (user_sk);'))
            con.execute(text("ALTER TABLE dim_product ADD PRIMARY KEY (product_sk);"))
            con.execute(text("ALTER TABLE dim_branch ADD PRIMARY KEY (branch_sk);"))
            con.execute(text("ALTER TABLE dim_date ADD PRIMARY KEY (date_key);"))
            con.execute(text("""
                    ALTER TABLE fact_sales 
                    ADD CONSTRAINT fk_product FOREIGN KEY (product_sk) REFERENCES dim_product (product_sk),
                    ADD CONSTRAINT fk_user FOREIGN KEY (user_sk) REFERENCES dim_user (user_sk),
                    ADD CONSTRAINT fk_branch FOREIGN KEY (branch_sk) REFERENCES dim_branch (branch_sk),
                    ADD CONSTRAINT fk_date FOREIGN KEY (date_key) REFERENCES dim_date (date_key);
                """))
            con.commit()
        with engine_load.connect() as con:
            con.execute(text("CREATE INDEX idx_fact_product_sk ON fact_sales (product_sk);"))
            con.execute(text("CREATE INDEX idx_fact_user_sk ON fact_sales (user_sk);"))
            con.execute(text("CREATE INDEX idx_fact_branch_sk ON fact_sales (branch_sk);"))
            con.execute(text("CREATE INDEX idx_fact_date_key ON fact_sales (date_key);"))
            con.execute(text("CREATE INDEX idx_fact_status ON fact_sales (status);"))
            con.execute(text("CREATE INDEX idx_dim_product_id ON dim_product (product_id);"))
            con.execute(text("CREATE INDEX idx_dim_user_id ON dim_user (user_id);"))
            con.commit()
    except Exception as e:
        print(f'Error : {e}')


#this code was written by Kenan Adel
def run_etl_pipeline():
    try:
        df_orders, df_order_items, df_users, df_product, df_categories, df_brands, df_branches, df_currencies = get_data_from_DB()

        df_users_dim, df_branches_dim, df_product_dim, df_dim_date, df_order_items_fact = transform_data(
            df_orders, 
            df_order_items, 
            df_users, 
            df_product, 
            df_categories, 
            df_brands, 
            df_branches, 
            df_currencies
        )

        load_to_dwh(
            df_users_dim, 
            df_branches_dim, 
            df_product_dim, 
            df_dim_date, 
            df_order_items_fact
        )

    except Exception as e:
        print(f"Error : {e}")

# run_etl_pipeline()