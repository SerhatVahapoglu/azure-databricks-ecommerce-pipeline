from pyspark import pipelines as dp
from pyspark.sql.functions import count, sum, avg, round

@dp.table(name="gold_city_performance")
def gold_city_performance():
    df = spark.read.table("workspace.default.silver_enriched_orders")

    return (
        df.groupBy("city_name")
        .agg(
            count("order_id").alias("total_orders"),
            round(sum("order_value"), 2).alias("total_revenue"),
            round(avg("order_value"), 2).alias("avg_order_value")
        )
        .orderBy("total_revenue", ascending=False)
    )