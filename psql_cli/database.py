"""Database operations with read-only access using psql CLI."""

import logging
import subprocess
import json
from typing import List, Dict, Any, Optional
import os

from .config import DatabaseConfig

logger = logging.getLogger(__name__)


class DatabaseReader:
    """Read-only database access layer using psql CLI."""

    def __init__(self, config: DatabaseConfig):
        """Initialize database reader."""
        self.config = config
        self._connection_string = config.connection_string
        # Set PGPASSWORD environment variable for psql
        os.environ['PGPASSWORD'] = config.password

    def connect(self) -> None:
        """Test connection to the database."""
        try:
            result = subprocess.run(
                [
                    'psql',
                    '-h', self.config.host,
                    '-p', str(self.config.port),
                    '-U', self.config.user,
                    '-d', self.config.database,
                    '-c', 'SELECT 1;'
                ],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode != 0:
                raise RuntimeError(f"Failed to connect: {result.stderr}")
            logger.info("Successfully connected to database")
        except subprocess.TimeoutExpired:
            logger.error("Connection timeout")
            raise RuntimeError("Database connection timeout")
        except FileNotFoundError:
            logger.error("psql command not found")
            raise RuntimeError("psql command not found. Please install PostgreSQL client tools.")

    def disconnect(self) -> None:
        """Close database connection (no-op for CLI)."""
        logger.info("Database session ended")

    def execute_query(self, query: str) -> List[Dict[str, Any]]:
        """
        Execute a query and return results using psql CLI.
        
        Note: This connection uses a read-only database user. Any write operations
        (INSERT, UPDATE, DELETE, DROP, etc.) will be rejected by PostgreSQL with
        a permission denied error.
        
        Args:
            query: SQL query to execute
            
        Returns:
            List of dictionaries containing query results
            
        Raises:
            RuntimeError: If query execution fails or permission is denied
        """
        try:
            # Use psql with JSON output format
            result = subprocess.run(
                [
                    'psql',
                    '-h', self.config.host,
                    '-p', str(self.config.port),
                    '-U', self.config.user,
                    '-d', self.config.database,
                    '-t',  # tuples only (no headers/footers)
                    '-A',  # unaligned output
                    '-c', query
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                error_msg = result.stderr.strip()
                logger.error(f"Query execution failed: {error_msg}")
                
                # Check for permission errors
                if 'permission denied' in error_msg.lower():
                    raise ValueError(f"Operation not allowed: This user only has read (SELECT) permissions")
                
                raise RuntimeError(f"Query failed: {error_msg}")
            
            # Parse psql output into list of dicts
            output = result.stdout.strip()
            if not output:
                return []
            
            # Get column names from a separate query with \d format
            # For now, parse the pipe-delimited output
            return self._parse_psql_output(output, query)
            
        except subprocess.TimeoutExpired:
            logger.error("Query execution timeout")
            raise RuntimeError("Query execution timeout")
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    def _parse_psql_output(self, output: str, query: str) -> List[Dict[str, Any]]:
        """Parse psql pipe-delimited output into list of dictionaries."""
        lines = output.strip().split('\n')
        if not lines:
            return []
        
        # Get column names by running EXPLAIN (VERBOSE) format
        # For simplicity, we'll run the query again with different format to get column names
        try:
            result = subprocess.run(
                [
                    'psql',
                    '-h', self.config.host,
                    '-p', str(self.config.port),
                    '-U', self.config.user,
                    '-d', self.config.database,
                    '--csv',
                    '-c', query
                ],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode != 0:
                # Fall back to simple parsing
                return [{"result": line} for line in lines if line]
            
            csv_output = result.stdout.strip().split('\n')
            if len(csv_output) < 2:
                return []
            
            # First line is headers
            headers = csv_output[0].split(',')
            
            # Parse remaining lines
            results = []
            for line in csv_output[1:]:
                if line:
                    values = line.split(',')
                    row = {}
                    for i, header in enumerate(headers):
                        value = values[i] if i < len(values) else None
                        row[header.strip()] = value
                    results.append(row)
            
            return results
            
        except Exception as e:
            logger.warning(f"Failed to parse output properly: {e}")
            # Fallback: return raw lines
            return [{"result": line} for line in lines if line]

    def get_table_schema(self, table_name: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get schema information for tables.
        
        Args:
            table_name: Specific table name, or None for all tables
            
        Returns:
            List of dictionaries containing schema information
        """
        query = f"""
            SELECT 
                table_name,
                column_name,
                data_type,
                is_nullable,
                column_default
            FROM information_schema.columns
            WHERE table_schema = '{self.config.schema}'"
        """
        
        if table_name:
            query += f" AND table_name = '{table_name}'"
        
        query += " ORDER BY table_name, ordinal_position"
        
        return self.execute_query(query)

    def get_all_tables(self) -> List[str]:
        """Get list of all tables in the database."""
        query = f"""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = '{self.config.schema}'
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """
        results = self.execute_query(query)
        return [row['table_name'] for row in results]

    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.disconnect()
