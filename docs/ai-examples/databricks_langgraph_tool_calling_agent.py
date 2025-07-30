# databricks_langgraph_tool_calling_agent.py
"""
Databricks LangGraph Tool-Calling Agent Implementation

This module demonstrates how to build a sophisticated AI agent using LangGraph and Databricks
that can call external tools and functions to enhance its capabilities beyond text generation.

Key Features:
- Tool-calling capabilities using Unity Catalog functions
- Vector search integration for RAG (Retrieval-Augmented Generation)
- Streaming and non-streaming response modes
- MLflow integration for model logging and serving
- Stateful conversation handling with LangGraph

Architecture:
1. Agent receives user messages and decides if tools are needed
2. If tools are required, agent calls appropriate tools and processes results
3. Agent provides final response incorporating tool outputs
4. Process repeats until no more tools are needed

Usage:
- Configure LLM endpoint and system prompt
- Add tools (UC functions, vector search, custom tools)
- Deploy using MLflow PyFunc for production serving

Prerequisites:
- Databricks workspace with Unity Catalog enabled
- Model serving endpoint for LLM
- Appropriate permissions for tool access

Based on: https://docs.databricks.com/aws/en/notebooks/source/generative-ai/langgraph-tool-calling-agent.html
Author: Databricks AI/ML Team
"""
# ==============================================================================
# IMPORTS AND DEPENDENCIES
# ==============================================================================

from typing import Any, Generator, Optional, Sequence, Union

# MLflow components for model logging and serving
import mlflow

# Databricks LangChain integrations
from databricks_langchain import (
    ChatDatabricks,          # Chat interface for Databricks LLM endpoints
    UCFunctionToolkit,       # Unity Catalog function toolkit for agent tools
    VectorSearchRetrieverTool,  # Vector search tool for RAG capabilities
)

# LangChain core components
from langchain_core.language_models import LanguageModelLike
from langchain_core.runnables import RunnableConfig, RunnableLambda
from langchain_core.tools import BaseTool

# LangGraph components for building stateful agents
from langgraph.graph import END, StateGraph
from langgraph.graph.graph import CompiledGraph
from langgraph.graph.state import CompiledStateGraph
from langgraph.prebuilt.tool_node import ToolNode

# MLflow LangGraph integration components
from mlflow.langchain.chat_agent_langgraph import ChatAgentState, ChatAgentToolNode
from mlflow.pyfunc import ChatAgent

# MLflow agent types for structured responses
from mlflow.types.agent import (
    ChatAgentChunk,     # For streaming responses
    ChatAgentMessage,   # Individual messages in conversation
    ChatAgentResponse,  # Complete agent response
    ChatContext,        # Context for agent execution
)
# ==============================================================================
# LLM CONFIGURATION
# ==============================================================================

# Configure the Language Model endpoint
# Replace with your actual Databricks Model Serving endpoint name
# Examples: "databricks-claude-3-7-sonnet", "databricks-gpt-4", "my-custom-llm"
LLM_ENDPOINT_NAME = "databricks-claude-3-7-sonnet"

# Initialize the chat model using Databricks LangChain integration
# This creates a connection to your deployed LLM endpoint
llm = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME)

# Define system prompt to guide agent behavior
# This sets the agent's personality, role, and operational guidelines
# TODO: Customize this prompt for your specific use case
system_prompt = """
You are a helpful AI assistant with access to various tools and data sources.
When users ask questions, use the available tools to provide accurate, 
up-to-date information. Always explain your reasoning and cite sources when applicable.

Guidelines:
- Use tools when you need specific data or calculations
- Be precise and factual in your responses
- If you're unsure about something, say so
- Keep responses clear and concise
- When using code execution tools, explain what the code does
- For data retrieval, summarize findings clearly
"""

# ==============================================================================
# AGENT TOOLS CONFIGURATION
# ==============================================================================

