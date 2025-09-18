# Getting Started with SpineAPI

Welcome to SpineAPI! This guide will help you create your first AI-powered backend application from an OpenAPI specification.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.8+** installed on your system
- **pip** package manager
- **Docker** (optional, for containerized deployment)
- **OpenAPI specification** (YAML or JSON format)

## Installation

### Basic Installation

```bash
pip install spineapi
```

### Full Installation with AI Features

```bash
pip install spineapi[llm]
```

### Development Installation

```bash
pip install spineapi[dev,llm]
```

## Verify Installation

```bash
spineapi --version
spineapi --help
```

## Your First API

### Step 1: Create an OpenAPI Specification

Create a simple API specification file named `my-api.yaml`:

```yaml
openapi: 3.0.3
info:
  title: My First API
  description: A simple API to demonstrate SpineAPI
  version: 1.0.0
servers:
  - url: http://localhost:8000
    description: Development server
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          description: List of users
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
    post:
      summary: Create a user
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
  /users/{user_id}:
    get:
      summary: Get user by ID
      parameters:
        - name: user_id
          in: path
          required: true
          schema:
            type: integer
      responses:
        '200':
          description: User details
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        '404':
          description: User not found
components:
  schemas:
    User:
      type: object
      properties:
        id:
          type: integer
          example: 1
        name:
          type: string
          example: "John Doe"
        email:
          type: string
          format: email
          example: "john@example.com"
        created_at:
          type: string
          format: date-time
          example: "2023-01-01T00:00:00Z"
    UserCreate:
      type: object
      required: [name, email]
      properties:
        name:
          type: string
          example: "John Doe"
        email:
          type: string
          format: email
          example: "john@example.com"
```

### Step 2: Validate Your Specification

```bash
spineapi validate my-api.yaml
```

This will check your OpenAPI specification for errors and provide helpful feedback.

### Step 3: Generate Your API

```bash
spineapi generate my-api.yaml --output ./my-first-api
```

### Step 4: Explore the Generated Code

```bash
cd my-first-api
ls -la
```

You'll see a complete FastAPI application structure:

```
my-first-api/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── models/
│   │   ├── __init__.py
│   │   └── user.py             # SQLAlchemy models
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── user.py             # Pydantic schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   └── users.py            # API route handlers
│   ├── database.py             # Database configuration
│   └── auth/
├── tests/                      # Comprehensive test suite
├── docker/                     # Docker configuration
├── requirements.txt
├── pyproject.toml
└── README.md
```

### Step 5: Run Your API

#### Option A: Run Locally with Python

```bash
# Install dependencies
pip install -r requirements.txt

# Initialize the database
python -c "from app.database import engine; from app.models import Base; Base.metadata.create_all(bind=engine)"

# Run the development server
uvicorn app.main:app --reload
```

#### Option B: Run with Docker

```bash
# Build and run with Docker Compose
docker-compose up -d
```

### Step 6: Test Your API

Open your browser and navigate to:
- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

You can also test the endpoints directly:

```bash
# List users (initially empty)
curl http://localhost:8000/users

# Create a user
curl -X POST http://localhost:8000/users \
  -H "Content-Type: application/json" \
  -d '{"name": "John Doe", "email": "john@example.com"}'

# Get user by ID
curl http://localhost:8000/users/1
```

## Next Steps

### Add AI Enhancement

Generate your API with AI-powered improvements:

```bash
spineapi generate my-api.yaml --output ./my-enhanced-api --llm-enhance
```

This will:
- Add intelligent error handling
- Generate comprehensive documentation
- Optimize code patterns
- Add security best practices

### Customize Generation

Use additional options to customize your API:

```bash
spineapi generate my-api.yaml \
  --output ./my-custom-api \
  --database postgresql \
  --features redis,celery,monitoring \
  --llm-enhance
```

### Use Example Templates

Try one of the provided examples:

```bash
# E-commerce platform
spineapi generate examples/ecommerce.yaml --output ./ecommerce-api

# Social media platform
spineapi generate examples/social_media.yaml --output ./social-api --llm-enhance
```

