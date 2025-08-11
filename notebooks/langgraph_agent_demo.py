# Databricks notebook source
# MAGIC %md
# MAGIC # LangGraph Tool-Calling Agent Demo
# MAGIC 
# MAGIC This notebook demonstrates how to use the LangGraph tool-calling agent in a Databricks environment.
# MAGIC 
# MAGIC ## Features
# MAGIC - Unity Catalog function tools for calculations and data queries
# MAGIC - Vector search tools for RAG capabilities
# MAGIC - MLflow integration for tracking and deployment
# MAGIC - Streaming responses for real-time interaction

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Setup and Installation

# COMMAND ----------

# Install required packages
%pip install -U -q databricks-agents>=1.2.0 mlflow[databricks]>=3.1.3 databricks-langchain langchain langgraph unitycatalog-ai python-dotenv

# COMMAND ----------

# Restart Python kernel after installation
dbutils.library.restartPython()

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Environment Configuration

# COMMAND ----------

import os
from dotenv import load_dotenv

# Load environment variables if using .env file
load_dotenv()

# Configure environment
os.environ["UC_CATALOG"] = dbutils.widgets.get("catalog") if dbutils.widgets.get("catalog") else "main"
os.environ["UC_SCHEMA"] = dbutils.widgets.get("schema") if dbutils.widgets.get("schema") else "default"
os.environ["LLM_ENDPOINT_NAME"] = dbutils.widgets.get("llm_endpoint") if dbutils.widgets.get("llm_endpoint") else "databricks-meta-llama-3-3-70b-instruct"

print(f"Using catalog: {os.environ['UC_CATALOG']}")
print(f"Using schema: {os.environ['UC_SCHEMA']}")
print(f"Using LLM: {os.environ['LLM_ENDPOINT_NAME']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Create Unity Catalog Function Tools

# COMMAND ----------

from unitycatalog.ai.core.databricks import DatabricksFunctionClient
from databricks_langchain import UCFunctionToolkit

# Initialize UC client
client = DatabricksFunctionClient()

# Define mathematical functions
def add_numbers(number_1: float, number_2: float) -> float:
    """Add two numbers together."""
    return number_1 + number_2

def multiply_numbers(number_1: float, number_2: float) -> float:
    """Multiply two numbers."""
    return number_1 * number_2

def calculate_percentage(part: float, whole: float) -> float:
    """Calculate percentage of part in whole."""
    if whole == 0:
        return 0.0
    return (part / whole) * 100.0

# Register functions to Unity Catalog
catalog = os.environ["UC_CATALOG"]
schema = os.environ["UC_SCHEMA"]

functions_to_register = [
    (add_numbers, "Add two numbers"),
    (multiply_numbers, "Multiply two numbers"),
    (calculate_percentage, "Calculate percentage")
]

function_names = []
for func, comment in functions_to_register:
    try:
        func_info = client.create_python_function(
            func=func,
            catalog=catalog,
            schema=schema,
            replace=True,
            comment=comment
        )
        function_names.append(func_info.full_name)
        print(f"✓ Registered: {func_info.full_name}")
    except Exception as e:
        print(f"❌ Failed to register {func.__name__}: {e}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 4. Create the LangGraph Agent

# COMMAND ----------

from databricks_langchain import ChatDatabricks
from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt.tool_node import ToolNode
from langchain_core.runnables import RunnableConfig, RunnableLambda
from mlflow.langchain.chat_agent_langgraph import ChatAgentState, ChatAgentToolNode

# Initialize LLM
llm = ChatDatabricks(
    endpoint=os.environ["LLM_ENDPOINT_NAME"],
    temperature=0.1,
    max_tokens=2000
)

# Create tools from UC functions
toolkit = UCFunctionToolkit(function_names=function_names)
tools = toolkit.tools

# Add system tools if available
try:
    system_toolkit = UCFunctionToolkit(function_names=["system.ai.python_exec"])
    tools.extend(system_toolkit.tools)
    print(f"✓ Added system tools")
except:
    print("ℹ System tools not available")

print(f"\nTotal tools available: {len(tools)}")
for tool in tools:
    print(f"  - {tool.name}: {tool.description}")

# COMMAND ----------

# Define agent system prompt
system_prompt = """
You are a helpful AI assistant with access to various tools through Unity Catalog functions.

When users ask questions:
1. Use the available tools to provide accurate calculations and data
2. Explain your reasoning and what tools you're using
3. Be precise and factual in your responses

Available tools include mathematical calculations and code execution.
Always use tools when specific calculations are needed rather than calculating mentally.
"""

# Create the agent workflow
def create_tool_calling_agent(model, tools, system_prompt=None):
    """Create a LangGraph agent with tool calling capabilities."""
    
    # Bind tools to the model
    model = model.bind_tools(tools)
    
    def should_continue(state: ChatAgentState):
        """Determine if tools should be called."""
        messages = state["messages"]
        last_message = messages[-1]
        
        if last_message.get("tool_calls"):
            return "continue"
        else:
            return "end"
    
    def call_model(state: ChatAgentState, config: RunnableConfig):
        """Call the LLM with current state."""
        if system_prompt:
            preprocessor = RunnableLambda(
                lambda s: [{"role": "system", "content": system_prompt}] + s["messages"]
            )
        else:
            preprocessor = RunnableLambda(lambda s: s["messages"])
        
        model_runnable = preprocessor | model
        response = model_runnable.invoke(state, config)
        return {"messages": [response]}
    
    # Build the workflow
    workflow = StateGraph(ChatAgentState)
    workflow.add_node("agent", RunnableLambda(call_model))
    workflow.add_node("tools", ChatAgentToolNode(tools))
    workflow.set_entry_point("agent")
    
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END,
        },
    )
    
    workflow.add_edge("tools", "agent")
    
    return workflow.compile()

