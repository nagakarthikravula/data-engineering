import psycopg2
import random
from datetime import datetime, timedelta
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

DB_CONFIG = {
    'host': 'localhost',
    'database': 'practice_db',
    'user': 'postgres',
    'password': 'postgres'
}

INDIAN_NAMES = [
    'Arjun Sharma', 'Priya Patel', 'Rahul Kumar',
    'Sneha Reddy', 'Vikram Singh', 'Ananya Iyer',
    'Rohan Gupta', 'Pooja Nair', 'Karthik Rao',
    'Divya Menon', 'Aditya Joshi', 'Kavya Pillai',
    'Suresh Babu', 'Meera Krishnan', 'Rajesh Verma',
    'Swathi Naidu', 'Akash Tiwari', 'Lakshmi Devi',
    'Sanjay Mishra', 'Deepika Rajan', 'Harish Nambiar',
    'Yamini Sree', 'Pranav Bhat', 'Rashmi Hegde',
    'Varun Malhotra', 'Nithya Gopal', 'Abhishek Das',
    'Shruti Pillai', 'Naveen Kumar', 'Asha Rani',
    'Mohan Lal', 'Sunita Devi', 'Ravi Shankar',
    'Padma Priya', 'Ganesh Murthy', 'Usha Kumari',
    'Dinesh Chand', 'Radha Krishna', 'Sunil Yadav',
    'Geetha Bai', 'Manoj Pandey', 'Sarika Jain',
    'Deepak Nair', 'Anjali Mehta', 'Srinivas Rao',
    'Rekha Devi', 'Vivek Tomar', 'Mamta Sharma',
    'Ajay Bhatt', 'Vasantha Lakshmi'
]

INDIAN_CITIES = [
    'Mumbai', 'Delhi', 'Bangalore', 'Hyderabad',
    'Chennai', 'Kolkata', 'Pune', 'Ahmedabad',
    'Jaipur', 'Lucknow', 'Visakhapatnam', 'Nagpur',
    'Indore', 'Bhopal', 'Patna', 'Vadodara',
    'Coimbatore', 'Kochi', 'Chandigarh', 'Mysuru'
]

PRODUCT_DATA = [
    ('Basmati Rice 5kg', 'Groceries', 450.00, 280.00, 500),
    ('Toor Dal 1kg', 'Groceries', 120.00, 75.00, 800),
    ('Sunflower Oil 1L', 'Groceries', 145.00, 90.00, 600),
    ('Amul Butter 500g', 'Dairy', 280.00, 200.00, 300),
    ('Full Cream Milk 1L', 'Dairy', 58.00, 42.00, 1000),
    ('Paneer 200g', 'Dairy', 85.00, 60.00, 400),
    ('Colgate Toothpaste', 'Personal Care', 95.00, 55.00, 700),
    ('Dove Shampoo 200ml', 'Personal Care', 185.00, 110.00, 350),
    ('Dettol Soap', 'Personal Care', 45.00, 25.00, 900),
    ('Samsung Earphones', 'Electronics', 1299.00, 700.00, 150),
    ('Phone Case', 'Electronics', 299.00, 100.00, 500),
    ('USB Cable 2m', 'Electronics', 199.00, 80.00, 600),
    ('Notebook A4 200pg', 'Stationery', 85.00, 40.00, 800),
    ('Ball Pen Set 10pc', 'Stationery', 65.00, 30.00, 1000),
    ('Geometry Box', 'Stationery', 125.00, 65.00, 400),
    ('Cotton T-Shirt', 'Clothing', 399.00, 180.00, 300),
    ('Formal Shirt', 'Clothing', 799.00, 350.00, 200),
    ('Jeans', 'Clothing', 1299.00, 600.00, 150),
    ('Running Shoes', 'Footwear', 1999.00, 900.00, 100),
    ('Sandals', 'Footwear', 599.00, 250.00, 250)
]

CUSTOMER_SEGMENTS = ['Premium', 'Regular', 'Budget', 'New']
ORDER_STATUSES = [
    'Delivered', 'Delivered', 'Delivered',
    'Cancelled', 'Returned'
]
EVENT_TYPES = [
    'page_view', 'product_view', 'add_to_cart',
    'checkout', 'purchase'
]
DEVICE_TYPES = ['mobile', 'desktop', 'tablet']


def get_connection():
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        logger.info("Database connection successful")
        return conn
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        raise


