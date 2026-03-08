from pyspark import pipelines as dp

@dp.table(name="silver_enriched_orders")
def silver_enriched_orders():
    orders = spark.read.table("workspace.default.silver_orders")

    payments = (
        spark.read.table("workspace.default.silver_payments")
        .select(
            "order_id",
            "payment_id",
            "attempt_no",
            "payment_method",
            "installment_count",
            "payment_status",
            "paid_amount",
            "currency",
            "payment_timestamp"
        )
    )

    return (
        orders
        .join(payments, on="order_id", how="left")
    )