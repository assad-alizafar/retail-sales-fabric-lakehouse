-- Run via the Fabric Lakehouse SQL analytics endpoint after executing the notebooks.
-- These are read-only T-SQL SELECT queries over registered Delta tables.

-- KPI snapshot
SELECT COUNT(*) AS sales_days,
       CAST(SUM(net_revenue) AS DECIMAL(18,2)) AS total_net_revenue,
       SUM(orders) AS daily_distinct_order_counts_sum
FROM gold_daily_sales;

-- Top categories by net revenue
SELECT category,
       CAST(SUM(net_revenue) AS DECIMAL(18,2)) AS net_revenue,
       SUM(units_sold) AS units_sold
FROM gold_product_performance
GROUP BY category
ORDER BY net_revenue DESC;

-- Customer lifetime value by region
SELECT region,
       COUNT(*) AS customer_count,
       CAST(SUM(lifetime_revenue) AS DECIMAL(18,2)) AS lifetime_revenue,
       CAST(AVG(lifetime_revenue) AS DECIMAL(18,2)) AS average_customer_revenue
FROM gold_customer_360
GROUP BY region
ORDER BY lifetime_revenue DESC;

-- Revenue trend by month
SELECT LEFT(CAST(sales_date AS VARCHAR(10)),7) AS sales_month,
       CAST(SUM(net_revenue) AS DECIMAL(18,2)) AS revenue
FROM gold_daily_sales
GROUP BY LEFT(CAST(sales_date AS VARCHAR(10)),7)
ORDER BY sales_month;
