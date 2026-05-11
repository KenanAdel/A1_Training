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

        df_branches = df_branches.drop(columns=['location_details'])

        df_users= pd.merge(df_users, df_currencies , left_on='preferred_currency_id',right_on='currency_id', how='left')
        df_users = df_users.drop(columns=['preferred_currency_id','created_at_x'])
        df_users= df_users.rename(columns={'created_at_y': 'created_at'})


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
        df_order_items = pd.merge(df_order_items, df_orders[['order_id' , 'user_id','branch_id']] , on='order_id' , how='left')
        df_order_items = pd.merge(df_order_items,df_orders[['order_id' , 'order_date']] , on= 'order_id' , how='left')
        df_order_items['date_key'] = pd.to_datetime(df_order_items['order_date']).dt.strftime('%Y%m%d').astype(int)
        df_order_items = df_order_items.drop(columns=['order_date'])
    except Exception as e :
        print(f'خطا: {e}')
    return df_users , df_branches,df_product, df_order_items


#this code was written by Kenan Adel
def load_to_dwh_with_type2(df_users , df_branches,df_product,df_order_items):

    try:
        with engine_load.connect() as con:
            max_sk = con.execute(text("SELECT MAX(product_sk) FROM dim_product")).scalar()

        df_product['product_sk'] = range(max_sk + 1, max_sk + 1 + len(df_product))
        df_product.to_sql('stagin_product', engine_load, if_exists='replace', index=False)


        today_str = datetime.now().strftime('%Y%m%d')
        update_query = f"""
        UPDATE dim_product
        SET 
            is_active = False,
            end_date = '{today_str}'
        FROM stagin_product
        WHERE dim_product.product_id = stagin_product.product_id 
            AND dim_product.is_active = True
            AND (
                dim_product.sale_price != stagin_product.sale_price
                OR dim_product.purchase_price != stagin_product.purchase_price
                OR dim_product.category_id != stagin_product.category_id
                OR dim_product.product_name != stagin_product.product_name
                OR dim_product.brand_id != stagin_product.brand_id
                OR dim_product.country_of_origin != stagin_product.country_of_origin
            );
        """

        with engine_load.connect() as con:
            result = con.execute(text(update_query))
            con.commit()
            print(f'Products updated: {result.rowcount}')

        insert_query = f"""
        INSERT INTO dim_product (
            product_sk, product_id, brand_id, category_id, product_name, 
            purchase_price, sale_price, stock_quantity, min_stock_level, 
            category_name, brand_name, country_of_origin, created_at,
            start_date, end_date, is_active
        )
        SELECT
            s.product_sk, s.product_id, s.brand_id, s.category_id, s.product_name, 
            s.purchase_price, s.sale_price, s.stock_quantity, s.min_stock_level, 
            s.category_name, s.brand_name, s.country_of_origin, s.created_at,
            '{today_str}' AS start_date, 
            NULL AS end_date, 
            True AS is_active
        FROM stagin_product s
        LEFT JOIN dim_product d 
            ON s.product_id = d.product_id 
            AND d.is_active = True
        WHERE d.product_id IS NULL;
        """

        with engine_load.connect() as con:
            result_insert = con.execute(text(insert_query))
            con.commit()
            print(f"New products inserted: {result_insert.rowcount}")

        with engine_load.connect() as con:
            con.execute(text("DROP TABLE IF EXISTS stagin_product;"))
            con.commit()
            print("Product staging table dropped")
            print(20 * "--")
    except Exception as e:
        print(f'Error in product: {e}')


    try:
        with engine_load.connect() as con:
            max_sk = con.execute(text('SELECT MAX(user_sk) FROM dim_user')).scalar()
        stagin_sk = range(max_sk +1 , max_sk +1 + len(df_users))
        df_users['user_sk'] = stagin_sk

        df_users.to_sql('stagin_user' , engine_load , if_exists='replace' , index= False)

        today_str = datetime.now().strftime('%Y%m%d')

        update_query = f"""
        UPDATE dim_user
        SET
            is_active = False,
            end_date = '{today_str}'
        FROM stagin_user
        WHERE
            dim_user.user_id = stagin_user.user_id
            AND dim_user.is_active = TRUE
            AND(
                dim_user.full_name != stagin_user.full_name
                OR dim_user.email != stagin_user.email
                OR dim_user.phone != stagin_user.phone
                OR dim_user.address != stagin_user.address
                OR dim_user.currency_code != stagin_user.currency_code
                )
        """

        with engine_load.connect() as con :
            result = con.execute(text(update_query))
            con.commit()
            print(f'Users updated: {result.rowcount}')

        insert_query= f"""
        INSERT INTO dim_user 
            (
                user_sk,user_id,full_name,email,phone,address,
                currency_id,currency_code,currency_name,exchange_rate_to_sar,created_at,
                start_date , end_date, is_active
            )
        SELECT 
            s.user_sk , s.user_id,s.full_name,s.email,
            s.phone,s.address, s.currency_id , s.currency_code, s.currency_name,
            s.exchange_rate_to_sar, s.created_at,
            '{today_str}' AS start_date ,
            NULL AS end_date,
            TRUE AS is_active
        FROM stagin_user s
        LEFT JOIN dim_user d
            ON s.user_id = d.user_id
            AND d.is_active = TRUE
        WHERE d.user_id IS NULL;
        """

        with engine_load.connect() as con:
            result_insert = con.execute(text(insert_query))
            con.commit()
            print(f'New users inserted:  {result_insert.rowcount}')

        with engine_load.connect() as con:
            con.execute(text("DROP TABLE IF EXISTS stagin_user;"))
            con.commit()
            print("User staging table dropped")
            print(20 * "--")
    except Exception as e :
        print(f'Error in user: {e}')


    try:
        with engine_load.connect() as con:
            max_sk = con.execute(text('SELECT MAX(branch_sk) FROM dim_branch')).scalar()

        stagin_sk = range(max_sk +1, max_sk + 1 + len(df_branches))
        df_branches['branch_sk'] = stagin_sk
        df_branches.to_sql('stagin_branch' , engine_load , if_exists='replace' , index=False)

        today_str = datetime.now().strftime('%Y%m%d')

        update_query = f"""
        UPDATE dim_branch
        SET
            is_active = False,
            end_date = '{today_str}'

        FROM stagin_branch
        WHERE 
            dim_branch.branch_id = stagin_branch.branch_id
            AND dim_branch.is_active = TRUE
            AND
            (
                dim_branch.branch_name != stagin_branch.branch_name
                OR dim_branch.city != stagin_branch.city
                OR dim_branch.manager_name != stagin_branch.manager_name
            )
        """

        with engine_load.connect() as con:
            result = con.execute(text(update_query))
            con.commit()
            print(f'Branches updated: {result.rowcount}')

        insert_query = f"""
        INSERT INTO dim_branch(
            branch_sk , branch_id , branch_name,
            city , manager_name , created_at ,
            start_date , end_date, is_active
        )

        SELECT
            s.branch_sk , s.branch_id,s.branch_name,
            s.city, s.manager_name , s.created_at,
            {today_str} AS start_date  ,
            NULL AS end_date ,
            True AS  is_active 
        FROM stagin_branch s
        LEFT JOIN dim_branch d
            ON d.branch_id = s.branch_id
            AND d.is_active = TRUE
        WHERE d.branch_id IS NULL;
        """

        with engine_load.connect() as con:
            result_insert = con.execute(text(insert_query))
            con.commit()
            print(f'New branches inserted:  {result_insert.rowcount}')
            

        with engine_load.connect() as con:
            con.execute(text('DROP TABLE IF EXISTS stagin_branch;'))
            con.commit()
            print("Branch staging table dropped")
            print(20 * "--")
    except Exception as e :
        print(f'Error in branch: {e}')


