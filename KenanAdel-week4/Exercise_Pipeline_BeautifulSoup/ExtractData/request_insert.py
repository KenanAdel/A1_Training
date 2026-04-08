import requests
from bs4 import BeautifulSoup
import psycopg2



dsn = "dbname=BeautifulSoup_not_cleand user=postgres password=kenan123 host=localhost port=5432"
base_url= "https://www.scrapingcourse.com/ecommerce/page/1/"

def request():
    raw_products = []
    url = base_url
    current_page = 1

    while url and current_page < 13:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        products = soup.find_all('li', class_='product')


        for product in products:
            title = product.find('h2', class_='woocommerce-loop-product__title').text.strip()
            price = product.find('span', class_='woocommerce-Price-amount').text.replace('$', '').replace(',', '').strip()
            photo_url = product.find('img', class_='attachment-woocommerce_thumbnail')['src']

            ## لينك البرودكت مهم عشان نقدر نجيب الديسكريبشن والسكيو والكيتجوري والالوان والسايز
            product_link = product.find('a', class_='woocommerce-LoopProduct-link')['href']

            product_page = requests.get(product_link)
            product_soup = BeautifulSoup(product_page.text, "html.parser")

            ## هنا جبت الوصف عشان اقدر اشيل منها كلمة ديسكريبشن اللي بتتكرر في كل المنتجات
            description_div = product_soup.find('div', id='tab-description')
            description = description_div.get_text(separator="\n", strip=True)
            description = description.replace("Description", "").strip() if description else ""

            ## جبت السايز والالوان في حالة وجودهم لان مش كل المنتجات فيها سايزات او الوان
            size = product_soup.find('select', id='size')
            if size:
                options = size.find_all('option')[1:]
                sizes_list = [opt.text.strip() for opt in options]
                size_string = ", ".join(sizes_list)
            else:
                size_string = "NA"


            color = product_soup.find('select', id='color')
            if color:
                color_options = color.find_all('option')[1:]
                colors_list = [c.text.strip() for c in color_options]
                colors_string = ", ".join(colors_list)
            else:
                colors_string = "NA"

            sku = product_soup.find('span', class_='sku').text.strip() if product_soup.find('span', class_='sku') else "NA"

            category = product_soup.find('span', class_='posted_in').text.strip() if product_soup.find('span', class_='posted_in') else "NA"

            raw_products.append({
                "title": title,
                "description": description,
                "price": price,
                "size": size_string,
                "color": colors_string,
                "sku": sku,
                "category": category,
                "photo_url": photo_url
            })

        ## هنا بعمل ابديت للرابط عشان يروح للصفحة اللي بعدها لو موجودة
        next_page = soup.find('a', class_='next')
        current_page += 1
        url = f"https://www.scrapingcourse.com/ecommerce/page/{current_page}/" if next_page else None

    return raw_products


def insert_to_db(raw_products):
    query = """
    INSERT INTO raw_products (title, description, price, size, color, sku, category, photo_url)
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """

    with psycopg2.connect(dsn) as con:
        with con.cursor() as cur:
            for product in raw_products:
                cur.execute(query, (
                    product['title'],
                    product['description'],
                    product['price'],
                    product['size'],
                    product['color'],
                    product['sku'],
                    product['category'],
                    product['photo_url']
                ))
            con.commit()


def run_all():
    raw_products = request()
    insert_to_db(raw_products)


# run_all()