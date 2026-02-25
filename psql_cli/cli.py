"""Command-line interface for the application."""

import logging
import sys
from typing import Optional

from .config import AppConfig
from .database import DatabaseReader
from .llm_agent import LLMAgent

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class CLI:
    """Interactive command-line interface."""

    def __init__(self, config: AppConfig):
        """Initialize CLI."""
        self.config = config
        self.db_reader = DatabaseReader(config.database)
        self.agent: Optional[LLMAgent] = None

    def start(self) -> None:
        """Start the interactive CLI."""
        print("=" * 60)
        print("PostgreSQL + Ollama (Mistral) Query Assistant")
        print("=" * 60)
        print()

        try:
            # Connect to database
            print("Connecting to database...")
            self.db_reader.connect()
            
            # Initialize agent
            self.agent = LLMAgent(self.config.ollama, self.db_reader)
            
            # Show available tables
            tables = self.db_reader.get_all_tables()
            print(f"Connected! Available tables: {', '.join(tables)}")
            print()
            print("Commands:")
            print("  - Ask questions in natural language")
            print("  - Type 'schema' to see the database schema")
            print("  - Type 'tables' to list all tables")
            print("  - Type 'reset' to clear conversation history")
            print("  - Type 'quit' or 'exit' to exit")
            print()

            # Main loop
            self._run_loop()

        except Exception as e:
            logger.error(f"Failed to start application: {e}")
            print(f"\nError: {e}")
            sys.exit(1)
        finally:
            self.db_reader.disconnect()

    def _run_loop(self) -> None:
        """Main interaction loop."""
        while True:
            try:
                user_input = input("\n> ").strip()
                
                if not user_input:
                    continue

                if user_input.lower() in ['quit', 'exit']:
                    print("\nGoodbye!")
                    break

                if user_input.lower() == 'tables':
                    tables = self.db_reader.get_all_tables()
                    print(f"\nAvailable tables: {', '.join(tables)}")
                    continue

                if user_input.lower() == 'schema':
                    schema = self.db_reader.get_table_schema()
                    current_table = None
                    for col in schema:
                        if col['table_name'] != current_table:
                            current_table = col['table_name']
                            print(f"\n{current_table}:")
                        nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                        print(f"  - {col['column_name']}: {col['data_type']} {nullable}")
                    continue

                if user_input.lower() == 'reset':
                    self.agent.reset_conversation()
                    print("\nConversation history cleared.")
                    continue

                # Process query with LLM
                print("\nThinking...")
                result = self.agent.process_query(user_input)

                if result.get("thought"):
                    print(f"\n💭 {result['thought']}")

                if result.get("query"):
                    print(f"\n📝 SQL: {result['query']}")

                if result.get("results"):
                    print(f"\n📊 Results ({len(result['results'])} rows):")
                    for i, row in enumerate(result['results'][:10], 1):  # Show first 10
                        print(f"  {i}. {row}")
                    if len(result['results']) > 10:
                        print(f"  ... and {len(result['results']) - 10} more rows")

                print(f"\n💬 {result['response']}")

                if not result.get("success"):
                    print(f"\n⚠️  Error: {result.get('error')}")

            except KeyboardInterrupt:
                print("\n\nGoodbye!")
                break
            except Exception as e:
                logger.error(f"Error processing input: {e}")
                print(f"\n❌ Error: {e}")


def main():
    """Main entry point."""
    config = AppConfig.from_env()
    cli = CLI(config)
    cli.start()


if __name__ == "__main__":
    main()
