# Cosmo Backend Analysis Documentation

**Executive Summary**

Cosmo Backend is a comprehensive Go-based microservice platform designed for AI-powered sales and marketing automation. The system provides intelligent email outreach, campaign management, contact management, and multi-channel communication capabilities. It integrates with various third-party services including Gmail, HubSpot, Outlook, Google Ads, and AI providers like OpenAI. The platform follows clean architecture principles with clear separation between domain models, repositories, services, and API handlers across multiple API versions (v1, v2, v3). Its core value proposition lies in automating personalized outreach campaigns using AI to generate contextually relevant email templates and managing customer relationships at scale.

---

## Technology Stack

**Backend**
- **Language**: Go 1.25.5
- **Framework**: Fiber v3 (high-performance web framework)
- **Database**: PostgreSQL with pgvector extension
- **Cache**: Redis
- **Authentication**: JWT with refresh tokens
- **AI Integration**: OpenAI GPT-4
- **Queue**: Asynq (Redis-based task queue)

**Frontend** (not applicable - backend only)

**Infrastructure & Tools**
- **Deployment**: Docker, Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus metrics, Sentry
- **Documentation**: Swagger/OpenAPI
- **Testing**: Go testing framework

---

## Project Structure

```
cosmo-backend/
├── cmd/
│   ├── server/                 # HTTP server application
│   │   ├── main.go            # Server entry point
│   │   ├── app.go             # Fiber app configuration
│   │   ├── dependencies.go    # Dependency injection
│   │   └── routes_v*.go       # API route definitions
│   ├── worker/                # Background worker application
│   │   └── main.go            # Worker entry point
│   └── generate_test_token/   # Utility for JWT tokens
├── internal/
│   ├── domain/                # Business entities and models
│   ├── handler/               # HTTP handlers by API version
│   │   ├── v1/               # Version 1 API handlers
│   │   ├── v2/               # Version 2 API handlers
│   │   └── v3/               # Version 3 API handlers
│   ├── repository/            # Data access layer
│   ├── service/               # Business logic services
│   ├── usecase/               # Application use cases
│   ├── worker/                # Background task processors
│   ├── middleware/            # HTTP middleware
│   ├── mapper/                # Data transformation
│   └── schema/                # API request/response schemas
├── pkg/                       # Reusable packages
│   ├── ai/                    # AI client implementations
│   ├── auth/                  # Authentication utilities
│   ├── cache/                 # Cache management
│   ├── config/                # Configuration management
│   ├── database/              # Database connections
│   ├── logger/                # Logging utilities
│   ├── metrics/               # Prometheus metrics
│   ├── oauth2/                # OAuth2 clients
│   └── worker/                # Task queue client
├── migrations/                # Database migrations
├── docker/                    # Docker configurations
├── docs/                      # Swagger documentation
└── scripts/                   # Utility scripts
```

The project follows clean architecture with clear separation of concerns. Domain models are isolated from infrastructure concerns, repositories handle data persistence, services contain business logic, and handlers manage HTTP requests. The multi-version API structure allows for gradual evolution without breaking changes.

---

## Core Features & Modules

### Module 1: Agent Management
**Purpose**: AI agents that handle automated email communications and conversations

**Key Components**:
- **Agent Domain**: Core agent entity with configuration
- **Agent Repository**: Database operations for agents
- **Agent Handler**: HTTP endpoints for agent CRUD
- **Agent Worker**: Background processing for agent tasks

**API Endpoints**:
- `POST /v1/agents` - Create new agent
- `GET /v1/agents/:id` - Get agent by ID
- `POST /v1/agents/search` - Search agents with filters
- `PUT/PATCH /v1/agents/:id` - Update agent
- `DELETE /v1/agents/:id` - Delete agent
- `POST /v1/agents/:id/conversations/search` - Get agent conversations

**Database Tables**:
- `agents`: Agent configurations and settings

**Dependencies**:
- Internal: Conversation, Email, User repositories
- External: OpenAI API for AI capabilities

### Module 2: Campaign Management
**Purpose**: Create and manage email outreach campaigns with AI-generated templates

