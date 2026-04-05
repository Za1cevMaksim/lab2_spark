import sys
import os
import time
import json
import psutil
import logging
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.storagelevel import StorageLevel

os.environ["PYSPARK_LOG_LEVEL"] = "ERROR"
os.environ["HADOOP_ROOT_LOGGER"] = "ERROR,console"
logging.getLogger("py4j").setLevel(logging.CRITICAL)
logging.getLogger("pyspark").setLevel(logging.ERROR)

def get_mem_mb():
    try:
        current_process = psutil.Process(os.getpid())
        total_mem = current_process.memory_info().rss
        
        for child in current_process.children(recursive=True):
            try:
                total_mem += child.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
                
        return total_mem / (1024**2)
    except Exception:
        return 0.0

def run(optimized=False):
    mode = "OPT" if optimized else "BASE"
    print(f"\n[{mode}] Запуск", flush=True)
    
    mem_start = get_mem_mb()
    t_start = time.time()

    builder = SparkSession.builder \
        .appName(f"Lab2_{mode}") \
        .config("spark.driver.memory", "512m") \
        .config("spark.executor.memory", "512m") \
        .config("spark.sql.shuffle.partitions", "4" if optimized else "200") \
        .config("spark.hadoop.fs.defaultFS", "hdfs://localhost:9000") \
        .config("spark.log.level", "ERROR") \
        .config("spark.ui.enabled", "false") 

    spark = builder.getOrCreate()
    sc = spark.sparkContext
    sc.setLogLevel("ERROR")

    try:
        print("Чтение данных из HDFS", flush=True)
        df = spark.read.option("header", True).csv("/data/Online_Retail.csv")
        
        df = df.withColumn("Quantity", F.col("Quantity").cast("int")) \
               .withColumn("UnitPrice", F.col("UnitPrice").cast("double")) \
               .withColumn("CustomerID", F.col("CustomerID").cast("int"))

        df = df.filter((F.col("Quantity") > 0) & F.col("CustomerID").isNotNull())
        
        if optimized:
            print("Repartition + Cache)", flush=True)
            df = df.repartition(4).persist(StorageLevel.MEMORY_AND_DISK)
            df.count()  

        print("Выполнение тяжелой агрегации", flush=True)
        
        df_heavy = df.withColumn("price_squared", F.col("UnitPrice") ** 2) \
                     .withColumn("qty_log", F.log(F.col("Quantity") + 1))
        
        res = df_heavy.groupBy("Country", "StockCode") \
                .agg(
                    F.sum("Quantity").alias("total_qty"),
                    F.avg("price_squared").alias("avg_price_sq"),
                    F.countDistinct("CustomerID").alias("unique_cust")
                ) \
                .orderBy(F.desc("total_qty"))

        res.show(5)
        total_rows = df_heavy.count() 

        t_end = time.time()
        mem_end = get_mem_mb()
        
        duration = t_end - t_start
        ram_used = mem_end - mem_start

        result = {
            "mode": mode,
            "datanodes": int(os.environ.get("EXP_DN_COUNT", 1)), 
            "time_sec": round(duration, 2),
            "ram_mb": round(ram_used, 1),
            "rows_processed": total_rows,
            "status": "SUCCESS"
        }
        
        print(json.dumps(result, indent=2), flush=True)
        return result

    except Exception as e:
        print(f"Ошибка: {str(e)}", flush=True)
        return {"mode": mode, "status": "FAILED", "error": str(e)}

    finally:
        spark.stop()

if __name__ == "__main__":
    # Запуск: python spark_app.py [--opt]
    is_opt = "--opt" in sys.argv
    run(optimized=is_opt)