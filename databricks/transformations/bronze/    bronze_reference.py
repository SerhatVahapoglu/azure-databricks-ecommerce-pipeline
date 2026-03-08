from pyspark import pipelines as dp

CITIES_PATH = "/Volumes/workspace/end_to_end/raw_files/map_cities.csv"
STATUSES_PATH = "/Volumes/workspace/end_to_end/raw_files/map_statuses.csv"

@dp.table(name="bronze_cities")
def bronze_cities():
    return (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(CITIES_PATH)
    )

@dp.table(name="bronze_statuses")
def bronze_statuses():
    return (
        spark.read
        .option("header", True)
        .option("inferSchema", True)
        .csv(STATUSES_PATH)
    )