**Key Components**:
- **Campaign Domain**: Campaign entity with scheduling
- **Campaign Repository**: Database operations
- **Campaign Handler**: Multi-version API handlers
- **Campaign Worker**: Execute campaigns and schedule tasks

**API Endpoints**:
- `POST /v1/campaigns` - Create campaign
- `GET /v1/campaigns` - List campaigns
- `GET /v1/campaigns/:id` - Get campaign details
- `PATCH /v1/campaigns/:id` - Update campaign
- `DELETE /v1/campaigns/:id` - Delete campaign
- `POST /v1/campaigns/:id/generate` - Generate AI templates
- `POST /v1/campaigns/:id/assign` - Assign to members

**Database Tables**:
- `campaigns`: Campaign definitions and metadata
- `draft_templates`: AI-generated templates

**Dependencies**:
- Internal: Template, Contact, Agent, Notification repositories
- External: OpenAI API for template generation

### Module 3: Contact Management
**Purpose**: Manage contacts, custom fields, and list segmentation

**Key Components**:
- **Contact Domain**: Contact entity with custom fields
- **Contact Repository**: Database operations with complex queries
- **Contact Handler**: CRUD and import operations
- **Custom Field Service**: Dynamic field management

**API Endpoints**:
- `POST /v1/contacts` - Create contact
- `GET /v1/contacts` - List contacts
- `GET /v1/contact/:id` - Get contact details
- `PATCH /v1/contacts/:id` - Update contact
- `DELETE /v1/contacts` - Bulk delete contacts
- `POST /v1/contacts/search` - Search with filters
- `POST /v1/contacts/import-csv` - Import from CSV
- `POST /v1/contacts/import-hubspot` - Import from HubSpot

**Database Tables**:
- `contacts`: Contact records
- `custom_fields`: Dynamic field definitions
- `list_contacts`: Contact list associations

**Dependencies**:
- Internal: CustomField, ListContact, Organization repositories
- External: HubSpot API for integration

### Module 4: Email & Conversation Management
**Purpose**: Track email threads and conversations with AI-powered responses

**Key Components**:
- **Email Domain**: Email entity with threading
- **Conversation Domain**: Conversation tracking
- **Email Worker**: Send emails and sync with Gmail
- **AI Email Service**: Generate replies and classify intent

**API Endpoints**:
- `GET /v1/emails/:id` - Get email details
- `GET /v1/emails` - List emails
- `POST /v1/conversations/search` - Search conversations
- `GET /v1/conversations/:id` - Get conversation details
- `POST /v1/conversations/:id/assign` - Assign conversation
- `POST /v1/ai/emails/generate` - Generate email templates
- `POST /v1/ai/emails/reply` - Generate AI reply

**Database Tables**:
- `emails`: Email records
- `conversations`: Conversation threads

**Dependencies**:
- Internal: Agent, Contact repositories
- External: Gmail API, OpenAI API

### Module 5: Authentication & Authorization
**Purpose**: Secure API access with JWT and OAuth2 integrations

**Key Components**:
- **JWT Manager**: Token generation and validation
- **Auth Handler**: Login, refresh, OAuth callbacks
- **OAuth2 Clients**: Google, Microsoft, HubSpot integration
- **Personal API Keys**: Alternative authentication method

**API Endpoints**:
- `POST /v1/auth/login` - User login
- `POST /v1/auth/refresh` - Refresh token
- `GET /v1/auth/oauth2callback` - OAuth callback
- `GET /v1/auth/me` - Get current user
- `POST /v1/users/:user_id/personal-api-keys` - Create API key

**Database Tables**:
- `users`: User accounts
- `roles`: Role definitions
- `personal_api_keys`: API key management

**Dependencies**:
- Internal: User, Role repositories
- External: Google OAuth2, Microsoft OAuth2

### Module 6: Integration Hub
**Purpose**: Connect with external services (Gmail, HubSpot, Google Ads, etc.)

**Key Components**:
- **Gmail Service**: Gmail API integration with push notifications
- **HubSpot Service**: CRM synchronization
- **Google Ads Service**: Lead form integration
- **Outlook Service**: Microsoft email integration

