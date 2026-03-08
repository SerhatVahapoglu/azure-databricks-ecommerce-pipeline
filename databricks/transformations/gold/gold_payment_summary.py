from pyspark import pipelines as dp
from pyspark.sql.functions import count, sum, avg, round, col

@dp.table(name="gold_payment_summary")
def gold_payment_summary():
    df = spark.read.table("workspace.default.silver_enriched_orders")

    return (
        df.groupBy("payment_method", "payment_status")
        .agg(
            count("payment_id").alias("payment_count"),
            round(sum("paid_amount"), 2).alias("total_paid_amount"),
            round(avg("paid_amount"), 2).alias("avg_paid_amount")
        )
    )