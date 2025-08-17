# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a modern Telegram bot for moderating educational chats in the Czech Republic. The bot provides comprehensive moderation features including muting, banning, blacklisting users, welcome messages, and message history tracking. Built with Python using aiogram for Telegram integration and follows a clean Domain-Driven Design (DDD) architecture with modern best practices.

The project now includes a **React TypeScript web application** that provides an admin panel accessible via Telegram's WebApp API, offering a modern web interface for bot management and analytics.

## Technology Stack

### Backend
- **Python 3.12+** - Modern Python with full type hints
- **aiogram 3.x** - Async Telegram Bot API framework
- **SQLAlchemy 2.x** - Modern async ORM with declarative models
- **PostgreSQL 17.6** - Latest production database
- **Pydantic 2.x** - Data validation and settings management
- **structlog** - Structured logging
- **pytest** - Testing framework with async support
- **ruff** - Fast Python linter and formatter
- **uv 0.8.11** - Modern Python package manager

### Frontend
- **React 19+** - Latest React with concurrent features
- **TypeScript 5.9** - Type-safe JavaScript development
- **Vite 7+** - Ultra-fast build tool and development server
- **@telegram-apps/sdk-react** - Official Telegram WebApp integration
- **@tanstack/react-query** - Powerful data fetching and caching
- **Node.js 24** - Latest LTS runtime environment

### Infrastructure
- **Docker** - Containerized development and deployment
- **PostgreSQL 17.6** - Latest stable database version
- **Adminer 5.3.0** - Modern database administration interface
- **nginx** - Production web server and reverse proxy

## Development Setup

Dependencies are managed with `uv`. Set up the development environment:

```bash
# Create virtual environment and install dependencies
uv venv .venv
uv sync --dev
source .venv/bin/activate  # Linux/Mac
# or .venv\Scripts\activate  # Windows

# Setup environment
cp .env.example .env
# Edit .env with your configuration
```

## Running the Application

### Development Mode
Run with Docker Compose (includes PostgreSQL, React webapp, hot reload, and Adminer):
```bash
docker-compose -f docker-compose.dev.yaml up --build
```

This will start:
- **Bot service** - Telegram bot with hot reload
- **WebApp service** - React development server on port 3000
- **PostgreSQL** - Database server
- **Adminer** - Database administration UI on port 8080

### Production Mode
```bash
docker-compose up --build
```

### Local Development (without Docker)
```bash
# Make sure PostgreSQL is running and configured
uv run -m app.presentation.telegram
```

## Code Quality & Testing

### Run All Quality Checks
```bash
# Linting and formatting
ruff check app tests
ruff format app tests

# Type checking
mypy app tests

# Run tests
uv run -m pytest

# Run tests with coverage
uv run -m pytest --cov=app --cov-report=html
```

### Pre-commit Setup
```bash
# Install pre-commit hooks
uv run pre-commit install

# Run hooks manually
uv run pre-commit run --all-files
```

## Database Management

Uses Alembic for migrations with PostgreSQL in production and SQLite for testing.

```bash
# Create migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Architecture (Domain-Driven Design)

The project follows clean DDD architecture with clear separation of concerns:

### Core Layers

- **`app/core/`** - Application core (config, logging, DI container)
- **`app/domain/`** - Pure domain logic (entities, value objects, repository interfaces, exceptions)
- **`app/application/`** - Application services and use cases
- **`app/infrastructure/`** - External concerns (database, external APIs)
- **`app/presentation/`** - User interface layer (Telegram handlers, middlewares)

### Domain Layer (`app/domain/`)

- **`entities.py`** - Rich domain entities with business logic
- **`value_objects.py`** - Immutable value objects (UserId, ChatId, etc.)
- **`repositories.py`** - Repository interfaces (ports)
- **`exceptions.py`** - Domain-specific exceptions
- **`models.py`** - SQLAlchemy ORM models (infrastructure concern)

### Key Design Patterns

- **Repository Pattern** - Abstracts data access with interfaces
- **Dependency Injection** - Managed through `app/core/container.py`
- **Value Objects** - Ensure data integrity and encapsulation
- **Domain Services** - Complex business logic that doesn't belong to entities
- **Structured Logging** - Contextual logging with structured data

### Configuration Management

Modern Pydantic-based configuration with environment variable support:

```python
from app.core.config import settings

# Access nested configuration
bot_token = settings.telegram.token
db_url = settings.database.url
log_level = settings.logging.level
```

### Dependency Injection

Services are managed through a lightweight DI container:

```python
from app.core.container import container

