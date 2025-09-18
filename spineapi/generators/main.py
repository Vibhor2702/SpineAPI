"""
Main Code Generator

Orchestrates the generation of FastAPI applications from OpenAPI specs.
"""
import logging
import os
import shutil
from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, Template
try:
    from loguru import logger
    HAS_LOGURU = True
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    HAS_LOGURU = False

from spineapi.parsers.openapi import ParsedSpec
from spineapi.llm.enhancer import LLMEnhancer


class CodeGenerator:
    """Main code generator class."""
    
    def __init__(
        self,
        framework: str = "fastapi",
        database: str = "sqlite",
        enable_llm: bool = False,
        llm_enhancer: Optional[LLMEnhancer] = None,
    ):
        self.framework = framework
        self.database = database
        self.enable_llm = enable_llm
        self.llm_enhancer = llm_enhancer
        
        # Initialize Jinja2 environment
        template_dir = Path(__file__).parent.parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            trim_blocks=True,
            lstrip_blocks=True,
        )
    
    def generate(
        self,
        spec_data: ParsedSpec,
        output_dir: Path,
        project_name: str,
        include_tests: bool = True,
        include_docker: bool = True,
        include_monitoring: bool = False,
        include_k8s: bool = False,
    ) -> Dict[str, Any]:
        """
        Generate complete backend application.
        
        Args:
            spec_data: Parsed OpenAPI specification
            output_dir: Directory to generate code in
            project_name: Name of the project
            include_tests: Whether to generate tests
            include_docker: Whether to generate Docker configs
            include_monitoring: Whether to include monitoring setup
            include_k8s: Whether to generate Kubernetes configs
            
        Returns:
            Dictionary with generation results
        """
        logger.info(f"Generating {self.framework} application: {project_name}")
        
        # Create output directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Template context
        context = {
            "title": spec_data.title,
            "description": spec_data.description,
            "version": spec_data.version,
            "project_name": project_name,
            "database": self.database,
            "endpoints": spec_data.endpoints,
            "schemas": spec_data.schemas,
            "servers": spec_data.servers,
            "security_schemes": spec_data.security_schemes,
            "tags": spec_data.tags,
        }
        
        generated_files = []
        
        # Generate core application files
        generated_files.extend(self._generate_core_files(output_dir, context))
        
        # Generate tests
        if include_tests:
            generated_files.extend(self._generate_test_files(output_dir, context))
        
        # Generate Docker configurations
        if include_docker:
            generated_files.extend(self._generate_docker_files(output_dir, context))
        
        # Generate monitoring setup
        if include_monitoring:
            generated_files.extend(self._generate_monitoring_files(output_dir, context))
        
        # Generate Kubernetes configurations
        if include_k8s:
            generated_files.extend(self._generate_k8s_files(output_dir, context))
        
        # Generate additional files
        generated_files.extend(self._generate_additional_files(output_dir, context))
        
        # Apply LLM enhancement if enabled
        if self.enable_llm and self.llm_enhancer:
            logger.info("Applying LLM enhancements...")
            self._apply_llm_enhancements(output_dir, generated_files)
        
        logger.info(f"Generated {len(generated_files)} files")
        
        return {
            "project_name": project_name,
            "output_dir": str(output_dir),
            "generated_files": generated_files,
            "framework": self.framework,
            "database": self.database,
            "total_endpoints": len(spec_data.endpoints),
            "total_schemas": len(spec_data.schemas),
        }
    
    def _generate_core_files(self, output_dir: Path, context: Dict[str, Any]) -> List[str]:
        """Generate core application files."""
        generated_files = []
        
        # Main FastAPI application
        content = self._render_template("fastapi_main.py.j2", context)
        self._write_file(output_dir / "main.py", content)
        generated_files.append("main.py")
        
        # Database configuration
        content = self._render_template("database.py.j2", context)
        self._write_file(output_dir / "database.py", content)
        generated_files.append("database.py")
        
        # SQLAlchemy models
        content = self._render_template("models.py.j2", context)
        self._write_file(output_dir / "models.py", content)
        generated_files.append("models.py")
        
        # Pydantic schemas
        content = self._render_template("schemas.py.j2", context)
        self._write_file(output_dir / "schemas.py", content)
        generated_files.append("schemas.py")
        
        # CRUD operations for each schema
        for schema in context["schemas"]:
            schema_context = {**context, "schema": schema}
            content = self._render_template("crud.py.j2", schema_context)
            self._write_file(output_dir / f"crud_{schema.name.lower()}.py", content)
            generated_files.append(f"crud_{schema.name.lower()}.py")
        
        # Requirements file
        content = self._render_template("requirements.txt.j2", context)
        self._write_file(output_dir / "requirements.txt", content)
        generated_files.append("requirements.txt")
        
        return generated_files
    
    def _generate_test_files(self, output_dir: Path, context: Dict[str, Any]) -> List[str]:
        """Generate test files."""
        generated_files = []
        
        # Create tests directory
        tests_dir = output_dir / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Main test file
        content = self._render_template("test_main.py.j2", context)
        self._write_file(tests_dir / "test_main.py", content)
        generated_files.append("tests/test_main.py")
        
        # Test configuration
        self._write_file(tests_dir / "__init__.py", "")
        generated_files.append("tests/__init__.py")
        
        # pytest configuration
        pytest_config = """[tool:pytest]
testpaths = tests
python_files = test_*.py
python_functions = test_*
python_classes = Test*
addopts = -v --tb=short --strict-markers
markers =
    slow: marks tests as slow (deselect with '-m \"not slow\"')
    integration: marks tests as integration tests
"""
        self._write_file(output_dir / "pytest.ini", pytest_config)
        generated_files.append("pytest.ini")
        
        return generated_files
    
    def _generate_docker_files(self, output_dir: Path, context: Dict[str, Any]) -> List[str]:
        """Generate Docker configuration files."""
        generated_files = []
        
        # Dockerfile
        content = self._render_template("Dockerfile.j2", context)
        self._write_file(output_dir / "Dockerfile", content)
        generated_files.append("Dockerfile")
        
        # docker-compose.yml
        content = self._render_template("docker-compose.yml.j2", context)
        self._write_file(output_dir / "docker-compose.yml", content)
        generated_files.append("docker-compose.yml")
        
        # .dockerignore
        dockerignore_content = """__pycache__
*.pyc
*.pyo
*.pyd
.Python
env
pip-log.txt
pip-delete-this-directory.txt
.tox
.coverage
.coverage.*
.cache
nosetests.xml
coverage.xml
*.cover
*.log
.git
.mypy_cache
.pytest_cache
.hypothesis

.DS_Store
.vscode
.idea
*.swp
*.swo

tests/
docs/
*.md
!README.md
"""
        self._write_file(output_dir / ".dockerignore", dockerignore_content)
        generated_files.append(".dockerignore")
        
        return generated_files
    
    def _generate_monitoring_files(self, output_dir: Path, context: Dict[str, Any]) -> List[str]:
        """Generate monitoring configuration files."""
        generated_files = []
        
        # Create monitoring directory
        monitoring_dir = output_dir / "monitoring"
        monitoring_dir.mkdir(exist_ok=True)
        
        # Prometheus configuration
        prometheus_config = f"""global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: '{context["project_name"]}-api'
    static_configs:
      - targets: ['{context["project_name"]}-api:8000']
    metrics_path: /metrics
    scrape_interval: 5s

  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']
"""
        self._write_file(monitoring_dir / "prometheus.yml", prometheus_config)
        generated_files.append("monitoring/prometheus.yml")
        
        # Grafana directory structure
        grafana_dir = monitoring_dir / "grafana"
        grafana_dir.mkdir(exist_ok=True)
        
        dashboards_dir = grafana_dir / "dashboards"
        dashboards_dir.mkdir(exist_ok=True)
        
        datasources_dir = grafana_dir / "datasources"
        datasources_dir.mkdir(exist_ok=True)
        
        # Grafana datasource
        datasource_config = """apiVersion: 1

datasources:
  - name: Prometheus
    type: prometheus
    access: proxy
    url: http://prometheus:9090
    isDefault: true
    editable: true
"""
        self._write_file(datasources_dir / "prometheus.yml", datasource_config)
        generated_files.append("monitoring/grafana/datasources/prometheus.yml")
        
        # Grafana dashboard provisioning
        dashboard_config = """apiVersion: 1

providers:
  - name: 'default'
    orgId: 1
    folder: ''
    type: file
    disableDeletion: false
    editable: true
    options:
      path: /etc/grafana/provisioning/dashboards
"""
        self._write_file(dashboards_dir / "dashboard.yml", dashboard_config)
        generated_files.append("monitoring/grafana/dashboards/dashboard.yml")
        
        return generated_files
    
    def _generate_k8s_files(self, output_dir: Path, context: Dict[str, Any]) -> List[str]:
        """Generate Kubernetes configuration files."""
        generated_files = []
        
        # Create kubernetes directory
        k8s_dir = output_dir / "kubernetes"
        k8s_dir.mkdir(exist_ok=True)
        
        project_name = context["project_name"]
        
        # Deployment
        deployment_yaml = f"""apiVersion: apps/v1
kind: Deployment
metadata:
  name: {project_name}-api
  labels:
    app: {project_name}-api
spec:
  replicas: 3
  selector:
    matchLabels:
      app: {project_name}-api
  template:
    metadata:
      labels:
        app: {project_name}-api
    spec:
      containers:
      - name: {project_name}-api
        image: {project_name}-api:latest
        ports:
        - containerPort: 8000
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: {project_name}-secrets
              key: database-url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
        resources:
          requests:
            memory: "256Mi"
            cpu: "250m"
          limits:
            memory: "512Mi"
            cpu: "500m"
"""
        self._write_file(k8s_dir / "deployment.yaml", deployment_yaml)
        generated_files.append("kubernetes/deployment.yaml")
        
        # Service
        service_yaml = f"""apiVersion: v1
kind: Service
metadata:
  name: {project_name}-api-service
spec:
  selector:
    app: {project_name}-api
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
"""
        self._write_file(k8s_dir / "service.yaml", service_yaml)
        generated_files.append("kubernetes/service.yaml")
        
        # ConfigMap
        configmap_yaml = f"""apiVersion: v1
kind: ConfigMap
metadata:
  name: {project_name}-config
data:
  app-name: "{context['title']}"
  app-version: "{context['version']}"
"""
        self._write_file(k8s_dir / "configmap.yaml", configmap_yaml)
        generated_files.append("kubernetes/configmap.yaml")
        
        # Secret template
        secret_yaml = f"""apiVersion: v1
kind: Secret
metadata:
  name: {project_name}-secrets
type: Opaque
data:
  # Base64 encoded values
  database-url: <base64-encoded-database-url>
  secret-key: <base64-encoded-secret-key>
"""
        self._write_file(k8s_dir / "secret.yaml", secret_yaml)
        generated_files.append("kubernetes/secret.yaml")
        
        return generated_files
    
    def _generate_additional_files(self, output_dir: Path, context: Dict[str, Any]) -> List[str]:
        """Generate additional configuration files."""
        generated_files = []
        
        # README.md
        readme_content = f"""# {context['title']}

{context['description']}

## Generated by SpineAPI

This FastAPI application was automatically generated from an OpenAPI specification using SpineAPI.

## Features

- ✅ FastAPI application with automatic API documentation
- ✅ SQLAlchemy ORM models and database integration
- ✅ Pydantic schemas for request/response validation
- ✅ Comprehensive test suite with pytest
- ✅ Docker containerization with docker-compose
- ✅ Prometheus metrics and monitoring
- ✅ Structured logging with Loguru
- ✅ Production-ready configuration

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the application:**
   ```bash
   uvicorn main:app --reload
   ```

3. **Access the API documentation:**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## API Endpoints

### Generated Endpoints
{chr(10).join(f"- {endpoint.method.upper()} `{endpoint.path}` - {endpoint.summary or 'No description'}" for endpoint in context['endpoints'])}

### System Endpoints
- GET `/health` - Health check
- GET `/metrics` - Prometheus metrics

## Database

Database type: **{context['database'].upper()}**

{'PostgreSQL connection string: `postgresql://user:password@localhost/dbname`' if context['database'] == 'postgresql' else 'SQLite database file: `./database.db`'}

## Testing

Run the test suite:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=. --cov-report=html
```

## Docker

Build and run with Docker Compose:
```bash
docker-compose up --build
```

## Development

### Code Formatting
```bash
black .
isort .
```

### Linting
```bash
flake8 .
mypy .
```

## Project Structure

```
.
├── main.py              # FastAPI application
├── database.py          # Database configuration
├── models.py            # SQLAlchemy models
├── schemas.py           # Pydantic schemas
├── crud_*.py           # CRUD operations
├── tests/              # Test suite
├── monitoring/         # Monitoring configuration
├── kubernetes/         # Kubernetes manifests
├── Dockerfile          # Docker configuration
├── docker-compose.yml  # Docker Compose setup
└── requirements.txt    # Python dependencies
```

## Environment Variables

Create a `.env` file with:
```env
DATABASE_URL={"postgresql://user:password@localhost/dbname" if context['database'] == 'postgresql' else "sqlite:///./database.db"}
SECRET_KEY=your-secret-key-here
DEBUG=False
```

## Monitoring

- **Prometheus metrics:** http://localhost:9090
- **Grafana dashboards:** http://localhost:3000 (admin/admin)

## License

This generated code is provided as-is. Please review and customize according to your needs.

---

*Generated by [SpineAPI](https://github.com/spineapi/spineapi) v0.1.0*
"""
        self._write_file(output_dir / "README.md", readme_content)
        generated_files.append("README.md")
        
        # .env.example
        env_example = f"""# Environment Configuration
DATABASE_URL={'postgresql://user:password@localhost/' + context['project_name'] if context['database'] == 'postgresql' else 'sqlite:///./' + context['project_name'] + '.db'}
SECRET_KEY=your-secret-key-here
DEBUG=False
CORS_ORIGINS=["http://localhost:3000", "http://localhost:8080"]

# Logging
LOG_LEVEL=INFO
LOG_FILE=logs/app.log

# Redis (Optional)
REDIS_URL=redis://localhost:6379/0

# Monitoring
PROMETHEUS_ENABLED=True
GRAFANA_ENABLED=True
"""
        self._write_file(output_dir / ".env.example", env_example)
        generated_files.append(".env.example")
        
        # .gitignore
        gitignore_content = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual environments
