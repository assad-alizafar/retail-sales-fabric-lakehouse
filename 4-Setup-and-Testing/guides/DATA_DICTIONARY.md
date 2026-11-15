# Data dictionary and modeling notes

All source data is **synthetic and fictional**, generated deterministically using seed `42`.

| Source | Grain | Main fields | Notes |
| --- | --- | --- | --- |
| customers.csv | One row per customer (before intentional duplicate) | customer_id, customer_name, region, signup_date | One duplicated customer; one blank region |
| products.csv | One row per product | product_id, product_name, category, list_price | Synthetic catalog |
| orders.csv | One row per order | order_id, customer_id, order_date, order_status | Completed, Cancelled, Returned |
| order_items.csv | One row per line item (before intentional duplicate) | order_item_id, order_id, product_id, quantity, unit_price, discount_pct | Duplicate row, invalid product, zero quantity |

**Metrics**

- `gross_sales = quantity × unit_price`.
- `net_sales = ROUND(gross_sales × (1 - discount_pct), 2)` **per line item**.
- Only orders with `order_status = 'Completed'` contribute to Gold sales metrics.
- `gold_daily_sales`: one row per completed sales date; distinct order count, units, net revenue.
- `gold_product_performance`: one row per product with completed sales.
- `gold_customer_360`: one row per valid customer, including customers with no completed orders.
- Order counts in Gold are **distinct order IDs**, not number of line items.

**Data quality choices**

- Bronze retains raw rows with ingestion metadata; it does not correct defective source records.
- Silver de-duplicates by business key, fills blank region as `Unknown`, parses types, rejects invalid item references/quantities/discounts.
- This is an intentionally small portfolio dataset with sample data-quality issues; no personally identifiable real customer information is used.
- The full-refresh sample does **not** demonstrate CDC or SCD Type 2; see `4-Setup-and-Testing/guides/EXTENSIONS.md` for extensions.
