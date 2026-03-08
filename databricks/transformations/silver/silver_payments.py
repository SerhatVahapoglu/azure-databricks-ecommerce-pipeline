from pyspark import pipelines as dp
from pyspark.sql.functions import col, to_timestamp

@dp.table(name="silver_payments")
def silver_payments():
    payments = spark.read.table("workspace.default.bronze_payments")

    return (
        payments
        .withColumn("paid_amount", col("paid_amount").cast("double"))
        .withColumn("installment_count", col("installment_count").cast("int"))
        .withColumn("attempt_no", col("attempt_no").cast("int"))
        .withColumn("payment_timestamp", to_timestamp(col("payment_timestamp")))
    )