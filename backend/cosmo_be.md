**Cosmo Backend - (Claude review SKILL.md)**

**Executive Summary**

Cosmo Backend is a comprehensive Go-based AI-powered email automation and CRM integration platform. The system provides intelligent email agents, marketing campaign management, contact synchronization across multiple platforms, and AI-driven content generation. It serves as the backend infrastructure for the Cosmo Agents platform, integrating with Gmail/Outlook, HubSpot, OpenAI, and various advertising platforms to automate sales and marketing workflows.

**Technology Stack**

**Backend**

- **Language**: Go 1.25.3
- **Web Framework**: Fiber v3 (high-performance HTTP framework)
- **Database**: PostgreSQL via GORM ORM
- **Queue System**: Redis with Asynq for background job processing
- **Authentication**: JWT-based with OAuth2 integration (Google, Microsoft)
- **AI Integration**: OpenAI GPT-4 for content generation and intent classification
- **Logging**: Zerolog structured logging
- **Configuration**: Viper for environment-based config management

**Infrastructure & External Services**

- **Email Providers**: Gmail API, Microsoft Graph/Outlook
- **CRM Integration**: HubSpot API
- **File Storage**: AWS S3 (with MinIO for local development)
- **Communication**: WebSocket support via FastHTTP
- **Metrics**: Prometheus client library
- **Error Tracking**: Sentry integration
- **Background Processing**: Asynq with Redis broker

**Development Tools**

- **Testing**: Standard Go testing with testify
- **API Documentation**: Swagger/OpenAPI generation
- **Code Quality**: golangci-lint, gofmt, goimports
- **Database Migrations**: golang-migrate
- **Containerization**: Docker with docker-compose

**Project Structure**

**Backend Architecture**

Plain Text  
cosmo-backend/  
├── cmd/ # Application entry points  
│ ├── server/ # HTTP API server  
│ │ ├── main.go # Server bootstrap  
│ │ ├── app.go # Fiber app setup  
│ │ ├── dependencies.go # DI container setup  
│ │ └── routes_v\*.go # API route definitions (v1, v2, v3)  
│ └── worker/ # Background job processor  
│ └── main.go # Worker bootstrap with Asynq  
├── internal/ # Private application code  
│ ├── domain/ # Core business entities  
│ ├── handler/ # HTTP request handlers  
│ │ ├── v1/, v2/, v3/ # API versioning  
│ │ └── common/ # Shared handler utilities  
│ ├── service/ # Business logic layer  
│ ├── repository/ # Data access layer  
│ ├── schema/ # Request/response DTOs  
│ ├── middleware/ # HTTP middleware  
│ ├── worker/ # Background job handlers  
│ ├── usecase/ # Use case implementations  
│ ├── core/ # Core utilities  
│ └── templates/ # HTML templates  
├── pkg/ # Public packages  
│ ├── config/ # Configuration management  
│ ├── database/ # Database connection utilities  
│ ├── logger/ # Logging utilities  
│ ├── ai/ # AI client wrappers  
│ ├── oauth2/ # OAuth2 utilities  
│ ├── gmail/ # Gmail API client  
│ └── worker/ # Job queue utilities  
├── migrations/ # Database schema migrations  
├── docker/ # Docker configurations  
├── docs/ # Generated API documentation  
└── scripts/ # Utility scripts

**Core Features & Modules**

**Module 1: Agent Management System**

**Purpose**: AI-powered email agents that handle automated communication **Location**: internal/domain/agent.go, internal/service/agent/, internal/handler/v1/agent/ **Key Components**:

- **Agent Entity**: Core agent representation with OAuth credentials, email providers (Gmail/Outlook)
- **Agent Service**: Business logic for agent lifecycle, credential management, daily limits
- **OAuth Integration**: Google OAuth2 and Microsoft Graph authentication
- **Token Management**: Automatic token refresh and expiry handling

**API Endpoints**:

- GET /v1/agents - List agents with filtering and pagination
- POST /v1/agents - Create new agent
- PUT /v1/agents/{id} - Update agent configuration
- DELETE /v1/agents/{id} - Soft delete agent
- POST /v1/agents/{id}/sync - Trigger Gmail history sync

**Database Tables**:

- agents: Core agent data with credentials and OAuth tokens

**Dependencies**:

- Internal: User management, Organization system
- External: Google OAuth2, Microsoft Graph, Gmail API

**Module 2: Campaign & Email Automation**

**Purpose**: Multi-channel email marketing campaigns with AI-generated content **Location**: internal/domain/campaign.go, internal/service/campaign_service.go **Key Components**:

