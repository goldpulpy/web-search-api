# Project configuration
SOURCE_DIR := src
VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip
UV := $(VENV)/bin/uv
ENV_FILE := .env

# Colors for pretty output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
NC := \033[0m # No Color

# Default goal
.DEFAULT_GOAL := help

.PHONY: help
help:
	@echo "$(GREEN)Development Commands$(NC)"
	@echo ""
	@echo "$(YELLOW)Environment Setup:$(NC)"
	@echo "  $(GREEN)install$(NC) - Create venv and install dependencies"
	@echo "  $(GREEN)requirements$(NC) - Export dependencies to requirements.txt"
	@echo "  $(GREEN)clean$(NC) - Clean development environment"
	@echo ""
	@echo "$(YELLOW)Application:$(NC)"
	@echo "  $(GREEN)run$(NC) - Run application"
	@echo ""
	@echo "$(YELLOW)Testing:$(NC)"
	@echo "  $(GREEN)tests$(NC) - Run unit tests"
	@echo ""
	@echo "$(YELLOW)Code Quality:$(NC)"
	@echo "  $(GREEN)format$(NC) - Format code (ruff)"
	@echo "  $(GREEN)lint$(NC) - Lint code (ruff)"
	@echo "  $(GREEN)type-check$(NC) - Type check code (pyright)"
	@echo "  $(GREEN)security$(NC) - Security check code (bandit)"
	@echo ""

.PHONY: venv
venv:
	@echo "$(YELLOW)Creating virtual environment...$(NC)"
	@python3 -m venv $(VENV)
	@$(PIP) install --upgrade pip
	@$(PIP) install uv
	@echo "$(GREEN)Virtual environment created successfully!$(NC)"

.PHONY: install
install: venv
	@echo "$(YELLOW)Installing dependencies...$(NC)"
	@$(UV) sync
	@echo "$(GREEN)Dependencies installed successfully!$(NC)"

.PHONY: requirements
requirements:
	@echo "$(YELLOW)Exporting dependencies to requirements.txt...$(NC)"
	@$(UV) export --no-dev > requirements.txt
	@echo "$(GREEN)Dependencies exported successfully!$(NC)"

.PHONY: run
run:
	@echo "$(YELLOW)Running application...$(NC)"
	@PYTHONPATH=$(SOURCE_DIR) $(UV) run --env-file $(ENV_FILE) python -m websearchapi

.PHONY: tests
tests:
	@echo "$(YELLOW)Running tests...$(NC)"
	@PYTHONPATH=$(SOURCE_DIR) $(UV) run --env-file $(ENV_FILE) pytest --cov=$(SOURCE_DIR)
	@echo "$(GREEN)Tests passed successfully!$(NC)"

.PHONY: clean
clean:
	@echo "$(YELLOW)Cleaning development environment...$(NC)"
	@rm -rf $(VENV)
	@rm -rf $(ENV_FILE)
	@rm -rf .ruff_cache
	@rm -rf .pytest_cache
	@rm -rf .coverage
	@find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)Development environment cleaned!$(NC)"

.PHONY: format
format:
	@echo "$(YELLOW)Formatting code...$(NC)"
	@$(UV) run ruff format .
	@echo "$(GREEN)Code formatted successfully!$(NC)"

.PHONY: lint
lint:
	@echo "$(YELLOW)Linting code...$(NC)"
	@$(UV) run ruff check .
	@echo "$(GREEN)Code linted successfully!$(NC)"

.PHONY: type-check
type-check:
	@echo "$(YELLOW)Type checking code...$(NC)"
	@$(UV) run pyright .
	@echo "$(GREEN)Code type checked successfully!$(NC)"

.PHONY: security
security:
	@echo "$(YELLOW)Security checking code...$(NC)"
	@$(UV) run bandit -r $(SOURCE_DIR)
	@echo "$(GREEN)Code security checked successfully!$(NC)"
