from pyspark import pipelines as dp
from pyspark.sql.functions import col, to_timestamp

@dp.table(name="silver_orders")
def silver_orders():
    orders = spark.read.table("workspace.default.bronze_orders")
    cities = spark.read.table("workspace.default.bronze_cities")
    statuses = spark.read.table("workspace.default.bronze_statuses")

    orders_clean = (
        orders
        .withColumn("order_value", col("order_value").cast("double"))
        .withColumn("order_timestamp", to_timestamp(col("timestamp")))
        .drop("timestamp")
    )

    enriched = (
        orders_clean
        .join(cities, on="city_id", how="left")
        .join(statuses, on="status_id", how="left")
    )

    return enriched