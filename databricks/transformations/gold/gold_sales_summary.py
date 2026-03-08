from pyspark import pipelines as dp
from pyspark.sql.functions import count, countDistinct, sum, avg, round

@dp.table(name="gold_sales_summary")
def gold_sales_summary():
    df = spark.read.table("workspace.default.silver_enriched_orders")

    return df.agg(
        count("order_id").alias("total_orders"),
        round(sum("order_value"), 2).alias("total_revenue"),
        round(avg("order_value"), 2).alias("avg_order_value"),
        countDistinct("customer_name").alias("unique_customers"),
        countDistinct("city_name").alias("active_cities")
    )