"""
Unity Catalog Function Tools Documentation
========================================

This module demonstrates how to create, register, and use Unity Catalog functions
as tools in LangChain agents for building intelligent AI applications.

Key Features:
- Create Python and SQL functions in Unity Catalog
- Integrate UC functions with LangChain agents
- Enable tool calling for LLMs with UC function toolkit
- Provide governance and security through Unity Catalog

Prerequisites:
- Databricks workspace with Unity Catalog enabled
- Proper permissions to create functions in the specified catalog/schema
- Python packages: unitycatalog, databricks-langchain, langchain

For more information:
- Unity Catalog Functions: https://docs.databricks.com/en/sql/language-manual/sql-ref-functions.html
- UC AI Client: https://docs.unitycatalog.io/ai/client/#unity-catalog-function-client
- Databricks LangChain: https://docs.databricks.com/en/generative-ai/databricks-langchain.html
"""

from pyspark import sql
from unitycatalog.ai.core.databricks import DatabricksFunctionClient
from databricks_langchain import UCFunctionToolkit, ChatDatabricks
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.prompts import ChatPromptTemplate
import mlflow
import os

# =============================================================================
# CONFIGURATION
# =============================================================================

# Unity Catalog configuration - Replace with your actual catalog and schema
CATALOG = "my_catalog"  # Replace with your catalog name
SCHEMA = "my_schema"    # Replace with your schema name

# Validate that catalog and schema are set properly
if CATALOG == "my_catalog" or SCHEMA == "my_schema":
    print("⚠️  Remember to update CATALOG and SCHEMA with your actual Unity Catalog names")

# Initialize Unity Catalog Function Client
client = DatabricksFunctionClient()

# =============================================================================
# EXAMPLE 1: PYTHON FUNCTION CREATION AND REGISTRATION
# =============================================================================

def create_python_function_example():
    """
    Demonstrates creating and registering a Python function in Unity Catalog.
    """
    print("=== Creating Python Function in Unity Catalog ===")
    
    def add_numbers(number_1: float, number_2: float) -> float:
        """
        A function that accepts two floating point numbers, adds them,
        and returns the resulting sum as a float.

        Args:
            number_1 (float): The first of the two numbers to add.
            number_2 (float): The second of the two numbers to add.

        Returns:
            float: The sum of the two input numbers.
        """
        return number_1 + number_2

    try:
        # Create and register the function in Unity Catalog
        function_info = client.create_python_function(
            func=add_numbers,
            catalog=CATALOG,
            schema=SCHEMA,
            replace=True  # Replace if function already exists
        )
        
        print(f"✅ Function created: {function_info.full_name}")
        
        # Test the function directly
        result = client.execute_function(
            function_name=f"{CATALOG}.{SCHEMA}.add_numbers",
            parameters={"number_1": 36939.0, "number_2": 8922.4}
        )
        
        print(f"✅ Function test result: {result.value}")  # OUTPUT: 45861.4
        return function_info
        
    except Exception as e:
        print(f"❌ Error creating function: {e}")
        print("Check your catalog/schema permissions and names")
        return None

# =============================================================================
# EXAMPLE 2: LANGCHAIN TOOLKIT INTEGRATION
# =============================================================================

def create_langchain_toolkit_example():
    """
    Demonstrates how to use Unity Catalog functions as LangChain tools.
    """
    print("=== Creating LangChain Toolkit with UC Functions ===")
    
    try:
        # Create a toolkit with the Unity Catalog function
        func_name = f"{CATALOG}.{SCHEMA}.add_numbers"
        toolkit = UCFunctionToolkit(function_names=[func_name])
        
        # Get the tools from the toolkit
        tools = toolkit.tools
        print(f"✅ Created toolkit with {len(tools)} tools")
        
        # Display tool information
        for tool in tools:
            print(f"   Tool: {tool.name}")
            print(f"   Description: {tool.description}")
        
        return tools
        
    except Exception as e:
        print(f"❌ Error creating toolkit: {e}")
        print("Ensure the function exists and you have proper permissions")
        return []

# =============================================================================
# EXAMPLE 3: COMPLETE AGENT WITH UC FUNCTION TOOLS
# =============================================================================

