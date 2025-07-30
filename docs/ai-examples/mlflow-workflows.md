# MLflow Workflows for Databricks

## Experiment Tracking
- Use MLflow 3 for all model experiments
- Implement proper parameter logging
- Track model artifacts and metrics
- Set up automated model evaluation


## Model Registry
- Register models with proper versioning
- Implement staging and production workflows
- Set up automated model deployment
- Monitor model performance and drift

## MLflow Chat Agents

Use the MLflow `ChatAgent` interface to build production-ready chat agents on Databricks. `ChatAgent` supports multi-agent workflows, tool-calling, streaming responses, and integrates with Databricks monitoring and evaluation tools.

**Benefits:**
- Multi-agent and tool-calling support
- Streaming and intermediate message handling
- Easy deployment, monitoring, and evaluation
- Framework-agnostic and type-safe authoring

**Example:**  
See `mlflow_chat_agent.py` for a full example of wrapping an agent with `ChatAgent`.

```python
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatAgentResponse, ChatAgentChunk

class MyWrappedAgent(ChatAgent):
    def predict(self, messages, context=None, custom_inputs=None):
        # Convert messages to your agent's format
        agent_input = ...  # build from messages
        agent_output = self.agent.invoke(agent_input)
        
        return ChatAgentResponse(
            messages=[
                ChatAgentMessage(
                    role="assistant",
                    content=agent_output,
                    id=str(uuid.uuid4()),
                )
            ]
        )
    
    def predict_stream(self, messages, context=None, custom_inputs=None):
        # Stream responses for real-time interaction
        for chunk in self.agent.stream(...):
            yield ChatAgentChunk(
                delta=ChatAgentMessage(
                    role="assistant",
                    content=chunk,
                    id=str(uuid.uuid4())
                )
            )
```

## MLflow Tracing for GenAI Apps

MLflow Tracing lets you easily capture and analyze GenAI app execution, including all LLM and tool calls, for debugging and optimization.

### Key Features

- **@mlflow.trace decorator**: Automatically records your app's execution, including nested LLM/tool calls.
- **Autologging**: Use `mlflow.openai.autolog()` to capture all LLM calls in traces.
- **Trace Visualization**: View traces in the Databricks UI or with MLflow's Python API.

### Example

Here's how to trace a simple chat app:

```python
# Use the trace decorator to capture the application's entry point
@mlflow.trace
def my_app(input: str):
    # This call is automatically instrumented by `mlflow.openai.autolog()`
    response = client.chat.completions.create(
        model=model_name,  # This example uses a Databricks hosted LLM - you can replace this with any AI Gateway or Model Serving endpoint. If you provide your own OpenAI credentials, replace with a valid OpenAI model e.g., gpt-4o, etc.
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": input,
            },
        ],
    )
    return response.choices[0].message.content

result = my_app(input="What is MLflow?")
print(result)
```
## MLflow Evaluation

MLflow Evaluation enables you to systematically assess the quality and safety of GenAI model outputs using production traces or curated datasets. You can create evaluation datasets, add records (such as traces from your application), and apply built-in or custom scorers to measure metrics like relevance, groundedness, and safety.

**Typical workflow:**
1. **Create an evaluation dataset** in Unity Catalog.
2. **Collect traces** from your GenAI application (e.g., recent production runs).
3. **Add traces to the evaluation dataset** for analysis.
4. **Preview and analyze** the dataset, then apply evaluation scorers to generate metrics.

This process helps you monitor and improve your GenAI workflows by providing actionable insights into model performance and safety.


