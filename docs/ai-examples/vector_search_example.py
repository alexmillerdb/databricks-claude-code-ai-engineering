"""
Databricks Vector Search Client Documentation
===========================================

This module demonstrates comprehensive usage of Databricks Vector Search with LangChain
for building intelligent retrieval-augmented generation (RAG) applications.

Prerequisites:
- Databricks workspace with Vector Search enabled
- Vector Search index created and populated with data
- Proper authentication (workspace token or service principal)
- Required packages: databricks-langchain, langchain

Vector Search Index Types:
1. Delta Sync Index: Auto-sync with Delta tables, managed embeddings
2. Direct Vector Access Index: Direct vector uploads, self-managed embeddings
3. Hybrid Index: Combines semantic and keyword search

For more information, visit: https://docs.databricks.com/en/generative-ai/vector-search.html
"""

from databricks_langchain import VectorSearchRetrieverTool, ChatDatabricks, DatabricksEmbeddings
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.prompts import ChatPromptTemplate
import os

# =============================================================================
# BASIC USAGE EXAMPLE
# =============================================================================

def basic_vector_search_example():
    """
    Basic example showing how to use VectorSearchRetrieverTool for simple queries.
    Best for Delta Sync indexes with managed embeddings.
    """
    print("=== Basic Vector Search Example ===")
    
    # Initialize the retriever tool with minimal configuration
    vs_tool = VectorSearchRetrieverTool(
        index_name="catalog.schema.my_databricks_docs_index",  # Replace with your index
        tool_name="databricks_docs_retriever",
        tool_description="Retrieves information about Databricks products from official documentation."
    )
    
    # Test the retriever directly
    try:
        results = vs_tool.invoke("What is Databricks Agent Framework?")
        print(f"Retrieved {len(results)} results")
        for i, result in enumerate(results[:2]):  # Show first 2 results
            print(f"Result {i+1}: {result}")
    except Exception as e:
        print(f"Error during search: {e}")
    
    return vs_tool

# =============================================================================
# ADVANCED CONFIGURATION EXAMPLE
# =============================================================================

def advanced_vector_search_example():
    """
    Advanced example with custom embeddings and detailed configuration.
    Required for Direct Vector Access indexes or self-managed embeddings.
    """
    print("=== Advanced Vector Search Example ===")
    
    # Initialize custom embedding model
    embedding_model = DatabricksEmbeddings(
        endpoint="databricks-bge-large-en",  # Use your embedding endpoint
        # target_uri="databricks",  # Uncomment if using external Databricks workspace
    )
    
    # Create retriever with advanced configuration
    vs_tool = VectorSearchRetrieverTool(
        index_name="catalog.schema.index_name",  # Replace with your index
        num_results=5,  # Maximum number of documents to retrieve
        columns=["id", "content", "source", "metadata"],  # Columns to return
        filters={"source": "databricks_docs"},  # Optional filters for search
        query_type="HYBRID",  # Options: "ANN" (semantic), "HYBRID" (semantic + keyword)
        tool_name="advanced_databricks_retriever",
        tool_description="Advanced retriever for Databricks documentation with filtering and hybrid search",
        text_column="content",  # Column containing the text for embeddings
        embedding=embedding_model,  # Required for direct-access or self-managed embeddings
    )
    
    return vs_tool

# =============================================================================
# LLM INTEGRATION WITH TOOL CALLING
# =============================================================================

def llm_with_vector_search():
    """
    Demonstrates integration of vector search with LLM for conversational AI.
    """
    print("=== LLM + Vector Search Integration ===")
    
    # Initialize vector search tool
    vs_tool = basic_vector_search_example()
    
    # Initialize Databricks LLM
    llm = ChatDatabricks(
        endpoint="databricks-claude-3-7-sonnet",  # Replace with your endpoint
        max_tokens=1000,
        temperature=0.1,
    )
    
    # Bind tools to LLM for direct tool calling
    llm_with_tools = llm.bind_tools([vs_tool])
    
    # Test direct tool calling
    try:
        response = llm_with_tools.invoke(
            "Based on the Databricks documentation, explain what Vector Search is and how it works."
        )
        print("LLM Response with tool calling:")
        print(response.content)
    except Exception as e:
        print(f"Error during LLM tool calling: {e}")
    
    return llm_with_tools

# =============================================================================
# AGENT FRAMEWORK EXAMPLE
# =============================================================================

