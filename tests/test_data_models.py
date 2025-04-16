"""
Unit tests for the data models used in the application.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError

from models.data_models import (
    Contact,
    FunnelEntry,
    FunnelData,
    ExcelSheetMetadata,
    ExcelFileMetadata,
    ProbabilityStatus,
)


class TestDataModels:
    """Test suite for the Pydantic data models."""

    def test_contact_model(self):
        """Test the Contact model."""
        # Valid contact
        contact = Contact(
            name="John Doe", email="john@example.com", phone="123-456-7890"
        )
        assert contact.name == "John Doe"
        assert contact.email == "john@example.com"
        assert contact.phone == "123-456-7890"

        # Valid contact with only name
        contact = Contact(name="Jane Smith")
        assert contact.name == "Jane Smith"
        assert contact.email is None
        assert contact.phone is None

        # Invalid email format
        with pytest.raises(ValidationError):
            Contact(name="Invalid Email", email="not-an-email")

    def test_funnel_entry_model(self):
        """Test the FunnelEntry model."""
        # Valid entry with all fields
        entry = FunnelEntry(
            id="ENT-001",
            company_name="ABC Corp",
            project_name="Website Redesign",
            value=50000.0,
            probability=80.0,
            status=ProbabilityStatus.HIGH,
            start_date=datetime(2025, 1, 1),
            expected_close_date=datetime(2025, 3, 31),
            notes="Redesign of corporate website",
            last_updated=datetime(2025, 1, 15),
            contacts=[Contact(name="John Doe", email="john@example.com")],
            custom_fields={"industry": "Technology", "priority": "High"},
        )

        assert entry.id == "ENT-001"
        assert entry.company_name == "ABC Corp"
        assert entry.value == 50000.0
        assert entry.probability == 80.0
        assert entry.status == ProbabilityStatus.HIGH
        assert len(entry.contacts) == 1
        assert entry.contacts[0].name == "John Doe"
        assert entry.custom_fields["industry"] == "Technology"

        # Valid entry with minimal required fields
        entry = FunnelEntry(
            company_name="XYZ Ltd",
            project_name="Mobile App",
            value=75000.0,
        )

        assert entry.company_name == "XYZ Ltd"
        assert entry.project_name == "Mobile App"
        assert entry.value == 75000.0
        assert entry.probability is None
        assert entry.status is None
        assert entry.contacts == []
        assert entry.custom_fields == {}

        # Invalid probability (over 100)
        with pytest.raises(ValidationError):
            FunnelEntry(
                company_name="Invalid",
                project_name="Invalid",
                value=100.0,
                probability=120.0,
            )

        # Invalid probability (negative)
        with pytest.raises(ValidationError):
            FunnelEntry(
                company_name="Invalid",
                project_name="Invalid",
                value=100.0,
                probability=-10.0,
            )

        # Invalid dates (start after end)
        with pytest.raises(ValidationError):
            FunnelEntry(
                company_name="Invalid Dates",
                project_name="Project",
                value=100.0,
                start_date=datetime(2025, 4, 1),
                expected_close_date=datetime(2025, 3, 1),
            )

    def test_funnel_data_model(self, sample_funnel_entries):
        """Test the FunnelData model."""
        # Valid FunnelData with entries
        funnel_data = FunnelData(
            entries=sample_funnel_entries,
            extraction_date=datetime(2025, 4, 16),
            source_file="path/to/file.xlsx",
            sheet_name="Sheet1",
        )

        assert len(funnel_data.entries) == 3
        assert funnel_data.source_file == "path/to/file.xlsx"
        assert funnel_data.sheet_name == "Sheet1"

        # Check total_value calculation
        assert funnel_data.total_value == 225000.0  # Sum of all entry values

        # Empty entries list should raise ValidationError
        with pytest.raises(ValidationError):
            FunnelData(
                entries=[],
                extraction_date=datetime(2025, 4, 16),
                source_file="path/to/file.xlsx",
            )

    def test_excel_sheet_metadata_model(self):
        """Test the ExcelSheetMetadata model."""
        # Valid sheet metadata
        sheet_metadata = ExcelSheetMetadata(
            sheet_name="Sheet1",
            row_count=100,
            column_count=10,
            column_headers=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        )

        assert sheet_metadata.sheet_name == "Sheet1"
        assert sheet_metadata.row_count == 100
        assert sheet_metadata.column_count == 10
        assert len(sheet_metadata.column_headers) == 10

        # Invalid row count (zero or negative)
        with pytest.raises(ValidationError):
            ExcelSheetMetadata(
                sheet_name="Invalid",
                row_count=0,
                column_count=10,
                column_headers=["A", "B", "C"],
            )

        # Invalid column count (zero or negative)
        with pytest.raises(ValidationError):
            ExcelSheetMetadata(
                sheet_name="Invalid",
                row_count=10,
                column_count=-1,
                column_headers=["A", "B", "C"],
            )

    def test_excel_file_metadata_model(self):
        """Test the ExcelFileMetadata model."""
        # Create sheet metadata for testing
        sheet_metadata1 = ExcelSheetMetadata(
            sheet_name="Sheet1",
            row_count=100,
            column_count=10,
            column_headers=["A", "B", "C", "D", "E", "F", "G", "H", "I", "J"],
        )

        sheet_metadata2 = ExcelSheetMetadata(
            sheet_name="Sheet2",
            row_count=50,
            column_count=5,
            column_headers=["A", "B", "C", "D", "E"],
        )

        # Valid file metadata
        file_metadata = ExcelFileMetadata(
            file_path="path/to/file.xlsx",
            file_size=1024,
            last_modified=datetime(2025, 4, 16),
            sheets=[sheet_metadata1, sheet_metadata2],
        )

        assert file_metadata.file_path == "path/to/file.xlsx"
        assert file_metadata.file_size == 1024
        assert file_metadata.last_modified == datetime(2025, 4, 16)
        assert len(file_metadata.sheets) == 2

        # Valid file metadata with minimal fields
        file_metadata = ExcelFileMetadata(
            file_path="path/to/file.xlsx",
        )

        assert file_metadata.file_path == "path/to/file.xlsx"
        assert file_metadata.file_size is None
        assert file_metadata.last_modified is None
        assert file_metadata.sheets == []