- **Campaign Engine**: Complex workflow orchestration with intent-based routing
- **AI Content Generation**: OpenAI integration for personalized email templates
- **Intent Classification**: Automatic response categorization (Interested, Not Interested, Referral, etc.)
- **Multi-step Sequences**: Email drip campaigns with conditional logic
- **Round-robin Assignment**: Sales representative assignment automation

**API Endpoints**:

- GET /v1/campaigns - List campaigns with metadata
- POST /v1/campaigns - Create campaign with playbook
- PUT /v1/campaigns/{id} - Update campaign configuration
- POST /v1/campaigns/{id}/assign - Assign to sales representatives
- POST /v1/campaigns/{id}/schedule - Schedule campaign execution

**Database Tables**:

- campaigns: Campaign configuration and metadata
- templates: Email templates associated with campaigns
- notifications: Campaign response notifications

**Dependencies**:

- Internal: Agent system, Contact management, AI services
- External: OpenAI API, Email providers

**Module 3: Contact Management & CRM Integration**

**Purpose**: Unified contact database with multi-platform synchronization **Location**: internal/domain/contact.go, internal/service/contact_service.go **Key Components**:

- **Contact Entity**: Unified contact model with custom fields support
- **Multi-source Import**: CSV, HubSpot, Google Ads, Facebook Ads integration
- **List Management**: Contact segmentation and targeting
- **Custom Fields**: Flexible metadata system for contact attributes
- **Duplicate Detection**: Intelligent contact deduplication

**API Endpoints**:

- GET /v1/contacts - Search and filter contacts
- POST /v1/contacts - Create new contact
- POST /v1/contacts/import - Bulk import from various sources
- GET /v1/lists/{id}/contacts - Get contacts from specific list
- POST /v1/lists - Create contact lists

**Database Tables**:

- contacts: Core contact data with profile JSONB
- list_contacts: Contact list management
- list_contact_association: Many-to-many relationship
- custom_fields: Flexible field definitions

**Dependencies**:

- Internal: Organization system, User management
- External: HubSpot API, CSV processing, Ad platforms

**Module 4: AI Services & Content Generation**

**Purpose**: AI-powered content generation and intelligent email processing **Location**: internal/service/ai_email_service.go, internal/handler/v1/ai_handler.go **Key Components**:

- **Intent Classification**: Automatic email response categorization
- **AI Reply Generation**: Context-aware email response generation
- **Template Creation**: AI-generated email templates for campaigns
- **Conversation Analysis**: Email thread understanding and context extraction

**API Endpoints**:

- POST /v1/ai/classify-intent - Classify email intent
- POST /v1/ai/generate-reply - Generate AI email reply
- POST /v1/ai/generate-template - Create campaign templates
- POST /v1/ai/analyze-conversation - Analyze email conversation

**Dependencies**:

- Internal: Email repository, Conversation management
- External: OpenAI API (GPT-4)

**Module 5: Background Job Processing**

**Purpose**: Asynchronous task processing for email operations and integrations **Location**: internal/worker/, cmd/worker/main.go **Key Components**:

- **Email Worker**: Send emails, sync Gmail history, process incoming emails
- **Campaign Worker**: Execute campaign sequences, handle follow-ups
- **AI Worker**: Process AI tasks, intent classification
- **Daily Reset Worker**: Reset agent daily limits, cleanup tasks

**Job Types**:

- agent:send_email - Send emails via agent
- agent:daily_reset - Reset daily sending limits
- email:process_incoming - Process incoming emails
- email:sync_history - Sync Gmail history
- campaign:execute - Execute campaign steps

**Dependencies**:

- Internal: All service layers
- External: Redis (job queue), Email APIs

**Module 6: Authentication & Authorization**

**Purpose**: Secure API access with multi-provider OAuth integration **Location**: internal/handler/v1/auth_handler.go, pkg/oauth2/ **Key Components**:

- **JWT Authentication**: Token-based API authentication
- **Multi-provider OAuth**: Google, Microsoft, Coze integration
- **Role-based Access**: User and organization-based permissions
- **API Key Management**: Personal API keys for programmatic access

**API Endpoints**:

- POST /v1/auth/login - User authentication
- GET /v1/auth/oauth2callback - OAuth callback handler
- POST /v1/auth/refresh - Refresh JWT tokens
- GET /v1/auth/me - Get current user info
- POST /v1/auth/coze/token - Coze platform authentication

**Database Tables**:

- users: User authentication data
- personal_api_keys: API key management
- organizations: Organization management

