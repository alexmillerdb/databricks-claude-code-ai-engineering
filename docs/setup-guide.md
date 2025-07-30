# Databricks Development Setup Guide

## Prerequisites
- Python 3.11 or higher
- Git
- VS Code (recommended) or Cursor
- Databricks workspace access

## Quick Start

### 1. Clone and Setup
git clone <your-repo>
cd databricks-claude-template
cp .env.template .env
**Edit** .env with your workspace details


### 2. Use Claude Code Agents
**Set up environment** /agents environment-manager "Set up my local Databricks development environment"
**Verify setup** python scripts/test_local_connection.py


## Detailed Setup Instructions

### Environment Manager Setup
The env-manager agent will guide you through:
- Databricks CLI installation
- Authentication configuration
- databricks-connect setup
- VS Code extension installation

### Local Development
- Use databricks-connect for local Spark execution
- Sync notebooks with Databricks workspace
- Run tests locally before deployment
