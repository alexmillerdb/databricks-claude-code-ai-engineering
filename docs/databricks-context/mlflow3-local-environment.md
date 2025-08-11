# MLflow 3.0 Local Development Environment Setup

**Source**: https://docs.databricks.com/aws/en/mlflow3/genai/getting-started/connect-environment#local-development-environment
**Domain**: docs.databricks.com
**Fetched**: 2025-08-08
**Type**: Databricks MLflow 3.0 Documentation

## Overview

This documentation provides comprehensive guidance for setting up MLflow 3.0 for GenAI applications in a local development environment, with focus on connecting to Databricks workspace for experiment tracking and model management.

## Key Concepts

### Prerequisites
- Python development environment
- Databricks workspace access
- Personal access token for authentication

### Step-by-Step Setup Process

#### Step 1: Install MLflow
```bash
pip install --upgrade "mlflow[databricks]>=3.1"
```

#### Step 2: Create MLflow Experiment
1. Open Databricks workspace
2. Navigate to "AI/ML" > "Experiments"
3. Click "GenAI apps & agents"
4. Note the experiment ID for configuration

#### Step 3: Configure Authentication

**Environment Variables Configuration**
```bash
export DATABRICKS_TOKEN=<databricks-personal-access-token>
export DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com
export MLFLOW_TRACKING_URI=databricks
export MLFLOW_REGISTRY_URI=databricks-uc
export MLFLOW_EXPERIMENT_ID=<experiment-id>
```

**.env File Configuration**
```env
DATABRICKS_TOKEN=<databricks-personal-access-token>
DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com
MLFLOW_TRACKING_URI=databricks
MLFLOW_REGISTRY_URI=databricks-uc
MLFLOW_EXPERIMENT_ID=<experiment-id>
```

**Setup for .env file usage:**
```bash
pip install python-dotenv
```

**Load environment variables in Python:**
```python
from dotenv import load_dotenv
load_dotenv()
```

## Code Examples

### Connection Verification
```python
import mlflow
import os

@mlflow.trace
def hello_mlflow(message: str):
    experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID')
    databricks_host = os.getenv('DATABRICKS_HOST')
    
    hello_data = {
        "experiment_url": f"{databricks_host}/mlflow/experiments/{experiment_id}",
        "experiment_name": mlflow.get_experiment(experiment_id=experiment_id).name,
        "message": message,
    }
    return hello_data

# Test connection
result = hello_mlflow("hello, world!")
print(result)
```

### Complete Setup Example
```python
import mlflow
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Configure MLflow
mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")

# Set experiment
experiment_id = os.getenv('MLFLOW_EXPERIMENT_ID')
mlflow.set_experiment(experiment_id=experiment_id)

# Verify setup
experiment = mlflow.get_experiment(experiment_id)
print(f"Connected to experiment: {experiment.name}")
```

## Implementation Notes

### Authentication Methods
1. **Environment Variables**: Direct export in shell
2. **.env File**: Secure file-based configuration with python-dotenv
3. **Databricks CLI**: Alternative authentication method

### Key Configuration Variables
- `DATABRICKS_TOKEN`: Personal access token for authentication
- `DATABRICKS_HOST`: Workspace URL
- `MLFLOW_TRACKING_URI`: Set to "databricks" for Databricks integration
- `MLFLOW_REGISTRY_URI`: Set to "databricks-uc" for Unity Catalog integration
- `MLFLOW_EXPERIMENT_ID`: Target experiment for logging

### Local Development Benefits
- **Full IDE Support**: Complete development experience in local environment
- **Databricks Integration**: Seamless connection to workspace resources
- **Unity Catalog**: Access to centralized model registry
- **Experiment Tracking**: Comprehensive logging and monitoring

### Best Practices
1. **Secure Credentials**: Use .env files and never commit tokens to code
2. **Environment Isolation**: Use virtual environments for dependency management
3. **Experiment Organization**: Create dedicated experiments for different projects
4. **Version Pinning**: Pin MLflow version for consistency

### Troubleshooting Common Issues
- **Authentication Errors**: Verify token permissions and workspace access
- **Connection Timeouts**: Check network connectivity and workspace availability
- **Experiment Not Found**: Ensure experiment ID exists and is accessible
- **Version Conflicts**: Verify MLflow version compatibility (>=3.1 required)

## Related Resources
- Reference CLAUDE.md for project guidelines
- Check /docs folder for additional MLflow examples
- See mlflow3-tracing-ide.md for tracing implementation details
- Review Mosaic AI Agent Framework integration patterns