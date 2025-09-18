"""
SpineAPI CLI - Main command line interface
"""
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import typer
try:
    from loguru import logger
    HAS_LOGURU = True
except ImportError:
    logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    HAS_LOGURU = False
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from spineapi.generators.main import CodeGenerator
from spineapi.parsers.openapi import OpenAPIParser
from spineapi.llm.enhancer import LLMEnhancer

app = typer.Typer(
    name="spineapi",
    help="🦴 SpineAPI - AI-powered backend scaffolding tool",
    rich_markup_mode="rich",
)

console = Console()


def version_callback(value: bool):
    """Show version information."""
    if value:
        from spineapi import __version__
        console.print(f"SpineAPI version: {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Optional[bool] = typer.Option(
        None, "--version", "-v", callback=version_callback, is_eager=True,
        help="Show version information"
    ),
    verbose: bool = typer.Option(
        False, "--verbose", "-V", help="Enable verbose logging"
    ),
):
    """
    🦴 SpineAPI - Transform OpenAPI specs into production-ready backends
    
    Generate FastAPI applications with models, tests, and deployment configs
    from your OpenAPI/Swagger specifications.
    """
    # Logging is configured based on the available logger
    if verbose:
        logger.info("Verbose mode enabled")
    pass  # Logging configuration handled during import


@app.command()
def generate(
    spec: str = typer.Argument(
        ..., 
        help="Path to OpenAPI/Swagger specification file (YAML or JSON)"
    ),
    output_dir: str = typer.Option(
        "./generated",
        "--output", "-o",
        help="Output directory for generated project"
    ),
    framework: str = typer.Option(
        "fastapi",
        "--framework", "-f",
        help="Backend framework to generate (currently supports: fastapi)"
    ),
    database: str = typer.Option(
        "sqlite",
        "--database", "-d",
        help="Database type to use (sqlite, postgresql)"
    ),
    enable_llm: bool = typer.Option(
        False,
        "--llm",
        help="Enable LLM enhancement for better code generation"
    ),
    llm_provider: str = typer.Option(
        "openai",
        "--llm-provider",
        help="LLM provider to use (openai, huggingface)"
    ),
    include_tests: bool = typer.Option(
        True,
        "--tests/--no-tests",
        help="Generate test suites"
    ),
    include_docker: bool = typer.Option(
        True,
        "--docker/--no-docker",
        help="Generate Docker configurations"
    ),
    include_monitoring: bool = typer.Option(
        False,
        "--monitoring",
        help="Include monitoring and observability setup"
    ),
    include_k8s: bool = typer.Option(
        False,
        "--k8s",
        help="Generate Kubernetes deployment configurations"
    ),
    project_name: Optional[str] = typer.Option(
        None,
        "--name", "-n",
        help="Project name (defaults to spec filename)"
    ),
    force: bool = typer.Option(
        False,
        "--force",
        help="Overwrite existing output directory"
    ),
):
    """
    Generate a complete backend application from OpenAPI specification.
    
    This command parses your OpenAPI/Swagger spec and generates:
    - FastAPI application with routes and models
    - SQLAlchemy ORM models
    - Pytest test suites
    - Docker and docker-compose configurations
    - Optional monitoring and Kubernetes configs
    """
    
    # Validate inputs
    spec_path = Path(spec)
    if not spec_path.exists():
        console.print(f"❌ OpenAPI spec file not found: {spec}", style="red")
        raise typer.Exit(1)
    
    output_path = Path(output_dir)
    
    if output_path.exists() and not force:
        console.print(f"❌ Output directory already exists: {output_dir}", style="red")
        console.print("Use --force to overwrite", style="yellow")
        raise typer.Exit(1)
    
    if framework != "fastapi":
        console.print(f"❌ Unsupported framework: {framework}", style="red")
        console.print("Currently supported: fastapi", style="yellow")
        raise typer.Exit(1)
    
    # Set project name
    if not project_name:
        project_name = spec_path.stem.replace("-", "_").replace(" ", "_")
    
    # Show generation summary
    table = Table(title="🦴 SpineAPI Generation Plan")
    table.add_column("Component", style="cyan")
    table.add_column("Status", style="green")
    
    table.add_row("OpenAPI Spec", f"✅ {spec_path.name}")
    table.add_row("Framework", f"✅ {framework.upper()}")
    table.add_row("Database", f"✅ {database.upper()}")
    table.add_row("Output Directory", f"✅ {output_path}")
    table.add_row("Project Name", f"✅ {project_name}")
    
    if enable_llm:
        table.add_row("LLM Enhancement", f"✅ {llm_provider.upper()}")
    if include_tests:
        table.add_row("Test Suites", "✅ Pytest")
    if include_docker:
        table.add_row("Docker Configs", "✅ Dockerfile + Compose")
    if include_monitoring:
        table.add_row("Monitoring", "✅ Prometheus + Grafana")
    if include_k8s:
        table.add_row("Kubernetes", "✅ Deployment + Service")
    
    console.print(table)
    console.print()
    
    # Start generation process
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        # Parse OpenAPI spec
        task = progress.add_task("🔍 Parsing OpenAPI specification...", total=None)
        try:
            parser = OpenAPIParser()
            spec_data = parser.parse(spec_path)
            progress.update(task, description="✅ OpenAPI spec parsed successfully")
        except Exception as e:
            progress.update(task, description="❌ Failed to parse OpenAPI spec")
            console.print(f"Error: {e}", style="red")
            raise typer.Exit(1)
        
        # Initialize LLM enhancer if enabled
        llm_enhancer = None
        if enable_llm:
            task = progress.add_task("🤖 Initializing LLM enhancer...", total=None)
            try:
                llm_enhancer = LLMEnhancer(provider=llm_provider)
                progress.update(task, description="✅ LLM enhancer ready")
            except Exception as e:
                progress.update(task, description="⚠️  LLM enhancement disabled")
                console.print(f"Warning: {e}", style="yellow")
                enable_llm = False
        
        # Generate code
        task = progress.add_task("🏗️  Generating backend application...", total=None)
        try:
            generator = CodeGenerator(
                framework=framework,
                database=database,
                enable_llm=enable_llm,
                llm_enhancer=llm_enhancer,
            )
            
            result = generator.generate(
                spec_data=spec_data,
                output_dir=output_path,
                project_name=project_name,
                include_tests=include_tests,
                include_docker=include_docker,
                include_monitoring=include_monitoring,
                include_k8s=include_k8s,
            )
            
            progress.update(task, description="✅ Backend application generated")
            
        except Exception as e:
            progress.update(task, description="❌ Generation failed")
            console.print(f"Error: {e}", style="red")
            raise typer.Exit(1)
    
    # Show success message
    panel = Panel(
        f"""[green]✅ Successfully generated {framework.upper()} backend![/green]

[bold]Project Location:[/bold] {output_path.absolute()}
[bold]Project Name:[/bold] {project_name}

[bold]Next Steps:[/bold]
1. [cyan]cd {output_path}[/cyan]
2. [cyan]pip install -r requirements.txt[/cyan]
3. [cyan]uvicorn main:app --reload[/cyan]

[bold]Generated Files:[/bold]
• FastAPI application with routes
• SQLAlchemy models and migrations  
• Pytest test suites
{"• Docker and docker-compose configs" if include_docker else ""}
{"• Prometheus metrics and Grafana dashboards" if include_monitoring else ""}
{"• Kubernetes deployment configs" if include_k8s else ""}

[bold]API Documentation:[/bold] http://localhost:8000/docs
""",
        title="🦴 SpineAPI Generation Complete",
        border_style="green",
    )
    
    console.print(panel)


