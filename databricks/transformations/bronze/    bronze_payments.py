from pyspark import pipelines as dp
from pyspark.sql.functions import col, to_timestamp

PAYMENTS_PATH = "/Volumes/workspace/end_to_end/raw_files/payments_generated.csv"

@dp.table(name="bronze_payments")
def bronze_payments():
    df = (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(PAYMENTS_PATH)
    )

    return (
        df
        .withColumn("payment_timestamp", to_timestamp(col("payment_timestamp")))
    )