# NCN Backend Documentation Context

## Project Overview

The NCN backend is a FastAPI-based service that handles all business logic, data persistence, and external communications for the automated AI agents managing. It provides REST API endpoints for managing projects, flows, and test executions, integrates with databases and message queues, and orchestrates AI-powered management and workflows.

### Key Features
- REST API endpoints following `/api/ncn/v1/` pattern
- Data persistence through PostgreSQL database with SQLAlchemy ORM
- Asynchronous task orchestration through Apache Kafka message broker
- LLM integration for AI-powered test generation
- User authentication and authorization systems
- Healthcheck and monitoring endpoints

### Tech Stack
- **Framework**: FastAPI for high-performance REST API development
- **Async Support**: Full async/await implementation
- **Database**: PostgreSQL with SQLAlchemy 2.0 ORM
- **Message Broker**: Apache Kafka integration
- **Authentication**: JWT-based authentication with OAuth2
- **Validation**: Pydantic for request/response validation
- **Monitoring**: Prometheus for metrics collection

## Backend Structure

The backend follows a layered architecture with clear separation of concerns:

### Models Layer
Located in `models/` directory, contains data models organized by type:
- **enum/**: Enum definitions for constants
- **pydantic/api/**: API models for request/response validation
- **pydantic/dto/**: Data Transfer Objects for internal logic
- **sqlalchemy/**: Database models mapping to PostgreSQL tables

Pydantic base models are based on `OrmModel` and `UUIDModel` (with `id: UUID` default factory) for `.model_validate()` initialization

API paginating models are based on `ViewList` and `ViewListQueries`

Naming convention: `{resource}_{layer}.{extension}` (e.g., `project_api.py`, `project_dto.py`, `project.py`)

### Database Layer (`api/db/`)
Implements data access using generic repository pattern:
- Inherits from `BaseDatabaseGeneric` for standard CRUD operations
- Provides type-safe database interactions
- Uses SQLAlchemy async sessions
- Leverages base repository methods for common operations

### Services Layer (`api/services/`)
Handles external integrations and business operations:
- Manages connections to external systems (Kafka, LLM providers)
- Implements service orchestration
- Provides centralized configuration access
- Coordinates multiple external services

### Managers Layer (`api/managers/`)
Contains business logic and orchestrates operations:
- Translates API requests to data operations
- Implements business rules and validations
- Coordinates multiple database operations
- Handles authentication and authorization

### Router Layer (`api/router/`)
Defines API endpoints and request handling:
- Maps HTTP routes to manager methods
- Applies FastAPI decorators for request/response handling
- Implements dependency injection for authentication
- Defines API documentation metadata

### HTTP Dependencies (`api/dependencies/http/`)
Manages request-scoped dependencies:
- User authentication and authorization
- Token validation and decoding
- Request logging and tracking
- Dependency injection for FastAPI

## Architectural Patterns

### Model Mapping Strategy
Three-layer model architecture:
1. **API Models**: Public interface for requests/responses
2. **DTO Models**: Internal data transfer for business logic
3. **SQLAlchemy Models**: Database entity mappings

Provides encapsulation between external interfaces and internal implementation.

### Generic Repository Pattern
All DB operations extend `BaseDatabaseGeneric` providing:
- Standard CRUD operations (create, get, update, delete)
- Bulk operations support
- Search and filtering
- Pagination and sorting
- Transaction management

Database row locks are not used in this project. Do not add `SELECT ... FOR UPDATE`,
SQLAlchemy `.with_for_update()`, or repository lock helpers. Use generic reads,
database constraints, and optimistic version filters for concurrent changes.

### Dependency Injection
Uses FastAPI's dependency injection:
- HTTP dependencies for authentication
- Singleton services for external connections
- Session management for database transactions
- Configuration injection through settings

## Code Style Guidelines

### File Organization
- Single primary class/function per module
- Descriptive and consistent filenames
- Import order: stdlib, third-party, internal
- Separation of public/private implementation

### Naming Conventions
- Classes: `PascalCase` (e.g., `ProjectsManager`)
- Variables: `snake_case` (e.g., `user_id`)
- Constants: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_TIMEOUT`)
- Type aliases: `PascalCase` (e.g., `ProjectID = UUID`)

### Exception Handling
- Specific HTTP exceptions from FastAPI
- Custom exception handling for domain-specific errors
- Proper status codes for error conditions
- Centralized exception handling

### Async/Await Patterns
- I/O operations use async/await
- Proper async context management
- Concurrent execution where beneficial
- Correct handling of async session lifecycles

## Development Guidelines

When working with this codebase:
- Follow the layered architecture and templates pattern
- Use existing model mapping strategy for new resources
- Extend BaseDatabaseGeneric for DB operations
- Implement business logic in managers layer
- Apply FastAPI decorators in routers
- Follow naming conventions and code style guidelines
- Ensure async/await patterns are properly implemented
- Add appropriate exception handling

## Architectural Patterns

### PATCH for Optimistic Updates
The backend supports optimistic UI updates through PATCH endpoints:

**Design principles:**
- PATCH endpoints accept partial payloads (only changed fields)
- Use `StepUpdateFieldsAPI` pattern with `NoneValidationMixin` for nullable fields
- Return full resource representation after update
- Keep `_none_allowed_fields` in sync with optional fields

**Example implementation:**
```python
class StepUpdateFieldsAPI(NoneValidationMixin):
    name: str | None = Field(default=None, min_length=3, max_length=100)
    description: str | None = Field(default=None)
    meta: dict | None = Field(default=None)
    
    _none_allowed_fields = {"description", "meta"}
```

**Manager pattern:**
```python
@staticmethod
async def patch_step(..., data: api_models.PatchStepRequest):
    step_update_dto = step_dto.StepUpdateFieldsDTO(
        **data.model_dump(exclude_unset=True)
    )
    updated_step = await Database.steps.update(id=step_id, data=step_update_dto)
```

This ensures minimal payload transfer and supports frontend optimistic updates efficiently.