def create_vector_search_agent():
    """
    Creates a conversational agent using vector search for RAG capabilities.
    """
    print("=== Vector Search Agent Example ===")
    
    # Initialize components
    vs_tool = advanced_vector_search_example()
    llm = ChatDatabricks(endpoint="databricks-claude-3-7-sonnet")
    
    # Create agent prompt template
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a helpful Databricks expert assistant. Use the vector search tool to find 
        relevant information from Databricks documentation to answer user questions accurately. 
        Always cite your sources when providing information."""),
        ("user", "{input}"),
        ("assistant", "{agent_scratchpad}"),
    ])
    
    # Create agent
    agent = create_tool_calling_agent(llm, [vs_tool], prompt)
    agent_executor = AgentExecutor(agent=agent, tools=[vs_tool], verbose=True)
    
    # Test the agent
    try:
        response = agent_executor.invoke({
            "input": "How do I create and manage a vector search index in Databricks?"
        })
        print("Agent Response:")
        print(response["output"])
    except Exception as e:
        print(f"Error during agent execution: {e}")
    
    return agent_executor

# =============================================================================
# ERROR HANDLING AND BEST PRACTICES
# =============================================================================

def vector_search_with_error_handling():
    """
    Demonstrates proper error handling and validation for vector search operations.
    """
    print("=== Error Handling Best Practices ===")
    
    try:
        # Validate environment variables
        if not os.getenv("DATABRICKS_HOST") and not os.getenv("DATABRICKS_TOKEN"):
            print("Warning: Databricks authentication not configured")
        
        # Initialize with validation
        vs_tool = VectorSearchRetrieverTool(
            index_name="catalog.schema.my_index",
            tool_name="safe_retriever",
            tool_description="Safely retrieves information with error handling",
            num_results=3,  # Conservative number for faster responses
        )
        
        # Test with different query types
        test_queries = [
            "What is machine learning?",
            "",  # Empty query test
            "very_specific_technical_term_that_might_not_exist",
        ]
        
        for query in test_queries:
            try:
                if not query.strip():
                    print("Skipping empty query")
                    continue
                    
                print(f"Testing query: '{query}'")
                results = vs_tool.invoke(query)
                
                if results:
                    print(f"  ✓ Found {len(results)} results")
                else:
                    print("  ⚠ No results found")
                    
            except Exception as query_error:
                print(f"  ✗ Query failed: {query_error}")
                
    except Exception as setup_error:
        print(f"Setup error: {setup_error}")
        print("Check your index name, authentication, and network connectivity")

# =============================================================================
# PERFORMANCE OPTIMIZATION TIPS
# =============================================================================

def performance_optimization_example():
    """
    Demonstrates performance optimization techniques for vector search.
    """
    print("=== Performance Optimization ===")
    
    # Optimized configuration for performance
    vs_tool = VectorSearchRetrieverTool(
        index_name="catalog.schema.optimized_index",
        num_results=3,  # Lower number for faster responses
        columns=["id", "text"],  # Minimal columns to reduce data transfer
        query_type="ANN",  # Faster than HYBRID for pure semantic search
        tool_name="fast_retriever",
        tool_description="Optimized retriever for fast responses",
    )
    
    print("Performance Tips:")
    print("1. Use fewer num_results for faster queries")
    print("2. Limit columns to only what you need")
    print("3. Use ANN query type for pure semantic search")
    print("4. Apply filters to reduce search space")
    print("5. Consider caching for frequently asked questions")
    
    return vs_tool

# =============================================================================
# EXAMPLE USAGE
# =============================================================================

if __name__ == "__main__":
    """
    Run examples to demonstrate different vector search capabilities.
    Uncomment the examples you want to test.
    """
    
    # Basic usage
    basic_vector_search_example()
    
    # Advanced configuration
    # advanced_vector_search_example()
    
    # LLM integration
    # llm_with_vector_search()
    
    # Agent framework
    # create_vector_search_agent()
    
    # Error handling
    # vector_search_with_error_handling()
    
    # Performance optimization
    # performance_optimization_example()
    
    print("\n=== Documentation Complete ===")
    print("Remember to:")
    print("1. Replace index names with your actual indexes")
    print("2. Configure proper authentication")
    print("3. Test with your specific data and use case")
    print("4. Monitor performance and adjust parameters as needed")