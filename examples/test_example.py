"""
Example usage and testing of the PostgreSQL CLI with Ollama integration.
"""

from psql_cli.config import AppConfig
from psql_cli.database import DatabaseReader
from psql_cli.llm_agent import LLMAgent


def test_database_connection():
    """Test basic database connectivity and queries."""
    config = AppConfig.from_env()
    
    with DatabaseReader(config.database) as db:
        # Test getting all tables
        tables = db.get_all_tables()
        print(f"Tables found: {tables}")
        
        # Test schema retrieval
        schema = db.get_table_schema("employees")
        print(f"\nEmployees table schema:")
        for col in schema:
            print(f"  - {col['column_name']}: {col['data_type']}")
        
        # Test a simple query
        results = db.execute_query("SELECT name, department FROM employees LIMIT 3")
        print(f"\nSample employees:")
        for row in results:
            print(f"  - {row['name']} ({row['department']})")


def test_llm_agent():
    """Test LLM agent with a sample question."""
    config = AppConfig.from_env()
    
    with DatabaseReader(config.database) as db:
        agent = LLMAgent(config.ollama, db)
        
        # Test a simple question
        question = "How many employees do we have?"
        print(f"\nQuestion: {question}")
        
        result = agent.process_query(question)
        
        print(f"Thought: {result.get('thought')}")
        print(f"Query: {result.get('query')}")
        print(f"Response: {result.get('response')}")
        
        if result.get('results'):
            print(f"Results: {result['results']}")


if __name__ == "__main__":
    print("Testing Database Connection...")
    print("=" * 60)
    test_database_connection()
    
    print("\n\nTesting LLM Agent...")
    print("=" * 60)
    test_llm_agent()
