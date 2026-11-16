"""Source-data smoke checks and independent replay of notebook business rules.

Run: python tests/local_data_checks.py
This validates synthetic inputs, not execution of the Fabric notebooks.
"""

import csv
from collections import Counter
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data"


def load(filename):
    with (DATA / filename).open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def classify(order, customer_ids, product_ids):
    if not order["order_id"]:
        return "invalid_identifier_or_status"
    try:
        date.fromisoformat(order["order_date"])
    except ValueError:
        return "invalid_order_date"
    try:
        datetime.fromisoformat(order["updated_at"])
    except ValueError:
        return "invalid_updated_at"
    if not order["customer_id"] or order["customer_id"] not in customer_ids:
        return "invalid_customer"
    if not order["product_id"] or order["product_id"] not in product_ids:
        return "invalid_product"
    try:
        qty = int(order["quantity"])
    except ValueError:
        return "invalid_quantity"
    if qty <= 0:
        return "invalid_quantity"
    try:
        price = Decimal(order["unit_price"])
    except Exception:
        return "invalid_price"
    if price <= 0:
        return "invalid_price"
    if order["status"] not in {"Completed", "Returned", "Cancelled"}:
        return "invalid_identifier_or_status"
    return None


def reconcile(rows, customer_ids, product_ids):
    latest = {}
    for i, row in enumerate(rows):
        # Mirrors latest updated_at logic; input order breaks timestamp ties in fixture.
        key = row["order_id"]
        stamp = datetime.fromisoformat(row["updated_at"])
        if key not in latest or (stamp, i) > latest[key][0]:
            latest[key] = ((stamp, i), row)
    valid = []
    rejected = []
    for _, row in latest.values():
        reason = classify(row, customer_ids, product_ids)
        (rejected if reason else valid).append((row, reason))
    revenue = sum(
        (Decimal(row["quantity"]) * Decimal(row["unit_price"])
         for row, _ in valid if row["status"] == "Completed"),
        Decimal("0.00")
    )
    return len(latest), len(valid), len(rejected), revenue, Counter(r for _, r in rejected)


def main():
    customers = load("customers.csv")
    products = load("products.csv")
    batch1 = load("orders_batch_01.csv")
    batch2 = load("orders_batch_02.csv")
    assert (len(customers), len(products), len(batch1), len(batch2)) == (150, 30, 1604, 402)
    customer_ids = {x["customer_id"] for x in customers}
    product_ids = {x["product_id"] for x in products}
    assert len(customer_ids) == 150 and len(product_ids) == 30
    assert len({r["order_id"] for r in batch1}) == 1604
    corrections = {r["order_id"] for r in batch1} & {r["order_id"] for r in batch2}
    assert len(corrections) == 1, f"Expected one corrected order, got {corrections}"

    expected = {
        "batch 01": (1604, 1600, 4, Decimal("319205.28")),
        "batch 01 + 02": (2005, 2000, 5, Decimal("402844.35")),
    }
    for label, rows in (("batch 01", batch1), ("batch 01 + 02", batch1 + batch2)):
        distinct, valid, bad, revenue, reasons = reconcile(rows, customer_ids, product_ids)
        assert (distinct, valid, bad, revenue) == expected[label], (
            label, distinct, valid, bad, revenue
        )
        assert valid + bad == distinct
        print(f"PASS {label}: raw={len(rows):,}; unique={distinct:,}; "
              f"silver={valid:,}; quarantine={bad}; completed_revenue={revenue}")
        print(f"  reject reasons: {dict(reasons)}")


if __name__ == "__main__":
    main()
