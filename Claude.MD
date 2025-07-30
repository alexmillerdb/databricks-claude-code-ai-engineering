# Databricks Custom GenAI Application Development

This project template provides specialized Claude Code sub-agents for building, testing, debugging, and deploying custom GenAI applications on Databricks using Mosaic AI, MLflow 3.0, and modern orchestration frameworks.

## Agent Architecture

### Core Development Agents
- **databricks-researcher**: Documentation and research specialist - use PROACTIVELY to find relevant documentation, API references, and best practices before implementation
- **environment-manager**: Local IDE and Databricks environment setup with databricks-connect, Unity Catalog, and MLflow integration
- **ai-engineer**: Custom GenAI model and application development using Mosaic AI Agent Framework, RAG systems, LangChain/LangGraph, and DSPy
- **product-manager**: Requirements gathering, PRD creation, and feature prioritization for AI products

## Development Focus Areas

### Custom GenAI Applications
- **RAG Systems**: Document ingestion, vector search with Unity Catalog, retrieval chains
- **Agent Frameworks**: Tool-calling agents, multi-agent workflows with LangGraph
- **DSPy Optimization**: DSPy programs for systematic prompt engineering
- **Model Deployment**: MLflow 3.0 patterns with tracing, evaluation, and monitoring; and Databricks Agents (agents.deploy()) for model serving endpoints

### Local Development & Testing
- **IDE Integration**: Local development with databricks-connect
- **Testing**: Unit tests, integration tests
- **Code Quality**: Linting, type checking, security validation

### Production Deployment
- **Model Serving**: Deploy to Databricks Model Serving endpoints
- **Monitoring**: Performance tracking, cost optimization, quality metrics
- **Governance**: Unity Catalog integration, secret management, access controls
- **CI/CD**: Automated testing, deployment pipelines, rollback strategies

## Agent Coordination Patterns

### Sequential Workflows
**New Project Setup:**
```
databricks-researcher → environment-manager → ai-engineer → product-manager
```

**Feature Development:**
```
databricks-researcher → product-manager → ai-engineer → (testing & debugging) → deployment
```

**Troubleshooting:**
```
databricks-researcher → environment-manager → ai-engineer (debug & fix)
```

### Parallel Execution
**Complex AI Development:**
```
databricks-researcher + ai-engineer (working simultaneously on research & implementation)
product-manager + ai-engineer (requirements + technical implementation)
```

## Development Standards

### GenAI Development Requirements
- **Mosaic AI First**: Use Databricks Mosaic AI Agent Framework for production-ready AI applications
- **Unity Catalog Integration**: Implement governance for all data, models, tools, and vector indexes
- **MLflow 3.0 Patterns**: Use enhanced MLflow 3, experiment tracking, evaluation, monitoring, and integrated tracing
- **Local-First Development**: Develop and test locally with databricks-connect before deployment
- **Framework Integration**: Leverage LangChain/LangGraph for orchestration, DSPy for optimization, MLflow 3 for model management

### Code Quality Standards
- **Dependencies**: Pin all versions in requirements.txt, use `uv` for fast package management
- **Testing**: Unit tests for functions, integration tests for agents, evaluation frameworks for GenAI
- **Debugging**: MLflow tracing, comprehensive logging, proper error handling
- **Documentation**: Type hints, docstrings, and clear examples
- **Standards**: Follow PEP 8, use linting and type checking

### Security & Governance
- **Secrets Management**: Use Unity Catalog secrets, never commit credentials to code
- **Input Validation**: Sanitize and validate all user inputs and prompts
- **Access Control**: Implement proper permissions for models, data, and serving endpoints
- **Audit Trail**: Track model usage, data access, and deployment changes
- **Privacy**: Handle PII appropriately, implement data governance policies

### Performance & Cost Optimization
- **Model Efficiency**: Optimize prompt length, use appropriate model sizes, implement caching
- **Serving Strategy**: Choose between pay-per-token and provisioned throughput based on usage
- **Resource Management**: Use serverless compute when possible, optimize cluster configurations
- **Monitoring**: Track token usage, latency, error rates, and cost metrics
- **Evaluation**: Implement comprehensive evaluation frameworks for quality and performance

## Project Structure

### Environment Configuration
```
.env.template          # Template for environment variables
databricks.yml         # Databricks bundle configuration
requirements.txt       # Python dependencies with pinned versions
pyproject.toml         # Python project configuration
```

### Source Code Organization

#### RAG System Agent
```
src/
├── rag_system/        # Example: Customer support RAG system
│   ├── agents/        # Agent implementations
│   ├── vector_search/ # Vector store and search logic
│   ├── evaluation/    # Custom metrics and evaluation
│   ├── deploy/        # Deploy agents
│   └── monitoring/    # Production monitoring
├── shared/            # Shared utilities and components
└── notebooks/         # Databricks notebooks for experimentation
```
#### Tool-calling Agent
```
src/
├── tool_calling/      # Example: Tool-calling Agent System
│   ├── agents/        # Agent implementations
│   ├── vector_search/ # Vector store and search logic
│   ├── tools/         # Agent tools (UC, MCP)
│   ├── evaluation/    # Custom metrics and evaluation
│   ├── deploy/        # Deploy agents
│   └── monitoring/    # Production monitoring
├── shared/            # Shared utilities and components
└── notebooks/         # Databricks notebooks for experimentation
```