"""
Tools enable the agent to perform actions beyond text generation, such as:
- Data retrieval from databases or APIs
- Mathematical calculations and code execution
- Document search and retrieval (RAG)
- External system integrations

For comprehensive tool documentation, see:
https://docs.databricks.com/en/generative-ai/agent-framework/agent-tool.html
"""

# Initialize empty tools list - we'll populate this with various tool types
tools = []

# -----------------------------------------------------------------------------
# Unity Catalog Function Tools
# -----------------------------------------------------------------------------

# Unity Catalog functions can be used as agent tools, providing secure access
# to data processing capabilities. The system.ai.python_exec function provides
# a sandboxed Python code execution environment for calculations and analysis.

# TODO: Add additional UC function names as needed
# Examples: "my_catalog.my_schema.data_processor", "system.ai.sql_exec"
uc_tool_names = ["system.ai.python_exec"]

# Create toolkit from UC functions
uc_toolkit = UCFunctionToolkit(function_names=uc_tool_names)
tools.extend(uc_toolkit.tools)

# -----------------------------------------------------------------------------
# Vector Search Tools (RAG)
# -----------------------------------------------------------------------------

# Vector search tools enable retrieval-augmented generation (RAG) by allowing
# the agent to search through document embeddings for relevant context.
# 
# For detailed setup instructions, see:
# https://docs.databricks.com/en/generative-ai/agent-framework/unstructured-retrieval-tools.html

# TODO: Configure your vector search indexes
# Replace with your actual vector search index names and configure filters as needed
# 
# Example configuration:
# vector_search_tools = [
#     VectorSearchRetrieverTool(
#         index_name="my_catalog.my_schema.documents_index",
#         # Optional: Add metadata filters to restrict search scope
#         # filters="document_type = 'manual' AND department = 'engineering'"
#     ),
#     VectorSearchRetrieverTool(
#         index_name="my_catalog.my_schema.knowledge_base_index",
#         # You can add multiple indexes for different data sources
#     )
# ]
# tools.extend(vector_search_tools)

# -----------------------------------------------------------------------------
# Custom LangChain Tools
# -----------------------------------------------------------------------------

# You can also add custom LangChain tools for specific functionality
# See https://python.langchain.com/docs/concepts/tools for examples
#
# Example custom tools:
# from langchain_community.tools import DuckDuckGoSearchRun
# from langchain_community.tools.yahoo_finance_news import YahooFinanceNewsTool
# 
# custom_tools = [
#     DuckDuckGoSearchRun(),  # Web search capability
#     YahooFinanceNewsTool(),  # Financial data access
# ]
# tools.extend(custom_tools)

# ==============================================================================
# AGENT LOGIC IMPLEMENTATION
# ==============================================================================

