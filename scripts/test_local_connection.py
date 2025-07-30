from databricks.connect import DatabricksSession
from dotenv import load_dotenv
import os

load_dotenv()

try:
    spark = DatabricksSession.builder.getOrCreate()
    result = spark.sql("SELECT 'Local connection works!' as message, current_user() as user").collect()
    print("✅ Success:", result[0]['message'])
    print("👤 Connected as:", result[0]['user'])
except Exception as e:
    print("❌ Connection failed:", str(e))