"""
OpenAPI Specification Parser

Parses OpenAPI/Swagger specifications and extracts endpoints, schemas, and models.
"""
import json
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from openapi_spec_validator import validate_spec
from openapi_spec_validator.readers import read_from_filename


class ParsedEndpoint:
    """Represents a parsed API endpoint."""
    
    def __init__(
        self,
        path: str,
        method: str,
        operation_id: str,
        summary: Optional[str] = None,
        description: Optional[str] = None,
        parameters: Optional[List[Dict[str, Any]]] = None,
        request_body: Optional[Dict[str, Any]] = None,
        responses: Optional[Dict[str, Any]] = None,
        tags: Optional[List[str]] = None,
        security: Optional[List[Dict[str, Any]]] = None,
    ):
        self.path = path
        self.method = method.upper()
        self.operation_id = operation_id
        self.summary = summary
        self.description = description
        self.parameters = parameters or []
        self.request_body = request_body
        self.responses = responses or {}
        self.tags = tags or []
        self.security = security or []
    
    @property
    def function_name(self) -> str:
        """Generate a Python function name from operation ID."""
        if self.operation_id:
            return self.operation_id.lower().replace("-", "_")
        else:
            # Fallback: generate from method and path
            path_parts = [p for p in self.path.split("/") if p and not p.startswith("{")]
            return f"{self.method.lower()}_{'_'.join(path_parts)}"
    
    @property
    def path_params(self) -> List[Dict[str, Any]]:
        """Get path parameters."""
        return [p for p in self.parameters if p.get("in") == "path"]
    
    @property
    def query_params(self) -> List[Dict[str, Any]]:
        """Get query parameters."""
        return [p for p in self.parameters if p.get("in") == "query"]
    
    @property
    def header_params(self) -> List[Dict[str, Any]]:
        """Get header parameters."""
        return [p for p in self.parameters if p.get("in") == "header"]
    
    @property
    def has_request_body(self) -> bool:
        """Check if endpoint has request body."""
        return self.request_body is not None
    
    def get_success_response_schema(self) -> Optional[Dict[str, Any]]:
        """Get the schema for successful response (2xx)."""
        for status_code, response in self.responses.items():
            if str(status_code).startswith("2"):
                content = response.get("content", {})
                json_content = content.get("application/json", {})
                return json_content.get("schema")
        return None


class ParsedSchema:
    """Represents a parsed data schema/model."""
    
    def __init__(
        self,
        name: str,
        schema: Dict[str, Any],
        description: Optional[str] = None,
    ):
        self.name = name
        self.schema = schema
        self.description = description
        self.properties = schema.get("properties", {})
        self.required_fields = schema.get("required", [])
        self.schema_type = schema.get("type", "object")
    
    @property
    def class_name(self) -> str:
        """Generate a Python class name."""
        # Convert to PascalCase
        words = self.name.replace("-", "_").replace(" ", "_").split("_")
        return "".join(word.capitalize() for word in words)
    
    @property
    def table_name(self) -> str:
        """Generate a database table name."""
        # Convert to snake_case plural
        name = self.name.lower().replace("-", "_").replace(" ", "_")
        if not name.endswith("s"):
            name += "s"
        return name
    
    def get_property_type(self, prop_name: str) -> Optional[str]:
        """Get the Python type for a property."""
        prop = self.properties.get(prop_name, {})
        prop_type = prop.get("type")
        prop_format = prop.get("format")
        
        if prop_type == "string":
            if prop_format == "date-time":
                return "datetime"
            elif prop_format == "date":
                return "date"
            elif prop_format == "email":
                return "str"  # Could use EmailStr from pydantic
            else:
                return "str"
        elif prop_type == "integer":
            return "int"
        elif prop_type == "number":
            return "float"
        elif prop_type == "boolean":
            return "bool"
        elif prop_type == "array":
            items = prop.get("items", {})
            item_type = items.get("type", "Any")
            return f"List[{item_type}]"
        else:
            return "Any"
    
    def is_required(self, prop_name: str) -> bool:
        """Check if a property is required."""
        return prop_name in self.required_fields