def create_tool_calling_agent(
    model: LanguageModelLike,
    tools: Union[ToolNode, Sequence[BaseTool]],
    system_prompt: Optional[str] = None,
) -> CompiledGraph:
    """
    Creates a LangGraph-based tool-calling agent with the following workflow:
    
    1. Agent receives user messages and processes them with the LLM
    2. LLM decides whether to call tools based on the user's request
    3. If tools are needed, agent executes them and incorporates results
    4. Process repeats until no more tools are needed
    5. Agent provides final response to user
    
    Args:
        model: The language model to use for the agent (must support tool calling)
        tools: Collection of tools the agent can use
        system_prompt: Optional system prompt to guide agent behavior
        
    Returns:
        CompiledGraph: A runnable LangGraph agent ready for inference
        
    Example:
        >>> agent = create_tool_calling_agent(llm, tools, system_prompt)
        >>> response = agent.invoke({"messages": [{"role": "user", "content": "Hello!"}]})
    """
    # Bind tools to the model so it knows what tools are available for calling
    model = model.bind_tools(tools)

    def should_continue(state: ChatAgentState):
        """
        Determines the next step in the agent workflow based on the last message.
        
        Args:
            state: Current conversation state containing message history
            
        Returns:
            str: "continue" if tools need to be called, "end" if conversation is complete
        """
        messages = state["messages"]
        last_message = messages[-1]
        
        # Check if the LLM wants to call any tools
        # If tool_calls are present, we need to execute them before responding
        if last_message.get("tool_calls"):
            return "continue"  # Go to tools node
        else:
            return "end"  # End the conversation

    # Set up message preprocessing to include system prompt if provided
    if system_prompt:
        # Prepend system prompt to conversation history
        preprocessor = RunnableLambda(
            lambda state: [{"role": "system", "content": system_prompt}]
            + state["messages"]
        )
    else:
        # Use messages as-is without system prompt
        preprocessor = RunnableLambda(lambda state: state["messages"])
    
    # Create the model runnable with preprocessing
    model_runnable = preprocessor | model

    def call_model(
        state: ChatAgentState,
        config: RunnableConfig,
    ):
        """
        Calls the language model with the current conversation state.
        
        Args:
            state: Current conversation state with message history
            config: Runtime configuration for the model call
            
        Returns:
            dict: Updated state with the model's response
        """
        # Invoke the model with current conversation state
        response = model_runnable.invoke(state, config)
        
        # Return updated state with model response added to messages
        return {"messages": [response]}

    # -----------------------------------------------------------------------------
    # Build the LangGraph Workflow
    # -----------------------------------------------------------------------------
    
    # Create a state graph with ChatAgentState to track conversation history
    workflow = StateGraph(ChatAgentState)

    # Add nodes to the workflow
    workflow.add_node("agent", RunnableLambda(call_model))  # LLM processing node
    workflow.add_node("tools", ChatAgentToolNode(tools))    # Tool execution node

    # Set the agent as the entry point for all conversations
    workflow.set_entry_point("agent")
    
    # Add conditional edges from agent node based on tool calling decision
    workflow.add_conditional_edges(
        "agent",           # Source node
        should_continue,   # Decision function
        {
            "continue": "tools",  # If tools needed, go to tools node
            "end": END,          # If no tools needed, end conversation
        },
    )
    
    # After tools are executed, always return to agent for response generation
    workflow.add_edge("tools", "agent")

    # Compile the workflow into an executable graph
    return workflow.compile()


# ==============================================================================
# CHAT AGENT WRAPPER CLASS
# ==============================================================================

