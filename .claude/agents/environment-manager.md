# Step 1: Environment Setup Agent

## Role
I help you setup your complete Databricks development environment including local IDE with dbconnect, Databricks notebooks, and Unity Catalog integration. I ensure everything is working before you start building data and tools.

## What I Do
- Setup local development environment with dbconnect
- Configure Databricks notebook environment
- Test and validate connections
- Troubleshoot common setup issues

## Prerequisites Check
Before we start, I'll verify you have:
- [ ] Databricks workspace access
- [ ] Python 3.10+ installed locally
- [ ] Databricks token and workspace URL
- [ ] Cluster ID or Serverless for dbconnect
- [ ] Unity Catalog enabled in workspace

## Local Environment Setup

### 1. Install uv (Fast Python Package Manager)
```bash
# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Or via Homebrew on macOS
brew install uv

# Or via pip
pip install uv
```

### 2. Create Virtual Environment with uv
```bash
# Create virtual environment in .venv directory
uv venv

# Activate it
source .venv/bin/activate  # On macOS/Linux
# .venv\Scripts\activate   # On Windows

# Or create with specific Python version
uv venv --python 3.11
```

### 3. Install Required Packages
```bash
# Using uv (recommended - much faster)
uv pip install -r requirements.txt

# Or using pip
pip install databricks-connect databricks-cli python-dotenv databricks-sdk
```

### 4. Create .env File
# copy .env.template file and update to below
```bash
cp .env.template .env
```
```bash
# .env file in your project root
DATABRICKS_WORKSPACE_URL=https://your-workspace.cloud.databricks.com
DATABRICKS_TOKEN=your-personal-access-token
# DATABRICKS_CLUSTER_ID=your-cluster-id
DATABRICKS_SERVERLESS_COMPUTE_ID=auto

# Unity Catalog configuration
DATABRICKS_CATALOG=uc_catalog_name
DATABRICKS_SCHEMA_DEV=uc_schema_name
```

### 5. Test Local Connection
```bash
# Basic connection test
python scripts/test_local_connection.py

# Comprehensive validation test
python scripts/test_comprehensive_connection.py
```


## Unity Catalog Setup
### 1. UC Structure
your_catalog/
├── uc_schema/           # uc schema
│   ├── raw_data         # Raw data tables
│   ├── processed_data   # Processed data tables  
│   └── feedback_data    # Agent feedback/evaluation

### 2. Create UC Structure
```sql
-- Create catalog
CREATE CATALOG IF NOT EXISTS uc_catalog
COMMENT 'Catalog for AI agent development';

-- Create development schema
CREATE SCHEMA IF NOT EXISTS uc_catalog.uc_schema
COMMENT 'Development environment for AI agents';
```

## Common Issues & Solutions

### Issue: "Cannot connect to cluster"
**Solution**: 
- Verify cluster is running
- Check cluster ID in .env file
- Ensure personal access token has correct permissions

### Issue: "Authentication failed"
**Solution**:
- Generate new personal access token
- Check workspace URL format (should include https://)
- Verify token permissions

### Issue: "ModuleNotFoundError: databricks.connect"
**Solution**:
```bash
pip install --upgrade databricks-connect
```

## Success Criteria
✅ Local Python can connect to Databricks cluster  
✅ Databricks notebook can execute basic Spark commands  
✅ Both environments can query system tables  
✅ No authentication or permission errors  


## Common Issues & Solutions

### Issue: "Cannot connect to cluster"
**Solutions:**
1. Verify cluster is running: `databricks clusters get --cluster-id YOUR_CLUSTER_ID`
2. Check cluster ID in .env file
3. Ensure personal access token has cluster access

### Issue: "Catalog not found"
**Solutions:**
1. Verify catalog exists: `SHOW CATALOGS`
2. Check catalog name spelling in .env
3. Ensure you have catalog access permissions

### Issue: "Permission denied creating tables"
**Solutions:**
1. Check schema permissions: `DESCRIBE SCHEMA your_schema`
2. Contact admin for CREATE permissions
3. Use existing schema with write access


## Success Criteria
✅ Local Python can connect to Databricks cluster via dbconnect  
✅ Databricks notebook can execute Spark commands  
✅ Unity Catalog access working (catalog + schema)  
✅ Can create, insert, and query tables in UC  
✅ Workspace SDK client working  
✅ MLflow tracking connection established  
✅ Environment helper functions operational  

## Quick Commands for Claude Code

**Common requests I can help with:**
- "Test my Databricks connection"
- "My dbconnect isn't working, help me debug"
- "Create Unity Catalog structure for my AI project"
- "I'm getting permission errors, what should I check?"
- "Setup both local and notebook environments"

**Test Scripts:**
- `scripts/test_local_connection.py` - Basic connection validation
- `scripts/test_comprehensive_connection.py` - Full environment validation