#this code was written by Kenan Adel
def load_fact_sales(df_order_items):
    try:
        df_order_items.to_sql('stagin_fact_sales', engine_load, if_exists='replace', index=False)

        insert_query = """
        INSERT INTO fact_sales (
            order_id, order_item_id, product_sk, user_sk, branch_sk, date_key,
            quantity, line_subtotal_sar, line_purchase_sar, line_tax_sar, line_profit_sar, status
        )
        SELECT 
            s.order_id, s.order_item_id, 
            p.product_sk, u.user_sk, b.branch_sk, 
            s.date_key, s.quantity, s.line_subtotal_sar, 
            s.line_purchase_sar, s.line_tax_sar, s.line_profit_sar, s.status
        FROM stagin_fact_sales s
        LEFT JOIN dim_product p ON s.product_id = p.product_id AND p.is_active = True
        LEFT JOIN dim_user u    ON s.user_id = u.user_id       AND u.is_active = True
        LEFT JOIN dim_branch b  ON s.branch_id = b.branch_id   AND b.is_active = True
        WHERE NOT EXISTS (
            SELECT 1 FROM fact_sales f WHERE f.order_item_id = s.order_item_id
        );
        """
        
        with engine_load.connect() as con:
            result_insert = con.execute(text(insert_query))
            con.commit()
            print(f'New Fact Table inserted:  {result_insert.rowcount}')
    

        with engine_load.connect() as con:
            con.execute(text('DROP TABLE IF EXISTS stagin_fact_sales;'))
            con.commit()
            print('stagin fact sales table dropped')
            print(20 * "--")

    except Exception as e:
        print(f"Error in fact: {e}")


#this code was written by Kenan Adel
def run_etl_pipeline():
    try:
        df_orders, df_order_items, df_users, df_product, df_categories, df_brands, df_branches, df_currencies = get_data_from_DB()

        df_users_dim, df_branches_dim, df_product_dim, df_order_items_fact = transform_data(
            df_orders, df_order_items, df_users, df_product, 
            df_categories, df_brands, df_branches, df_currencies
        )

        load_to_dwh_with_type2(
            df_users_dim, 
            df_branches_dim, 
            df_product_dim, 
            df_order_items_fact 
        )
        
        load_fact_sales(df_order_items_fact)
        
        print("ETL Pipeline executed successfully")
        print(20 * "--")

    except Exception as e:
        print(f"Error in run_Pipeline: {e}")


# run_etl_pipeline()