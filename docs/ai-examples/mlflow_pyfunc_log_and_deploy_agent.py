"""
MLflow PyFunc Agent Logging and Deployment Script

This script demonstrates how to:
1. Log an AI agent as an MLflow PyFunc model with all necessary resources
2. Evaluate the agent using MLflow's built-in scorers
3. Test the logged model locally
4. Register the model to Unity Catalog
5. Deploy the agent to a Databricks Model Serving endpoint

Prerequisites:
- An existing agent defined in agent.py with tools, LLM_ENDPOINT_NAME, and AGENT
- Databricks workspace with Unity Catalog enabled
- Appropriate permissions for model registration and deployment

Usage:
    python mlflow_pyfunc_log_and_deploy_agent.py

Author: Databricks AI/ML Team
"""

import mlflow
from agent import tools, LLM_ENDPOINT_NAME, AGENT
from databricks_langchain import VectorSearchRetrieverTool
from mlflow.models.resources import DatabricksFunction, DatabricksServingEndpoint
from unitycatalog.ai.langchain.toolkit import UnityCatalogTool
from pkg_resources import get_distribution

# ==============================================================================
# STEP 1: Prepare Resources for MLflow Model Logging
# ==============================================================================

# Initialize resources list with the LLM serving endpoint
# This ensures the logged model has access to the required LLM endpoint
resources = [DatabricksServingEndpoint(endpoint_name=LLM_ENDPOINT_NAME)]

# Iterate through agent tools to collect additional resources
# This automatically discovers and includes dependencies like vector search indices
# and Unity Catalog functions that the agent uses
for tool in tools:
    if isinstance(tool, VectorSearchRetrieverTool):
        # Add vector search index resources for RAG functionality
        resources.extend(tool.resources)
    elif isinstance(tool, UnityCatalogTool):
        # Add Unity Catalog function resources for data access
        resources.append(DatabricksFunction(function_name=tool.uc_function_name))


# ==============================================================================
# STEP 2: Log Agent as MLflow PyFunc Model
# ==============================================================================

# Start an MLflow run to track the model logging process
with mlflow.start_run():
    # Log the agent as a PyFunc model with all dependencies
    # This creates a deployable model artifact that can be served via Model Serving
    logged_agent_info = mlflow.pyfunc.log_model(
        name="agent",  # Model name in the MLflow run
        python_model="agent.py",  # Python file containing the agent implementation
        resources=resources,  # Databricks resources the model depends on
        pip_requirements=[
            # Pin dependency versions to ensure reproducible deployments
            f"databricks-connect=={get_distribution('databricks-connect').version}",
            f"mlflow=={get_distribution('mlflow').version}",
            f"databricks-langchain=={get_distribution('databricks-langchain').version}",
            f"langgraph=={get_distribution('langgraph').version}",
        ],
    )

# ==============================================================================
# STEP 3: Evaluate Agent Performance
# ==============================================================================

import mlflow
from mlflow.genai.scorers import RelevanceToQuery, Safety

# Define evaluation dataset with test queries
# Add more diverse test cases to comprehensively evaluate agent performance
eval_dataset = [
    {
        "inputs": {"messages": [{"role": "user", "content": "What is an LLM?"}]},
        "expected_response": None,  # Set to None for auto-evaluation, or provide expected responses
    }
    # TODO: Add more test cases covering different agent capabilities
]

# Evaluate the agent using MLflow's built-in scorers
# This helps assess the quality and safety of agent responses
eval_results = mlflow.genai.evaluate(
    data=eval_dataset,
    predict_fn=lambda messages: AGENT.predict({"messages": messages}),
    scorers=[
        RelevanceToQuery(),  # Measures how relevant responses are to the query
        Safety()  # Checks for potentially harmful or inappropriate content
    ],
)

# ==============================================================================
# STEP 4: Test Logged Model Locally
# ==============================================================================

# Test the logged model locally to ensure it works correctly before deployment
# This is crucial for catching issues early in the development process
mlflow.models.predict(
    model_uri=f"runs:/{logged_agent_info.run_id}/agent",  # Reference to the logged model
    input_data={"messages": [{"role": "user", "content": "Hello!"}]},  # Test input
    env_manager="uv",  # Use uv for faster dependency resolution
)

# ==============================================================================
# STEP 5: Register Model to Unity Catalog
# ==============================================================================

# Configure MLflow to use Unity Catalog as the model registry
# This enables centralized model governance and access control
mlflow.set_registry_uri("databricks-uc")

# Define Unity Catalog model location
# TODO: Replace these empty strings with your actual catalog, schema, and model names
catalog = ""  # e.g., "main" or your workspace catalog
schema = ""   # e.g., "ai_agents" or your schema name
model_name = ""  # e.g., "customer_support_agent" - descriptive model name
UC_MODEL_NAME = f"{catalog}.{schema}.{model_name}"

# Register the logged model to Unity Catalog
# This creates a versioned model that can be governed and accessed across the organization
uc_registered_model_info = mlflow.register_model(
    model_uri=logged_agent_info.model_uri,  # Source model from the MLflow run
    name=UC_MODEL_NAME  # Target location in Unity Catalog
)

# ==============================================================================
# STEP 6: Deploy Agent to Model Serving
# ==============================================================================

from databricks import agents

# Deploy the registered model to a Databricks Model Serving endpoint
# This creates a REST API endpoint that can serve the agent in production
agents.deploy(
    UC_MODEL_NAME,  # Model name in Unity Catalog
    uc_registered_model_info.version,  # Specific model version to deploy
    tags={"endpointSource": "docs"}  # Tags for tracking and organization
)

# ==============================================================================
# Additional Notes and Best Practices
# ==============================================================================

"""
Important considerations when using this script:

1. Resource Dependencies:
   - Ensure all tools in your agent have proper resource dependencies defined
   - Vector search indices must be properly configured and accessible
   - Unity Catalog functions must exist and have appropriate permissions

2. Model Versioning:
   - Each run creates a new model version in Unity Catalog
   - Use meaningful model names and tags for easier tracking
   - Consider implementing automated versioning strategies

3. Evaluation:
   - Expand the evaluation dataset with diverse test cases
   - Monitor evaluation metrics over time to track model performance
   - Consider adding custom scorers for domain-specific evaluation

4. Deployment:
   - Test thoroughly in development before production deployment
   - Monitor endpoint performance and costs after deployment
   - Implement proper error handling and logging in production

5. Security:
   - Ensure proper access controls are in place for Unity Catalog models
   - Review and audit model permissions regularly
   - Follow your organization's security guidelines for AI/ML deployments
"""