**API Endpoints**:
- `GET /v1/gmail/auth/url` - Get Gmail auth URL
- `GET /v1/hubspot/authorize` - HubSpot OAuth
- `POST /v1/google-ads/generate-webhook` - Google Ads webhook
- `GET /v1/outlook/authorize` - Outlook OAuth

**Database Tables**:
- `integrations`: Third-party service connections
- `gmail_accounts`: Gmail account tokens
- `facebook_tokens`: Social media tokens

**Dependencies**:
- Internal: User, Contact repositories
- External: Gmail API, HubSpot API, Google Ads API

---

## System Architecture

**Architecture Pattern**: Clean Architecture with Hexagonal Ports

**Data Flow**:
```
Client → API Gateway → HTTP Handlers → Services → Repositories → Database
                                    ↓
                              Worker Queue → Background Workers
                                    ↓
                              External APIs (OpenAI, Gmail, etc.)
```

**Key Design Patterns**:
- **Repository Pattern**: Abstract data access behind interfaces
- **Service Layer**: Business logic encapsulation
- **Dependency Injection**: Centralized dependency management
- **Command Pattern**: Background task processing
- **Strategy Pattern**: Multiple AI provider implementations
- **Adapter Pattern**: External service integrations

---

## API Documentation

### Authentication API

**Endpoint**: `POST /v1/auth/login`
- **Purpose**: Authenticate user and return JWT tokens
- **Request**: `{ "email": "user@example.com", "password": "password" }`
- **Response**: `{ "access_token": "jwt", "refresh_token": "jwt" }`
- **Auth Required**: No

### Agent Management API

**Endpoint**: `POST /v1/agents`
- **Purpose**: Create new AI agent
- **Request**: Agent configuration object
- **Response**: Created agent details
- **Auth Required**: Yes

### Campaign API

**Endpoint**: `POST /v1/campaigns/:id/generate`
- **Purpose**: Generate AI-powered email templates for campaign
- **Request**: Campaign context and parameters
- **Response**: Generated email templates
- **Auth Required**: Yes

### Contact API

**Endpoint**: `POST /v1/contacts/search`
- **Purpose**: Search contacts with complex filters
- **Request**: Search filters and pagination
- **Response**: Paginated contact list
- **Auth Required**: Yes

### AI Email API

**Endpoint**: `POST /v1/ai/emails/reply`
- **Purpose**: Generate AI reply for email thread
- **Request**: Conversation context or ID
- **Response**: Generated email reply
- **Auth Required**: Yes

---

## Database Schema

```sql
-- Core entities
users (1:many) → organizations
organizations (1:many) → campaigns
campaigns (1:many) → draft_templates
campaigns (many:many) → contacts → list_contacts

-- Agent system
agents (1:many) → conversations
conversations (1:many) → emails

-- Custom fields
custom_fields (1:many) → custom_field_values

-- Integrations
users (1:many) → integrations
integrations (1:many) → gmail_accounts
```

**Main Tables**:
- `users`: User accounts and authentication
- `organizations`: Multi-tenant organizations
- `contacts`: Contact records with custom fields
- `campaigns`: Email campaign definitions
- `agents`: AI agent configurations
- `conversations`: Email conversation threads
- `templates`: Email templates
- `knowledge`: AI knowledge base

---

## Notable Features

1. **Multi-Version API**: Parallel v1, v2, v3 APIs allowing gradual migration
2. **AI-Powered Templates**: OpenAI integration for dynamic email generation
3. **Real-time Gmail Sync**: Push notifications for immediate email processing
4. **Custom Field System**: Dynamic contact fields without schema changes
5. **Background Processing**: Asynq-based task queue for scalable operations
6. **Multi-Channel Integration**: Gmail, Outlook, HubSpot, Google Ads
7. **WebSocket Support**: Real-time PubSub messaging
8. **Comprehensive Metrics**: Prometheus integration for monitoring

---

## Code Patterns & Conventions

**Naming Conventions**:
- Files: snake_case (e.g., `agent_handler.go`)
- Functions: camelCase for exported, snake_case for private
- Classes: PascalCase (e.g., `AgentHandler`)
- Variables: camelCase
- Constants: UPPER_SNAKE_CASE

**Code Organization**:
- Domain-driven design with clear boundaries
- Repository pattern for data access
- Service layer for business logic
- Handler layer for HTTP concerns
- Worker layer for background tasks