def create_complete_agent_example():
    """
    Creates a complete LangChain agent that can use Unity Catalog functions.
    """
    print("=== Creating Complete Agent with UC Function Tools ===")
    
    try:
        # Get tools from UC functions
        func_name = f"{CATALOG}.{SCHEMA}.add_numbers"
        toolkit = UCFunctionToolkit(function_names=[func_name])
        tools = toolkit.tools
        
        if not tools:
            print("❌ No tools available. Ensure UC function exists.")
            return None
        
        # Initialize the LLM - replace with your preferred endpoint
        LLM_ENDPOINT_NAME = "databricks-meta-llama-3-3-70b-instruct"
        llm = ChatDatabricks(endpoint=LLM_ENDPOINT_NAME, temperature=0.1)
        
        # Define the agent prompt
        prompt = ChatPromptTemplate.from_messages([
            (
                "system",
                "You are a helpful assistant with access to Unity Catalog functions. "
                "Use the available tools to solve mathematical problems and data queries. "
                "Always explain what tools you're using and why."
            ),
            ("placeholder", "{chat_history}"),
            ("human", "{input}"),
            ("placeholder", "{agent_scratchpad}"),
        ])
        
        # Enable MLflow tracing for debugging and monitoring
        mlflow.langchain.autolog()
        
        # Create the agent
        agent = create_tool_calling_agent(llm, tools, prompt)
        
        # Create the agent executor
        agent_executor = AgentExecutor(
            agent=agent, 
            tools=tools, 
            verbose=True,
            max_iterations=3,  # Prevent infinite loops
            handle_parsing_errors=True  # Graceful error handling
        )
        
        # Test the agent
        test_result = agent_executor.invoke({
            "input": "What is 36939.0 + 8922.4? Please use the available tools to calculate this."
        })
        
        print("✅ Agent test completed")
        print(f"Result: {test_result.get('output', 'No output')}")
        
        return agent_executor
        
    except Exception as e:
        print(f"❌ Error creating agent: {e}")
        return None

# =============================================================================
# SQL FUNCTION CREATION WITH UC AI CLIENT
# =============================================================================

def create_sql_function_examples():
    """
    Demonstrates creating SQL functions using the Unity Catalog AI client.
    This is the recommended approach for data query functions in agents.
    """
    print("=== Creating SQL Functions with UC AI Client ===")
    
    try:
        # Example 1: Table query function
        query_function_sql = f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.query_table_with_filter(
    table_name STRING COMMENT 'Full table name (catalog.schema.table)',
    filter_condition STRING COMMENT 'SQL WHERE clause condition', 
    row_limit INT COMMENT 'Maximum rows to return'
)
RETURNS STRING
COMMENT 'Query a Unity Catalog table with filtering and return JSON result'
RETURN (
    SELECT TO_JSON(COLLECT_LIST(STRUCT(*))) 
    FROM (
        SELECT * FROM identifier(table_name) 
        WHERE CASE 
            WHEN filter_condition = '1=1' THEN TRUE
            ELSE eval(filter_condition)
        END
        LIMIT row_limit
    )
);"""
        
        client.create_function(sql_function_body=query_function_sql)
        print(f"✅ Created SQL function: {CATALOG}.{SCHEMA}.query_table_with_filter")
        
        # Example 2: Table statistics function  
        stats_function_sql = f"""
CREATE OR REPLACE FUNCTION {CATALOG}.{SCHEMA}.get_table_statistics(
    table_name STRING COMMENT 'Full table name to analyze'
)
RETURNS STRING
COMMENT 'Get comprehensive statistics about a Unity Catalog table'
RETURN (
    SELECT TO_JSON(
        STRUCT(
            COUNT(*) as row_count,
            SIZE(ARRAY_DISTINCT(FLATTEN(ARRAY(STRUCT(*))))) as column_count,
            ARRAY_DISTINCT(TRANSFORM(
                SEQUENCE(0, SIZE(ARRAY(STRUCT(*))) - 1),
                i -> ELEMENT_AT(ARRAY(STRUCT(*)), i + 1)
            )) as sample_data
        )
    )
    FROM identifier(table_name)
    LIMIT 1000
);"""
        
        client.create_function(sql_function_body=stats_function_sql)
        print(f"✅ Created SQL function: {CATALOG}.{SCHEMA}.get_table_statistics")
        
        return [f"{CATALOG}.{SCHEMA}.query_table_with_filter", 
                f"{CATALOG}.{SCHEMA}.get_table_statistics"]
        
    except Exception as e:
        print(f"❌ Error creating SQL functions: {e}")
        return []

def sql_function_examples():
    """
    Provides examples of SQL functions that can be created in Unity Catalog.
    These can be executed in Databricks SQL cells or via the UC AI client.
    """
    print("=== SQL Function Examples ===")
    
    sql_examples = {
        "Customer Lookup Function": """
