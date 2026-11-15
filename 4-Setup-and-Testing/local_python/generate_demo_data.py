"""Deterministic FICTIONAL retail source data with controlled data-quality defects."""
import argparse
import csv
import random
from datetime import date,timedelta
from pathlib import Path

CATEGORIES = ['Electronics', 'Home', 'Office', 'Fitness', 'Accessories']
REGIONS = ['North', 'South', 'East', 'West']

def write_csv(path, headers, records):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(records)

def generate(output: Path, customers_count=350, orders_count=1800, seed=42):
    rng = random.Random(seed)
    customers = []
    for n in range(1, customers_count + 1):
        signup = date(2025, 1, 1) + timedelta(days=rng.randint(0, 330))
        customers.append((f'C{n:04d}', f'Customer {n:04d}', rng.choice(REGIONS), signup.isoformat()))
    products = []
    for n in range(1, 51):
        products.append((f'P{n:03d}', f'Product {n:03d}', CATEGORIES[(n - 1) % 5], round(rng.uniform(12, 350), 2)))
    product_price = {r[0]: r[3] for r in products}
    orders, items = [], []
    for n in range(1, orders_count + 1):
        customer = rng.choice(customers)
        order_date = date.fromisoformat(customer[3]) + timedelta(days=rng.randint(0, 380))
        status = rng.choices(['Completed', 'Cancelled', 'Returned'], weights=[86, 9, 5])[0]
        order_id = f'O{n:06d}'
        orders.append((order_id, customer[0], order_date.isoformat(), status))
        for j, product in enumerate(rng.sample(products, rng.randint(1, 4)), start=1):
            qty = rng.randint(1, 4)
            discount = rng.choice([0, 0, 0, 0.05, 0.10, 0.15])
            items.append((f'{order_id}-{j}', order_id, product[0], qty, product_price[product[0]], discount))
    # Intentional quality issues: 1 duplicate dimension record, 1 null customer region,
    # 1 orphan item (invalid product), 1 zero quantity, 1 duplicate item record.
    customers.append(customers[0])
    customers[1] = (customers[1][0], customers[1][1], '', customers[1][3])
    items[0] = (items[0][0], items[0][1], 'P999', items[0][3], items[0][4], items[0][5])
    items[1] = (items[1][0], items[1][1], items[1][2], 0, items[1][4], items[1][5])
    items.append(items[2])
    write_csv(output/'customers.csv', ['customer_id','customer_name','region','signup_date'], customers)
    write_csv(output/'products.csv', ['product_id','product_name','category','list_price'], products)
    write_csv(output/'orders.csv', ['order_id','customer_id','order_date','order_status'], orders)
    write_csv(output/'order_items.csv', ['order_item_id','order_id','product_id','quantity','unit_price','discount_pct'], items)
    return {'customers_raw':len(customers),'products_raw':len(products),'orders_raw':len(orders),'order_items_raw':len(items)}

if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',default='2-Sample-Retail-Data')
    parser.add_argument('--customers',type=int,default=350)
    parser.add_argument('--orders',type=int,default=1800)
    args=parser.parse_args()
    print(generate(Path(args.output), args.customers,args.orders))