class LangGraphChatAgent(ChatAgent):
    """
    MLflow-compatible wrapper for LangGraph agents.
    
    This class provides the standard MLflow ChatAgent interface while internally
    using a LangGraph-based agent for processing. It supports both streaming
    and non-streaming responses, making it suitable for various deployment scenarios.
    
    Key Features:
    - MLflow PyFunc compatibility for model serving
    - Streaming and non-streaming response modes
    - Automatic message format conversion
    - State management through LangGraph
    
    Args:
        agent: Compiled LangGraph agent (from create_tool_calling_agent)
        
    Example:
        >>> compiled_agent = create_tool_calling_agent(llm, tools, system_prompt)
        >>> chat_agent = LangGraphChatAgent(compiled_agent)
        >>> response = chat_agent.predict([ChatAgentMessage(role="user", content="Hello!")])
    """
    
    def __init__(self, agent: CompiledStateGraph):
        """
        Initialize the chat agent wrapper.
        
        Args:
            agent: Compiled LangGraph state graph from create_tool_calling_agent
        """
        self.agent = agent

    def predict(
        self,
        messages: list[ChatAgentMessage],
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[dict[str, Any]] = None,
    ) -> ChatAgentResponse:
        """
        Generate a complete response to the given messages.
        
        This method processes the entire conversation through the LangGraph agent
        and returns the complete response once all tool calls and reasoning are finished.
        
        Args:
            messages: List of chat messages forming the conversation history
            context: Optional context for the agent (currently unused)
            custom_inputs: Optional custom inputs (currently unused)
            
        Returns:
            ChatAgentResponse: Complete response with all messages from the conversation
            
        Example:
            >>> messages = [ChatAgentMessage(role="user", content="What's 2+2?")]
            >>> response = agent.predict(messages)
            >>> print(response.messages[-1].content)  # "4"
        """
        # Convert MLflow message format to LangGraph format
        request = {"messages": self._convert_messages_to_dict(messages)}

        # Collect all messages from the agent execution
        response_messages = []
        
        # Stream through the agent execution to collect all intermediate steps
        for event in self.agent.stream(request, stream_mode="updates"):
            for node_data in event.values():
                # Extract messages from each node execution
                response_messages.extend(
                    ChatAgentMessage(**msg) for msg in node_data.get("messages", [])
                )
        
        # Return complete response with all conversation messages
        return ChatAgentResponse(messages=response_messages)

    def predict_stream(
        self,
        messages: list[ChatAgentMessage],
        context: Optional[ChatContext] = None,
        custom_inputs: Optional[dict[str, Any]] = None,
    ) -> Generator[ChatAgentChunk, None, None]:
        """
        Generate a streaming response to the given messages.
        
        This method yields response chunks as they become available during agent
        execution, enabling real-time streaming of the agent's reasoning process
        and tool usage.
        
        Args:
            messages: List of chat messages forming the conversation history
            context: Optional context for the agent (currently unused)
            custom_inputs: Optional custom inputs (currently unused)
            
        Yields:
            ChatAgentChunk: Individual message chunks as they become available
            
        Example:
            >>> messages = [ChatAgentMessage(role="user", content="Explain AI")]
            >>> for chunk in agent.predict_stream(messages):
            ...     print(chunk.delta.content, end="", flush=True)
        """
        # Convert MLflow message format to LangGraph format
        request = {"messages": self._convert_messages_to_dict(messages)}
        
        # Stream agent execution and yield chunks as they become available
        for event in self.agent.stream(request, stream_mode="updates"):
            for node_data in event.values():
                # Yield each message as a streaming chunk
                yield from (
                    ChatAgentChunk(**{"delta": msg}) for msg in node_data["messages"]
                )


# ==============================================================================
# AGENT INITIALIZATION AND MLFLOW CONFIGURATION
# ==============================================================================

# Enable MLflow autologging for LangChain components
# This automatically tracks model parameters, metrics, and artifacts
mlflow.langchain.autolog()

# Create the compiled LangGraph agent with configured LLM, tools, and system prompt
agent = create_tool_calling_agent(llm, tools, system_prompt)

# Wrap the LangGraph agent in MLflow-compatible interface
# This AGENT object will be used for inference when the model is loaded
AGENT = LangGraphChatAgent(agent)

# Register the agent with MLflow for model serving
# This enables the agent to be served via Databricks Model Serving endpoints
mlflow.models.set_model(AGENT)

# ==============================================================================
# USAGE EXAMPLES AND NEXT STEPS
# ==============================================================================

"""
Example Usage:

1. Local Testing:
   >>> messages = [ChatAgentMessage(role="user", content="What is 2+2?")]
   >>> response = AGENT.predict(messages)
   >>> print(response.messages[-1].content)

2. Streaming Example:
   >>> for chunk in AGENT.predict_stream(messages):
   ...     print(chunk.delta.content, end="", flush=True)

Next Steps:
1. Customize the system prompt for your specific use case
2. Add relevant tools (UC functions, vector search indexes, custom tools)
3. Test the agent locally to ensure it works as expected
4. Use mlflow_pyfunc_log_and_deploy_agent.py to deploy to production

For deployment, see:
- mlflow_pyfunc_log_and_deploy_agent.py in this directory
- Databricks documentation: https://docs.databricks.com/generative-ai/agents/

Troubleshooting:
- Ensure your LLM endpoint supports tool calling
- Verify tool configurations and permissions
- Check that all required dependencies are installed
- Test tools individually before adding to the agent
"""