# Get repositories
user_repo = container.get(IUserRepository)
user_service = UserService(user_repo)
```

## Bot Commands

### Moderation Commands (Admins only)
- `/mute [minutes]` - Mute user (default 5 minutes)
- `/unmute` - Unmute user
- `/ban` - Ban user from chat and add to blacklist
- `/unban` - Remove from blacklist
- `black` - Add user to global blacklist (all chats)
- `/blacklist` - Show blacklisted users with unban buttons

### Configuration Commands
- `welcome [text]` - Configure welcome message
- `welcome -t [seconds]` - Set welcome message auto-delete time
- `/admin` - Add admin (reply to user)
- `/unadmin` - Remove admin (reply to user)

### Public Commands
- `/chats` - Show educational chat links
- `/start` - Bot introduction

### WebApp Commands (Admins only)
- `/webapp` - Open React-based admin panel via Telegram WebApp
- `/help_webapp` - Show help for webapp functionality

## Testing Strategy

### Framework
- **pytest** with **pytest-asyncio** for async test support
- **SQLite in-memory** database for fast, isolated tests
- **Fixtures** provide clean test data and dependencies
- **Coverage reporting** with minimum 60% requirement

### Test Structure
```bash
tests/
├── conftest.py          # Shared fixtures and configuration
├── test_user_repository.py
├── test_chat_repository.py
├── test_admin_repository.py
└── unit/                # Unit tests
└── integration/         # Integration tests
```

### Running Tests
```bash
# All tests
uv run -m pytest

# Specific test types
uv run -m pytest -m unit
uv run -m pytest -m integration
uv run -m pytest -m "not slow"

# With coverage
uv run -m pytest --cov=app --cov-fail-under=60
```

## Logging

Structured logging with contextual information:

```python
from app.core.logging import BotLogger

logger = BotLogger("service_name")

# Log user actions
logger.log_user_action(user_id=123, action="user_blocked", chat_id=456)

# Log moderation actions
logger.log_moderation_action(
    admin_id=789,
    target_user_id=123,
    action="ban",
    chat_id=456,
    reason="spam"
)
```

## Environment Variables

See `.env.example` for all available configuration options. Key variables:

```bash
# Bot
BOT_TOKEN=your_bot_token_here
BOT_WEBHOOK_URL=
BOT_WEBHOOK_SECRET=
BOT_USE_WEBHOOK=false
ADMIN_SUPER_ADMINS=123456789,987654321
ADMIN_REPORT_CHAT_ID=

# Database
DB_USER=postgres
DB_PASSWORD=your_password_here
DB_NAME=moderator_bot

# Application
DEBUG=false
ENVIRONMENT=development
TIMEZONE=UTC
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(name)s - %(levelname)s - %(message)s
LOG_FILE_PATH=logs/bot.log
LOG_MAX_BYTES=10485760
LOG_BACKUP_COUNT=5

# Web App Configuration
WEBAPP_URL=http://localhost:3000
WEBAPP_API_SECRET=your_webapp_secret_key_here