class ParsedSpec:
    """Represents a fully parsed OpenAPI specification."""
    
    def __init__(
        self,
        info: Dict[str, Any],
        endpoints: List[ParsedEndpoint],
        schemas: List[ParsedSchema],
        servers: List[Dict[str, Any]],
        security_schemes: Dict[str, Any],
        tags: List[Dict[str, Any]],
    ):
        self.info = info
        self.endpoints = endpoints
        self.schemas = schemas
        self.servers = servers
        self.security_schemes = security_schemes
        self.tags = tags
    
    @property
    def title(self) -> str:
        """Get API title."""
        return self.info.get("title", "Generated API")
    
    @property
    def version(self) -> str:
        """Get API version."""
        return self.info.get("version", "1.0.0")
    
    @property
    def description(self) -> str:
        """Get API description."""
        return self.info.get("description", "")
    
    @property
    def project_name(self) -> str:
        """Generate project name from title."""
        return self.title.lower().replace(" ", "_").replace("-", "_")
    
    def get_endpoints_by_tag(self, tag: str) -> List[ParsedEndpoint]:
        """Get endpoints filtered by tag."""
        return [e for e in self.endpoints if tag in e.tags]
    
    def get_schema_by_name(self, name: str) -> Optional[ParsedSchema]:
        """Get schema by name."""
        for schema in self.schemas:
            if schema.name == name or schema.class_name == name:
                return schema
        return None


class OpenAPIParser:
    """OpenAPI/Swagger specification parser."""
    
    def __init__(self):
        self.spec_data: Optional[Dict[str, Any]] = None
        
    def validate(self, spec_path: Path) -> None:
        """Validate OpenAPI specification."""
        try:
            spec_dict, spec_url = read_from_filename(str(spec_path))
            validate_spec(spec_dict)
        except Exception as e:
            raise ValueError(f"Invalid OpenAPI specification: {e}")
    
    def parse(self, spec_path: Path) -> ParsedSpec:
        """Parse OpenAPI specification file."""
        # Load specification
        try:
            if spec_path.suffix.lower() in ['.yaml', '.yml']:
                with open(spec_path, 'r', encoding='utf-8') as f:
                    self.spec_data = yaml.safe_load(f)
            elif spec_path.suffix.lower() == '.json':
                with open(spec_path, 'r', encoding='utf-8') as f:
                    self.spec_data = json.load(f)
            else:
                raise ValueError(f"Unsupported file format: {spec_path.suffix}")
        except Exception as e:
            raise ValueError(f"Failed to load specification file: {e}")
        
        # Validate specification
        self.validate(spec_path)
        
        # Parse components
        info = self._parse_info()
        endpoints = self._parse_endpoints()
        schemas = self._parse_schemas()
        servers = self._parse_servers()
        security_schemes = self._parse_security_schemes()
        tags = self._parse_tags()
        
        return ParsedSpec(
            info=info,
            endpoints=endpoints,
            schemas=schemas,
            servers=servers,
            security_schemes=security_schemes,
            tags=tags,
        )
    
    def _parse_info(self) -> Dict[str, Any]:
        """Parse API info section."""
        if self.spec_data is None:
            return {}
        return self.spec_data.get("info", {})
    
    def _parse_endpoints(self) -> List[ParsedEndpoint]:
        """Parse API endpoints from paths section."""
        endpoints = []
        if self.spec_data is None:
            return endpoints
            
        paths = self.spec_data.get("paths", {})
        
        for path, path_item in paths.items():
            # Global parameters for this path
            global_params = path_item.get("parameters", [])
            
            # Parse each HTTP method
            for method in ["get", "post", "put", "patch", "delete", "head", "options"]:
                if method not in path_item:
                    continue
                
                operation = path_item[method]
                
                # Combine global and operation-specific parameters
                parameters = global_params.copy()
                parameters.extend(operation.get("parameters", []))
                
                endpoint = ParsedEndpoint(
                    path=path,
                    method=method,
                    operation_id=operation.get("operationId", ""),
                    summary=operation.get("summary"),
                    description=operation.get("description"),
                    parameters=parameters,
                    request_body=operation.get("requestBody"),
                    responses=operation.get("responses", {}),
                    tags=operation.get("tags", []),
                    security=operation.get("security", []),
                )
                
                endpoints.append(endpoint)
        
        return endpoints
    
    def _parse_schemas(self) -> List[ParsedSchema]:
        """Parse schemas from components section."""
        schemas = []
        if self.spec_data is None:
            return schemas
            
        components = self.spec_data.get("components", {})
        schema_definitions = components.get("schemas", {})
        
        for name, schema_def in schema_definitions.items():
            schema = ParsedSchema(
                name=name,
                schema=schema_def,
                description=schema_def.get("description"),
            )
            schemas.append(schema)
        
        return schemas
    
    def _parse_servers(self) -> List[Dict[str, Any]]:
        """Parse servers section."""
        if self.spec_data is None:
            return []
        return self.spec_data.get("servers", [])
    
    def _parse_security_schemes(self) -> Dict[str, Any]:
        """Parse security schemes from components."""
        if self.spec_data is None:
            return {}
        components = self.spec_data.get("components", {})
        return components.get("securitySchemes", {})
    
    def _parse_tags(self) -> List[Dict[str, Any]]:
        """Parse tags section."""
        if self.spec_data is None:
            return []
        return self.spec_data.get("tags", [])