-- Create a SQL function for customer information lookup
-- Execute this in a Databricks SQL cell

CREATE OR REPLACE FUNCTION {catalog}.{schema}.lookup_customer_info(
    customer_name STRING COMMENT 'Name of the customer whose info to look up.'
)
RETURNS STRING
COMMENT 'Returns metadata about a specific customer including their email and ID.'
RETURN (
    SELECT CONCAT(
        'Customer ID: ', customer_id, ', ',
        'Customer Email: ', customer_email
    )
    FROM {catalog}.{schema}.customer_data
    WHERE customer_name = lookup_customer_info.customer_name
    LIMIT 1
);
""".format(catalog=CATALOG, schema=SCHEMA),

        "Data Quality Check Function": """
-- Create a function to check data quality metrics
-- Execute this in a Databricks SQL cell

CREATE OR REPLACE FUNCTION {catalog}.{schema}.check_data_quality(
    table_name STRING COMMENT 'Name of the table to check'
)
RETURNS STRING
COMMENT 'Returns data quality metrics for the specified table.'
RETURN (
    SELECT CONCAT(
        'Row Count: ', COUNT(*), ', ',
        'Null Values: ', SUM(CASE WHEN id IS NULL THEN 1 ELSE 0 END)
    )
    FROM identifier(table_name)
);
""".format(catalog=CATALOG, schema=SCHEMA),

        "Business Calculation Function": """
-- Create a function for business calculations
-- Execute this in a Databricks SQL cell