### Deploy to Production

```bash
# Deploy with Docker
docker-compose -f docker-compose.prod.yml up -d

# Deploy to Kubernetes
kubectl apply -f k8s/
```

## Configuration

### Environment Variables

Create a `.env` file in your project root:

```env
# Database
DATABASE_URL=sqlite:///./app.db
# DATABASE_URL=postgresql://user:password@localhost/dbname

# Authentication
SECRET_KEY=your-super-secret-key
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# LLM Integration (optional)
OPENAI_API_KEY=your-openai-api-key
HUGGINGFACE_API_TOKEN=your-hf-token

# Redis (optional)
REDIS_URL=redis://localhost:6379

# Monitoring (optional)
PROMETHEUS_ENABLED=true
GRAFANA_ENABLED=true
```

### Configuration File

Create `spineapi.toml` for advanced configuration:

```toml
[database]
type = "postgresql"
url = "postgresql://user:password@localhost/dbname"
pool_size = 10
max_overflow = 20

[features]
redis = true
celery = true
monitoring = true
websockets = false

[llm]
provider = "openai"
model = "gpt-3.5-turbo"
temperature = 0.1
max_tokens = 2000

[templates]
custom_dir = "./custom-templates"
override_defaults = false

[generation]
include_tests = true
include_docs = true
include_docker = true
include_k8s = true
```

## Common Issues

### Import Errors

If you see import errors, ensure all dependencies are installed:

```bash
pip install -r requirements.txt
```

### Database Connection Issues

For PostgreSQL or MySQL, ensure the database server is running and accessible:

```bash
# PostgreSQL
docker run --name postgres -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres

# MySQL
docker run --name mysql -e MYSQL_ROOT_PASSWORD=password -p 3306:3306 -d mysql
```

### OpenAPI Validation Errors

Use the validate command to check your specification:

```bash
spineapi validate my-api.yaml --detailed
```

Common issues:
- Missing required fields in schemas
- Invalid references (`$ref`)
- Incorrect HTTP status codes
- Missing response definitions

## Best Practices

### OpenAPI Specification

1. **Use descriptive names** for operations and schemas
2. **Include examples** in your schemas
3. **Document all responses**, including error cases
4. **Use appropriate HTTP status codes**
5. **Define security schemes** for protected endpoints

### Generated Code

1. **Review generated code** before deploying
2. **Customize business logic** in service files
3. **Add validation rules** beyond basic type checking
4. **Implement proper error handling**
5. **Add logging and monitoring**

### Development Workflow

1. **Version control** your OpenAPI specifications
2. **Use CI/CD pipelines** for automated testing
3. **Generate APIs** in clean environments
4. **Test thoroughly** before deployment
5. **Monitor** production APIs

## Learning Resources

### Tutorials
- [Building a REST API](docs/tutorials/rest-api.md)
- [Adding Authentication](docs/tutorials/authentication.md)
- [Database Integration](docs/tutorials/database.md)
- [Deployment Strategies](docs/tutorials/deployment.md)

### Examples
- [Petstore API](examples/petstore.yaml) - Basic CRUD operations
- [E-commerce API](examples/ecommerce.yaml) - Complex business logic
- [Social Media API](examples/social_media.yaml) - Real-time features

### External Resources
- [OpenAPI Specification](https://swagger.io/specification/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/14/tutorial/)
- [Pydantic Documentation](https://pydantic-docs.helpmanual.io/)

## Getting Help

### Community Support
- **GitHub Issues**: [Report bugs and request features](https://github.com/spineapi/spineapi/issues)
- **Discord**: [Join our community](https://discord.gg/spineapi)
- **Stack Overflow**: Tag questions with `spineapi`

### Documentation
- [CLI Reference](docs/cli-reference.md)
- [Configuration Guide](docs/configuration.md)
- [Template Development](docs/templates.md)
- [LLM Integration](docs/llm-integration.md)

Congratulations! You've successfully created your first API with SpineAPI. Continue exploring the documentation to learn about advanced features and deployment strategies.
