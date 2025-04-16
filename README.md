# README of Weekly Analytics

# AI-Powered ETL and Analysis Workflow Checklist

## Project Overview
This checklist covers the implementation of an AI-powered workflow that:
- Reads Excel files from a specified folder
- Updates a MongoDB local collection with the data
- Reads the collection as a dataframe
- Uses Claude 3.5 Haiku via the Anthropic API to perform analysis
- Formats and returns the output to the user

## 1. Project Setup
- [x] Create project directory structure
- [x] Set up virtual environment using uv: `uv venv`
- [x] Create `pyproject.toml` for dependencies and project metadata
- [x] Install dependencies with uv: `uv pip install -e .`
- [x] Add development dependencies: `uv pip install -e ".[dev]"`
- [x] Set up pre-commit hooks for code quality
- [x] Create configuration files (TOML format for readability)
- [x] Initialize Git repository and add `.gitignore`

## 2. Data Extraction Module
- [x] Implement ExcelExtractor class with type hints
- [x] Add methods to scan folder for Excel files
- [x] Create Pydantic models for data validation
- [x] Implement comprehensive error handling with custom exceptions
- [ ] Add logging with context information
- [ ] Create unit tests with pytest fixtures
- [ ] Add type checking with mypy

## 3. MongoDB Integration
- [ ] Implement MongoDBHandler class
- [ ] Add connection management functionality
- [ ] Create methods for CRUD operations
- [ ] Implement conversion from MongoDB to DataFrame
- [ ] Add error handling for database operations
- [ ] Test MongoDB integration with sample data

## 4. AI Analysis Component
- [ ] Set up Anthropic API integration
- [ ] Implement ClaudeAnalyzer class
- [ ] Create prompt templates for different analysis types
- [ ] Add error handling for API calls
- [ ] Implement rate limiting and retry logic
- [ ] Test analysis functionality with sample data

## 5. Output Formatting
- [ ] Implement OutputFormatter class
- [ ] Create templating system for different output formats
- [ ] Add methods to structure analysis results
- [ ] Create unit tests for the formatter

## 6. Design Pattern Implementation
- [ ] Implement Factory Pattern for component creation
- [ ] Create Builder Pattern for data pipeline construction
- [ ] Implement Strategy Pattern for analysis approaches
- [ ] Structure the overall workflow as a Pipeline

## 7. Workflow Orchestration
- [ ] Implement WorkflowOrchestrator class
- [ ] Connect all components in the pipeline
- [ ] Add logging at key points in the workflow
- [ ] Implement error recovery mechanisms
- [ ] Create main entry point script

## 8. Testing
- [ ] Write unit tests for all components
- [ ] Create integration tests for end-to-end workflow
- [ ] Set up test fixtures and mock objects
- [ ] Test with various Excel file formats and sizes
- [ ] Validate MongoDB operations in test environment

## 9. Performance Optimization
- [ ] Profile the application to identify bottlenecks
- [ ] Optimize MongoDB queries
- [ ] Implement caching where appropriate
- [ ] Add batch processing for large files

## 10. Documentation and Deployment
- [ ] Write comprehensive docstrings for all classes and methods
- [ ] Create README with usage instructions
- [ ] Document architecture decisions
- [ ] Prepare deployment instructions
- [ ] Create sample usage examples

## 11. Monitoring and Maintenance
- [ ] Implement logging system
- [ ] Add performance metrics collection
- [ ] Create monitoring dashboard (optional)
- [ ] Set up alerts for critical failures (optional)
- [ ] Document maintenance procedures

## Design Patterns Reference

### Factory Pattern
Used for creating different components (data extraction, MongoDB operations, AI analysis) without specifying their concrete classes.

### Builder Pattern
Used for constructing the data preprocessing pipeline, separating complex object construction from representation.

### Strategy Pattern
Implements different analysis strategies that can be swapped at runtime, encapsulating varying algorithms.

### Pipeline Pattern
Structures the entire workflow as a sequential pipeline with defined stages for extraction, transformation, loading, and analysis.

