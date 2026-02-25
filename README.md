# PostgreSQL CLI with Ollama LLM Integration

A Python application that uses Ollama with the Mistral model to interact with PostgreSQL databases using natural language queries. The agent has read-only access to the database for safe exploration and querying.

## Features

- 🤖 Natural language to SQL conversion using Ollama and Mistral
- 🔒 Read-only database access for safe querying
- 🐳 Docker Compose setup for local PostgreSQL testing
- 💬 Interactive CLI with conversation history
- 📊 Automatic schema detection and context building
- ✅ Query validation and error handling

## Prerequisites

- Python 3.12 or higher
- [Poetry](https://python-poetry.org/docs/#installation) for dependency management
- [Docker](https://docs.docker.com/get-docker/) and Docker Compose for running PostgreSQL
- [Ollama](https://ollama.ai/) installed and running locally

## Installation

1. **Clone or navigate to the project directory:**
   ```bash
   cd /Users/xiaowen/dev/psql_cli
   ```

2. **Install dependencies using Poetry:**
   ```bash
   poetry install
   ```

3. **Set up environment variables:**
   ```bash
   cp .env.example .env
   ```
   Edit `.env` if you need to customize any settings.

4. **Install and run Ollama with Mistral model:**
   ```bash
   # Install Ollama from https://ollama.ai/
   
   # Pull the Mistral model
   ollama pull mistral
   
   # Verify Ollama is running
   ollama list
   ```

## Usage

### 1. Start PostgreSQL Database

Start the PostgreSQL database with sample data:

```bash
docker-compose up -d
```

This will:
- Start a PostgreSQL 16 container
- Create a database called `testdb`
- Initialize with sample tables (employees, departments, projects)
- Create a read-only user for the application

Wait a few seconds for the database to initialize, then verify it's running:

```bash
docker-compose ps
```

### 2. Run the Application

Start the interactive CLI:

```bash
poetry run psql-cli
```

Or activate the virtual environment first:

```bash
poetry shell
psql-cli
```

### 3. Interact with the Database

Once the CLI starts, you can ask questions in natural language:

```
> How many employees do we have?

> Show me all employees in the Engineering department

> What's the average salary by department?

> List all active projects with their budgets

> Who is working on the Mobile App project?

> Which department has the highest total budget?
```

**Special Commands:**
- `schema` - Display the complete database schema
- `tables` - List all available tables
- `reset` - Clear conversation history
- `quit` or `exit` - Exit the application

## Project Structure

```
psql_cli/
├── psql_cli/
│   ├── __init__.py          # Package initialization
│   ├── cli.py               # Interactive CLI interface
│   ├── config.py            # Configuration management
│   ├── database.py          # Read-only database operations
│   └── llm_agent.py         # Ollama/Mistral LLM integration
├── init-db/
│   └── 01-init.sql          # Database initialization script
├── docker-compose.yml        # PostgreSQL container setup
├── pyproject.toml           # Project dependencies
├── .env.example             # Environment variables template
└── README.md                # This file
```

## How It Works

1. **User Input**: You ask a question in natural language
2. **Schema Context**: The agent loads the database schema
3. **LLM Processing**: Ollama/Mistral generates an appropriate SQL query
4. **Query Execution**: The query is executed with read-only permissions
5. **Response**: Results are formatted and explained in natural language

## Database Schema

The sample database includes:

- **employees**: Employee information (name, email, department, salary, hire date)
- **departments**: Department details (name, budget, manager)
- **projects**: Project information (name, description, dates, budget, status)
- **employee_projects**: Many-to-many relationship between employees and projects

## Configuration

Environment variables (in `.env`):

```bash
# Database Configuration
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=testdb
POSTGRES_USER=readonly_user
POSTGRES_PASSWORD=readonly_pass

# Ollama Configuration
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=mistral
OLLAMA_TIMEOUT=120
```

## Security Features

- **Read-Only Access**: Database user has only SELECT permissions
- **Query Validation**: Only SELECT and WITH (CTE) queries are allowed
- **No Destructive Operations**: INSERT, UPDATE, DELETE, DROP are blocked
- **Transaction Safety**: All operations run in read-only transactions

## Troubleshooting

### Ollama Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not running, start Ollama (usually starts automatically on macOS)
# Or start manually based on your installation
```

### Database Connection Issues

```bash
# Check if PostgreSQL is running
docker-compose ps

# View logs
docker-compose logs postgres

# Restart the database
docker-compose restart postgres
```

### Missing Mistral Model

```bash
# Pull the Mistral model
ollama pull mistral

# List available models
ollama list
```

## Development

To add new features or modify the code:

```bash
# Activate the virtual environment
poetry shell

# Run the application in development mode
python -m psql_cli.cli

# Install additional dependencies
poetry add <package-name>
```

## Stopping the Application

1. Exit the CLI (type `quit` or `exit`, or press Ctrl+C)
2. Stop the PostgreSQL container:
   ```bash
   docker-compose down
   ```

To remove all data:
```bash
docker-compose down -v
```

## License

MIT

## Contributing

Feel free to open issues or submit pull requests!