### Testing & Validation
```
tests/
├── unit/              # Unit tests for individual functions
├── integration/       # Integration tests for agent workflows
├── evaluation/        # GenAI evaluation test suites
└── scripts/           # Test connection and validation scripts
```

### Documentation & Examples
```
docs/
├── ai-examples/       # GenAI implementation examples and patterns
│   ├── agent-tools.md                              # Tool-calling agent patterns
│   ├── databricks_langgraph_tool_calling_agent.py  # LangGraph implementation example
│   ├── mlflow_chat_agent.py                        # MLflow ChatAgent example
│   ├── mlflow-workflows.md                         # MLflow 3.0 deployment patterns
│   └── mlflow_pyfunc_log_and_deploy_agent.py       # MLflow pyfunc example
├── api-reference/     # API documentation and references
│   └── databricks-sdk.md                          # Databricks SDK patterns
├── best-practices/    # Development guidelines and standards
│   ├── agent-coordination.md                       # Multi-agent coordination patterns
│   └── security-guidelines.md                      # Security and governance guidelines
├── devops-examples/   # Deployment and CI/CD patterns
│   └── ci-cd.pipeline.md                          # CI/CD pipeline examples
└── setup-guide.md     # Environment setup instructions
```

**Reference Priority**: Always check `/docs` folder first for examples and documentation before searching external sources.

## Agent Usage Instructions

### Starting a New GenAI Project

1. **Research & Documentation** (Always start here - check `/docs` first)
```bash
/agents databricks-researcher "Research Mosaic AI Agent Framework patterns from docs/ai-examples/, vector search setup, and MLflow 3.0 deployment patterns from docs/mlflow-workflows.md for building a customer support RAG system"
```

2. **Environment Setup** (Reference `/docs/setup-guide.md`)
```bash
/agents environment-manager "Set up local development environment following docs/setup-guide.md with databricks-connect, Unity Catalog access, and MLflow tracking for GenAI development"
```

3. **Requirements & Planning**
```bash
/agents product-manager "Help me create a PRD for a customer support chatbot with RAG capabilities, using patterns from docs/best-practices/ for success metrics and evaluation criteria"
```

4. **AI Development** (Use `/docs/ai-examples/` for patterns)
```bash
/agents ai-engineer "Build a RAG system for customer support using examples from docs/ai-examples/mlflow-workflows.md and agent-tools.md with Mosaic AI Agent Framework and Unity Catalog vector search"
```

### Development Workflow Examples

#### Building a RAG System (Reference `/docs/ai-examples/`)
```bash
# 1. Research first - check docs folder
/agents databricks-researcher "Research Unity Catalog vector search setup from docs/ai-examples/ and Mosaic AI Agent Framework patterns from docs/mlflow-workflows.md"

# 2. Set up environment following docs
/agents environment-manager "Configure databricks-connect and Unity Catalog following docs/setup-guide.md for vector search development"

# 3. Build using documented patterns
/agents ai-engineer "Create a RAG system using patterns from docs/ai-examples/agent-tools.md with document ingestion, vector indexing, and retrieval chain using Mosaic AI"
```

#### Creating Multi-Agent Workflows (Reference `/docs/ai-examples/databricks_langgraph_tool_calling_agent.py`)
```bash
# 1. Research orchestration patterns from docs
/agents databricks-researcher "Research LangGraph multi-agent patterns from docs/ai-examples/databricks_langgraph_tool_calling_agent.py and coordination patterns from docs/best-practices/agent-coordination.md"

# 2. Define requirements using best practices
/agents product-manager "Create specifications for a multi-agent customer service system using patterns from docs/best-practices/ with escalation workflows"

# 3. Implement using documented examples
/agents ai-engineer "Build LangGraph workflow using docs/ai-examples/databricks_langgraph_tool_calling_agent.py as reference with multiple specialized agents and conditional routing"
```

#### Debugging & Optimization (Reference `/docs/`)
```bash  
# 1. Research debugging from docs first
/agents databricks-researcher "Research MLflow tracing and debugging patterns from docs/mlflow-workflows.md and docs/best-practices/ for GenAI applications"

# 2. Debug using setup guide
/agents environment-manager "Help debug databricks-connect authentication issues using docs/setup-guide.md and Unity Catalog troubleshooting"

# 3. Optimize using documented patterns
/agents ai-engineer "Debug slow RAG performance using optimization patterns from docs/ai-examples/mlflow-workflows.md and optimize retrieval and generation pipeline"
```

### Agent-Specific Usage Patterns

#### Databricks Researcher
- **Use for**: Documentation research from `/docs/` folder, API references, best practices, technical examples
- **Best practice**: ALWAYS run first, check `/docs/` folder before external sources
- **Example**: `"Research Mosaic AI Agent Framework from docs/mlflow-workflows.md and vector search patterns from docs/ai-examples/ for deployment"`