**System Architecture**

**Overall Architecture Pattern**

The system follows **Clean Architecture** principles with clear separation of concerns:

Plain Text  
HTTP Layer (Handlers) → Service Layer (Business Logic) → Repository Layer (Data Access) → Domain Layer (Core Entities)

**API Layer**

**Multi-version API Structure**:

- /v1/ - Legacy Python parity endpoints
- /v2/ - Enhanced endpoints with additional features
- /v3/ - Latest endpoints with improved performance

**Authentication Flow**:

- JWT middleware for authenticated endpoints
- OAuth2 integration for external service connections
- Provider-specific authentication (Google, Microsoft)

**Service Layer**

**Key Services**:

- **AgentService**: Agent lifecycle, credential management, OAuth handling
- **CampaignService**: Campaign orchestration, workflow execution
- **AIEmailService**: AI content generation, intent classification
- **ContactService**: Contact management, import/export operations
- **CozeService**: Third-party platform integration

**Design Patterns**:

- **Repository Pattern**: Data access abstraction with GORM
- **Service Layer Pattern**: Business logic encapsulation
- **Dependency Injection**: Container-based service composition
- **Factory Pattern**: Worker and handler creation

**Data Layer**

**Database Schema**:

SQL  
\-- Core entity relationships  
users (1:many) → agents  
users (1:many) → organizations  
organizations (1:many) → agents  
agents (1:many) → conversations  
campaigns (1:many) → conversations  
campaigns (1:many) → templates  
users (1:many) → contacts  
list_contacts (many:many) → contacts

**Repository Pattern**:

- Generic GormRepository\[T\] for common CRUD operations
- Specialized repositories for complex queries
- Transaction support for multi-entity operations

**External Integrations**

**Integration 1: Google Workspace**

- **Purpose**: Gmail integration for email sending and history sync
- **Implementation**: OAuth2 with Gmail API and People API
- **Configuration**: Google Cloud Console project setup

**Integration 2: Microsoft Graph**

- **Purpose**: Outlook email integration
- **Implementation**: OAuth2 with Microsoft Graph API
- **Configuration**: Azure AD application registration

**Integration 3: OpenAI**

- **Purpose**: AI content generation and intent classification
- **Implementation**: Direct API integration with GPT-4
- **Configuration**: OpenAI API key management

**Integration 4: HubSpot**

- **Purpose**: CRM synchronization and contact management
- **Implementation**: HubSpot API with webhook support
- **Configuration**: HubSpot developer account setup

**Integration 5: Coze Platform**

- **Purpose**: Third-party platform authentication
- **Implementation**: JWT-based authentication with RSA keys
- **Configuration**: RSA key pair generation and registration

**Code Patterns & Conventions**

**Naming Conventions**

- **Files**: snake_case.go (e.g., agent_service.go)
- **Functions**: PascalCase for exported, camelCase for private
- **Classes/Structs**: PascalCase (e.g., AgentService)
- **Constants**: UPPER_SNAKE_CASE (e.g., DefaultPageSize)
- **Database**: snake_case table and column names

**Code Organization**

- **Domain-Driven Design**: Business logic separated from infrastructure
- **Layered Architecture**: Clear separation between handlers, services, repositories
- **Package-by-feature**: Related functionality grouped in packages
- **Interface-based design**: Dependency injection through interfaces

**Error Handling**

- **Structured Error Types**: Domain-specific error types with wrapping
- **HTTP Error Mapping**: Consistent error response format
- **Logging Integration**: All errors logged with context
- **Graceful Degradation**: Fallback behaviors for external service failures

**Logging & Monitoring**

**Structured Logging**:

Go  
logger.Info("Agent created",  
"agent_id", agent.ID,  
"user_id", userID,  
"duration_ms", time.Since(start).Milliseconds())

**Metrics Collection**:

- Prometheus counters for HTTP requests
- Histograms for request duration
- Custom business metrics (emails sent, campaigns executed)

**Configuration & Environment**

**Environment Variables**

Plain Text  
REQUIRED:  
\- SQLALCHEMY_POSTGRES_URI: PostgreSQL connection string  
\- REDIS_URL: Redis connection URL  
\- JWT_SECRET: JWT signing secret  
\- OPENAI_API_KEY: OpenAI API access key  
<br/>OPTIONAL:  
\- GOOGLE_CLIENT_ID/SECRET: Google OAuth configuration  
\- COZE_APP_ID/PUBLIC_KEY_ID/PRIVATE_KEY_PATH: Coze integration  
\- AWS_ACCESS_KEY_ID/SECRET_ACCESS_KEY: S3 file storage  
\- SENTRY_DSN: Error tracking