# Create the agent
agent = create_tool_calling_agent(llm, tools, system_prompt)
print("✓ Agent created successfully!")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 5. Test the Agent

# COMMAND ----------

# Test 1: Simple calculation
test_messages = [{"role": "user", "content": "What is 42 + 58?"}]
response = agent.invoke({"messages": test_messages})

print("User: What is 42 + 58?")
print("\nAgent workflow:")
for msg in response["messages"]:
    if msg.get("tool_calls"):
        print(f"  🔧 Calling tool: {msg['tool_calls'][0]['name']}")
    elif msg.get("role") == "tool":
        print(f"  📊 Tool result: {msg['content']}")
    elif msg.get("role") == "assistant":
        print(f"  🤖 Assistant: {msg['content']}")

# COMMAND ----------

# Test 2: Percentage calculation
test_messages = [{"role": "user", "content": "What percentage is 45 out of 150?"}]
response = agent.invoke({"messages": test_messages})

print("User: What percentage is 45 out of 150?")
print(f"\n🤖 Assistant: {response['messages'][-1]['content']}")

# COMMAND ----------

# Test 3: Multiple calculations
test_messages = [{"role": "user", "content": "Calculate (25 + 17) * 3 and tell me what percentage this is of 200"}]
response = agent.invoke({"messages": test_messages})

