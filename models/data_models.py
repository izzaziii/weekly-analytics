"""
Pydantic models for data validation of Excel data.
"""

from datetime import datetime
from typing import Dict, List, Optional, Union, Any
from enum import Enum
from pydantic import BaseModel, Field, validator, root_validator

from utils.logging_utils import ContextLogger

# Create a logger for the data models module
logger = ContextLogger("data_models")


class ProbabilityStatus(str, Enum):
    """Enum for probability status values."""

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"
    CLOSED_WON = "Closed Won"
    CLOSED_LOST = "Closed Lost"


class Contact(BaseModel):
    """Model for contact information."""

    name: str = Field(..., description="Contact name")
    email: Optional[str] = Field(None, description="Contact email")
    phone: Optional[str] = Field(None, description="Contact phone number")

    @validator("email")
    def validate_email(cls, v):
        """Validate email format if provided."""
        if v is not None and "@" not in v:
            logger.warning(f"Invalid email format: {v}")
            raise ValueError("Invalid email format")
        return v


class FunnelEntry(BaseModel):
    """Model for a single funnel entry from the Excel file."""

    id: Optional[str] = Field(None, description="Unique identifier")
    company_name: str = Field(..., description="Company name")
    project_name: str = Field(..., description="Project name")
    value: float = Field(..., description="Project value")
    probability: Optional[float] = Field(
        None, description="Probability percentage (0-100)"
    )
    status: Optional[ProbabilityStatus] = Field(None, description="Current status")
    start_date: Optional[datetime] = Field(None, description="Project start date")
    expected_close_date: Optional[datetime] = Field(
        None, description="Expected closing date"
    )
    contacts: Optional[List[Contact]] = Field(
        default_factory=list, description="List of contacts"
    )
    notes: Optional[str] = Field(None, description="Additional notes")
    last_updated: Optional[datetime] = Field(None, description="Last update timestamp")
    custom_fields: Dict[str, Any] = Field(
        default_factory=dict, description="Custom fields"
    )

    @validator("probability")
    def validate_probability(cls, v):
        """Validate probability is between 0 and 100."""
        if v is not None and (v < 0 or v > 100):
            logger.warning(f"Invalid probability value: {v}")
            raise ValueError("Probability must be between 0 and 100")
        return v

    @root_validator
    def check_dates(cls, values):
        """Validate that start_date is before expected_close_date if both are provided."""
        start_date = values.get("start_date")
        close_date = values.get("expected_close_date")

        if start_date and close_date and start_date > close_date:
            company = values.get("company_name", "Unknown")
            project = values.get("project_name", "Unknown")
            logger.warning(
                f"Invalid dates for {company}/{project}: start date {start_date} is after close date {close_date}"
            )
            raise ValueError("Start date must be before expected close date")

        # Log creation of valid entry
        if "company_name" in values and "project_name" in values:
            logger.debug(
                f"Created FunnelEntry for {values['company_name']}/{values['project_name']}"
            )

        return values


class FunnelData(BaseModel):
    """Model for the complete funnel data set."""

    entries: List[FunnelEntry] = Field(..., description="List of funnel entries")
    extraction_date: datetime = Field(
        default_factory=datetime.now, description="Date when data was extracted"
    )
    source_file: str = Field(..., description="Source Excel file path")
    sheet_name: Optional[str] = Field(None, description="Excel sheet name")
    total_value: Optional[float] = Field(None, description="Sum of all entry values")

    @root_validator
    def calculate_total_value(cls, values):
        """Calculate the total value of all entries."""
        entries = values.get("entries", [])
        source_file = values.get("source_file", "Unknown")
        sheet_name = values.get("sheet_name", "Unknown")

        if entries:
            values["total_value"] = sum(entry.value for entry in entries)
            logger.info(
                f"Calculated total value {values['total_value']} for {len(entries)} entries from {source_file}/{sheet_name}"
            )

        return values


class ExcelSheetMetadata(BaseModel):
    """Model for Excel sheet metadata."""

    sheet_name: str = Field(..., description="Name of the sheet")
    row_count: int = Field(..., description="Number of rows")
    column_count: int = Field(..., description="Number of columns")
    column_headers: List[str] = Field(..., description="Column headers")

    @validator("row_count", "column_count")
    def validate_counts(cls, v, values, **kwargs):
        """Validate counts are positive."""
        if v <= 0:
            field_name = next(
                name for name, value in kwargs.get("field").items() if value == v
            )
            sheet_name = values.get("sheet_name", "Unknown")
            logger.warning(f"Invalid {field_name} for sheet {sheet_name}: {v}")
            raise ValueError("Count must be positive")

        return v

    def __init__(self, **data):
        super().__init__(**data)
        logger.debug(
            f"Created metadata for sheet {self.sheet_name}: {self.row_count} rows, {self.column_count} columns"
        )


class ExcelFileMetadata(BaseModel):
    """Model for Excel file metadata."""

    file_path: str = Field(..., description="Path to the Excel file")
    file_size: Optional[int] = Field(None, description="File size in bytes")
    last_modified: Optional[datetime] = Field(
        None, description="Last modification date"
    )
    sheets: List[ExcelSheetMetadata] = Field(
        default_factory=list, description="Metadata for each sheet"
    )

    def __init__(self, **data):
        super().__init__(**data)
        logger.info(
            f"Created metadata for file {self.file_path}: {len(self.sheets)} sheets, {self.file_size} bytes"
        )
