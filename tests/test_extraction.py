"""
Unit tests for the Excel extraction functionality.
"""

import os
import pytest
import pandas as pd
from unittest import mock
from datetime import datetime

from core.extraction import ExcelExtractor
from models.data_models import FunnelData, ExcelFileMetadata


class TestExcelExtractor:
    """Test suite for the ExcelExtractor class."""

    def test_init(self):
        """Test the initialization of ExcelExtractor."""
        file_path = "test_path.xlsx"
        extractor = ExcelExtractor(file_path)
        assert extractor.file_path == file_path

    @mock.patch("pandas.read_excel")
    def test_extract_data(self, mock_read_excel, mock_excel_data):
        """Test the extract_data method with mocked pandas."""
        # Configure the mock to return our test DataFrame
        mock_read_excel.return_value = mock_excel_data["Sheet1"]

        # Create an extractor with a dummy file path
        extractor = ExcelExtractor("dummy_path.xlsx")

        # Call the method
        result = extractor.extract_data(sheet_name="Sheet1")

        # Check the result
        assert isinstance(result, pd.DataFrame)
        assert mock_read_excel.called
        assert len(result) == len(mock_excel_data["Sheet1"])
        assert list(result.columns) == list(mock_excel_data["Sheet1"].columns)

    @mock.patch("os.path.exists")
    def test_extract_data_file_not_found(self, mock_exists):
        """Test the extract_data method when the file is not found."""
        # Configure the mock to return False for os.path.exists
        mock_exists.return_value = False

        # Create an extractor with a dummy file path
        extractor = ExcelExtractor("nonexistent_file.xlsx")

        # Expect a FileNotFoundError
        with pytest.raises(FileNotFoundError):
            extractor.extract_data()

    @mock.patch("pandas.ExcelFile")
    def test_get_sheet_names(self, mock_excel_file):
        """Test the get_sheet_names method."""
        # Configure the mock to return a list of sheet names
        mock_excel_file.return_value.sheet_names = ["Sheet1", "Sheet2", "Sheet3"]

        # Create an extractor with a dummy file path
        extractor = ExcelExtractor("dummy_path.xlsx")

        # Call the method
        result = extractor.get_sheet_names()

        # Check the result
        assert isinstance(result, list)
        assert len(result) == 3
        assert result == ["Sheet1", "Sheet2", "Sheet3"]

    def test_get_file_metadata(self, temp_excel_file, mock_excel_data):
        """Test the get_file_metadata method with an actual file."""
        # Create an extractor with the temporary file path
        extractor = ExcelExtractor(temp_excel_file)

        # Call the method
        result = extractor.get_file_metadata()

        # Check the result
        assert isinstance(result, ExcelFileMetadata)
        assert result.file_path == temp_excel_file
        assert result.file_size is not None
        assert result.last_modified is not None
        assert len(result.sheets) == len(mock_excel_data)

        # Check the sheet metadata
        sheet_metadata = result.sheets[0]
        assert sheet_metadata.sheet_name == "Sheet1"
        assert sheet_metadata.row_count == len(mock_excel_data["Sheet1"])
        assert sheet_metadata.column_count == len(mock_excel_data["Sheet1"].columns)

    def test_extract_validated_data(self, temp_excel_file):
        """Test the extract_validated_data method with an actual file."""
        # Create an extractor with the temporary file path
        extractor = ExcelExtractor(temp_excel_file)

        # Call the method
        result = extractor.extract_validated_data(sheet_name="Sheet1")

        # Check the result
        assert isinstance(result, FunnelData)
        assert len(result.entries) == 3
        assert result.source_file == temp_excel_file
        assert result.sheet_name == "Sheet1"
        assert result.total_value == 225000.0  # Sum of the values in mock_excel_data

        # Check a sample entry
        entry = result.entries[0]
        assert entry.company_name == "ABC Corp"
        assert entry.project_name == "Website Redesign"
        assert entry.value == 50000.0

    def test_scan_folder_for_excel_files(self, temp_excel_files):
        """Test the scan_folder_for_excel_files method."""
        folder_path, expected_files = temp_excel_files

        # Create an extractor (the file path doesn't matter for this method)
        extractor = ExcelExtractor("dummy_path.xlsx")

        # Call the method
        result = extractor.scan_folder_for_excel_files(folder_path)

        # Check the result
        assert isinstance(result, list)
        assert len(result) == len(expected_files)

        # Sort both lists for comparison (file paths may be in different order)
        result.sort()
        expected_files.sort()

        # Verify that all expected files are in the result
        for expected_file in expected_files:
            assert expected_file in result

    @mock.patch("os.path.exists")
    def test_scan_folder_not_found(self, mock_exists):
        """Test the scan_folder_for_excel_files method when the folder is not found."""
        # Configure the mock to return False for os.path.exists
        mock_exists.return_value = False

        # Create an extractor
        extractor = ExcelExtractor("dummy_path.xlsx")

        # Expect a FileNotFoundError
        with pytest.raises(FileNotFoundError):
            extractor.scan_folder_for_excel_files("nonexistent_folder")

    @mock.patch("os.path.exists")
    @mock.patch("os.path.isdir")
    def test_scan_not_a_directory(self, mock_isdir, mock_exists):
        """Test the scan_folder_for_excel_files method when the path is not a directory."""
        # Configure the mocks
        mock_exists.return_value = True
        mock_isdir.return_value = False

        # Create an extractor
        extractor = ExcelExtractor("dummy_path.xlsx")

        # Expect a ValueError
        with pytest.raises(ValueError):
            extractor.scan_folder_for_excel_files("not_a_directory")

    def test_custom_mapping(self, temp_excel_file):
        """Test extracting data with a custom mapping."""
        # Create an extractor with the temporary file path
        extractor = ExcelExtractor(temp_excel_file)

        # Create a custom mapping
        custom_mapping = {
            "Company": "company_name",
            "Project": "project_name",
            "Value": "value",
            # Map to different field names than default
            "Probability (%)": "custom_fields.probability_pct",
            "Status": "custom_fields.status_text",
        }

        # Call the method with custom mapping
        result = extractor.extract_validated_data(
            sheet_name="Sheet1", mapping=custom_mapping
        )

        # Check the result
        assert isinstance(result, FunnelData)

        # Check that custom fields were populated
        entry = result.entries[0]
        assert "probability_pct" in entry.custom_fields
        assert "status_text" in entry.custom_fields
        assert entry.custom_fields["probability_pct"] == 80.0
        assert entry.custom_fields["status_text"] == "High"
