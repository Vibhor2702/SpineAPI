# 🦴 SpineAPI

**AI-Powered Backend Scaffolding Tool**

Transform your OpenAPI/Swagger specifications into production-ready backend applications automatically.

## 🎯 What SpineAPI Does

SpineAPI takes your OpenAPI specification (YAML/JSON file that describes your API) and generates a **complete, production-ready backend** including:

- **FastAPI application** with all your routes and endpoints
- **Database models** (SQLAlchemy) with relationships
- **Input/output validation** (Pydantic schemas)
- **Unit tests** (pytest)
- **Docker configuration** for containerization
- **API documentation** (automatic OpenAPI docs)
- **Database migrations** (Alembic)

## 🤔 Why SpineAPI Exists

**The Problem**: Writing backend APIs involves tons of repetitive boilerplate code. You spend days/weeks writing the same patterns over and over:
- Route handlers
- Database models  
- Validation schemas
- Tests
- Docker files
- Documentation

**The Solution**: SpineAPI eliminates this repetitive work. Design your API once in OpenAPI format, then generate everything else automatically.

**Result**: Go from API specification to running backend in minutes, not weeks.

## 🚀 How It Works

### 1. Installation
```bash
pip install spineapi
```

### 2. Create or Use an OpenAPI Spec
```yaml
# api-spec.yaml
openapi: 3.0.0
info:
  title: My API
  version: 1.0.0
paths:
  /users:
    get:
      summary: Get all users
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
        name:
          type: string
        email:
          type: string
```

### 3. Generate Your Backend
```bash
# Generate complete backend
spineapi generate api-spec.yaml --output my-backend

# Run the generated API
cd my-backend
pip install -r requirements.txt
uvicorn main:app --reload
```

### 4. Your API is Ready!
- Visit `http://localhost:8000/docs` for interactive API documentation
- All endpoints are working with proper validation
- Database models are created and ready
- Tests are included and passing

## 📁 What Gets Generated

```
my-backend/
├── main.py                     # FastAPI application entry point
├── models/                     # Database models (SQLAlchemy)
│   └── user.py
├── schemas/                    # Request/response models (Pydantic)
│   └── user.py
├── routes/                     # API endpoints
│   └── users.py
├── tests/                      # Unit tests
│   └── test_users.py
├── database.py                 # Database configuration
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker container config
└── docker-compose.yml         # Local development setup
```

## �️ CLI Commands

```bash
# Generate backend from OpenAPI spec
spineapi generate api-spec.yaml

# Initialize a new project structure  
spineapi init my-project

# Validate your OpenAPI specification
spineapi validate api-spec.yaml

# Show version
spineapi version
```

## 📖 Examples

Check out the `examples/` folder for complete OpenAPI specifications:

- **`petstore.yaml`** - Classic pet store API with CRUD operations
- **`ecommerce.yaml`** - E-commerce platform with products, orders, cart
- **`social_media.yaml`** - Social media API with posts, comments, users

Try them out:
```bash
spineapi generate examples/petstore.yaml --output petstore-api
cd petstore-api
docker-compose up
```

## 🔧 Features

### Core Generation
- ✅ **FastAPI Routes** - All endpoints with proper HTTP methods
- ✅ **SQLAlchemy Models** - Database schemas with relationships  
- ✅ **Pydantic Schemas** - Request/response validation
- ✅ **Database Setup** - SQLite by default, PostgreSQL ready
- ✅ **Error Handling** - Proper HTTP status codes and error responses

### Development Ready
- ✅ **Unit Tests** - pytest tests for all endpoints
- ✅ **Docker Support** - Containerized application
- ✅ **API Documentation** - Auto-generated OpenAPI docs
- ✅ **Development Server** - Hot reload with uvicorn
- ✅ **Database Migrations** - Alembic integration

### Production Features  
- ✅ **Input Validation** - Automatic request validation
- ✅ **Response Serialization** - Type-safe JSON responses
- ✅ **Health Checks** - Built-in health monitoring
- ✅ **CORS Support** - Cross-origin resource sharing
- ✅ **Environment Config** - Settings management

That's it! SpineAPI turns your API design into working code automatically. 🎉
