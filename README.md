# Databricks Claude Code AI Engineering Template

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://www.python.org/downloads/)
[![Databricks](https://img.shields.io/badge/Databricks-Unity%20Catalog-red)](https://databricks.com/)
[![MLflow](https://img.shields.io/badge/MLflow-3.0%2B-orange)](https://mlflow.org/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.3.4-green)](https://langchain-ai.github.io/langgraph/)

> A comprehensive template for building, testing, and deploying custom GenAI applications on Databricks using Claude AI agents, MLflow 3.0, and modern orchestration frameworks.

## 🚀 Overview

This project provides specialized Claude Code sub-agents and examples for developing production-ready AI applications on Databricks. It includes everything you need to build RAG systems, multi-agent workflows, and deploy models at scale using Databricks' Mosaic AI platform.

## 🤖 Claude AI Agents

The template includes specialized Claude agents for different development roles:

- **🔬 databricks-researcher**: Documentation and API research specialist - use proactively to find relevant documentation and best practices
- **⚙️ environment-manager**: Local IDE and Databricks environment setup with databricks-connect and Unity Catalog integration  
- **🧠 ai-engineer**: Custom GenAI model and application development using Mosaic AI Agent Framework, RAG systems, and LangGraph
- **📋 product-manager**: Requirements gathering, PRD creation, and feature prioritization for AI products

## ✨ Features

### 🏗️ Custom GenAI Applications
- **RAG Systems**: Document ingestion, vector search with Unity Catalog, retrieval chains
- **Agent Frameworks**: Tool-calling agents, multi-agent workflows with LangGraph  
- **DSPy Optimization**: Systematic prompt engineering and optimization
- **Model Deployment**: MLflow 3.0 patterns with tracing, evaluation, and monitoring

### 🛠️ Local Development & Testing
- **IDE Integration**: Local development with databricks-connect
- **Testing**: Unit tests, integration tests, and model evaluation
- **Code Quality**: Linting, type checking, security validation
- **Notebooks**: Jupyter notebook development and sync with Databricks

### 🚀 Production Deployment
- **Model Serving**: Deploy to Databricks Model Serving endpoints
- **Monitoring**: Performance tracking, cost optimization, quality metrics
- **Governance**: Unity Catalog integration, secret management, access controls
- **CI/CD**: Automated testing, deployment pipelines, rollback strategies

## 📁 Project Structure

```
databricks-claude-code-ai-engineering/
├── .claude/                           # Claude AI agent configurations
│   ├── agents/                        
│   │   ├── ai-engineer.md            # AI engineering specialist agent
│   │   ├── databricks-researcher.md   # Research and documentation agent
│   │   ├── environment-manager.md     # Setup and configuration agent
│   │   └── product-manager.md         # Product management agent
│   └── settings.local.json           # Local Claude settings
├── docs/                              # Documentation and guides
│   ├── ai-examples/                   # AI/ML implementation examples
│   │   ├── databricks_langgraph_tool_calling_agent.py
│   │   ├── mlflow_chat_agent.py
│   │   ├── mlflow_pyfunc_log_and_deploy_agent.py
│   │   ├── mlflow-workflows.md
│   │   └── agent-tools.md
│   ├── api-reference/                 # API documentation
│   ├── best-practices/                # Security and development best practices
│   └── devops-examples/               # CI/CD and deployment examples
├── notebooks/                         # Jupyter notebooks for development
├── scripts/                           # Utility and testing scripts
│   ├── test_comprehensive_connection.py
│   └── test_local_connection.py
├── .env.template                      # Environment configuration template
├── databricks.yml                     # Databricks project configuration
├── pyproject.toml                     # Python project configuration
└── requirements.txt                   # Python dependencies
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
git clone https://github.com/alexmillerdb/databricks-claude-code-ai-engineering.git
cd databricks-claude-code-ai-engineering
```

### 2. Environment Configuration

```bash
# Copy the environment template
cp .env.template .env

# Edit .env with your Databricks workspace details
# IMPORTANT: Never commit real secrets to version control!
```

Required environment variables:
- `DATABRICKS_HOST`: Your Databricks workspace URL
- `DATABRICKS_TOKEN`: Your personal access token
- `DATABRICKS_CATALOG`: Unity Catalog name (e.g., "users")
- `DATABRICKS_SCHEMA`: Schema name (e.g., "your_username")

### 3. Install Dependencies

```bash
# Install the package in development mode
pip install -e ".[dev]"

# Or install just the core dependencies
pip install -r requirements.txt
```

### 4. Use Claude Code Agents

**Set up environment:**
```
/agents environment-manager "Set up my local Databricks development environment"
```

**Verify setup:**
```bash
python scripts/test_local_connection.py
```

**Start building:**
```
/agents ai-engineer "Help me build a RAG system with Unity Catalog vector search"
```

## 🔧 Development Workflow

### Agent Coordination Patterns

**New Project Setup:**
```
databricks-researcher → environment-manager → ai-engineer → product-manager
```

**Feature Development:**
```
databricks-researcher → product-manager → ai-engineer → testing → deployment
```

**Troubleshooting:**
```
databricks-researcher → environment-manager → ai-engineer (debug & fix)
```

### Local Development

1. **Environment Setup**: Use the `environment-manager` agent to configure your local development environment
2. **Research**: Use `databricks-researcher` to find relevant documentation and best practices
3. **Implementation**: Use `ai-engineer` for building AI applications and models
4. **Testing**: Run tests locally with `pytest` and validate connections
5. **Deployment**: Deploy to Databricks using MLflow and the Agent Framework

## 📚 Examples

### AI/ML Examples
- **[LangGraph Tool-Calling Agent](docs/ai-examples/databricks_langgraph_tool_calling_agent.py)**: Multi-agent workflow with tool calling
- **[MLflow Chat Agent](docs/ai-examples/mlflow_chat_agent.py)**: Conversational AI with MLflow integration
- **[MLflow PyFunc Deployment](docs/ai-examples/mlflow_pyfunc_log_and_deploy_agent.py)**: Model packaging and deployment
- **[MLflow Workflows](docs/ai-examples/mlflow-workflows.md)**: Complete MLflow lifecycle examples

### Development Tools
- **[Connection Testing](scripts/test_comprehensive_connection.py)**: Validate Databricks connectivity
- **[Agent Tools Reference](docs/ai-examples/agent-tools.md)**: Unity Catalog and MCP integration

## 🔒 Security

This template follows Databricks security best practices:

- ✅ **Secret Management**: Environment variables and Unity Catalog secret scopes
- ✅ **Access Controls**: Unity Catalog governance and RBAC
- ✅ **Code Scanning**: Automated secret detection in git hooks
- ✅ **Secure Deployment**: Secure model serving and endpoint management

**Important**: Never commit real secrets to version control. The `.env.template` file contains placeholder values only.

## 🧪 Testing

```bash
# Run all tests
pytest

# Run tests with coverage
pytest --cov=src --cov-report=html

# Test Databricks connection
python scripts/test_local_connection.py
```

## 📖 Documentation

- **[Setup Guide](docs/setup-guide.md)**: Detailed setup instructions
- **[Security Guidelines](docs/best-practices/security-guidelines.md)**: Security best practices
- **[API Reference](docs/api-reference/databricks-sdk.md)**: Databricks SDK documentation
- **[CI/CD Guide](docs/devops-examples/ci-cd.pipeline.md)**: Deployment pipeline examples

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: Check the [docs/](docs/) directory for guides and examples
- **Issues**: Report bugs and request features via [GitHub Issues](https://github.com/alexmillerdb/databricks-claude-code-ai-engineering/issues)
- **Claude Agents**: Use the specialized agents for guided development assistance

## 🙏 Acknowledgments

- Built for the [Databricks](https://databricks.com/) Mosaic AI platform
- Powered by [Claude](https://claude.ai/) AI agents
- Integrates [MLflow](https://mlflow.org/), [LangGraph](https://langchain-ai.github.io/langgraph/), and [Unity Catalog](https://docs.databricks.com/unity-catalog/)

---

**Ready to build the future of AI?** Start with `/agents environment-manager "Set up my development environment"` and let the Claude agents guide you! 🚀