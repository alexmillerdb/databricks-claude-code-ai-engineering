#!/usr/bin/env python3
"""Comprehensive Databricks connection and environment test."""

from databricks.connect import DatabricksSession
from dotenv import load_dotenv
import os
import sys

# Load environment variables
load_dotenv()

def test_environment_variables():
    """Test that all required environment variables are set."""
    print("\n1. Testing Environment Variables...")
    
    # Check for either DATABRICKS_HOST or DATABRICKS_WORKSPACE_URL
    host = os.getenv("DATABRICKS_HOST") or os.getenv("DATABRICKS_WORKSPACE_URL")
    host_var = "DATABRICKS_HOST" if os.getenv("DATABRICKS_HOST") else "DATABRICKS_WORKSPACE_URL"
    
    required_vars = [
        "DATABRICKS_TOKEN",
    ]
    
    optional_vars = [
        "DATABRICKS_CLUSTER_ID",
        "DATABRICKS_SERVERLESS_COMPUTE_ID",
        "DATABRICKS_CATALOG",
        "DATABRICKS_SCHEMA_DEV",
        "DATABRICKS_SCHEMA"
    ]
    
    missing_required = []
    
    # Check host configuration
    if not host:
        missing_required.append("Host configuration")
        print(f"   ❌ Host: Neither DATABRICKS_HOST nor DATABRICKS_WORKSPACE_URL is set")
    else:
        print(f"   ✅ {host_var}: {host}")
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_required.append(var)
            print(f"   ❌ {var}: Not set")
        else:
            # Mask sensitive values
            if var == "DATABRICKS_TOKEN":
                masked_value = value[:4] + "..." + value[-4:] if len(value) > 8 else "***"
                print(f"   ✅ {var}: {masked_value}")
            else:
                print(f"   ✅ {var}: {value}")
    
    # Check compute configuration
    cluster_id = os.getenv("DATABRICKS_CLUSTER_ID")
    serverless_id = os.getenv("DATABRICKS_SERVERLESS_COMPUTE_ID")
    
    if not cluster_id and not serverless_id:
        print(f"   ❌ Compute: Neither DATABRICKS_CLUSTER_ID nor DATABRICKS_SERVERLESS_COMPUTE_ID is set")
        missing_required.append("Compute configuration")
    elif serverless_id:
        print(f"   ✅ Compute: Using serverless ({serverless_id})")
    else:
        print(f"   ✅ Compute: Using cluster ({cluster_id})")
    
    # Check optional variables
    print("\n   Optional configurations:")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
            print(f"   ✅ {var}: {value}")
        else:
            print(f"   ⚠️  {var}: Not set (optional)")
    
    return len(missing_required) == 0

def test_databricks_connection():
    """Test basic Databricks connection."""
    print("\n2. Testing Databricks Connection...")
    
    try:
        spark = DatabricksSession.builder.getOrCreate()
        result = spark.sql("SELECT current_user() as user, current_database() as database, current_timestamp() as timestamp").collect()
        
        row = result[0]
        print(f"   ✅ Connected successfully!")
        print(f"   👤 User: {row['user']}")
        print(f"   📁 Database: {row['database']}")
        print(f"   🕐 Server time: {row['timestamp']}")
        
        return True
    except Exception as e:
        print(f"   ❌ Connection failed: {str(e)}")
        return False

def test_unity_catalog():
    """Test Unity Catalog access and configuration."""
    print("\n3. Testing Unity Catalog...")
    
    catalog = os.getenv("DATABRICKS_CATALOG")
    schema = os.getenv("DATABRICKS_SCHEMA_DEV") or os.getenv("DATABRICKS_SCHEMA")
    
    if not catalog or not schema:
        print("   ⚠️  Unity Catalog not configured (DATABRICKS_CATALOG and DATABRICKS_SCHEMA/DATABRICKS_SCHEMA_DEV not set)")
        return True  # Not a failure, just not configured
    
    try:
        spark = DatabricksSession.builder.getOrCreate()
        
        # Test catalog access
        catalogs = spark.sql("SHOW CATALOGS").collect()
        catalog_names = [c['catalog'] for c in catalogs]
        
        if catalog in catalog_names:
            print(f"   ✅ Catalog '{catalog}' exists and is accessible")
        else:
            print(f"   ❌ Catalog '{catalog}' not found. Available catalogs: {catalog_names}")
            return False
        
        # Test schema access
        spark.sql(f"USE CATALOG {catalog}")
        schemas = spark.sql("SHOW SCHEMAS").collect()
        schema_names = [s['databaseName'] for s in schemas]
        
        if schema in schema_names:
            print(f"   ✅ Schema '{schema}' exists in catalog '{catalog}'")
        else:
            print(f"   ❌ Schema '{schema}' not found in catalog '{catalog}'. Available schemas: {schema_names}")
            return False
        
        # Test table creation permissions
        test_table = f"{catalog}.{schema}._connection_test_temp"
        try:
            spark.sql(f"CREATE TABLE IF NOT EXISTS {test_table} (id INT) USING DELTA")
            spark.sql(f"DROP TABLE IF EXISTS {test_table}")
            print(f"   ✅ Create/Drop permissions verified in {catalog}.{schema}")
        except Exception as e:
            print(f"   ⚠️  Limited permissions in {catalog}.{schema}: {str(e)}")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Unity Catalog test failed: {str(e)}")
        return False

def test_python_packages():
    """Test that required Python packages are installed."""
    print("\n4. Testing Python Packages...")
    
    packages = {
        "databricks-connect": "databricks.connect",
        "databricks-sdk": "databricks.sdk",
        "python-dotenv": "dotenv",
        "databricks-cli": "databricks_cli"
    }
    
    all_installed = True
    for package, import_name in packages.items():
        try:
            # Handle nested module imports
            if "." in import_name:
                parts = import_name.split(".")
                module = __import__(import_name)
                for part in parts[1:]:
                    module = getattr(module, part)
            else:
                module = __import__(import_name)
            
            # Try to get version from various places
            version = "installed"
            try:
                # Check main module
                main_module = __import__(package.replace("-", "_"))
                version = getattr(main_module, "__version__", version)
            except:
                pass
            
            print(f"   ✅ {package}: {version}")
        except ImportError:
            print(f"   ❌ {package}: Not installed")
            all_installed = False
    
    return all_installed

def main():
    """Run all tests and provide summary."""
    print("=" * 60)
    print("🔍 Databricks Environment Test Suite")
    print("=" * 60)
    
    results = {
        "Environment Variables": test_environment_variables(),
        "Databricks Connection": test_databricks_connection(),
        "Unity Catalog": test_unity_catalog(),
        "Python Packages": test_python_packages()
    }
    
    print("\n" + "=" * 60)
    print("📊 Test Summary:")
    print("=" * 60)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"   {test_name}: {status}")
        if not passed:
            all_passed = False
    
    print("\n" + "=" * 60)
    if all_passed:
        print("✅ All tests passed! Your Databricks environment is ready.")
    else:
        print("❌ Some tests failed. Please check the errors above.")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())