def insert_customers(conn):
    logger.info("Inserting customers...")
    cursor = conn.cursor()
    start_date = datetime(2022, 1, 1)
    end_date = datetime(2024, 12, 31)
    date_range = (end_date - start_date).days
    customers_data = []
    for name in INDIAN_NAMES:
        email = (name.lower().replace(' ', '.')
                 + str(random.randint(1, 99))
                 + '@gmail.com')
        city = random.choice(INDIAN_CITIES)
        age = random.randint(18, 65)
        signup_date = start_date + timedelta(
            days=random.randint(0, date_range)
        )
        segment = random.choice(CUSTOMER_SEGMENTS)
        customers_data.append(
            (name, email, city, age, signup_date, segment)
        )
    cursor.executemany("""
        INSERT INTO customers
        (name, email, city, age, signup_date, customer_segment)
        VALUES (%s, %s, %s, %s, %s, %s)
    """, customers_data)
    conn.commit()
    logger.info(f"Inserted {len(customers_data)} customers")
    cursor.close()


def insert_products(conn):
    logger.info("Inserting products...")
    cursor = conn.cursor()
    cursor.executemany("""
        INSERT INTO products
        (product_name, category, price, cost, stock_quantity)
        VALUES (%s, %s, %s, %s, %s)
    """, PRODUCT_DATA)
    conn.commit()
    logger.info(f"Inserted {len(PRODUCT_DATA)} products")
    cursor.close()


def insert_orders_and_items(conn):
    logger.info("Inserting orders and order items...")
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    cursor.execute("SELECT product_id, price FROM products")
    products = cursor.fetchall()
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2025, 3, 31)
    date_range = (end_date - start_date).days
    total_orders = 0
    total_items = 0
    for _ in range(300):
        customer_id = random.choice(customer_ids)
        order_date = start_date + timedelta(
            days=random.randint(0, date_range)
        )
        status = random.choice(ORDER_STATUSES)
        city = random.choice(INDIAN_CITIES)
        cursor.execute("""
            INSERT INTO orders
            (customer_id, order_date, status, city)
            VALUES (%s, %s, %s, %s)
            RETURNING order_id
        """, (customer_id, order_date, status, city))
        order_id = cursor.fetchone()[0]
        total_orders += 1
        num_items = random.randint(1, 4)
        selected_products = random.sample(
            products, min(num_items, len(products))
        )
        for product_id, price in selected_products:
            quantity = random.randint(1, 5)
            discount = random.choice(
                [0, 0, 0, 5, 10, 15, 20]
            )
            cursor.execute("""
                INSERT INTO order_items
                (order_id, product_id, quantity,
                unit_price, discount_percent)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, product_id,
                  quantity, price, discount))
            total_items += 1
    conn.commit()
    logger.info(
        f"Inserted {total_orders} orders "
        f"and {total_items} items"
    )
    cursor.close()


def insert_events(conn):
    logger.info("Inserting user events...")
    cursor = conn.cursor()
    cursor.execute("SELECT customer_id FROM customers")
    customer_ids = [row[0] for row in cursor.fetchall()]
    start_date = datetime(2024, 1, 1)
    end_date = datetime(2025, 3, 31)
    date_range = (end_date - start_date).days
    events_data = []
    for _ in range(1000):
        customer_id = random.choice(customer_ids)
        event_type = random.choice(EVENT_TYPES)
        event_timestamp = start_date + timedelta(
            days=random.randint(0, date_range),
            hours=random.randint(0, 23),
            minutes=random.randint(0, 59)
        )
        page_url = f"/product/{random.randint(1, 20)}"
        device_type = random.choice(DEVICE_TYPES)
        events_data.append((
            customer_id, event_type,
            event_timestamp, page_url, device_type
        ))
    cursor.executemany("""
        INSERT INTO user_events
        (customer_id, event_type, event_timestamp,
        page_url, device_type)
        VALUES (%s, %s, %s, %s, %s)
    """, events_data)
    conn.commit()
    logger.info(f"Inserted {len(events_data)} events")
    cursor.close()


def verify_data(conn):
    cursor = conn.cursor()
    tables = [
        'customers', 'products', 'orders',
        'order_items', 'user_events'
    ]
    logger.info("Data verification:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        logger.info(f"  {table}: {count} rows")
    cursor.close()


def main():
    logger.info("Starting data insertion")
    conn = get_connection()
    try:
        insert_customers(conn)
        insert_products(conn)
        insert_orders_and_items(conn)
        insert_events(conn)
        verify_data(conn)
        logger.info("All data inserted successfully")
    except Exception as e:
        logger.error(f"Error: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()
        logger.info("Connection closed")


if __name__ == "__main__":
    main()