**Error Handling**:
- Consistent error response format
- Proper HTTP status codes
- Error wrapping with context
- Centralized error types

---

## External Integrations

### Integration 1: OpenAI
- **Purpose**: AI-powered email generation and intent classification
- **Implementation**: Direct API client with retry logic
- **Configuration**: API key and model selection

### Integration 2: Gmail API
- **Purpose**: Email sending, receiving, and real-time notifications
- **Implementation**: OAuth2 with push notifications via PubSub
- **Configuration**: OAuth credentials and webhook setup

### Integration 3: HubSpot
- **Purpose**: CRM synchronization and contact management
- **Implementation**: REST API client with webhook support
- **Configuration**: OAuth app credentials

### Integration 4: Google Ads
- **Purpose**: Lead form integration for campaign tracking
- **Implementation**: Webhook processing and lead conversion
- **Configuration**: Webhook URL and verification

---

## Configuration & Environment

**Required Environment Variables**:
```env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
JWT_SECRET=your-jwt-secret
OPENAI_API_KEY=your-openai-key
GOOGLE_CLIENT_ID=oauth-client-id
GOOGLE_CLIENT_SECRET=oauth-client-secret
```

**Optional Environment Variables**:
```env
SENTRY_DSN=error-tracking-dsn
AWS_ACCESS_KEY_ID=s3-access-key
AWS_SECRET_ACCESS_KEY=s3-secret-key
HUBSPOT_CLIENT_ID=hubspot-client-id
```

---

## Development Workflow

**Setup Instructions**:
1. Clone repository
2. Copy `.env.example` to `.env` and configure
3. Start services: `docker-compose -f docker/docker-compose.local.yml up`
4. Run migrations: `docker-compose exec migrate /migrate/migrate.sh`
5. Install dependencies: `go mod download`
6. Run server: `go run cmd/server/main.go`

**Common Commands**:
```bash
go run cmd/server/main.go          # Start server
go run cmd/worker/main.go          # Start worker
go test ./...                       # Run tests
go build -o bin/server ./cmd/server # Build binary
swag init -g cmd/server/main.go    # Generate docs
```

---

## Insights for Future Development

**Strengths**:
- Clean architecture with excellent separation of concerns
- Comprehensive test coverage across all layers
- Multi-version API design for backward compatibility
- Robust background processing with task queues
- Extensive third-party integrations

**Potential Improvements**:
- Add database connection pooling configuration
- Implement API rate limiting per user
- Add request/response compression
- Improve error messages for better debugging
- Add comprehensive API documentation examples

**Missing Features**:
- Real-time analytics dashboard
- A/B testing for email campaigns
- Advanced reporting and export features
- Email template preview functionality
- Bulk operations optimization

**Technical Debt**:
- Some worker implementations use placeholder patterns
- Gmail service integration needs refactoring
- Database queries could benefit from optimization
- Error handling could be more granular
- Some v1 endpoints need deprecation planning

---

## 🤖 Insights for AI-Powered Module & Task Generation

### Module Generation Guidelines

**Project Type**: Web Backend (REST API) with Background Workers

**Step 1: Project Type Detection**
This is a Go-based web backend service with:
- REST API endpoints across multiple versions
- Background worker processing
- Database persistence with PostgreSQL
- Redis for caching and queuing
- Multiple third-party integrations

**Step 2: Module Patterns Discovered**

**Pattern 1: Domain-Repository-Service-Handler**
```
internal/domain/[entity]/
├── [entity].go              # Domain model and business rules
├── [entity]_test.go         # Domain unit tests

internal/repository/[entity]/
├── [entity]_repository.go   # Database operations
├── [entity]_test.go         # Repository tests

internal/service/[entity]/
├── [entity]_service.go      # Business logic
├── [entity]_test.go         # Service tests

internal/handler/v[1-3]/[entity]/
├── [entity]_handler.go      # HTTP handlers
├── [entity]_test.go         # Handler tests
```

Key characteristics:
- File naming: snake_case with entity prefix
- Organization: By feature/entity with layered architecture
- Dependencies: Constructor injection through interfaces
- Size range: 200-800 lines per file