CREATE OR REPLACE FUNCTION {catalog}.{schema}.calculate_revenue(
    product_id STRING COMMENT 'Product ID to calculate revenue for',
    start_date DATE COMMENT 'Start date for revenue calculation',
    end_date DATE COMMENT 'End date for revenue calculation'
)
RETURNS DECIMAL(10,2)
COMMENT 'Calculates total revenue for a product in the given date range.'
RETURN (
    SELECT SUM(quantity * unit_price)
    FROM {catalog}.{schema}.sales_data
    WHERE product_id = calculate_revenue.product_id
    AND sale_date BETWEEN start_date AND end_date
);
""".format(catalog=CATALOG, schema=SCHEMA)
    }
    
    print("SQL Function Examples (execute these in Databricks SQL cells):")
    for name, sql in sql_examples.items():
        print(f"\n--- {name} ---")
        print(sql)
    
    return sql_examples

# =============================================================================
# BEST PRACTICES AND TROUBLESHOOTING
# =============================================================================

def best_practices_guide():
    """
    Provides best practices for working with Unity Catalog functions.
    """
    print("=== Best Practices for Unity Catalog Functions ===")
    
    practices = {
        "Function Design": [
            "Use descriptive function names that indicate purpose",
            "Include comprehensive docstrings with parameter descriptions",
            "Handle edge cases and invalid inputs gracefully",
            "Keep functions focused on a single responsibility",
            "Use appropriate data types for parameters and returns"
        ],
        
        "Security & Permissions": [
            "Grant minimal required permissions to users/groups",
            "Use service principals for production applications",
            "Avoid hardcoding sensitive data in functions",
            "Implement input validation to prevent injection attacks",
            "Use Unity Catalog's governance features for compliance"
        ],
        
        "Performance Optimization": [
            "Keep function logic simple and efficient",
            "Use appropriate data types to minimize memory usage",
            "Consider caching for frequently called functions",
            "Optimize SQL queries within functions",
            "Monitor function execution times and costs"
        ],
        
        "Error Handling": [
            "Implement proper exception handling in Python functions",
            "Use meaningful error messages for debugging",
            "Test functions thoroughly before deployment",
            "Implement fallback logic for critical functions",
            "Monitor function execution logs"
        ]
    }
    
    for category, items in practices.items():
        print(f"\n{category}:")
        for item in items:
            print(f"  • {item}")

def troubleshooting_guide():
    """
    Common issues and solutions for Unity Catalog functions.
    """
    print("=== Troubleshooting Unity Catalog Functions ===")
    
    issues = {
        "Function Creation Fails": [
            "Check catalog and schema permissions",
            "Verify catalog and schema exist",
            "Ensure function name doesn't conflict",
            "Validate Python syntax and imports",
            "Check workspace Unity Catalog settings"
        ],
        
        "Function Execution Errors": [
            "Verify function parameters match signature",
            "Check data types of input parameters",
            "Ensure referenced tables/data exist",
            "Validate SQL syntax in SQL functions",
            "Check for null value handling"
        ],
        
        "LangChain Integration Issues": [
            "Verify databricks-langchain package version",
            "Check function is properly registered in UC",
            "Ensure toolkit has correct function names",
            "Validate LLM endpoint permissions",
            "Test function independently before agent use"
        ],
        
        "Performance Problems": [
            "Optimize SQL queries in functions",
            "Consider function complexity and data size",
            "Monitor execution times and resource usage",
            "Implement appropriate caching strategies",
            "Use async patterns for long-running operations"
        ]
    }
    
    for issue, solutions in issues.items():
        print(f"\n{issue}:")
        for solution in solutions:
            print(f"  • {solution}")

# =============================================================================
# ADDITIONAL RESOURCES
# =============================================================================

def additional_resources():
    """
    Provides links to additional resources and documentation.
    """
    print("=== Additional Resources ===")
    
    resources = {
        "Official Documentation": [
            "Unity Catalog Functions: https://docs.databricks.com/en/sql/language-manual/sql-ref-functions.html",
            "UC AI Client: https://docs.unitycatalog.io/ai/client/#unity-catalog-function-client",
            "Databricks LangChain: https://docs.databricks.com/en/generative-ai/databricks-langchain.html",
            "Function Security: https://docs.databricks.com/en/sql/language-manual/sql-ref-functions-builtin.html",
            "Unity Catalog Overview: https://docs.databricks.com/en/unity-catalog/index.html"
        ],
        
        "Code Examples": [
            "UC Function Samples: https://github.com/databricks/databricks-ml-examples",
            "LangChain Integration: https://python.langchain.com/docs/integrations/providers/databricks",
            "Agent Examples: https://github.com/langchain-ai/langchain",
            "MLflow Integration: https://mlflow.org/docs/latest/index.html"
        ],
        
        "Community Resources": [
            "Databricks Community: https://community.databricks.com/",
            "Stack Overflow: https://stackoverflow.com/questions/tagged/databricks",
            "GitHub Issues: https://github.com/databricks/databricks-ml-examples/issues",
            "YouTube Tutorials: Search for 'Databricks Unity Catalog Functions'"
        ]
    }
    
    for category, links in resources.items():
        print(f"\n{category}:")
        for link in links:
            print(f"  • {link}")

# =============================================================================
# MAIN EXECUTION
# =============================================================================

if __name__ == "__main__":
    """
    Main execution block to run examples and display information.
    """
    print("Unity Catalog Function Tools Examples")
    print("=" * 50)
    
    # Check environment
    if not os.getenv("DATABRICKS_HOST") or not os.getenv("DATABRICKS_TOKEN"):
        print("⚠️  Warning: Databricks authentication not configured")
        print("   Set DATABRICKS_HOST and DATABRICKS_TOKEN environment variables")
    
    # Run examples (uncomment to test)
    try:
        # 1. Create Python function
        function_info = create_python_function_example()
        
        # 2. Create LangChain toolkit
        if function_info:
            tools = create_langchain_toolkit_example()
            
            # 3. Create complete agent (commented out to avoid API calls during testing)
            # agent = create_complete_agent_example()
        
        # 4. Create SQL functions using UC AI client
        sql_functions = create_sql_function_examples()
        
        # 5. Display additional SQL examples
        sql_function_examples()
        
        # 6. Show best practices
        best_practices_guide()
        
        # 7. Show troubleshooting guide
        troubleshooting_guide()
        
        # 8. Show additional resources
        additional_resources()
        
    except Exception as e:
        print(f"❌ Error running examples: {e}")
        print("Check your Databricks configuration and permissions")
    
    print("\n" + "=" * 50)
    print("Examples completed! Remember to:")
    print("1. Update CATALOG and SCHEMA variables with your actual names")
    print("2. Ensure proper Unity Catalog permissions")
    print("3. Test functions independently before agent integration")
    print("4. Monitor function usage and performance")
    print("5. Follow security best practices for production use")