```python
import mlflow
import mlflow.genai.datasets
import time
from databricks.connect import DatabricksSession

# 0. If you are using a local development environment, connect to Serverless Spark which powers MLflow's evaluation dataset service
spark = DatabricksSession.builder.remote(serverless=True).getOrCreate()

# 1. Create an evaluation dataset

# Replace with a Unity Catalog schema where you have CREATE TABLE permission
uc_schema = "workspace.default"
# This table will be created in the above UC schema
evaluation_dataset_table_name = "email_generation_eval"

eval_dataset = mlflow.genai.datasets.create_dataset(
    uc_table_name=f"{uc_schema}.{evaluation_dataset_table_name}",
)
print(f"Created evaluation dataset: {uc_schema}.{evaluation_dataset_table_name}")

# 2. Search for the simulated production traces from step 2: get traces from the last 20 minutes with our trace name.
ten_minutes_ago = int((time.time() - 10 * 60) * 1000)

traces = mlflow.search_traces(
    filter_string=f"attributes.timestamp_ms > {ten_minutes_ago} AND "
                 f"attributes.status = 'OK' AND "
                 f"tags.`mlflow.traceName` = 'generate_sales_email'",
    order_by=["attributes.timestamp_ms DESC"]
)

print(f"Found {len(traces)} successful traces from beta test")

# 3. Add the traces to the evaluation dataset
eval_dataset.merge_records(traces)
print(f"Added {len(traces)} records to evaluation dataset")

# Preview the dataset
df = eval_dataset.to_df()
print(f"\nDataset preview:")
print(f"Total records: {len(df)}")
print("\nSample record:")
sample = df.iloc[0]
print(f"Inputs: {sample['inputs']}")

from mlflow.genai.scorers import (
    RetrievalGroundedness,
    RelevanceToQuery,
    Safety,
    Guidelines,
)

# Save the scorers as a variable so we can re-use them in step 7

email_scorers = [
        RetrievalGroundedness(),  # Checks if email content is grounded in retrieved data
        Guidelines(
            name="follows_instructions",
            guidelines="The generated email must follow the user_instructions in the request.",
        ),
        Guidelines(
            name="concise_communication",
            guidelines="The email MUST be concise and to the point. The email should communicate the key message efficiently without being overly brief or losing important context.",
        ),
        Guidelines(
            name="mentions_contact_name",
            guidelines="The email MUST explicitly mention the customer contact's first name (e.g., Alice, Bob, Carol) in the greeting. Generic greetings like 'Hello' or 'Dear Customer' are not acceptable.",
        ),
        Guidelines(
            name="professional_tone",
            guidelines="The email must be in a professional tone.",
        ),
        Guidelines(
            name="includes_next_steps",
            guidelines="The email MUST end with a specific, actionable next step that includes a concrete timeline.",
        ),
        RelevanceToQuery(),  # Checks if email addresses the user's request
        Safety(),  # Checks for harmful or inappropriate content
    ]

# Run evaluation with predefined scorers
eval_results = mlflow.genai.evaluate(
    data=eval_dataset,
    predict_fn=generate_sales_email,
    scorers=email_scorers,
)

eval_traces = mlflow.search_traces(run_id=eval_results.run_id)

# eval_traces is a Pandas DataFrame that has the evaluated traces.  The column `assessments` includes each scorer's feedback.
print(eval_traces)
```

## Monitor quality in production

### The code below sets up an external monitor in Databricks to automatically assess production model outputs using built-in and custom guidelines. It configures a suite of quality checks (e.g., safety, groundedness, relevance, and brand tone) that are applied to a sample of responses, storing results in a Unity Catalog table for ongoing monitoring and analysis.


```python
# These packages are automatically installed with mlflow[databricks]
from databricks.agents.monitoring import create_external_monitor, AssessmentsSuiteConfig, BuiltinJudge, GuidelinesJudge

external_monitor = create_external_monitor(
    # Change to a Unity Catalog schema where you have CREATE TABLE permissions.
    catalog_name="workspace",
    schema_name="default",
    assessments_config=AssessmentsSuiteConfig(
        sample=1.0,  # sampling rate
        assessments=[
            # Predefined scorers "safety", "groundedness", "relevance_to_query", "chunk_relevance"
            BuiltinJudge(name="safety"),  # or {'name': 'safety'}
            BuiltinJudge(
                name="groundedness", sample_rate=0.4
            ),  # or {'name': 'groundedness', 'sample_rate': 0.4}
            BuiltinJudge(
                name="relevance_to_query"
            ),  # or {'name': 'relevance_to_query'}
            BuiltinJudge(name="chunk_relevance"),  # or {'name': 'chunk_relevance'}
            # Guidelines can refer to the request and response.
            GuidelinesJudge(
                guidelines={
                    # You can have any number of guidelines, each defined as a key-value pair.
                    "mlflow_only": [
                        "If the request is unrelated to MLflow, the response must refuse to answer."
                    ],  # Must be an array of strings
                    "customer_service_tone": [
                        """The response must maintain our brand voice which is:
    - Professional yet warm and conversational (avoid corporate jargon)
    - Empathetic, acknowledging emotional context before jumping to solutions
    - Proactive in offering help without being pushy

    Specifically:
    - If the customer expresses frustration, anger, or disappointment, the first sentence must acknowledge their emotion
    - The response must use "I" statements to take ownership (e.g., "I understand" not "We understand")
    - The response must avoid phrases that minimize concerns like "simply", "just", or "obviously"
    - The response must end with a specific next step or open-ended offer to help, not generic closings"""
                    ],
                }
            ),
        ],
    ),
)

print(external_monitor)
```

## Helpful documentation
- Get Started with MLflow 3: https://docs.databricks.com/aws/en/mlflow/mlflow-3-install
- MLflow 3 for GenAI: https://docs.databricks.com/aws/en/mlflow3/genai
- MLflow 3 GenAI API Docs: https://mlflow.org/docs/latest/api_reference/python_api/mlflow.genai.html
- MLflow 3 Tracing API Docs: https://mlflow.org/docs/latest/api_reference/python_api/mlflow.tracing.html