**Configuration Files**

- .env.example: Environment variable template
- docker/docker-compose.yml: Local development environment
- pkg/config/: Configuration structure and loading

**Data Models & Schemas**

**Core Domain Models**

Go  
type Agent struct {  
Base // UUID, timestamps, soft delete  
UserID uuid.UUID  
OrganizationID \*uuid.UUID  
Name string  
Email string  
Status AgentStatus  
EmailProvider AgentEmailProvider  
Credentials JSON // OAuth tokens (encrypted)  
DailyLimit \*int  
MaxDailyLimit \*int  
EmailsSentToday \*int  
}  
<br/>type Campaign struct {  
Base  
UserID uuid.UUID  
Name string  
Playbook string  
Status CampaignStatus  
CMetadata CampaignMetadata // JSONB for complex config  
AgentID \*uuid.UUID  
}  
<br/>type Contact struct {  
Base  
UserID uuid.UUID  
Source string // ContactSource enum  
Email string  
Profile JSONB // Flexible contact data  
Tags JSONB // Custom tags  
}

**API Request/Response Schemas**

Go  
type CreateAgentRequest struct {  
UserID uuid.UUID \`validate:"required"\`  
Name string \`validate:"required"\`  
Email string \`validate:"required,email"\`  
EmailProvider domain.AgentEmailProvider \`validate:"required"\`  
Persona \[\]string  
DailyLimit \*int  
}

**API Documentation**

**Agent Management API**

**GET /v1/agents**

- Purpose: List agents with filtering and pagination
- Request: Query parameters for status, organization, pagination
- Response: Paginated agent list with metadata
- Auth Required: Yes

**POST /v1/agents**

- Purpose: Create new email agent
- Request: Agent configuration with OAuth credentials
- Response: Created agent details
- Auth Required: Yes

**Campaign Management API**

**GET /v1/campaigns**

- Purpose: List marketing campaigns
- Request: Filtering by status, user, organization
- Response: Campaign list with configuration metadata
- Auth Required: Yes

**POST /v1/campaigns/{id}/assign**

- Purpose: Assign campaign to sales representatives
- Request: Assignment configuration with intent handlers
- Response: Updated campaign assignment
- Auth Required: Yes

**AI Services API**

**POST /v1/ai/classify-intent**

- Purpose: Classify email intent using AI
- Request: Email content and context
- Response: Intent classification with confidence scores
- Auth Required: Yes

**POST /v1/ai/generate-reply**

- Purpose: Generate AI-powered email reply
- Request: Conversation context and reply parameters
- Response: Generated email content with metadata
- Auth Required: Yes

**Insights for Automatic Generation**

**Module Generation Guidelines**

**Existing Module Patterns**: Each module consistently follows this structure:

- **Domain Entity**: internal/domain/{feature}.go
- **Service Layer**: internal/service/{feature}/
- **Repository Layer**: internal/repository/{feature}/
- **API Handler**: internal/handler/v{version}/{feature}/
- **Schema Definitions**: internal/schema/v{version}/{feature}.go
- **Worker Tasks**: internal/worker/{feature}/ (if background processing needed)

**Recommended Structure for New Modules**:

Plain Text  
New Feature: \[FeatureName\]  
1\. Create domain entity: internal/domain/feature_name.go  
2\. Create repository: internal/repository/feature_name/  
3\. Create service: internal/service/feature_name/  
4\. Create handler: internal/handler/v1/feature_name/  
5\. Create schemas: internal/schema/v1/feature_name.go  
6\. Add routes: cmd/server/routes_v1.go  
7\. Add worker (if needed): internal/worker/feature_name_worker.go  
8\. Create migration: migrations/XXX_create_feature_table.up.sql

**Task Generation Guidelines**

**Common Task Types**:

- **CRUD Operations**: Standard create, read, update, delete for entities
- **Integration Tasks**: Connect to external APIs and services
- **Background Jobs**: Async processing with worker system
- **AI Tasks**: Content generation and classification
- **Migration Tasks**: Database schema updates

**Task Template**:

Plain Text  
Task: \[Action\] \[Entity/Feature\]  
Module: \[Related module\]  
Files to Create/Modify:  
\- internal/domain/\[entity\].go: \[Domain model definition\]  
\- internal/repository/\[entity\]/: \[Data access layer\]  
\- internal/service/\[entity\]/: \[Business logic\]  
\- internal/handler/v1/\[entity\]/: \[HTTP handlers\]  
\- migrations/XXX_\[description\].sql: \[Database changes\]  
Dependencies:  
\- \[Required internal modules\]  
\- \[Required external services\]  
Acceptance Criteria:  
\- \[Functional requirements\]  
\- \[API contract compliance\]  
\- \[Error handling requirements\]  
\- \[Testing requirements\]

**Identified Gaps & Opportunities**

**Missing Features**:

- **Real-time Analytics**: Campaign performance dashboards and metrics
- **Advanced Email Templates**: WYSIWYG template editor with preview
- **A/B Testing**: Campaign variant testing and performance comparison
- **Advanced Segmentation**: Dynamic contact segmentation based on behavior
- **Mobile App Support**: Native mobile applications for iOS/Android

**Improvement Areas**:

- **API Rate Limiting**: Implement more sophisticated rate limiting
- **Caching Strategy**: Redis-based caching for frequently accessed data
- **Search Optimization**: Full-text search for contacts and conversations
- **Performance Monitoring**: APM integration and performance baselines
- **Testing Coverage**: Increase unit and integration test coverage

**Technical Debt**:

- **OAuth Token Security**: Implement more secure token storage
- **Database Indexing**: Add missing indexes for query optimization
- **Error Handling**: Standardize error response formats
- **API Documentation**: Keep Swagger docs updated with latest changes

**Dependencies Map**

**Backend Dependencies**

Plain Text  
cmd/server/main.go  
├── pkg/config/ # Configuration loading  
├── pkg/database/ # Database connections  
├── internal/middleware/ # HTTP middleware  
├── internal/handler/ # API handlers  
│ └── internal/service/ # Business logic  
│ └── internal/repository/ # Data access  
│ └── internal/domain/ # Core entities  
├── internal/worker/ # Background jobs  
└── pkg/ # Shared utilities

**External Service Dependencies**

Plain Text  
Application Layer  
├── PostgreSQL (Primary Database)  
├── Redis (Queue & Cache)  
├── OpenAI API (AI Services)  
├── Google APIs (Gmail, OAuth2)  
├── Microsoft Graph (Outlook)  
├── HubSpot API (CRM Integration)  
├── AWS S3 (File Storage)  
└── Sentry (Error Tracking)

**Development Workflow**

**Setup Instructions**

- **Prerequisites**: Go ≥ 1.25, Docker Desktop, Make
- **Clone & Configure**:

Bash  
git clone <https://github.com/rockship/cosmo-agents-go.git>  
cd cosmo-agents-go  
cp .env.example .env

- **Development Environment**:

Bash  
make docker-up # PostgreSQL + Redis  
make build # Build binaries  
make migrate-up # Run database migrations  
make run-server # Start API server  
make run-worker # Start background worker

**Build Process**

Bash  
make build # Build server and worker  
make test # Run unit tests  
make lint # Code quality checks  
make fmt # Format code  
make tidy # Clean go.mod

**Testing Strategy**

- **Unit Tests**: Service layer testing with mocked dependencies
- **Integration Tests**: API endpoint testing with test database
- **Database Tests**: Repository layer testing with test fixtures
- **Worker Tests**: Background job processing validation

**Deployment**

- **Development**: Docker Compose with hot reload
- **Staging**: Kubernetes deployment with configuration management
- **Production**: Blue-green deployment with health checks

**Recommendations**

**For Module Generation**

- **Follow Domain-Driven Design**: Start with domain entities and business rules
- **Implement Repository Pattern**: Always abstract data access behind interfaces
- **Use Service Layer**: Keep business logic separate from HTTP handling
- **Add Background Workers**: For any long-running or external API calls
- **Include Comprehensive Tests**: Unit tests for services, integration tests for APIs

**For Task Generation**

- **Break Down Features**: Split large features into small, atomic tasks
- **Include Database Changes**: Always consider migration requirements
- **Add Monitoring**: Include logging and metrics for new functionality
- **Plan Error Handling**: Consider failure modes and recovery strategies
- **Document APIs**: Keep Swagger documentation updated

**Best Practices**

- **Security First**: Never commit credentials, use environment variables
- **Performance Mindset**: Consider database queries and external API calls
- **Observability**: Add structured logging and metrics everywhere
- **Testing**: Aim for 65-70% code coverage with meaningful tests
- **Documentation**: Maintain clear API documentation and code comments

**Generated**: December 3, 2025  
**Analyzer Version**: SKILL.md v1.0  
**Project**: Cosmo Backend - AI Email Automation Platform