@app.command()
def validate(
    spec: str = typer.Argument(
        ..., 
        help="Path to OpenAPI/Swagger specification file to validate"
    ),
):
    """
    Validate an OpenAPI specification file.
    
    Checks if the specification is valid and provides detailed error messages
    if any issues are found.
    """
    spec_path = Path(spec)
    if not spec_path.exists():
        console.print(f"❌ OpenAPI spec file not found: {spec}", style="red")
        raise typer.Exit(1)
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
    ) as progress:
        
        task = progress.add_task("🔍 Validating OpenAPI specification...", total=None)
        
        try:
            parser = OpenAPIParser()
            parser.validate(spec_path)
            progress.update(task, description="✅ OpenAPI spec is valid")
            
            console.print(
                Panel(
                    f"[green]✅ Valid OpenAPI Specification[/green]\n\nFile: {spec_path}",
                    title="Validation Result",
                    border_style="green",
                )
            )
            
        except Exception as e:
            progress.update(task, description="❌ Validation failed")
            console.print(
                Panel(
                    f"[red]❌ Invalid OpenAPI Specification[/red]\n\nError: {e}",
                    title="Validation Result", 
                    border_style="red",
                )
            )
            raise typer.Exit(1)


@app.command()
def init(
    name: str = typer.Argument(
        ...,
        help="Project name for the new OpenAPI specification"
    ),
    output_dir: str = typer.Option(
        ".",
        "--output", "-o", 
        help="Directory to create the spec file"
    ),
):
    """
    Initialize a new OpenAPI specification template.
    
    Creates a basic OpenAPI 3.0 specification file that you can use as a starting
    point for your API definition.
    """
    output_path = Path(output_dir)
    spec_file = output_path / f"{name.lower().replace(' ', '-')}.yaml"
    
    if spec_file.exists():
        console.print(f"❌ File already exists: {spec_file}", style="red")
        raise typer.Exit(1)
    
    # Create basic OpenAPI spec template
    template_content = f"""openapi: 3.0.3
info:
  title: {name} API
  description: API specification for {name}
  version: 1.0.0
  contact:
    name: API Support
    email: support@example.com
  license:
    name: MIT
    url: https://opensource.org/licenses/MIT

servers:
  - url: http://localhost:8000
    description: Development server
  - url: https://api.{name.lower().replace(' ', '')}.com
    description: Production server

paths:
  /health:
    get:
      summary: Health check endpoint
      description: Returns the health status of the API
      operationId: health_check
      responses:
        '200':
          description: API is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: "healthy"
                  timestamp:
                    type: string
                    format: date-time

  /items:
    get:
      summary: List items
      description: Retrieve a list of items
      operationId: list_items
      parameters:
        - name: limit
          in: query
          description: Maximum number of items to return
          required: false
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 10
        - name: offset
          in: query
          description: Number of items to skip
          required: false
          schema:
            type: integer
            minimum: 0
            default: 0
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  items:
                    type: array
                    items:
                      $ref: '#/components/schemas/Item'
                  total:
                    type: integer
                  limit:
                    type: integer
                  offset:
                    type: integer

    post:
      summary: Create item
      description: Create a new item
      operationId: create_item
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ItemCreate'
      responses:
        '201':
          description: Item created successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Item'
        '400':
          description: Invalid input
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

  /items/{{item_id}}:
    get:
      summary: Get item by ID
      description: Retrieve a specific item by its ID
      operationId: get_item
      parameters:
        - name: item_id
          in: path
          required: true
          description: Item ID
          schema:
            type: integer
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Item'
        '404':
          description: Item not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    put:
      summary: Update item
      description: Update an existing item
      operationId: update_item
      parameters:
        - name: item_id
          in: path
          required: true
          description: Item ID
          schema:
            type: integer
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/ItemUpdate'
      responses:
        '200':
          description: Item updated successfully
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Item'
        '404':
          description: Item not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

    delete:
      summary: Delete item
      description: Delete an existing item
      operationId: delete_item
      parameters:
        - name: item_id
          in: path
          required: true
          description: Item ID
          schema:
            type: integer
      responses:
        '204':
          description: Item deleted successfully
        '404':
          description: Item not found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Error'

components:
  schemas:
    Item:
      type: object
      required:
        - id
        - name
        - created_at
      properties:
        id:
          type: integer
          description: Unique identifier for the item
          example: 1
        name:
          type: string
          description: Name of the item
          example: "Sample Item"
        description:
          type: string
          description: Description of the item
          example: "This is a sample item description"
        price:
          type: number
          format: float
          description: Price of the item
          example: 29.99
        in_stock:
          type: boolean
          description: Whether the item is in stock
          example: true
        created_at:
          type: string
          format: date-time
          description: When the item was created
        updated_at:
          type: string
          format: date-time
          description: When the item was last updated

    ItemCreate:
      type: object
      required:
        - name
      properties:
        name:
          type: string
          description: Name of the item
          example: "New Item"
        description:
          type: string
          description: Description of the item
          example: "Description for new item"
        price:
          type: number
          format: float
          description: Price of the item
          example: 19.99
        in_stock:
          type: boolean
          description: Whether the item is in stock
          default: true

    ItemUpdate:
      type: object
      properties:
        name:
          type: string
          description: Name of the item
          example: "Updated Item"
        description:
          type: string
          description: Description of the item
          example: "Updated description"
        price:
          type: number
          format: float
          description: Price of the item
          example: 24.99
        in_stock:
          type: boolean
          description: Whether the item is in stock

    Error:
      type: object
      required:
        - message
      properties:
        message:
          type: string
          description: Error message
          example: "An error occurred"
        code:
          type: string
          description: Error code
          example: "VALIDATION_ERROR"
        details:
          type: object
          description: Additional error details

  securitySchemes:
    BearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT

security:
  - BearerAuth: []

tags:
  - name: health
    description: Health check operations
  - name: items
    description: Item management operations
"""
    
    try:
        spec_file.write_text(template_content, encoding="utf-8")
        
        console.print(
            Panel(
                f"""[green]✅ OpenAPI specification created successfully![/green]

[bold]File Location:[/bold] {spec_file.absolute()}

[bold]Next Steps:[/bold]
1. Edit the specification to match your API requirements
2. Validate it: [cyan]spineapi validate {spec_file}[/cyan]
3. Generate backend: [cyan]spineapi generate {spec_file}[/cyan]

[bold]Template Includes:[/bold]
• Basic CRUD operations for items
• Health check endpoint
• Request/response schemas
• Error handling
• Authentication setup
• Documentation examples
""",
                title="🦴 OpenAPI Template Created",
                border_style="green",
            )
        )
        
    except Exception as e:
        console.print(f"❌ Failed to create specification: {e}", style="red")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()