.env
.venv
env/
venv/
ENV/
env.bak/
venv.bak/

# IDEs
.vscode/
.idea/
*.swp
*.swo
*~

# Testing
.coverage
.pytest_cache/
.tox/
nosetests.xml
coverage.xml
*.cover
*.py,cover
.hypothesis/

# Jupyter Notebook
.ipynb_checkpoints

# Database
*.db
*.sqlite3

# Logs
logs/
*.log

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Docker
.dockerignore

# Environment variables
.env.local
.env.development.local
.env.test.local
.env.production.local
"""
        self._write_file(output_dir / ".gitignore", gitignore_content)
        generated_files.append(".gitignore")
        
        return generated_files
    
    def _apply_llm_enhancements(self, output_dir: Path, generated_files: List[str]) -> None:
        """Apply LLM enhancements to generated code."""
        if not self.llm_enhancer:
            return
        
        python_files = [f for f in generated_files if f.endswith('.py')]
        
        for file_path in python_files:
            full_path = output_dir / file_path
            if full_path.exists():
                try:
                    with open(full_path, 'r', encoding='utf-8') as f:
                        original_content = f.read()
                    
                    enhanced_content = self.llm_enhancer.enhance_code(
                        original_content,
                        file_type="python",
                        context=f"FastAPI application file: {file_path}"
                    )
                    
                    if enhanced_content and enhanced_content != original_content:
                        with open(full_path, 'w', encoding='utf-8') as f:
                            f.write(enhanced_content)
                        logger.info(f"Enhanced {file_path} with LLM")
                
                except Exception as e:
                    logger.warning(f"Failed to enhance {file_path}: {e}")
    
    def _render_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """Render a Jinja2 template with the given context."""
        template = self.jinja_env.get_template(template_name)
        return template.render(**context)
    
    def _write_file(self, file_path: Path, content: str) -> None:
        """Write content to a file."""
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
