# SpineAPI Examples

This directory contains example OpenAPI specifications to demonstrate SpineAPI's capabilities for generating production-ready backend applications.

## Available Examples

### 1. Petstore API (`petstore.yaml`)
A classic example showcasing basic CRUD operations for a pet store application.

**Features:**
- Pet management (create, read, update, delete)
- Store operations (inventory, orders)
- User management and authentication
- File uploads for pet images
- OAuth2 and API key security schemes

**Generated Components:**
- FastAPI endpoints with automatic OpenAPI documentation
- SQLAlchemy models for pets, orders, and users
- Pydantic schemas for request/response validation
- Authentication middleware
- File upload handlers

**Usage:**
```bash
spineapi generate petstore.yaml --output ./petstore-api
```

### 2. E-Commerce Platform API (`ecommerce.yaml`)
A comprehensive e-commerce API demonstrating complex business logic and relationships.

**Features:**
- User registration, authentication, and profiles
- Product catalog with categories and variants
- Shopping cart operations
- Order processing and fulfillment
- Payment processing integration
- Product reviews and ratings
- Address management
- Inventory tracking

**Generated Components:**
- Multi-table database schema with relationships
- JWT authentication system
- Payment gateway integration templates
- Email notification templates
- Admin dashboard endpoints
- Advanced filtering and pagination

**Usage:**
```bash
spineapi generate ecommerce.yaml --output ./ecommerce-api --llm-enhance
```

### 3. Social Media Platform API (`social_media.yaml`)
A feature-rich social media API showcasing real-time features and complex interactions.

**Features:**
- User profiles with avatars and bio
- Post creation with media uploads
- Social interactions (likes, comments, follows)
- Real-time messaging system
- Notification system
- Content search and discovery
- Media file management
- Content moderation and reporting

**Generated Components:**
- WebSocket endpoints for real-time features
- Media processing pipeline
- Notification queue system
- Search indexing with full-text search
- Content moderation workflows
- Analytics and insights endpoints

**Usage:**
```bash
spineapi generate social_media.yaml --output ./social-media-api --llm-enhance --features websockets,search,media-processing
```

## Running the Examples

### Quick Start
Generate any example with default settings:
```bash
# Basic generation
spineapi generate examples/petstore.yaml --output ./my-petstore-api

# With LLM enhancement
spineapi generate examples/ecommerce.yaml --output ./my-ecommerce-api --llm-enhance

# With specific features
spineapi generate examples/social_media.yaml --output ./my-social-api --features websockets,redis,celery
```

### Advanced Configuration
Customize the generation with additional options:

```bash
# Generate with specific database
spineapi generate examples/ecommerce.yaml \
  --output ./my-ecommerce-api \
  --database postgresql \
  --llm-enhance \
  --features redis,celery,monitoring

# Generate with custom templates
spineapi generate examples/social_media.yaml \
  --output ./my-social-api \
  --template-dir ./custom-templates \
  --llm-enhance
```

### Testing Generated APIs

Each generated API includes:
- Comprehensive test suites
- Docker configurations
- Database setup scripts
- API documentation

To test a generated API:
```bash
cd ./generated-api
docker-compose up -d
pytest tests/
```

## Customizing Examples

You can modify these examples to fit your specific needs:

1. **Add new endpoints**: Extend the OpenAPI spec with additional paths
2. **Modify schemas**: Customize the data models and validation rules
3. **Change security**: Update authentication and authorization schemes
4. **Add custom features**: Include additional OpenAPI extensions

## Best Practices Demonstrated

These examples showcase SpineAPI best practices:

- **Comprehensive Error Handling**: Detailed error responses with proper HTTP status codes
- **Security Implementation**: JWT authentication, API keys, OAuth2 flows
- **Data Validation**: Strong input validation using Pydantic schemas
- **Documentation**: Rich OpenAPI descriptions and examples
- **Scalability**: Proper pagination, filtering, and caching strategies
- **Testing**: Complete test coverage with realistic test data
- **Deployment**: Production-ready Docker and Kubernetes configurations

## Learn More

For detailed documentation and tutorials, visit:
- [SpineAPI Documentation](https://spineapi.dev/docs)
- [OpenAPI Specification Guide](https://swagger.io/specification/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

If you have questions about these examples or need help customizing them:
- [GitHub Issues](https://github.com/spineapi/spineapi/issues)
- [Community Discord](https://discord.gg/spineapi)
- [Email Support](mailto:support@spineapi.dev)