# Docker Configuration (for development)
WEBAPP_PORT=3000
ADMINER_PORT=8080
```

## Web Application (React Admin Panel)

### Overview
The project includes a modern React TypeScript web application that provides a comprehensive admin interface accessible through Telegram's WebApp API. This allows administrators to manage the bot through a native web interface within Telegram, offering a more intuitive and feature-rich experience than traditional chat commands.

### Purpose and Use Cases

The frontend is designed to provide administrators with:

#### **Chat and Channel Management**
- **Real-time overview** of all managed chats and channels
- **Detailed chat statistics** including member count, activity levels, message volume
- **Chat configuration management** - welcome messages, auto-moderation settings, captcha configuration
- **Bulk operations** across multiple chats simultaneously
- **Chat health monitoring** with alerts for unusual activity patterns

#### **Advanced User Management**
- **Comprehensive user profiles** with moderation history, join dates, activity patterns
- **Global blacklist management** with search, filtering, and bulk operations
- **User behavior analytics** to identify potential troublemakers before they act
- **Cross-chat user tracking** to see user behavior across different communities
- **Appeal system management** for banned users

#### **Analytics and Reporting**
- **Interactive dashboards** with charts and graphs showing moderation trends
- **Custom date range reports** for specific time periods
- **Moderator performance metrics** to track admin activity and effectiveness
- **Automated report generation** for community oversight
- **Export functionality** for data analysis in external tools

#### **Bot Configuration and Settings**
- **Visual configuration interface** for bot settings without editing config files
- **Real-time bot status monitoring** and health checks
- **Log viewing and filtering** for troubleshooting and auditing
- **Feature toggles** for enabling/disabling specific bot functionality
- **Integration management** with external services and APIs

#### **Emergency Response Tools**
- **Mass action capabilities** for crisis situations (mass bans, lockdowns)
- **Real-time alerts and notifications** for urgent moderation needs
- **Quick response templates** for common moderation scenarios
- **Incident tracking and management** for serious violations

### Technology Stack
- **React 19+** with TypeScript - Latest React features with full type safety
- **Vite 7+** - Ultra-fast build tool and development server
- **@telegram-apps/sdk-react 3.3+** - Official Telegram WebApp integration
- **@tanstack/react-query 5.85+** - Powerful data fetching and caching
- **Axios** - HTTP client for API communication
- **Node.js 24** - Latest LTS runtime environment
- **ESLint & TypeScript 5.9** - Code quality and type checking

### Current Features (v1.0)
- **Telegram Integration** - Native Telegram WebApp experience with theme support
- **User Authentication** - Secure admin verification via Telegram initData
- **Theme Adaptation** - Automatically adapts to user's Telegram theme (dark/light)
- **User Information Display** - Shows detailed user info from Telegram
- **Debug Interface** - Development tools for debugging Telegram integration
- **Responsive Design** - Optimized for both mobile and desktop usage
- **Real-time Updates** - Live data synchronization with the bot backend

### Planned Features (Roadmap)
- **Dashboard Analytics** - Charts and graphs for moderation statistics
- **Chat Management Interface** - Visual chat configuration and monitoring
- **Advanced User Search** - Find users across all managed chats
- **Bulk Actions** - Perform operations on multiple users/chats
- **Report Generation** - Automated and custom reporting tools
- **Notification Center** - Real-time alerts for moderation events
- **Mobile Optimization** - Enhanced mobile experience within Telegram
- **Multi-language Support** - Localization for Czech and English interfaces

### Development
```bash
# Navigate to webapp directory
cd webapp

# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint
```

### Access
Administrators can access the webapp by:
1. Sending `/webapp` command to the bot
2. Clicking the "🎛️ Открыть админ панель" button
3. The webapp opens within Telegram's native WebApp interface

## Docker Development

The development setup includes:
- **Bot service** - Python bot with hot reload
- **WebApp service** - React development server (http://localhost:3000)
- **PostgreSQL** - Database
- **Adminer** - Database administration UI (http://localhost:8080)
- **Hot reload** - Automatic restart on code changes for both bot and webapp
- **Volume mounts** - Live code editing

## Migration Guide

When migrating from older versions:

1. **Update dependencies**: `uv sync --dev`
2. **Update environment**: Copy new variables from `.env.example`
3. **Run migrations**: `alembic upgrade head`
4. **Update imports**: Domain entities are now in `app/domain/entities.py`
5. **Update tests**: Use new fixtures from `conftest.py`

## WebApp Security

### Authentication
- **Super Admin Only** - WebApp access restricted to configured super admins
- **Telegram Validation** - Uses Telegram's built-in user validation
- **API Secret** - Configurable secret for webapp-bot communication

### Development vs Production
- **Development** - Runs on localhost with hot reload
- **Production** - Served through nginx with proper security headers
- **HTTPS Required** - Telegram WebApps require HTTPS in production

## Performance Considerations

### Backend Optimization
- **Connection pooling** - Configured for production use with PostgreSQL
- **Async everywhere** - Fully async/await pattern throughout the application
- **Concurrent operations** - Batch operations for multiple chats and users
- **Structured logging** - Minimal performance impact with structured data
- **Type hints** - Full mypy compliance for better IDE support and runtime performance
- **Database indexing** - Optimized queries for large-scale chat management

### Frontend Optimization
- **WebApp Optimization** - React app built with Vite for ultra-fast loading
- **Code splitting** - Lazy loading for different admin panel sections
- **Theme Integration** - Native Telegram theme support for seamless UX
- **Caching strategy** - Smart data caching with React Query for offline capability
- **Bundle optimization** - Tree shaking and minification for production builds
- **Progressive loading** - Skeleton screens and loading states for better perceived performance

### Development Experience
- **Hot reload** - Instant updates during development for both backend and frontend
- **Modern tooling** - Latest versions of all dependencies for best performance
- **Type safety** - Full TypeScript coverage prevents runtime errors
- **Pre-commit hooks** - Automated code quality checks and formatting
- **Docker optimization** - Multi-stage builds and layer caching for faster deployments
