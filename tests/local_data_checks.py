"""Standard-library checks: python tests/local_data_checks.py"""
import csv
from pathlib import Path
p = Path(__file__).resolve().parents[1] / 'data'
def rows(name):
    with (p / name).open(newline='', encoding='utf-8') as fh:
        return list(csv.DictReader(fh))
c=rows('customers.csv'); products=rows('products.csv')
a=rows('orders_batch_01.csv'); b=rows('orders_batch_02.csv')
assert (len(c),len(products),len(a),len(b)) == (150,30,1604,402)
assert len({x['customer_id'] for x in c}) == 150
assert len({x['product_id'] for x in products}) == 30
assert len({x['order_id'] for x in a+b}) == 2005
assert len([x for x in b if x['order_id'] in {a0['order_id'] for a0 in a}]) == 1
print('PASS: sample files, dimensions, incremental batch and correction')