**Pattern 2: Worker Module**
```
internal/worker/[entity]/
├── [entity]_worker.go       # Task handlers
├── [entity]_worker_test.go  # Worker tests
```

**Common Elements Across All Modules**:
- Required files: Domain model, repository, service, handler
- Optional files: Worker for background processing, use case for complex operations
- Shared utilities: `pkg/` directory for common functionality
- Configuration: Environment-based with struct mapping

**Boilerplate Template for New Module**:
```go
// Domain Model
package domain

import (
    "time"
    "github.com/google/uuid"
)

type [Entity] struct {
    ID        uuid.UUID  `gorm:"type:uuid;primary_key;default:gen_random_uuid()"`
    CreatedAt time.Time  `gorm:"autoCreateTime"`
    UpdatedAt time.Time  `gorm:"autoUpdateTime"`
    DeletedAt *time.Time `gorm:"index"`
    
    // Add fields here
    Name string `gorm:"not null"`
}

// Repository Interface
type [Entity]Repository interface {
    Create(ctx context.Context, entity *[Entity]) error
    GetByID(ctx context.Context, id uuid.UUID) (*[Entity], error)
    Update(ctx context.Context, entity *[Entity]) error
    Delete(ctx context.Context, id uuid.UUID) error
    List(ctx context.Context, offset, limit int) ([]*[Entity], error)
}

// Service
package service

type [Entity]Service struct {
    repo [Entity]Repository
}

func New[Entity]Service(repo [Entity]Repository) *[Entity]Service {
    return &[Entity]Service{repo: repo}
}

// Handler
package handler

type [Entity]Handler struct {
    service *service.[Entity]Service
}

func New[Entity]Handler(service *service.[Entity]Service) *[Entity]Handler {
    return &[Entity]Handler{service: service}
}
```

**Module Dependencies & Communication**:
- **Inter-module communication**: Direct interface injection
- **Dependency injection**: Constructor-based with interface parameters
- **Shared resources**: Database connection, Redis client, logger
- **Error propagation**: Wrapped errors with context

**Naming Conventions**:
- **File/Module names**: `entity_handler.go`, `entity_service.go`
- **Class names**: `[Entity]Handler`, `[Entity]Service`, `[Entity]Repository`
- **Function names**: `Create[Entity]`, `Get[Entity]ByID`, `Update[Entity]`
- **Variable names**: `entityService`, `entityRepository`
- **Constants**: `MAX_[ENTITY]_COUNT`, `DEFAULT_[ENTITY]_LIMIT`

**Registration/Integration Pattern**:
```go
// In cmd/server/dependencies.go
func init[Entity]Handler(deps *Dependencies) *[Entity]Handler {
    return handler.New[Entity]Handler(
        deps.Services.[Entity],
    )
}

// In cmd/server/routes_v1.go
func RegisterV1Routes(app *App, deps *Dependencies) {
    h := deps.V1Handlers
    v1 := app.Fiber.Group("/v1")
    
    v1.Post("/[entities]", h.[Entity].Create)
    v1.Get("/[entities]/:id", h.[Entity].GetByID)
}
```

**Testing Pattern**:
```
internal/domain/[entity]/
├── [entity]_test.go         # Domain logic tests
internal/repository/[entity]/
├── [entity]_test.go         # Repository tests with test DB
internal/service/[entity]/
├── [entity]_test.go         # Service tests with mocks
internal/handler/v1/[entity]/
├── [entity]_handler_test.go # HTTP tests with test server
```

### Task Generation Guidelines

**Task Complexity Classification**:

**Simple Tasks** (1-3 hours):
- Add new API endpoint with basic CRUD
- Add validation to existing endpoint
- Fix bug in service logic
- Add unit tests for existing function

**Medium Tasks** (4-8 hours):
- Implement new service with business logic
- Add worker for background processing
- Integrate new external API
- Refactor existing module

**Complex Tasks** (1-3 days):
- Add new domain entity with full stack
- Implement multi-step workflow
- Major database schema changes
- Performance optimization

**Task Breakdown Template**:

```markdown
## Task: Add [Feature Name] to [Entity]

**Context**: [Business value and user story]

**Type**: API Development / Service Layer / Database Migration

**Complexity**: Medium (6 hours estimated)

**Module/Area**: internal/domain/[entity], internal/handler/v1/[entity]

### Implementation Details

**Files to Create**:
```
internal/domain/[entity]/[feature].go (100 lines)
├── Purpose: Add [feature] functionality to domain
├── Responsibilities: Business rules for [feature]
├── Dependencies: Existing [entity] domain
└── Exports: [Feature] struct and methods

internal/handler/v1/[entity]/[feature]_handler.go (150 lines)
├── Purpose: HTTP endpoints for [feature]
├── Responsibilities: Request handling and validation
├── Dependencies: [Entity]Service
└── Exports: [Feature]Handler struct
```

**Files to Modify**:
```
1. internal/domain/[entity]/[entity].go
   Location: [Entity] struct definition
   Change: Add [Feature] field
   Reason: Support new feature in domain model

2. internal/repository/[entity]/[entity]_repository.go
   Location: Repository interface
   Change: Add [Feature]CRUD methods
   Reason: Data access for new feature

3. cmd/server/routes_v1.go
   Location: Route registration
   Change: Add [feature] endpoints
   Reason: Expose new functionality via API
```

**Dependencies**:
- **Internal**: [Entity]Repository, [Entity]Service
- **External**: None
- **Configuration**: New env vars if needed
- **Database**: Migration to add [feature] column
- **Infrastructure**: None

**Data Model Changes**:
```sql
-- Migration: add_[feature]_to_[entity].sql
ALTER TABLE [entities] 
ADD COLUMN [feature] VARCHAR(255);
```

**API Changes**:
```
New Endpoints:
- POST /v1/[entities]/:id/[feature]
  Request: { [feature]_data }
  Response: { [feature]_result }
  Auth: Required

Modified Endpoints:
- GET /v1/[entities]/:id
  Changes: Include [feature] in response
```

**Acceptance Criteria**:
- [ ] [Feature] field added to [entity] model
- [ ] API endpoints created and documented
- [ ] Database migration written and tested
- [ ] Unit tests cover new functionality (80%+ coverage)
- [ ] Integration tests verify end-to-end flow
- [ ] Error handling follows project patterns
- [ ] Code passes all linting checks

**Testing Requirements**:
```
Test files to create/update:
- internal/domain/[entity]/[feature]_test.go
- internal/handler/v1/[entity]/[feature]_handler_test.go

Test cases needed:
1. Happy path: Create [feature] successfully
2. Validation: Invalid [feature] data rejected
3. Error handling: Database errors handled gracefully
4. Authorization: Unauthorized access blocked

Mock/Stub requirements:
- Mock [Entity]Repository for handler tests
```

**Implementation Order**:
1. Create database migration
2. Update domain model
3. Implement repository methods
4. Add service layer logic
5. Create HTTP handlers
6. Register routes
7. Write tests
8. Update documentation
```

### Reusable Components Identified

**Highly Reusable Components**:

**Component**: Base Repository
- **Location**: `internal/repository/base/base_repository.go`
- **Current Usage**: Used by all repositories for common CRUD operations
- **Why It's Reusable**: Generic CRUD patterns, pagination, filtering
- **How to Extract**: Already extracted as base repository
- **Dependencies**: GORM DB instance
- **Example Usage**:
```go
type CustomRepository struct {
    *base.BaseRepository[CustomEntity]
}
```

**Component**: JWT Manager
- **Location**: `pkg/auth/jwt.go`
- **Current Usage**: Authentication across all API versions
- **Why It's Reusable**: Token generation, validation, refresh logic
- **How to Extract**: Already a standalone package
- **Dependencies**: None (just crypto libraries)

**Component**: Response Helper
- **Location**: `internal/handler/response_helper.go`
- **Current Usage**: Standardized API responses
- **Why It's Reusable**: Consistent error/success response format
- **How to Extract**: Already extracted
- **Dependencies**: Fiber context

**Component**: Pagination Helper
- **Location**: `internal/handler/v1/pagination/pagination_helper.go`
- **Current Usage**: List endpoints across all entities
- **Why It's Reusable**: Standardized pagination logic
- **How to Extract**: Already extracted
- **Dependencies**: None