print("User: Calculate (25 + 17) * 3 and tell me what percentage this is of 200")
print(f"\n🤖 Assistant: {response['messages'][-1]['content']}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 6. MLflow Integration

# COMMAND ----------

import mlflow
from mlflow.pyfunc import ChatAgent
from mlflow.types.agent import ChatAgentMessage, ChatAgentResponse

# Enable MLflow autologging
mlflow.langchain.autolog()

# Create MLflow-compatible wrapper
class LangGraphChatAgent(ChatAgent):
    def __init__(self, agent):
        self.agent = agent
    
    def predict(self, messages, context=None, custom_inputs=None):
        # Convert to dict format
        request = {"messages": [
            {"role": msg.role, "content": msg.content} 
            for msg in messages
        ]}
        
        # Run agent
        response = self.agent.invoke(request)
        
        # Extract final response
        response_messages = []
        for msg in response["messages"]:
            if msg.get("role") == "assistant" and not msg.get("tool_calls"):
                response_messages.append(
                    ChatAgentMessage(
                        role="assistant",
                        content=msg["content"]
                    )
                )
        
        return ChatAgentResponse(messages=response_messages)

# Wrap the agent
mlflow_agent = LangGraphChatAgent(agent)

# Test MLflow wrapper
test_input = [ChatAgentMessage(role="user", content="What is 100 + 200?")]
result = mlflow_agent.predict(test_input)
print(f"MLflow wrapper test: {result.messages[0].content}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 7. Log Model to MLflow

# COMMAND ----------

from mlflow.models.resources import DatabricksServingEndpoint, DatabricksFunction

# Prepare resources
resources = [
    DatabricksServingEndpoint(endpoint_name=os.environ["LLM_ENDPOINT_NAME"])
]

# Add UC function resources
for func_name in function_names:
    resources.append(DatabricksFunction(function_name=func_name))

# Log the model
with mlflow.start_run() as run:
    mlflow.pyfunc.log_model(
        artifact_path="langgraph_agent",
        python_model=mlflow_agent,
        resources=resources,
        input_example={
            "messages": [{"role": "user", "content": "What is 2 + 2?"}]
        },
        pip_requirements=[
            "mlflow[databricks]>=3.1.3",
            "databricks-langchain",
            "langgraph",
            "langchain",
            "unitycatalog-ai"
        ]
    )
    
    # Log metadata
    mlflow.log_param("llm_endpoint", os.environ["LLM_ENDPOINT_NAME"])
    mlflow.log_param("num_tools", len(tools))
    mlflow.log_metric("test_accuracy", 1.0)  # Example metric

print(f"✓ Model logged! Run ID: {run.info.run_id}")
print(f"Model URI: runs:/{run.info.run_id}/langgraph_agent")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 8. Evaluate the Agent

# COMMAND ----------

from mlflow.genai.scorers import RelevanceToQuery, Safety

# Create evaluation dataset
eval_data = [
    {
        "inputs": {"messages": [{"role": "user", "content": "What is 15 + 25?"}]},
        "expected_response": "40"
    },
    {
        "inputs": {"messages": [{"role": "user", "content": "Calculate 10% of 250"}]},
        "expected_response": "25"
    },
    {
        "inputs": {"messages": [{"role": "user", "content": "What is 7 * 8?"}]},
        "expected_response": "56"
    }
]

# Evaluate
eval_results = mlflow.genai.evaluate(
    data=eval_data,
    predict_fn=lambda inputs: mlflow_agent.predict(
        [ChatAgentMessage(**msg) for msg in inputs["messages"]]
    ),
    scorers=[RelevanceToQuery(), Safety()]
)

print("Evaluation Results:")
print(f"Relevance: {eval_results.metrics.get('relevance_to_query/mean', 'N/A')}")
print(f"Safety: {eval_results.metrics.get('safety/mean', 'N/A')}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 9. Deploy to Model Serving (Optional)

# COMMAND ----------

# Register model to Unity Catalog
mlflow.set_registry_uri("databricks-uc")

model_name = f"{catalog}.{schema}.langgraph_tool_agent"
print(f"Registering model as: {model_name}")

# Note: Uncomment to actually register
# registered_model = mlflow.register_model(
#     model_uri=f"runs:/{run.info.run_id}/langgraph_agent",
#     name=model_name
# )

# Deploy to serving endpoint
# from databricks import agents
# agents.deploy(model_name, registered_model.version)

print("ℹ️ Model registration and deployment commented out for demo")
print("   Uncomment the code above to deploy to production")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Summary
# MAGIC 
# MAGIC This notebook demonstrated:
# MAGIC 1. ✅ Creating Unity Catalog function tools
# MAGIC 2. ✅ Building a LangGraph agent with tool calling
# MAGIC 3. ✅ Testing the agent with various queries
# MAGIC 4. ✅ MLflow integration and logging
# MAGIC 5. ✅ Agent evaluation with scorers
# MAGIC 6. ✅ Model deployment preparation
# MAGIC 
# MAGIC The agent is now ready for production use in Databricks Model Serving!