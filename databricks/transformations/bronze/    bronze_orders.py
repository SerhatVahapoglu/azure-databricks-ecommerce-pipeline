from pyspark import pipelines as dp
from pyspark.sql.functions import col, from_json
from pyspark.sql.types import *

# Event Hubs configuration
EH_NAMESPACE = "eh-ecommerce-std1461"
EH_NAME = "orders-topic"

EH_CONN_STR = spark.conf.get("connection_string")

KAFKA_OPTIONS = {
    "kafka.bootstrap.servers": f"{EH_NAMESPACE}.servicebus.windows.net:9093",
    "subscribe": EH_NAME,
    "kafka.sasl.mechanism": "PLAIN",
    "kafka.security.protocol": "SASL_SSL",
    "kafka.sasl.jaas.config": f'kafkashaded.org.apache.kafka.common.security.plain.PlainLoginModule required username="$ConnectionString" password="{EH_CONN_STR}";',
    "kafka.request.timeout.ms": spark.conf.get("kafka_request_timeout_ms"),
    "kafka.session.timeout.ms": spark.conf.get("kafka_session_timeout_ms"),
    "maxOffsetsPerTrigger": spark.conf.get("max_offsets_per_trigger"),
    "failOnDataLoss": spark.conf.get("fail_on_data_loss"),
    "startingOffsets": spark.conf.get("starting_offsets")
}

payload_schema = StructType([
    StructField("order_id", StringType(), True),
    StructField("customer_name", StringType(), True),
    StructField("city_id", StringType(), True),
    StructField("status_id", StringType(), True),
    StructField("order_value", DoubleType(), True),
    StructField("timestamp", StringType(), True)
])

@dp.table(name="bronze_orders")
def bronze_orders():
    df = (
        spark.readStream.format("kafka")
        .options(**KAFKA_OPTIONS)
        .load()
    )

    df = df.withColumn("json_str", col("value").cast("string"))
    df = df.withColumn("parsed", from_json(col("json_str"), payload_schema))

    return df.select("parsed.*")