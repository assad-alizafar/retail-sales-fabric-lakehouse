-- Run in the Lakehouse SQL analytics endpoint after notebook 03 completes.
SELECT TOP 10 order_date, orders, units_sold, revenue
FROM dbo.gold_daily_sales ORDER BY order_date DESC;

SELECT TOP 10 product_name, category, units_sold, revenue
FROM dbo.gold_product_performance ORDER BY revenue DESC;

SELECT region, SUM(lifetime_revenue) AS revenue
FROM dbo.gold_customer_value GROUP BY region ORDER BY revenue DESC;

SELECT reject_reason, COUNT(*) AS rejected_rows
FROM dbo.silver_orders_quarantine GROUP BY reject_reason ORDER BY rejected_rows DESC;