#### Environment Manager  
- **Use for**: Local IDE setup using `/docs/setup-guide.md`, databricks-connect configuration, Unity Catalog access
- **Best practice**: Run first for new projects, always reference `/docs/setup-guide.md`
- **Example**: `"Set up databricks-connect following docs/setup-guide.md with Unity Catalog and test MLflow tracking connection"`

#### AI Engineer
- **Use for**: GenAI development using `/docs/ai-examples/` patterns, RAG systems, agent frameworks, deployment
- **Best practice**: Reference `/docs/ai-examples/` for implementation patterns, combine with researcher for context
- **Example**: `"Build a customer support agent using patterns from docs/ai-examples/agent-tools.md with Mosaic AI vector search and tool calling"`

#### Product Manager
- **Use for**: Requirements gathering using `/docs/best-practices/`, PRD creation, success metrics, stakeholder alignment
- **Best practice**: Reference `/docs/best-practices/` for guidelines, use at project start for clear objectives
- **Example**: `"Create PRD for AI-powered code review assistant using docs/best-practices/ guidelines with evaluation criteria"`

## Technology Integration Patterns

### MLflow 3.0 Integration
- **Enhanced Tracking**: Use integrated tracing for GenAI workflows and debugging
- **Model Registry**: Leverage Unity Catalog-backed registry for governance and versioning
- **Deployment**: Deploy with proper pyfunc signatures for complex GenAI models
- **Evaluation**: Built-in evaluation tools for GenAI applications with custom metrics

### Unity Catalog Integration  
- **Vector Search**: Native vector indexing and search for RAG applications
- **Governance**: Centralized access control for models, data, and AI assets
- **Secrets Management**: Secure credential storage for external API integrations
- **Lineage**: Track data and model lineage across the AI application lifecycle

### Mosaic AI Agent Framework
- **Production-Ready**: Built-in governance, evaluation, and deployment capabilities
- **Integrated Serving**: One-click deployment to Databricks Model Serving
- **Monitoring**: Native observability and quality monitoring
- **Evaluation**: LLM-as-a-judge evaluation with custom metrics

## Troubleshooting Guidelines

### Common Development Issues

#### Environment & Connection Problems
- **databricks-connect issues**: Use `environment-manager` to debug authentication and cluster connectivity
- **Unity Catalog access**: Verify catalog permissions and schema access through `environment-manager`
- **MLflow tracking failures**: Check tracking server connectivity and experiment permissions

#### GenAI Development Issues  
- **Vector search not working**: Check Unity Catalog permissions, embedding model access, and index sync status
- **RAG performance problems**: Optimize chunk size, improve retrieval queries, add re-ranking steps
- **Agent tool errors**: Validate tool descriptions, check function signatures, test tools independently  
- **Model deployment failures**: Verify model signatures, check dependencies, review compute requirements

#### Code Quality Issues
- **Import errors**: Ensure all dependencies are pinned in requirements.txt and environment is consistent
- **Type checking failures**: Use proper type hints and validate with mypy or similar tools
- **Evaluation issues**: Implement comprehensive test suites and GenAI evaluation frameworks

### Agent Coordination Best Practices
- **Start with research**: Always use `databricks-researcher` first to validate approaches and find examples
- **Environment first**: Use `environment-manager` to ensure proper setup before development
- **Clear requirements**: Use `product-manager` to define success criteria and evaluation metrics
- **Iterative development**: Use `ai-engineer` for implementation with frequent testing and validation

## Development Best Practices Summary

### Core Workflow
1. **Research First**: Use `databricks-researcher` to find documentation, examples, and validate technical approaches
2. **Environment Setup**: Use `environment-manager` to configure local development with databricks-connect and Unity Catalog
3. **Define Requirements**: Use `product-manager` to create clear specifications and success criteria
4. **Build & Test**: Use `ai-engineer` for implementation with comprehensive testing and evaluation
5. **Deploy & Monitor**: Deploy to Databricks Model Serving with proper monitoring and governance

### Quality Standards
- **Local Development**: Always develop and test locally before deploying to production
- **Comprehensive Testing**: Unit tests, integration tests, and GenAI evaluation frameworks
- **Security First**: Use Unity Catalog for secrets, validate inputs, implement proper access controls
- **Performance Monitoring**: Track token usage, latency, cost, and quality metrics
- **Documentation**: Clear examples, API docs, and operational runbooks

### Technology Stack
- **Mosaic AI Agent Framework**: For production-ready GenAI applications
- **MLflow 3.0**: Enhanced tracking, deployment, and evaluation capabilities
- **Unity Catalog**: Governance for data, models, vectors, and secrets
- **LangChain/LangGraph**: Complex agent orchestration and workflows
- **DSPy**: Systematic prompt optimization and few-shot learning

This template enables comprehensive GenAI application development on Databricks with clear agent responsibilities, quality standards, and production-ready patterns.
