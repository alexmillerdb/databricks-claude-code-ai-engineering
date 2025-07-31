# Databricks Vector Search Client Guide

This guide provides comprehensive documentation for using Databricks Vector Search with LangChain to build intelligent retrieval-augmented generation (RAG) applications.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Quick Start](#quick-start)
4. [Configuration Options](#configuration-options)
5. [Index Types](#index-types)
6. [Query Types](#query-types)
7. [Best Practices](#best-practices)
8. [Troubleshooting](#troubleshooting)
9. [Examples](#examples)

## Overview

Databricks Vector Search enables you to store and query vector embeddings at scale, making it ideal for building RAG applications, semantic search, and recommendation systems. The `VectorSearchRetrieverTool` from `databricks-langchain` provides a seamless integration with LangChain for building AI applications.

### Key Features

- **Scalable vector storage**: Handle millions of vectors efficiently
- **Hybrid search**: Combine semantic and keyword search capabilities
- **Real-time updates**: Automatically sync with Delta tables
- **Security**: Enterprise-grade security and governance
- **Integration**: Native LangChain and LLM integration

## Prerequisites

Before using Databricks Vector Search, ensure you have:

1. **Databricks Workspace**: With Vector Search enabled
2. **Authentication**: Valid workspace token or service principal
3. **Vector Search Index**: Created and populated with your data
4. **Python Packages**:
   ```bash
   pip install databricks-langchain langchain
   ```

### Environment Setup

Set up your environment variables:

```bash
export DATABRICKS_HOST="https://your-workspace.cloud.databricks.com"
export DATABRICKS_TOKEN="your-access-token"
```

## Quick Start

```python
from databricks_langchain import VectorSearchRetrieverTool

# Basic usage for Delta Sync indexes
vs_tool = VectorSearchRetrieverTool(
    index_name="catalog.schema.my_index",
    tool_name="my_retriever",
    tool_description="Retrieves relevant documents"
)

# Query the index
results = vs_tool.invoke("your search query")
```

## Configuration Options

### Basic Parameters

| Parameter | Type | Description | Required |
|-----------|------|-------------|----------|
| `index_name` | str | Full index name (catalog.schema.index) | Yes |
| `tool_name` | str | Name for the tool (used by LLM) | Yes |
| `tool_description` | str | Description of tool purpose | Yes |

### Advanced Parameters

| Parameter | Type | Description | Default |
|-----------|------|-------------|---------|
| `num_results` | int | Maximum results to return | 10 |
| `columns` | List[str] | Columns to include in results | All |
| `filters` | Dict | Filter conditions for search | None |
| `query_type` | str | "ANN" or "HYBRID" | "ANN" |
| `text_column` | str | Column containing text for embeddings | None |
| `embedding` | Embeddings | Custom embedding model | None |

## Index Types

### 1. Delta Sync Index

- **Use case**: Auto-sync with Delta tables
- **Embeddings**: Managed by Databricks
- **Configuration**: Minimal setup required

```python
vs_tool = VectorSearchRetrieverTool(
    index_name="catalog.schema.delta_sync_index",
    tool_name="delta_retriever",
    tool_description="Retrieves from auto-synced Delta table"
)
```

### 2. Direct Vector Access Index

- **Use case**: Direct vector uploads
- **Embeddings**: Self-managed
- **Configuration**: Requires embedding model

```python
from databricks_langchain import DatabricksEmbeddings

embedding_model = DatabricksEmbeddings(endpoint="databricks-bge-large-en")

vs_tool = VectorSearchRetrieverTool(
    index_name="catalog.schema.direct_access_index",
    tool_name="direct_retriever",
    tool_description="Retrieves from direct access index",
    text_column="content",
    embedding=embedding_model
)
```

## Query Types

### Approximate Nearest Neighbor (ANN)

- **Purpose**: Pure semantic search
- **Performance**: Fastest
- **Use case**: When you want similarity-based retrieval

```python
vs_tool = VectorSearchRetrieverTool(
    index_name="catalog.schema.my_index",
    query_type="ANN",
    # ... other parameters
)
```

### Hybrid Search

- **Purpose**: Combines semantic and keyword search
- **Performance**: Slower but more comprehensive
- **Use case**: When you need both semantic understanding and exact keyword matches

```python
vs_tool = VectorSearchRetrieverTool(
    index_name="catalog.schema.my_index",
    query_type="HYBRID",
    # ... other parameters
)
```

## Best Practices

### Performance Optimization

1. **Limit Results**: Use appropriate `num_results` to balance quality and speed
2. **Column Selection**: Only retrieve necessary columns
3. **Query Type**: Use ANN for pure semantic search
4. **Filtering**: Apply filters to reduce search space
5. **Caching**: Implement caching for frequent queries

### Security Considerations

1. **Authentication**: Use service principals for production
2. **Access Control**: Implement proper table/index permissions
3. **Data Privacy**: Ensure sensitive data is properly handled
4. **Network Security**: Use private endpoints when available

### Error Handling

```python
try:
    results = vs_tool.invoke(query)
    if not results:
        print("No results found")
except Exception as e:
    print(f"Search failed: {e}")
    # Implement fallback strategy
```

## Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Check DATABRICKS_HOST and DATABRICKS_TOKEN
   - Verify token permissions

2. **Index Not Found**
   - Confirm index name format: `catalog.schema.index`
   - Check if index exists and is online

3. **Empty Results**
   - Verify index has data
   - Check query relevance
   - Review filter conditions

4. **Performance Issues**
   - Reduce `num_results`
   - Limit returned columns
   - Use appropriate query type

### Debugging Tips

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Enable debug mode for detailed logs
vs_tool = VectorSearchRetrieverTool(
    index_name="catalog.schema.my_index",
    # ... other parameters
)
```

## Examples

For complete code examples, see `vector_search_example.py`:

1. **Basic Usage**: Simple retrieval with minimal configuration
2. **Advanced Configuration**: Custom embeddings and filtering
3. **LLM Integration**: Tool calling with Databricks LLMs
4. **Agent Framework**: Conversational AI with RAG
5. **Error Handling**: Robust error handling patterns
6. **Performance Optimization**: Speed and efficiency tips

## Additional Resources

- [Databricks Vector Search Documentation](https://docs.databricks.com/en/generative-ai/vector-search.html)
- [LangChain Documentation](https://python.langchain.com/docs/get_started/introduction)
- [Databricks AI Examples](https://github.com/databricks/databricks-ml-examples)

## Support

For technical support and questions:
- Databricks Community Forums
- Databricks Support Portal
- GitHub Issues for databricks-langchain