### Code Generation Best Practices

**DO** (Patterns that work well in this project):
1. **Use interfaces for all repositories** - Enables testing and flexibility
2. **Wrap errors with context** - `fmt.Errorf("operation failed: %w", err)`
3. **Use dependency injection** - Constructor injection with interfaces
4. **Follow naming conventions** - Consistent across all modules
5. **Write comprehensive tests** - Unit, integration, and HTTP tests

**DON'T** (Anti-patterns to avoid):
1. **Don't use global variables** - Pass dependencies explicitly
2. **Don't ignore errors** - Always handle or wrap errors
3. **Don't hardcode values** - Use configuration and constants
4. **Don't skip validation** - Validate all inputs
5. **Don't mix concerns** - Keep layers separate

**Code Quality Standards**:
- **Function length**: Median 20 lines, Max 100 lines
- **File length**: Median 300 lines, Max 800 lines
- **Complexity**: Keep cyclomatic complexity < 10
- **Type annotations**: Required for all public functions
- **Documentation**: Godoc comments for all public types/functions
- **Error handling**: Always handle errors, wrap with context
- **Logging**: Use structured logging with logger.Logger

**Consistency Checklist for Generated Code**:
- [ ] Follows snake_case file naming
- [ ] Uses camelCase for exported functions
- [ ] Error handling matches project pattern
- [ ] Logging uses structured logger
- [ ] File organization matches module pattern
- [ ] Documentation includes Godoc comments
- [ ] Testing follows existing patterns

### Gaps & Opportunities for New Modules

**Missing Features** (ranked by priority):
1. **Analytics Dashboard** - Priority: High
   - Why needed: Business insights and campaign performance
   - Complexity: High
   - Dependencies: Metrics collection, data aggregation
   - Estimated effort: 5 days
   - Module pattern to use: New analytics domain with service layer

2. **A/B Testing Framework** - Priority: Medium
   - Why needed: Optimize email campaigns
   - Complexity: Medium
   - Dependencies: Campaign module, statistics
   - Estimated effort: 3 days
   - Module pattern to use: Extend campaign domain

3. **Email Template Preview** - Priority: Medium
   - Why needed: Better UX for template creation
   - Complexity: Low
   - Dependencies: Template module
   - Estimated effort: 2 days
   - Module pattern to use: Add to existing template handler

**Incomplete Implementations**:
- `internal/worker/email/worker.go`: Missing Gmail integration
- `internal/service/gmail/gmail_service.go`: TODO comments indicate incomplete features
- Database: Missing indexes on frequently queried columns

**Technical Debt to Address**:
1. **Worker Placeholder Implementations**: 
   - Impact: Medium
   - Effort to fix: 2 days
   - Risk if not fixed: Background jobs may fail
   - Suggested approach: Implement actual Gmail API integration

2. **Inconsistent Error Handling**:
   - Impact: Low
   - Effort to fix: 1 day
   - Risk if not fixed: Poor debugging experience
   - Suggested approach: Standardize error wrapping pattern

### Integration Patterns

**How to Add New External Service**:
```go
// 1. Create client in pkg/
pkg/[service]/
├── client.go          # API client implementation
├── config.go          # Configuration struct
└── types.go           # Service-specific types

// 2. Create service in internal/service/
internal/service/[service]/
├── [service]_service.go
├── [service]_service_test.go

// 3. Add configuration to pkg/config/config.go
type Config struct {
    [Service] [Service]Config `yaml:"[service]"`
}

// 4. Add to dependencies.go
deps.Services.[Service] = [service]Service.New(cfg.[Service])

// 5. Add handler if needed
internal/handler/v1/[service]/
├── [service]_handler.go
```

**How to Add New Database Table**:
```sql
-- 1. Create migration
migrations/XXX_create_[table].up.sql
migrations/XXX_create_[table].down.sql

-- 2. Create domain model
internal/domain/[entity]/[entity].go

-- 3. Create repository
internal/repository/[entity]/[entity]_repository.go

-- 4. Create service
internal/service/[entity]/[entity]_service.go

-- 5. Create handler
internal/handler/v1/[entity]/[entity]_handler.go

-- 6. Register routes
cmd/server/routes_v1.go
```