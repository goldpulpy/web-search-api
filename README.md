<div align="center">
  <h1>Web Search API 🔎</h1>

![Python](https://img.shields.io/badge/python-3.12+-blue.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.121+-009688.svg?logo=fastapi)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED.svg?logo=docker&logoColor=white)

![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/goldpulpy/web-search-api/ruff.yaml?label=ruff)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/goldpulpy/web-search-api/pyright.yaml?label=pyright)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/goldpulpy/web-search-api/bandit.yaml?label=bandit)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/goldpulpy/web-search-api/tests.yaml?label=docker)
![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/goldpulpy/web-search-api/docker.yaml?label=docker)

</div>

A simple FastAPI-based web search API that scrapes search engines and returns clean JSON data. Built with Python 3.12, FastAPI, and Playwright for reliable web scraping.

## Features

- 🔍 **Web Search Scraping**: Efficient web scraping using Playwright
- 🚀 **FastAPI Backend**: High-performance API with automatic documentation
- 🐳 **Docker Support**: Easy deployment with Docker and Docker Compose
- 🔒 **API Key Authentication**: Optional authentication for API endpoints

## Supported Search Engines

- **DuckDuckGo**: DuckDuckGo search engine

## Quick Start

### Prerequisites

- Python 3.12 or higher
- Docker and Docker Compose (optional)

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/goldpulpy/web-search-api
   cd web-search-api
   ```

2. **Set up environment**

   ```bash
   # Copy environment file
   cp .env.example .env

   # Install dependencies
   make install
   playwright install chrome
   ```

3. **Run the application**
   ```bash
   make run
   ```

The API will be available at `http://localhost:5000`

### Using Docker

```bash
# Build and run with Docker Compose
docker-compose up --build

# Or run in background
docker-compose up -d
```

## API Documentation

Once running, access the interactive API documentation at:

- **Scalar Documentation**: `http://localhost:5000/docs`

## API Endpoints

**Note**: Add Authorization header with `Bearer <API_KEY>` to access protected endpoints. (if `API_KEY` is set in `.env` file)

### Engines

**GET** `/api/v1/engines`

Get list of available search engines.

**Response:**

```json
{
  "engines": ["Engine name", ...]
}
```

### Search

**POST** `/api/v1/search`

Search for a query using a specific search engine.

**Request Body:**

```json
{
  "engine": "Engine name",
  "query": "Query to search",
  "page": 1
}
```

**Response:**

```json
{
  "engine": "Engine name",
  "result": [
    {
      "title": "Title of the result",
      "link": "Link to the result",
      "snippet": "Snippet of the result"
    },
    ...
  ],
  "page": 1
}
```

## Configuration

Configure the API using environment variables:

| Variable      | Default   | Description                           |
| ------------- | --------- | ------------------------------------- |
| `HOST`        | `0.0.0.0` | API server host                       |
| `PORT`        | `5000`    | API server port                       |
| `LOG_LEVEL`   | `INFO`    | Logging level                         |
| `API_KEY`     | `None`    | API key for authentication (optional) |
| `API_PREFIX`  | `/api`    | API route prefix                      |
| `ENABLE_DOCS` | `true`    | Enable API documentation              |

## Development

### Project Structure

```
web-search-api/
├── src/websearchapi/
│   ├── api/               # API routes and middleware
│   │   ├── v1/            # API version 1 endpoints
│   │   └── middlewares/   # Authentication middleware
│   ├── engine/            # Search engine implementations
│   ├── models/            # Pydantic models
│   └── shared/            # Configuration and utilities
├── tests/                 # Unit tests
├── docker-compose.yml     # Docker Compose configuration
├── Dockerfile             # Docker image definition
├── Makefile               # Development commands
└── pyproject.toml         # Project dependencies and configuration
```

### Development Commands

```bash
# Install dependencies
make install

# Run the application
make run

# Code quality checks
make format    # Format code with ruff
make lint      # Lint code with ruff
make type-check # Type check with pyright
make security  # Security check with bandit

# Run tests
make test

# Export dependencies (for deployment)
make requirements

# Clean environment
make clean
```

## Pre-commit Hooks

This project uses pre-commit hooks to ensure code quality before committing changes. The pre-commit configuration automatically runs:

- **trailing-whitespace** - 🧹 Remove trailing whitespace
- **end-of-file-fixer** - 🧹 Ensure files end with a newline
- **check-yaml** - 🧹 Validate YAML files
- **check-added-large-files** - 🧹 Prevent large files from being committed
- **Ruff** - 🧹 For linting and formatting
- **pyright** - 🔍 For type checking
- **bandit** - 🔒 For security checks

### Installation

To install the pre-commit hooks:

```bash
pre-commit install
```

After installation, the hooks will automatically run on every commit. If any issues are found, the commit will be blocked until they're fixed.

You can manually run all pre-commit hooks on all files with:

```bash
pre-commit run --all-files
```

## Deployment

### Docker Deployment

```bash
# Build image
docker build -t web-search-api .

# Run container
docker run -p 5000:5000 -e API_KEY=your-key web-search-api
```

### Production Considerations

- Set `ENABLE_DOCS=false` in production
- Configure proper API key authentication
- Set appropriate log levels
- Consider using a reverse proxy (nginx, Traefik)
- Monitor with health checks

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/new-feature`
3. Make your changes and tests: `pre-commit run --all-files`
4. Commit your changes: `git commit -m 'Add new feature'`
5. Push to the branch: `git push origin feature/new-feature`
6. Submit a pull request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
