# Databricks Agent Framework - Authoring Agents

**Source**: https://docs.databricks.com/aws/en/generative-ai/agent-framework/author-agent
**Domain**: docs.databricks.com
**Fetched**: 2025-08-11
**Type**: Technical Guide - Agent Development

## Overview

This documentation covers how to author production-ready AI agents using the Databricks Agent Framework. The framework provides a standardized interface for creating, deploying, and managing AI agents with features like multi-agent support, streaming capabilities, and comprehensive tool-calling history.

## Key Concepts

### ResponsesAgent Interface
The `ResponsesAgent` is the core abstraction for building agents in Databricks. It provides:
- **Multi-agent support**: Coordinate multiple specialized agents
- **Streaming output**: Real-time response generation
- **Tool-calling message history**: Complete audit trail
- **Simplified deployment**: Direct integration with Databricks Model Serving

### Requirements
- Python 3.10 or above
- `databricks-agents` package version 1.2.0+
- `mlflow` package version 3.1.3+

## Installation

```bash
# Recommended installation command
%pip install -U -qqqq databricks-agents mlflow

# For specific integrations
%pip install databricks-langchain  # For LangChain agents
%pip install databricks-openai     # For OpenAI-based agents
```

## Code Examples

### Basic ResponsesAgent Implementation

```python
from databricks_agents import ResponsesAgent, ResponsesAgentRequest, ResponsesAgentResponse

class MyCustomAgent(ResponsesAgent):
    def __init__(self, agent):
        """Initialize with an existing agent implementation"""
        self.agent = agent
    
    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        """Non-streaming prediction method"""
        # Convert request messages to agent format
        messages = self._convert_messages(request.messages)
        
        # Call underlying agent
        response = self.agent.invoke({"messages": messages})
        
        # Convert response to standard format
        return ResponsesAgentResponse(
            choices=[{
                "message": {
                    "role": "assistant",
                    "content": response.content
                }
            }]
        )
```

### Streaming Agent Implementation

```python
from typing import Iterator
from databricks_agents import StreamingEvent

class MyStreamingAgent(ResponsesAgent):
    def predict_stream(self, request: ResponsesAgentRequest) -> Iterator[StreamingEvent]:
        """Streaming prediction method"""
        # Initialize streaming
        yield StreamingEvent(event="start", data={"request_id": request.request_id})
        
        # Stream content chunks
        for chunk in self.agent.stream(request.messages):
            yield StreamingEvent(
                event="delta",
                data={
                    "choices": [{
                        "delta": {
                            "content": chunk.content
                        }
                    }]
                }
            )
        
        # Finish streaming
        yield StreamingEvent(event="done", data={})
```

### Environment Configuration

```python
from mlflow.models import ModelConfig

class ConfigurableAgent(ResponsesAgent):
    def __init__(self, model_config: ModelConfig):
        """Initialize with flexible configuration"""
        self.config = model_config
        
        # Access configuration values
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 1000)
        self.model_name = self.config.get("model_name", "databricks-meta-llama-3-70b")
        
        # Initialize agent with config
        self._init_agent()
```

### Tool-Calling Agent Example

```python
class ToolCallingAgent(ResponsesAgent):
    def __init__(self, tools: list):
        """Initialize with available tools"""
        self.tools = tools
        self.agent = self._create_agent_with_tools()
    
    def predict(self, request: ResponsesAgentRequest) -> ResponsesAgentResponse:
        """Handle tool calls in conversation"""
        messages = request.messages
        
        # Check for tool calls in history
        if self._has_tool_calls(messages):
            # Process with tool execution context
            response = self.agent.invoke_with_tools(messages)
        else:
            # Standard response
            response = self.agent.invoke(messages)
        
        return self._format_response(response)
```

## Implementation Notes

### Best Practices for Production

1. **State Management**:
   - Avoid local caching that persists between requests
   - Design thread-safe state handling
   - Initialize state within the `predict` method

2. **Code Structure**:
   - Use synchronous code (async not supported in serving)
   - Implement proper error handling
   - Log important events for debugging

3. **Configuration**:
   - Use `ModelConfig` for environment-specific settings
   - Support both dictionary and YAML configurations
   - Parameterize key values (models, endpoints, credentials)

4. **Performance**:
   - Implement streaming for better user experience
   - Cache reusable resources appropriately
   - Monitor token usage and latency

### Deployment Checklist

- [ ] Implement `ResponsesAgent` interface
- [ ] Add proper error handling
- [ ] Configure environment parameters
- [ ] Test streaming functionality
- [ ] Validate tool-calling behavior
- [ ] Document input/output schemas
- [ ] Set up monitoring and logging

### Common Patterns

1. **Wrapping Existing Agents**:
   ```python
   # Wrap LangChain agent
   from databricks_langchain import wrap_langchain_agent
   wrapped_agent = wrap_langchain_agent(langchain_agent)
   ```

2. **Custom Input/Output Handling**:
   ```python
   def predict(self, request):
       # Custom preprocessing
       processed_input = self.preprocess(request.messages)
       
       # Agent logic
       result = self.agent.process(processed_input)
       
       # Custom postprocessing
       return self.postprocess(result)
   ```

3. **Multi-Agent Coordination**:
   ```python
   class CoordinatorAgent(ResponsesAgent):
       def __init__(self, agents: dict):
           self.agents = agents  # {"research": agent1, "analysis": agent2}
       
       def predict(self, request):
           # Route to appropriate agent
           intent = self.classify_intent(request)
           selected_agent = self.agents[intent]
           return selected_agent.predict(request)
   ```

## Related Resources

- Reference CLAUDE.md for Databricks AI development guidelines
- Check `/docs/ai-examples/` for complete agent implementations
- Review `/docs/mlflow-workflows.md` for deployment patterns
- See `/docs/best-practices/agent-coordination.md` for multi-agent patterns

## Integration with Databricks Ecosystem

### Unity Catalog Integration
- Store agent configurations in UC volumes
- Access UC functions as tools
- Manage secrets through UC

### MLflow Integration
- Log agents with `mlflow.langchain.log_model()`
- Track agent performance metrics
- Deploy through MLflow Model Registry

### Model Serving Deployment
- Deploy ResponsesAgent to Model Serving endpoints
- Enable streaming for real-time responses
- Monitor with built-in observability tools

### Vector Search Integration
- Use UC-managed vector indexes for RAG
- Implement semantic search capabilities
- Manage embeddings lifecycle

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all packages are installed with correct versions
   - Check for namespace conflicts

2. **Streaming Not Working**:
   - Verify `predict_stream` method is implemented
   - Check Model Serving endpoint configuration

3. **Tool Calls Failing**:
   - Validate tool descriptions and schemas
   - Ensure proper error handling in tools

4. **Configuration Issues**:
   - Use `ModelConfig` for all environment variables
   - Avoid hardcoded values

### Debug Tips
- Enable verbose logging during development
- Test locally before deploying
- Use MLflow tracking for debugging
- Monitor token usage and costs