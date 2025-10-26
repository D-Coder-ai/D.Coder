.PHONY: help install infra-up infra-down service-up dev-up dev-down nx-graph affected-services clean reset

# Colors for output
BLUE := \033[36m
GREEN := \033[32m
YELLOW := \033[33m
RED := \033[31m
RESET := \033[0m

help: ## Show this help message
	@echo "$(BLUE)D.Coder Platform - Development Commands$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "$(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'

install: ## Install all dependencies
	@echo "$(BLUE)Installing dependencies...$(RESET)"
	pnpm install
	@echo "$(GREEN)✓ Dependencies installed$(RESET)"

infra-up: ## Start infrastructure services (Postgres, Redis, NATS, etc.)
	@echo "$(BLUE)Starting infrastructure services...$(RESET)"
	docker-compose -f infrastructure/docker-compose.base.yml up -d
	@echo "$(GREEN)✓ Infrastructure services started$(RESET)"
	@echo "$(YELLOW)Run 'make infra-logs' to view logs$(RESET)"

infra-down: ## Stop infrastructure services
	@echo "$(BLUE)Stopping infrastructure services...$(RESET)"
	docker-compose -f infrastructure/docker-compose.base.yml down
	@echo "$(GREEN)✓ Infrastructure services stopped$(RESET)"

infra-logs: ## View infrastructure logs
	docker-compose -f infrastructure/docker-compose.base.yml logs -f

service-up: ## Start a specific service (e.g., make service-up SERVICE=platform-api)
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)ERROR: SERVICE parameter required$(RESET)"; \
		echo "Usage: make service-up SERVICE=platform-api"; \
		exit 1; \
	fi
	@echo "$(BLUE)Starting service: $(SERVICE)...$(RESET)"
	docker-compose up -d $(SERVICE)
	@echo "$(GREEN)✓ Service $(SERVICE) started$(RESET)"

service-down: ## Stop a specific service
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)ERROR: SERVICE parameter required$(RESET)"; \
		exit 1; \
	fi
	docker-compose down $(SERVICE)

service-logs: ## View logs for a specific service
	@if [ -z "$(SERVICE)" ]; then \
		echo "$(RED)ERROR: SERVICE parameter required$(RESET)"; \
		exit 1; \
	fi
	docker-compose logs -f $(SERVICE)

dev-up: ## Start full development stack (infrastructure + all services)
	@echo "$(BLUE)Starting full development stack...$(RESET)"
	docker-compose up -d
	@echo "$(GREEN)✓ Full stack started$(RESET)"
	@echo "$(YELLOW)Services:$(RESET)"
	@echo "  - Kong Gateway:       http://localhost:8000"
	@echo "  - LiteLLM Proxy:      http://localhost:4000"
	@echo "  - Platform API:       http://localhost:8082"
	@echo "  - Grafana:            http://localhost:3005"
	@echo "  - Temporal UI:        http://localhost:8088"

dev-down: ## Stop full development stack
	@echo "$(BLUE)Stopping full development stack...$(RESET)"
	docker-compose down
	@echo "$(GREEN)✓ Full stack stopped$(RESET)"

dev-logs: ## View logs for all services
	docker-compose logs -f

nx-graph: ## Open Nx dependency graph
	@echo "$(BLUE)Opening Nx dependency graph...$(RESET)"
	pnpm nx graph

affected-services: ## Show services affected by recent changes
	@echo "$(BLUE)Detecting affected services...$(RESET)"
	pnpm nx show projects --affected --type=app

affected-build: ## Build only affected services
	@echo "$(BLUE)Building affected services...$(RESET)"
	pnpm nx affected --target=build

affected-test: ## Test only affected services
	@echo "$(BLUE)Testing affected services...$(RESET)"
	pnpm nx affected --target=test

build-all: ## Build all services
	@echo "$(BLUE)Building all services...$(RESET)"
	pnpm nx run-many --target=build --all

test-all: ## Run all tests
	@echo "$(BLUE)Running all tests...$(RESET)"
	pnpm nx run-many --target=test --all

lint-all: ## Lint all services
	@echo "$(BLUE)Linting all services...$(RESET)"
	pnpm nx run-many --target=lint --all

clean: ## Clean build artifacts and caches
	@echo "$(BLUE)Cleaning build artifacts...$(RESET)"
	pnpm nx reset
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "node_modules" -prune -o -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "$(GREEN)✓ Cleaned$(RESET)"

reset: clean infra-down ## Full reset (stop services, clean volumes)
	@echo "$(RED)WARNING: This will delete all data in volumes!$(RESET)"
	@echo "Press Ctrl+C to cancel, or wait 5 seconds to continue..."
	@sleep 5
	docker-compose down -v
	@echo "$(GREEN)✓ Full reset complete$(RESET)"

changeset: ## Create a new changeset for version management
	pnpm changeset

version: ## Update package versions from changesets
	pnpm version-packages

status: ## Show Docker services status
	@echo "$(BLUE)Infrastructure Services:$(RESET)"
	@docker-compose -f infrastructure/docker-compose.base.yml ps || echo "Infrastructure not running"
	@echo ""
	@echo "$(BLUE)Application Services:$(RESET)"
	@docker-compose ps || echo "Services not running"

