# MLflow 3.0 Tracing in Local IDE

**Source**: https://docs.databricks.com/aws/en/mlflow3/genai/getting-started/tracing/tracing-ide
**Domain**: docs.databricks.com
**Fetched**: 2025-08-08
**Type**: Databricks MLflow 3.0 Documentation

## Overview

This documentation covers integrating GenAI applications with MLflow Tracing using a local development environment. MLflow 3.0 provides enhanced tracing capabilities for GenAI applications with automatic logging and monitoring.

## Key Concepts

### Prerequisites
- Access to a Databricks workspace
- Python development environment
- Personal access token for Databricks

### Installation and Setup

#### 1. Install MLflow
```bash
pip install --upgrade "mlflow[databricks]>=3.1" openai
```

#### 2. Create MLflow Experiment
1. Open Databricks workspace
2. Navigate to **Experiments**
3. Click **New GenAI Experiment**

#### 3. Environment Configuration

**Option 1: Environment Variables**
```bash
export DATABRICKS_TOKEN=<databricks-personal-access-token>
export DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com
export MLFLOW_TRACKING_URI=databricks
export MLFLOW_EXPERIMENT_ID=<experiment-id>
```

**Option 2: .env File**
```bash
pip install python-dotenv
```

Create `.env` file:
```env
DATABRICKS_TOKEN=<databricks-personal-access-token>
DATABRICKS_HOST=https://<workspace-name>.cloud.databricks.com
MLFLOW_TRACKING_URI=databricks
MLFLOW_EXPERIMENT_ID=<experiment-id>
```

Load in Python code:
```python
from dotenv import load_dotenv
load_dotenv()
```

## Code Examples

### Databricks-Hosted LLM with Tracing
```python
import mlflow
from databricks.sdk import WorkspaceClient

# Enable MLflow autologging
mlflow.openai.autolog()

# Set up MLflow tracking
mlflow.set_tracking_uri("databricks")
mlflow.set_experiment("/Shared/docs-demo")

# Create Databricks-hosted LLM client
w = WorkspaceClient()
client = w.serving_endpoints.get_open_ai_client()
model_name = "databricks-claude-sonnet-4"

# Trace application
@mlflow.trace
def my_app(input: str):
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input}
        ],
        max_tokens=100
    )
    return response.choices[0].message.content

# Execute and trace
result = my_app("What is MLflow?")
```

## Implementation Notes

### Key Features
- **Automatic Logging**: MLflow 3.0 automatically captures traces for GenAI applications
- **Local Development**: Full tracing support in local IDE environments
- **Databricks Integration**: Seamless connection to Databricks workspace
- **Enhanced Monitoring**: Comprehensive tracking of LLM calls and responses

### Best Practices
1. **Use Environment Variables**: Keep credentials secure with environment variables or .env files
2. **Experiment Organization**: Create dedicated experiments for different projects
3. **Trace Decorators**: Use `@mlflow.trace` decorator for custom functions
4. **Model Selection**: Choose appropriate Databricks-hosted models for your use case

### Troubleshooting
- Verify authentication credentials are correct
- Ensure experiment ID exists in workspace
- Check network connectivity to Databricks workspace
- Validate MLflow version compatibility (>=3.1 required)

## Related Resources
- Reference CLAUDE.md for project guidelines
- Check /docs folder for additional MLflow examples
- See mlflow3-local-environment.md for environment setup details
- Review Unity Catalog integration patterns