## Recommended Project Structure (With uv)
```
ai_etl_workflow/                     # Main package directory (use underscores for imports)
├── __init__.py                      # Package initialization
├── core/                            # Core functionality
│   ├── __init__.py
│   ├── extraction.py                # Excel extraction logic
│   ├── storage.py                   # MongoDB operations
│   ├── analysis.py                  # Claude API integration
│   └── formatting.py                # Output formatting
├── patterns/                        # Design pattern implementations
│   ├── __init__.py
│   ├── factory.py                   # Factory pattern implementations
│   ├── builder.py                   # Builder pattern implementations
│   ├── strategy.py                  # Strategy pattern implementations
│   └── pipeline.py                  # Pipeline pattern implementation
├── utils/                           # Utility functions
│   ├── __init__.py
│   ├── validators.py                # Data validation utilities
│   ├── logging.py                   # Logging configuration
│   └── config.py                    # Configuration management
├── cli.py                           # Command-line interface
├── config/                          # Configuration files
│   ├── default_config.toml          # Default configuration (TOML format for readability)
│   └── logging_config.yaml          # Logging configuration
├── tests/                           # Test directory
│   ├── __init__.py
│   ├── conftest.py                  # pytest fixtures and configuration
│   ├── test_extraction.py
│   ├── test_storage.py
│   ├── test_analysis.py
│   └── test_integration.py          # Integration tests
├── examples/                        # Example usage scripts
│   ├── basic_workflow.py
│   └── custom_analysis.py
├── docs/                            # Documentation
│   ├── architecture.md              # Architecture documentation
│   ├── usage.md                     # Usage guide
│   └── maintenance.md               # Maintenance procedures
├── pyproject.toml                   # Project metadata and dependencies (uv compatible)
├── .pre-commit-config.yaml          # pre-commit hooks for code quality
├── .gitignore                       # Git ignore file
├── README.md                        # Project README
└── main.py                          # Main entry point
```

### uv Setup Notes

1. **Initialize uv Environment**:
   ```bash
   uv venv
   ```

2. **Install Dependencies with uv**:
   ```bash
   uv pip install -e .
   ```

3. **pyproject.toml Example**:
   ```toml
   [build-system]
   requires = ["hatchling"]
   build-backend = "hatchling.build"

   [project]
   name = "ai_etl_workflow"
   version = "0.1.0"
   description = "AI-powered ETL workflow with MongoDB and Claude analysis"
   readme = "README.md"
   requires-python = ">=3.9"
   license = {text = "MIT"}
   dependencies = [
       "pandas>=2.0.0",
       "pymongo>=4.4.0",
       "openpyxl>=3.1.0",
       "anthropic>=0.5.0",
       "pydantic>=2.0.0",
       "typer>=0.9.0",  # For CLI interface
       "rich>=13.3.5",  # For console output
       "tomli>=2.0.1",  # For TOML config parsing
   ]

   [project.optional-dependencies]
   dev = [
       "pytest>=7.3.1",
       "pytest-cov>=4.1.0",
       "pre-commit>=3.3.2",
       "black>=23.3.0",
       "isort>=5.12.0",
       "mypy>=1.3.0",
       "ruff>=0.0.270",
   ]

   [project.scripts]
   ai-etl = "ai_etl_workflow.cli:app"

   [tool.black]
   line-length = 88

   [tool.isort]
   profile = "black"

   [tool.mypy]
   python_version = "3.9"
   warn_return_any = true
   warn_unused_configs = true
   disallow_untyped_defs = true
   disallow_incomplete_defs = true

   [tool.pytest.ini_options]
   testpaths = ["tests"]
   pythonpath = ["."]
   ```

4. **Type Checking**:
   For better maintainability, use type hints throughout the code:
   ```python
   from typing import Dict, List, Optional, Any

   def process_data(data: Dict[str, Any], options: Optional[Dict[str, str]] = None) -> List[Dict[str, Any]]:
       """
       Process data with given options.

       Args:
           data: Input data dictionary
           options: Optional processing options

       Returns:
           Processed data as a list of dictionaries
       """
       # Implementation
   ```
