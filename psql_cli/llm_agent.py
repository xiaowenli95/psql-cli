"""LLM agent for natural language to SQL conversion."""

import logging
from typing import List, Dict, Any
import json
import requests

from .config import OllamaConfig
from .database import DatabaseReader

logger = logging.getLogger(__name__)


class LLMAgent:
    """Agent that uses Ollama/Mistral to interact with PostgreSQL."""

    def __init__(self, ollama_config: OllamaConfig, db_reader: DatabaseReader):
        """Initialize LLM agent."""
        self.config = ollama_config
        self.db_reader = db_reader
        self.conversation_history: List[Dict[str, str]] = []

    def _build_system_prompt(self, schema_info: List[Dict[str, Any]]) -> str:
        """Build system prompt with database schema information."""
        # Group schema by table
        tables = {}
        for col in schema_info:
            table = col['table_name']
            if table not in tables:
                tables[table] = []
            tables[table].append(col)

        schema_text = "Database Schema:\n\n"
        for table_name, columns in tables.items():
            schema_text += f"Table: {table_name}\n"
            for col in columns:
                nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
                schema_text += f"  - {col['column_name']}: {col['data_type']} {nullable}\n"
            schema_text += "\n"

        system_prompt = f"""You are a helpful PostgreSQL database assistant.

{schema_text}

Your job is to:
1. Understand user questions and requests about the data
2. Generate appropriate SQL queries to fulfill any request the user makes
3. Execute queries and explain results in a user-friendly way

When generating SQL:
- Generate any valid PostgreSQL query that the user requests (SELECT, INSERT, UPDATE, DELETE, etc.)
- Be precise and use proper PostgreSQL syntax
- Include appropriate WHERE, JOIN, GROUP BY, ORDER BY clauses as needed
- Use LIMIT to avoid overwhelming output when appropriate
- If the user explicitly asks for a write operation, generate it as requested

When responding:
- If the user asks a question or makes a request that requires a query, generate and execute it
- Explain the results in natural language
- If a query fails, explain the error (e.g., permission denied, syntax error, etc.)
- Be conversational and helpful

IMPORTANT: Always respond with valid JSON in this format:
{{
    "thought": "Your reasoning about what query to run or action to take",
    "query": "SQL query to execute (or null if no query needed)",
    "response": "Your natural language response to the user"
}}
"""
        return system_prompt

    def _call_ollama(self, prompt: str, system_prompt: str) -> str:
        """Call Ollama API."""
        url = f"{self.config.host}/api/generate"
        
        payload = {
            "model": self.config.model,
            "prompt": prompt,
            "system": system_prompt,
            "stream": False,
            "format": "json"
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=self.config.timeout
            )
            response.raise_for_status()
            result = response.json()
            return result.get("response", "")
        except requests.exceptions.RequestException as e:
            logger.error(f"Ollama API call failed: {e}")
            raise

    def process_query(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input and generate response.
        
        Args:
            user_input: Natural language question from user
            
        Returns:
            Dictionary with query results and response
        """
        # Get schema information
        schema_info = self.db_reader.get_table_schema()
        system_prompt = self._build_system_prompt(schema_info)

        # Build conversation context
        context = ""
        for msg in self.conversation_history[-3:]:  # Last 3 messages for context
            context += f"{msg['role']}: {msg['content']}\n"
        
        full_prompt = f"{context}User: {user_input}\n\nPlease respond with JSON."

        # Call LLM
        try:
            llm_response = self._call_ollama(full_prompt, system_prompt)
            response_data = json.loads(llm_response)
        except (json.JSONDecodeError, KeyError) as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return {
                "success": False,
                "error": "Failed to parse LLM response",
                "response": "I'm having trouble understanding how to help. Could you rephrase your question?"
            }

        # Store in conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input
        })

        # Execute query if provided
        query_results = None
        error = None
        
        if response_data.get("query"):
            try:
                query_results = self.db_reader.execute_query(response_data["query"])
                logger.info(f"Query executed successfully: {response_data['query']}")
            except Exception as e:
                error = str(e)
                logger.error(f"Query execution failed: {e}")
                response_data["response"] = f"Query failed: {error}. {response_data.get('response', '')}"

        self.conversation_history.append({
            "role": "assistant",
            "content": response_data.get("response", "")
        })

        return {
            "success": error is None,
            "thought": response_data.get("thought"),
            "query": response_data.get("query"),
            "results": query_results,
            "response": response_data.get("response"),
            "error": error
        }

    def reset_conversation(self) -> None:
        """Clear conversation history."""
        self.conversation_history.clear()
